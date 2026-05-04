"""Minimal IBM service connectivity checks for local CrisisGrid validation.

The script intentionally avoids printing secrets or raw environment values.
It performs read-only Cloudant checks and a tiny watsonx generation probe.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from typing import Any

from app.core.config import settings


logging.basicConfig(level=logging.CRITICAL)


UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)


def sanitize(value: Any) -> str:
    """Return an error summary with common secret-like values redacted."""
    text = str(value)
    text = UUID_RE.sub("<uuid-redacted>", text)
    for secret in (
        settings.CLOUDANT_API_KEY,
        settings.WATSONX_API_KEY,
        settings.IBM_CLOUD_API_KEY,
    ):
        if secret:
            text = text.replace(secret, "<secret-redacted>")
    return text[:500]


def check_cloudant() -> dict[str, Any]:
    result: dict[str, Any] = {
        "enabled": bool(settings.CLOUDANT_ENABLED),
        "configured": bool(settings.CLOUDANT_URL and settings.CLOUDANT_API_KEY),
        "ok": False,
        "databases": {},
    }

    if not result["enabled"]:
        result["status"] = "skipped_disabled"
        return result

    if not result["configured"]:
        result["status"] = "misconfigured"
        return result

    try:
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        from ibmcloudant.cloudant_v1 import CloudantV1

        authenticator = IAMAuthenticator(settings.CLOUDANT_API_KEY)
        client = CloudantV1(authenticator=authenticator)
        client.set_service_url(settings.CLOUDANT_URL)

        server_info = client.get_server_information().get_result()
        result["server"] = {
            "reachable": True,
            "vendor": server_info.get("vendor", {}).get("name"),
            "version_present": bool(server_info.get("version")),
        }

        for db_name in (
            settings.CLOUDANT_DB_REPORTS,
            settings.CLOUDANT_DB_AGENT_LOGS,
            settings.CLOUDANT_DB_AUDIT_EVENTS,
        ):
            try:
                info = client.get_database_information(db=db_name).get_result()
                result["databases"][db_name] = {
                    "reachable": True,
                    "doc_count": info.get("doc_count"),
                }
            except Exception as exc:  # noqa: BLE001 - report sanitized diagnostics
                result["databases"][db_name] = {
                    "reachable": False,
                    "error": sanitize(exc),
                }

        result["ok"] = bool(result["server"]["reachable"]) and all(
            db.get("reachable") for db in result["databases"].values()
        )
        result["status"] = "ok" if result["ok"] else "partial"
    except Exception as exc:  # noqa: BLE001 - report sanitized diagnostics
        result["status"] = "failed"
        result["error"] = sanitize(exc)

    return result


def check_watsonx() -> dict[str, Any]:
    result: dict[str, Any] = {
        "enabled": bool(settings.WATSONX_ENABLED),
        "configured": bool(settings.WATSONX_API_KEY and settings.WATSONX_PROJECT_ID),
        "model_id_present": bool(settings.WATSONX_MODEL_ID),
        "ok": False,
    }

    if not result["enabled"]:
        result["status"] = "skipped_disabled"
        return result

    if not result["configured"]:
        result["status"] = "misconfigured"
        return result

    try:
        from ibm_watsonx_ai import APIClient, Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

        credentials = Credentials(
            url=settings.WATSONX_URL,
            api_key=settings.WATSONX_API_KEY,
        )
        client = APIClient(credentials)
        model = ModelInference(
            model_id=settings.WATSONX_MODEL_ID,
            api_client=client,
            project_id=settings.WATSONX_PROJECT_ID,
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 8,
                GenParams.MIN_NEW_TOKENS: 1,
            },
        )
        response = model.generate_text(
            prompt="Reply with exactly this token and nothing else: CRISISGRID_OK"
        )
        result["response_present"] = bool(str(response).strip())
        result["contains_expected_token"] = "CRISISGRID_OK" in str(response)
        result["ok"] = result["response_present"]
        result["status"] = "ok" if result["ok"] else "empty_response"
    except Exception as exc:  # noqa: BLE001 - report sanitized diagnostics
        result["status"] = "failed"
        result["error"] = sanitize(exc)

    return result


def check_iam_token() -> dict[str, Any]:
    result: dict[str, Any] = {
        "enabled": bool(settings.WATSONX_ENABLED),
        "configured": bool(settings.WATSONX_API_KEY and settings.WATSONX_IAM_URL),
        "ok": False,
    }

    if not result["enabled"]:
        result["status"] = "skipped_disabled"
        return result

    if not result["configured"]:
        result["status"] = "misconfigured"
        return result

    try:
        from app.services.ibm_auth import get_iam_token

        token = get_iam_token()
        result["ok"] = bool(token)
        result["status"] = "ok" if result["ok"] else "empty_token"
    except Exception as exc:  # noqa: BLE001 - report sanitized diagnostics
        result["status"] = "failed"
        result["error"] = sanitize(exc)

    return result


def main() -> int:
    checks = {
        "cloudant": check_cloudant(),
        "iam_token": check_iam_token(),
        "watsonx": check_watsonx(),
    }
    enabled_checks = [value for value in checks.values() if value["enabled"]]
    overall_ok = bool(enabled_checks) and all(value["ok"] for value in enabled_checks)
    payload = {
        "overall_ok": overall_ok,
        "checks": checks,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())

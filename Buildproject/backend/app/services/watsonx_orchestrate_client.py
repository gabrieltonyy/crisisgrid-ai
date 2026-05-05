"""Secret-safe watsonx Orchestrate client abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import re
import time
from typing import Any, Callable

import requests

from app.core.config import settings
from app.services.ibm_auth import IBMIAMTokenManager, IBMIAMTokenError
from app.services.orchestration_modes import resolve_orchestration_mode


logger = logging.getLogger(__name__)

SECRET_KEY_PATTERN = re.compile(
    r"(api[_-]?key|token|secret|password|authorization|bearer|jwt|credential)",
    re.IGNORECASE,
)
SECRET_VALUE_PATTERN = re.compile(
    r"(?i)(bearer\s+)[a-z0-9._\-]+|"
    r"\beyJ[a-zA-Z0-9._\-]{20,}\b"
)


@dataclass(frozen=True)
class WatsonxOrchestrateResult:
    success: bool
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    reason_code: str | None = None
    remote_run_id: str | None = None
    remote_workflow_id: str | None = None
    latency_ms: int | None = None
    error: str | None = None


class WatsonxOrchestrateClient:
    """Client wrapper that never logs or persists secret values."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        iam_url: str | None = None,
        workflow_id: str | None = None,
        timeout_seconds: int | None = None,
        post: Callable[..., Any] | None = None,
        token_manager: IBMIAMTokenManager | None = None,
    ) -> None:
        mode_settings = resolve_orchestration_mode(settings)
        self._base_url = base_url if base_url is not None else settings.ORCHESTRATE_API_URL
        self._api_key = api_key if api_key is not None else settings.ORCHESTRATE_API_KEY
        self._iam_url = iam_url if iam_url is not None else settings.ORCHESTRATE_IAM_URL
        self._workflow_id = workflow_id if workflow_id is not None else mode_settings.workflow_id
        self._timeout_seconds = timeout_seconds if timeout_seconds is not None else mode_settings.timeout_seconds
        self._post = post or requests.post
        self._token_manager = token_manager

    def is_configured(self) -> bool:
        return bool(self._base_url and self._api_key and self._workflow_id)

    def health_check(self) -> dict[str, Any]:
        """Return safe readiness information without probing an unknown endpoint."""

        return {
            "configured": self.is_configured(),
            "reachable": None,
            "probe_status": "not_probed",
        }

    def execute_report_workflow(self, context: dict[str, Any]) -> WatsonxOrchestrateResult:
        """Execute the configured Orchestrate workflow using a safe input contract."""

        started = time.monotonic()
        if not self.is_configured():
            return self._failure(
                "remote_not_configured",
                started,
                "watsonx Orchestrate is not configured",
            )

        try:
            token = self._get_token()
            response = self._post(
                self._base_url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={
                    "workflow_id": self._workflow_id,
                    "input": build_remote_report_input(context),
                },
                timeout=self._timeout_seconds,
            )
        except IBMIAMTokenError as exc:
            return self._failure("iam_token_unavailable", started, str(exc))
        except requests.Timeout:
            return self._failure("remote_timeout", started, "watsonx Orchestrate request timed out")
        except requests.RequestException:
            return self._failure("remote_request_failed", started, "watsonx Orchestrate request failed")

        if not getattr(response, "ok", False):
            return self._failure(
                f"remote_http_{getattr(response, 'status_code', 'error')}",
                started,
                "watsonx Orchestrate returned an unsuccessful response",
            )

        try:
            payload = response.json()
        except ValueError:
            return self._failure(
                "remote_invalid_json",
                started,
                "watsonx Orchestrate response was not valid JSON",
            )

        parsed = parse_remote_workflow_response(payload)
        if not parsed.success:
            return WatsonxOrchestrateResult(
                success=False,
                status="FAILED",
                output=parsed.output,
                reason_code=parsed.reason_code,
                remote_run_id=parsed.remote_run_id,
                remote_workflow_id=self._workflow_id,
                latency_ms=_latency_ms(started),
                error=parsed.error,
            )

        return WatsonxOrchestrateResult(
            success=True,
            status="SUCCESS",
            output=mask_sensitive(parsed.output),
            reason_code=parsed.reason_code,
            remote_run_id=parsed.remote_run_id,
            remote_workflow_id=self._workflow_id,
            latency_ms=_latency_ms(started),
        )

    def _get_token(self) -> str:
        manager = self._token_manager or IBMIAMTokenManager(
            api_key=self._api_key,
            iam_url=self._iam_url,
            timeout_seconds=float(self._timeout_seconds),
        )
        return manager.get_token()

    def _failure(self, reason_code: str, started: float, error: str) -> WatsonxOrchestrateResult:
        logger.info("watsonx Orchestrate unavailable: %s", reason_code)
        return WatsonxOrchestrateResult(
            success=False,
            status="FAILED",
            reason_code=reason_code,
            remote_workflow_id=self._workflow_id,
            latency_ms=_latency_ms(started),
            error=mask_sensitive(error),
        )


def build_remote_report_input(context: dict[str, Any]) -> dict[str, Any]:
    """Build the safe remote workflow input contract from local context."""

    report = context.get("report") or {}
    user_context = context.get("user_context") or {}
    return mask_sensitive(
        {
            "report_id": str(_field(report, "id", "")),
            "source": context.get("source", "api"),
            "incident_type": _enum_value(_field(report, "crisis_type", "")),
            "description": _sanitize_text(_field(report, "description", ""), 1000),
            "latitude": _float_or_none(_field(report, "latitude")),
            "longitude": _float_or_none(_field(report, "longitude")),
            "location_text": _sanitize_text(_field(report, "location_text"), 255),
            "image_url_present": bool(_field(report, "image_url")),
            "video_url_present": bool(_field(report, "video_url")),
            "is_anonymous": bool(_field(report, "is_anonymous", False)),
            "user_context": {
                "authenticated": bool(user_context.get("authenticated")),
                "user_id": user_context.get("user_id"),
                "role": user_context.get("role"),
            },
            "current_context": {
                "cloudant_enabled": bool(context.get("cloudant_enabled")),
            },
        }
    )


def parse_remote_workflow_response(payload: Any) -> WatsonxOrchestrateResult:
    """Parse only the supported remote output contract shapes."""

    if not isinstance(payload, dict):
        return WatsonxOrchestrateResult(
            success=False,
            status="FAILED",
            reason_code="remote_output_contract_unrecognized",
            error="Remote response was not an object",
        )

    candidate = payload.get("output") or payload.get("result") or payload.get("crisisgrid_result")
    if not isinstance(candidate, dict):
        candidate = payload

    status_value = str(candidate.get("status") or payload.get("status") or "").upper()
    if status_value not in {"SUCCESS", "COMPLETED", "OK", "VERIFIED", "REVIEW"}:
        return WatsonxOrchestrateResult(
            success=False,
            status="FAILED",
            output=mask_sensitive(candidate),
            reason_code="remote_output_contract_unrecognized",
            remote_run_id=_string_or_none(payload.get("run_id") or payload.get("id")),
            error="Remote response did not match the CrisisGrid output contract",
        )

    confidence = _first_number(candidate, ["confidence", "confidence_score", "final_confidence_score"])
    severity = _first_number(candidate, ["severity", "severity_score", "final_severity_score"])
    if confidence is None or severity is None:
        return WatsonxOrchestrateResult(
            success=False,
            status="FAILED",
            output=mask_sensitive(candidate),
            reason_code="remote_output_contract_unrecognized",
            remote_run_id=_string_or_none(payload.get("run_id") or payload.get("id")),
            error="Remote response was missing confidence or severity",
        )

    output = {
        "confidence": _normalize_confidence(confidence),
        "severity_score": severity,
        "decision": candidate.get("decision") or candidate.get("report_status") or status_value,
        "report_status": candidate.get("report_status"),
        "incident_id": candidate.get("incident_id"),
        "alert_recommendation": candidate.get("alert_recommendation"),
        "dispatch_recommendation": candidate.get("dispatch_recommendation"),
        "admin_review_required": bool(candidate.get("admin_review_required", status_value == "REVIEW")),
        "reason_codes": candidate.get("reason_codes") or candidate.get("reason_code") or [],
        "orchestrator_provider": "watsonx_orchestrate",
    }
    return WatsonxOrchestrateResult(
        success=True,
        status="SUCCESS",
        output=mask_sensitive(output),
        reason_code="remote_success",
        remote_run_id=_string_or_none(
            payload.get("run_id") or payload.get("id") or candidate.get("remote_run_id")
        ),
    )


def mask_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "***MASKED***" if SECRET_KEY_PATTERN.search(str(key)) else mask_sensitive(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [mask_sensitive(item) for item in value]
    if isinstance(value, tuple):
        return tuple(mask_sensitive(item) for item in value)
    if isinstance(value, str):
        return SECRET_VALUE_PATTERN.sub("***MASKED***", value)
    return value


def _field(source: Any, name: str, default: Any = None) -> Any:
    if isinstance(source, dict):
        return source.get(name, default)
    return getattr(source, name, default)


def _enum_value(value: Any) -> Any:
    return getattr(value, "value", value)


def _sanitize_text(value: Any, max_length: int) -> str | None:
    if value is None:
        return None
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", str(value))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_length]


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_number(source: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        value = source.get(key)
        if value is not None:
            return _float_or_none(value)
    return None


def _normalize_confidence(value: float) -> float:
    return value / 100 if value > 1 else value


def _string_or_none(value: Any) -> str | None:
    return str(value) if value is not None else None


def _latency_ms(started: float) -> int:
    return int((time.monotonic() - started) * 1000)


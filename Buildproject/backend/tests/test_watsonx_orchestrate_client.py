"""Tests for the watsonx Orchestrate client abstraction."""

import requests

from app.services.watsonx_orchestrate_client import (
    WatsonxOrchestrateClient,
    build_remote_report_input,
    mask_sensitive,
)


class FakeTokenManager:
    def get_token(self):
        return "iam-token"


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.ok = 200 <= status_code < 300

    def json(self):
        return self._payload


def test_client_reports_not_configured_without_endpoint():
    client = WatsonxOrchestrateClient(base_url="", api_key="secret", workflow_id="workflow")

    assert client.is_configured() is False
    result = client.execute_report_workflow({})
    assert result.success is False
    assert result.reason_code == "remote_not_configured"
    assert "secret" not in (result.error or "")


def test_execute_report_workflow_success_maps_supported_contract():
    calls = []

    def fake_post(url, headers, json, timeout):
        calls.append((url, headers, json, timeout))
        return FakeResponse(
            {
                "run_id": "remote-run-1",
                "status": "SUCCESS",
                "output": {
                    "status": "SUCCESS",
                    "confidence": 0.86,
                    "severity_score": 91,
                    "decision": "VERIFIED",
                    "incident_id": "incident_remote_1",
                    "admin_review_required": False,
                },
            }
        )

    client = WatsonxOrchestrateClient(
        base_url="https://orchestrate.example.test/run",
        api_key="secret",
        workflow_id="workflow-1",
        post=fake_post,
        token_manager=FakeTokenManager(),
    )

    result = client.execute_report_workflow({"report": {"id": "report-1"}})

    assert result.success is True
    assert result.remote_run_id == "remote-run-1"
    assert result.remote_workflow_id == "workflow-1"
    assert result.output["confidence"] == 0.86
    assert result.output["incident_id"] == "incident_remote_1"
    assert calls[0][0] == "https://orchestrate.example.test/run"
    assert calls[0][2]["workflow_id"] == "workflow-1"


def test_unrecognized_remote_contract_fails_safely():
    def fake_post(url, headers, json, timeout):
        return FakeResponse({"message": "accepted but no CrisisGrid result"})

    client = WatsonxOrchestrateClient(
        base_url="https://orchestrate.example.test/run",
        api_key="secret",
        workflow_id="workflow-1",
        post=fake_post,
        token_manager=FakeTokenManager(),
    )

    result = client.execute_report_workflow({"report": {"id": "report-1"}})

    assert result.success is False
    assert result.reason_code == "remote_output_contract_unrecognized"


def test_timeout_error_is_sanitized():
    def fake_post(url, headers, json, timeout):
        raise requests.Timeout("timed out with super-secret-api-key")

    client = WatsonxOrchestrateClient(
        base_url="https://orchestrate.example.test/run",
        api_key="super-secret-api-key",
        workflow_id="workflow-1",
        post=fake_post,
        token_manager=FakeTokenManager(),
    )

    result = client.execute_report_workflow({"report": {"id": "report-1"}})

    assert result.success is False
    assert result.reason_code == "remote_timeout"
    assert "super-secret-api-key" not in (result.error or "")


def test_remote_input_contract_uses_safe_fields_only():
    payload = build_remote_report_input(
        {
            "report": {
                "id": "report-1",
                "crisis_type": "FIRE",
                "description": " Smoke near market ",
                "latitude": "1.1",
                "longitude": "2.2",
                "location_text": "Market",
                "image_url": "https://example.test/image.jpg",
                "is_anonymous": True,
                "api_key": "secret",
            },
            "user_context": {
                "authenticated": True,
                "user_id": "user-1",
                "role": "CITIZEN",
                "jwt": "secret-token",
            },
        }
    )

    assert payload["report_id"] == "report-1"
    assert payload["incident_type"] == "FIRE"
    assert payload["description"] == "Smoke near market"
    assert payload["image_url_present"] is True
    assert "api_key" not in payload
    assert "jwt" not in payload["user_context"]


def test_mask_sensitive_masks_nested_secret_values():
    masked = mask_sensitive(
        {
            "token": "secret-token",
            "message": "Authorization: Bearer abcdefghijklmnopqrstuvwxyz",
        }
    )

    assert masked["token"] == "***MASKED***"
    assert "abcdefghijklmnopqrstuvwxyz" not in masked["message"]

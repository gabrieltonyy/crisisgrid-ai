"""Tests for the IBM Cloud IAM token manager."""

from __future__ import annotations

import pytest
import requests

from app.services.ibm_auth import IBMIAMTokenError, IBMIAMTokenManager


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.ok = 200 <= status_code < 300

    def json(self):
        return self._payload


def test_missing_api_key_raises_error():
    manager = IBMIAMTokenManager(api_key="", iam_url="https://iam.cloud.ibm.com/identity/token")

    with pytest.raises(IBMIAMTokenError, match="missing WATSONX_API_KEY"):
        manager.get_token()


def test_successful_token_request_returns_token(monkeypatch):
    calls = []

    def fake_post(url, headers, data, timeout):
        calls.append((url, headers, data, timeout))
        return FakeResponse(payload={"access_token": "token-123", "expires_in": 3600})

    monkeypatch.setattr("app.services.ibm_auth.requests.post", fake_post)
    manager = IBMIAMTokenManager(api_key="api-key", iam_url="https://iam.example/token")

    assert manager.get_token() == "token-123"
    assert len(calls) == 1
    assert calls[0][0] == "https://iam.example/token"
    assert calls[0][1]["Content-Type"] == "application/x-www-form-urlencoded"
    assert calls[0][2]["grant_type"] == manager.GRANT_TYPE
    assert calls[0][2]["apikey"] == "api-key"


def test_repeated_call_uses_cached_token(monkeypatch):
    calls = 0

    def fake_post(url, headers, data, timeout):
        nonlocal calls
        calls += 1
        return FakeResponse(payload={"access_token": "cached-token", "expires_in": 3600})

    monkeypatch.setattr("app.services.ibm_auth.requests.post", fake_post)
    manager = IBMIAMTokenManager(api_key="api-key", iam_url="https://iam.example/token")

    assert manager.get_token() == "cached-token"
    assert manager.get_token() == "cached-token"
    assert calls == 1


def test_expired_token_triggers_refresh(monkeypatch):
    tokens = iter(["token-1", "token-2"])

    def fake_post(url, headers, data, timeout):
        return FakeResponse(payload={"access_token": next(tokens), "expires_in": 3600})

    monkeypatch.setattr("app.services.ibm_auth.requests.post", fake_post)
    manager = IBMIAMTokenManager(api_key="api-key", iam_url="https://iam.example/token")

    assert manager.get_token() == "token-1"
    manager._expiry_time = 0.0
    assert manager.get_token() == "token-2"


def test_http_error_is_sanitized(monkeypatch):
    def fake_post(url, headers, data, timeout):
        return FakeResponse(status_code=403, payload={"error": "secret body"})

    monkeypatch.setattr("app.services.ibm_auth.requests.post", fake_post)
    manager = IBMIAMTokenManager(api_key="super-secret-api-key", iam_url="https://iam.example/token")

    with pytest.raises(IBMIAMTokenError) as exc_info:
        manager.get_token()

    message = str(exc_info.value)
    assert "HTTP 403" in message
    assert "super-secret-api-key" not in message
    assert "secret body" not in message


def test_malformed_response_is_sanitized(monkeypatch):
    def fake_post(url, headers, data, timeout):
        return FakeResponse(payload={"not_access_token": "no-token"})

    monkeypatch.setattr("app.services.ibm_auth.requests.post", fake_post)
    manager = IBMIAMTokenManager(api_key="super-secret-api-key", iam_url="https://iam.example/token")

    with pytest.raises(IBMIAMTokenError) as exc_info:
        manager.get_token()

    message = str(exc_info.value)
    assert "access token" in message
    assert "super-secret-api-key" not in message


def test_timeout_error_is_sanitized(monkeypatch):
    def fake_post(url, headers, data, timeout):
        raise requests.Timeout("request timed out with super-secret-api-key")

    monkeypatch.setattr("app.services.ibm_auth.requests.post", fake_post)
    manager = IBMIAMTokenManager(api_key="super-secret-api-key", iam_url="https://iam.example/token")

    with pytest.raises(IBMIAMTokenError) as exc_info:
        manager.get_token()

    message = str(exc_info.value)
    assert "timed out" in message
    assert "super-secret-api-key" not in message

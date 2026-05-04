"""IBM Cloud IAM token management for watsonx REST integrations.

This module keeps IAM access tokens in process memory only. It never logs,
prints, persists, or exposes API keys or tokens outside the return value of
``get_iam_token``.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

import requests

from app.core.config import settings


logger = logging.getLogger(__name__)


class IBMIAMTokenError(RuntimeError):
    """Raised when an IBM IAM token cannot be obtained safely."""


class IBMIAMTokenManager:
    """Thread-safe in-memory IBM Cloud IAM access token cache."""

    GRANT_TYPE = "urn:ibm:params:oauth:grant-type:apikey"
    DEFAULT_EXPIRES_IN_SECONDS = 3600
    DEFAULT_REFRESH_BUFFER_SECONDS = 100
    MIN_CACHE_SECONDS = 60

    def __init__(
        self,
        api_key: str | None = settings.WATSONX_API_KEY,
        iam_url: str | None = settings.WATSONX_IAM_URL,
        timeout_seconds: float = 10.0,
        refresh_buffer_seconds: int = DEFAULT_REFRESH_BUFFER_SECONDS,
    ) -> None:
        self._api_key = api_key
        self._iam_url = iam_url
        self._timeout_seconds = timeout_seconds
        self._refresh_buffer_seconds = refresh_buffer_seconds
        self._access_token: str | None = None
        self._expiry_time: float = 0.0
        self._lock = threading.RLock()

    def _has_valid_cached_token(self) -> bool:
        return bool(self._access_token) and time.monotonic() < self._expiry_time

    def _request_new_token(self) -> str:
        """Request a new IAM token from IBM Cloud and update the cache."""
        if not self._api_key:
            raise IBMIAMTokenError("IBM IAM token request is not configured: missing WATSONX_API_KEY")

        if not self._iam_url:
            raise IBMIAMTokenError("IBM IAM token request is not configured: missing WATSONX_IAM_URL")

        try:
            response = requests.post(
                self._iam_url,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": self.GRANT_TYPE,
                    "apikey": self._api_key,
                },
                timeout=self._timeout_seconds,
            )
        except requests.Timeout as exc:
            raise IBMIAMTokenError("IBM IAM token request timed out") from exc
        except requests.RequestException as exc:
            raise IBMIAMTokenError("IBM IAM token request failed") from exc

        if not response.ok:
            raise IBMIAMTokenError(
                f"IBM IAM token request failed with HTTP {response.status_code}"
            )

        try:
            payload: dict[str, Any] = response.json()
        except ValueError as exc:
            raise IBMIAMTokenError("IBM IAM token response was not valid JSON") from exc

        access_token = payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise IBMIAMTokenError("IBM IAM token response did not include an access token")

        expires_in = payload.get("expires_in", self.DEFAULT_EXPIRES_IN_SECONDS)
        try:
            expires_in_seconds = int(expires_in)
        except (TypeError, ValueError):
            expires_in_seconds = self.DEFAULT_EXPIRES_IN_SECONDS

        cache_seconds = max(
            self.MIN_CACHE_SECONDS,
            expires_in_seconds - self._refresh_buffer_seconds,
        )
        self._access_token = access_token
        self._expiry_time = time.monotonic() + cache_seconds
        logger.debug("IBM IAM token cache refreshed")
        return access_token

    def get_token(self) -> str:
        """Return a currently valid IBM IAM token, refreshing when needed."""
        if self._has_valid_cached_token():
            return self._access_token or ""

        with self._lock:
            if self._has_valid_cached_token():
                return self._access_token or ""
            return self._request_new_token()


token_manager = IBMIAMTokenManager()


def get_iam_token() -> str:
    """Return an IBM Cloud IAM bearer token for watsonx REST calls."""
    return token_manager.get_token()


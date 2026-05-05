"""Tests for secret-safe watsonx Orchestrate health reporting."""

from __future__ import annotations

import json

import pytest

from app.api.routes import health as health_routes


class FakeSettings:
    APP_NAME = "CrisisGrid AI"
    APP_ENV = "test"

    CLOUDANT_ENABLED = False
    CLOUDANT_URL = None
    CLOUDANT_API_KEY = None
    WATSONX_ENABLED = False
    WATSONX_API_KEY = None
    WATSONX_PROJECT_ID = None
    WEATHER_ENABLED = False
    WEATHER_API_KEY = None
    SMS_ENABLED = False
    SMS_API_KEY = None

    AGENT_MODE = "local"
    ENABLE_SIMULATED_VERIFICATION = True
    ENABLE_SIMULATED_DISPATCH = True
    ENABLE_AGENT_RUN_LOGS = True

    ORCHESTRATE_ENABLED = True
    ORCHESTRATE_MODE = "local"
    ORCHESTRATE_API_URL = None
    ORCHESTRATE_API_KEY = None
    ORCHESTRATE_TIMEOUT_SECONDS = 15
    ORCHESTRATE_FALLBACK_TO_LOCAL = True
    ORCHESTRATE_PIPELINE_ID = "crisisgrid-main-pipeline"
    ORCHESTRATE_PIPELINE_CONFIG = "orchestration/pipeline.yaml"

    def validate_required_services(self):
        return {
            "postgres": True,
            "cloudant": False,
            "watsonx": False,
            "watsonx_orchestrate": self.ORCHESTRATE_ENABLED,
            "weather": False,
            "sms": False,
        }


def _patch_connected_database(monkeypatch):
    monkeypatch.setattr(health_routes, "check_db_connection", lambda: True)
    monkeypatch.setattr(
        health_routes,
        "get_db_info",
        lambda: {"connected": True, "database": "test"},
    )


@pytest.mark.asyncio
async def test_health_reports_local_ready_when_local_mode_has_remote_config(monkeypatch):
    settings = FakeSettings()
    settings.ORCHESTRATE_API_URL = "https://orchestrate.example.test"
    settings.ORCHESTRATE_API_KEY = "secret-key"
    _patch_connected_database(monkeypatch)

    response = await health_routes.health_check(settings=settings)

    assert response["services"]["watsonx_orchestrate"] == "local_ready"


@pytest.mark.asyncio
async def test_health_reports_hybrid_ready_when_hybrid_pipeline_and_remote_config_exist(monkeypatch):
    settings = FakeSettings()
    settings.ORCHESTRATE_MODE = "hybrid"
    settings.ORCHESTRATE_API_URL = "https://orchestrate.example.test"
    settings.ORCHESTRATE_API_KEY = "secret-key"
    _patch_connected_database(monkeypatch)

    response = await health_routes.health_check(settings=settings)

    assert response["services"]["watsonx_orchestrate"] == "hybrid_ready"


@pytest.mark.asyncio
async def test_health_reports_local_ready_without_remote_config(monkeypatch):
    settings = FakeSettings()
    _patch_connected_database(monkeypatch)

    response = await health_routes.health_check(settings=settings)

    assert response["services"]["watsonx_orchestrate"] == "local_ready"


@pytest.mark.asyncio
async def test_health_reports_misconfigured_for_invalid_local_pipeline(monkeypatch):
    settings = FakeSettings()
    settings.ORCHESTRATE_PIPELINE_CONFIG = "orchestration/missing-pipeline.yaml"
    _patch_connected_database(monkeypatch)

    response = await health_routes.health_check(settings=settings)

    assert response["services"]["watsonx_orchestrate"] == "misconfigured"


@pytest.mark.asyncio
async def test_detailed_health_includes_safe_orchestrate_metadata(monkeypatch):
    settings = FakeSettings()
    settings.ORCHESTRATE_API_URL = "https://orchestrate.example.test"
    settings.ORCHESTRATE_API_KEY = "secret-key"
    _patch_connected_database(monkeypatch)

    body = await health_routes.detailed_health_check(settings=settings)

    assert body["orchestrate"] == {
        "enabled": True,
        "mode": "local",
        "status": "local_ready",
        "pipeline_id": "crisisgrid-main-pipeline",
        "pipeline_valid": True,
        "registered_agent_count": 7,
        "remote_configured": True,
        "remote_reachable": None,
        "last_probe_status": "not_probed",
        "current_execution_mode": "local",
        "fallback_to_local": True,
    }

    serialized = json.dumps(body)
    assert "https://orchestrate.example.test" not in serialized
    assert "secret-key" not in serialized

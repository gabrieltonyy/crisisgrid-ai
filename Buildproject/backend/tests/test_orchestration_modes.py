"""Tests for orchestration mode resolution."""

from types import SimpleNamespace

from app.services.orchestration_modes import resolve_orchestration_mode


def _settings(**overrides):
    values = {
        "ORCHESTRATE_ENABLED": True,
        "ORCHESTRATE_MODE": "local",
        "ORCHESTRATE_API_URL": None,
        "ORCHESTRATE_API_KEY": None,
        "ORCHESTRATE_PIPELINE_ID": "crisisgrid-main-pipeline",
        "ORCHESTRATE_TIMEOUT_SECONDS": 15,
        "ORCHESTRATE_FALLBACK_TO_LOCAL": True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_local_is_safe_default_for_invalid_mode():
    resolved = resolve_orchestration_mode(_settings(ORCHESTRATE_MODE="unexpected"))

    assert resolved.mode == "local"
    assert resolved.enabled is True


def test_remote_configured_requires_url_key_and_workflow_id():
    resolved = resolve_orchestration_mode(
        _settings(
            ORCHESTRATE_MODE="hybrid",
            ORCHESTRATE_API_URL="https://orchestrate.example.test",
            ORCHESTRATE_API_KEY="secret",
        )
    )

    assert resolved.mode == "hybrid"
    assert resolved.remote_configured is True
    assert resolved.workflow_id == "crisisgrid-main-pipeline"


def test_remote_not_configured_without_api_key():
    resolved = resolve_orchestration_mode(
        _settings(
            ORCHESTRATE_MODE="remote",
            ORCHESTRATE_API_URL="https://orchestrate.example.test",
            ORCHESTRATE_API_KEY=None,
        )
    )

    assert resolved.mode == "remote"
    assert resolved.remote_configured is False


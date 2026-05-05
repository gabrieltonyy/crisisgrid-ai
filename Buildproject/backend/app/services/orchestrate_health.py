"""Safe health metadata for the watsonx Orchestrate control plane."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from app.core.agent_registry import get_agent_registry
from app.core.config import Settings
from app.schemas.agents import PipelineConfig
from app.services.orchestration_modes import resolve_orchestration_mode


SUCCESS_STATUSES = {"hybrid_ready", "local_ready", "remote_configured", "remote_reachable"}


def get_orchestrate_health(settings: Settings) -> dict[str, Any]:
    """Return secret-safe watsonx Orchestrate health metadata."""

    mode_settings = resolve_orchestration_mode(settings)
    enabled = mode_settings.enabled
    mode = mode_settings.mode
    remote_configured = mode_settings.remote_configured
    pipeline_valid = False
    pipeline_id = settings.ORCHESTRATE_PIPELINE_ID
    registered_agent_count = 0
    remote_reachable = None
    last_probe_status = "not_probed"

    if not enabled:
        return {
            "enabled": False,
            "mode": mode,
            "status": "disabled",
            "pipeline_id": pipeline_id,
            "pipeline_valid": False,
            "registered_agent_count": 0,
            "remote_configured": remote_configured,
            "remote_reachable": remote_reachable,
            "last_probe_status": last_probe_status,
            "current_execution_mode": mode,
            "fallback_to_local": mode_settings.fallback_to_local,
        }

    if mode in {"local", "hybrid"}:
        validation = validate_local_pipeline(settings.ORCHESTRATE_PIPELINE_CONFIG)
        pipeline_valid = validation["pipeline_valid"]
        pipeline_id = validation["pipeline_id"] or pipeline_id
        registered_agent_count = validation["registered_agent_count"]

    if mode == "local":
        if pipeline_valid:
            status = "local_ready"
        else:
            status = "misconfigured"
    elif mode == "hybrid":
        if pipeline_valid and remote_configured:
            status = "hybrid_ready"
        elif pipeline_valid and mode_settings.fallback_to_local:
            status = "local_ready"
        else:
            status = "misconfigured"
    elif remote_configured:
        status = "remote_configured"
    else:
        status = "misconfigured"

    return {
        "enabled": enabled,
        "mode": mode,
        "status": status,
        "pipeline_id": pipeline_id,
        "pipeline_valid": pipeline_valid,
        "registered_agent_count": registered_agent_count,
        "remote_configured": remote_configured,
        "remote_reachable": remote_reachable,
        "last_probe_status": last_probe_status,
        "current_execution_mode": mode,
        "fallback_to_local": mode_settings.fallback_to_local,
    }


def validate_local_pipeline(pipeline_path: str | Path) -> dict[str, Any]:
    """Validate the local orchestration pipeline without executing agents."""

    registry = get_agent_registry()
    registered_agent_count = len(registry)

    try:
        with _resolve_pipeline_path(pipeline_path).open("r", encoding="utf-8") as pipeline_file:
            payload = yaml.safe_load(pipeline_file) or {}
        pipeline = PipelineConfig.model_validate(payload)
    except (OSError, ValidationError, yaml.YAMLError):
        return {
            "pipeline_valid": False,
            "pipeline_id": None,
            "registered_agent_count": registered_agent_count,
        }

    unknown_agents = [step.name for step in pipeline.agents if step.name not in registry]

    return {
        "pipeline_valid": not unknown_agents,
        "pipeline_id": pipeline.pipeline_id,
        "registered_agent_count": registered_agent_count,
    }


def _resolve_pipeline_path(pipeline_path: str | Path) -> Path:
    path = Path(pipeline_path)
    if path.is_absolute() or path.exists():
        return path

    backend_root = Path(__file__).resolve().parents[2]
    backend_relative_path = backend_root / path
    if backend_relative_path.exists():
        return backend_relative_path

    return path

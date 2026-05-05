"""Mode resolution for CrisisGrid orchestration execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.core.config import Settings


OrchestrationMode = Literal["local", "remote", "hybrid"]


@dataclass(frozen=True)
class OrchestrationModeSettings:
    enabled: bool
    mode: OrchestrationMode
    remote_configured: bool
    fallback_to_local: bool
    timeout_seconds: int
    workflow_id: str


def resolve_orchestration_mode(settings: Settings) -> OrchestrationModeSettings:
    """Resolve orchestration settings with local as the safe default."""

    raw_mode = (settings.ORCHESTRATE_MODE or "local").lower().strip()
    mode: OrchestrationMode = raw_mode if raw_mode in {"local", "remote", "hybrid"} else "local"  # type: ignore[assignment]
    workflow_id = settings.ORCHESTRATE_PIPELINE_ID
    remote_configured = bool(
        settings.ORCHESTRATE_ENABLED
        and settings.ORCHESTRATE_API_URL
        and settings.ORCHESTRATE_API_KEY
        and workflow_id
    )

    return OrchestrationModeSettings(
        enabled=bool(settings.ORCHESTRATE_ENABLED),
        mode=mode,
        remote_configured=remote_configured,
        fallback_to_local=bool(settings.ORCHESTRATE_FALLBACK_TO_LOCAL),
        timeout_seconds=max(1, int(settings.ORCHESTRATE_TIMEOUT_SECONDS or 15)),
        workflow_id=workflow_id,
    )


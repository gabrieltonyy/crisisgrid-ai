"""Persistence helpers for orchestration pipeline traces."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun
from app.schemas.agents import PipelineExecutionTrace
from app.schemas.common import AgentName, AgentRunStatus
from app.services.cloudant_service import cloudant_service
from app.utils.ids import generate_agent_run_id


logger = logging.getLogger(__name__)


def persist_pipeline_trace(
    db: Session,
    report_id: UUID,
    trace: PipelineExecutionTrace,
) -> dict[str, Any]:
    """Persist a pipeline trace to PostgreSQL and Cloudant without failing the request."""

    payload = trace.model_dump(mode="json")
    result: dict[str, Any] = {
        "postgres_agent_run_id": None,
        "cloudant_log_id": None,
        "errors": [],
    }

    postgres_run_id = _persist_trace_to_postgres(db, report_id, trace, payload)
    result["postgres_agent_run_id"] = postgres_run_id
    if postgres_run_id is None:
        result["errors"].append("postgres_trace_persist_failed")

    cloudant_log_id = _persist_trace_to_cloudant(report_id, trace, payload)
    result["cloudant_log_id"] = cloudant_log_id
    if cloudant_service.enabled and cloudant_log_id is None:
        result["errors"].append("cloudant_trace_persist_failed")

    return result


def _persist_trace_to_postgres(
    db: Session,
    report_id: UUID,
    trace: PipelineExecutionTrace,
    payload: dict[str, Any],
) -> str | None:
    try:
        run_id = generate_agent_run_id("orchestrator")
        confidence = _normalize_confidence(trace.context.get("confidence"))
        started_at = trace.started_at
        completed_at = trace.completed_at
        duration_seconds = (completed_at - started_at).total_seconds()
        status = (
            AgentRunStatus.COMPLETED
            if trace.status == "SUCCESS"
            else AgentRunStatus.FAILED
        )

        execution_mode = trace.context.get("execution_mode", trace.mode)
        provider = trace.context.get("orchestrator_provider", "local")
        remote_workflow_id = trace.context.get("remote_workflow_id")
        remote_run_id = trace.context.get("remote_run_id")
        reason_code = trace.context.get("remote_reason_code")
        latency_ms = trace.context.get("latency_ms")

        agent_run = AgentRun(
            run_id=run_id,
            agent_name=AgentName.ANALYTICS_AGENT,
            status=status,
            report_id=report_id,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
            input_data={
                "pipeline_id": trace.pipeline_id,
                "mode": trace.mode,
                "execution_mode": execution_mode,
                "orchestrator_provider": provider,
                "remote_workflow_id": remote_workflow_id,
            },
            output_data=payload,
            confidence_score=confidence,
            decision=trace.status,
            retry_count=sum(step.attempts for step in trace.steps),
            tags=[
                "orchestration",
                str(provider),
                str(execution_mode),
                trace.pipeline_id,
            ],
            notes=(
                "Orchestration pipeline trace"
                f" provider={provider}"
                f" mode={execution_mode}"
                f" remote_run_id={remote_run_id or 'none'}"
                f" reason={reason_code or 'none'}"
                f" latency_ms={latency_ms if latency_ms is not None else 'none'}"
            ),
        )

        db.add(agent_run)
        db.commit()
        return run_id
    except Exception as exc:
        db.rollback()
        logger.error("Failed to persist pipeline trace to PostgreSQL: %s", exc)
        return None


def _persist_trace_to_cloudant(
    report_id: UUID,
    trace: PipelineExecutionTrace,
    payload: dict[str, Any],
) -> str | None:
    try:
        return cloudant_service.store_agent_log(
            agent_run_id=f"pipeline_{report_id}",
            agent_type=str(trace.context.get("orchestrator_provider", "orchestrator_engine")),
            payload={
                "report_id": str(report_id),
                "pipeline_id": trace.pipeline_id,
                "status": trace.status,
                "execution_mode": trace.context.get("execution_mode", trace.mode),
                "orchestrator_provider": trace.context.get("orchestrator_provider", "local"),
                "remote_workflow_id": trace.context.get("remote_workflow_id"),
                "remote_run_id": trace.context.get("remote_run_id"),
                "remote_reason_code": trace.context.get("remote_reason_code"),
                "latency_ms": trace.context.get("latency_ms"),
                "admin_review_required": trace.context.get("admin_review_required", False),
                "trace": payload,
            },
        )
    except Exception as exc:
        logger.error("Failed to persist pipeline trace to Cloudant: %s", exc)
        return None


def _normalize_confidence(value: Any) -> float | None:
    if value is None:
        return None
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return None
    return confidence * 100 if confidence <= 1 else confidence

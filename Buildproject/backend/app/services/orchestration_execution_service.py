"""Execution coordinator for local, remote, and hybrid orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.agents import AgentExecutionResult, PipelineExecutionTrace, PipelineStepTrace
from app.schemas.common import IncidentStatus
from app.services.orchestration_modes import resolve_orchestration_mode
from app.services.orchestrator_engine import OrchestratorEngine
from app.services.watsonx_orchestrate_client import (
    WatsonxOrchestrateClient,
    WatsonxOrchestrateResult,
    mask_sensitive,
)
from app.utils.time import utc_now


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OrchestrationExecutionResult:
    trace: PipelineExecutionTrace
    processing_status: str
    execution_mode: str
    orchestrator_provider: str
    fallback_used: bool = False


class OrchestrationExecutionService:
    """Coordinate report orchestration without breaking report persistence."""

    def __init__(
        self,
        remote_client: WatsonxOrchestrateClient | None = None,
        local_engine_factory: Any = OrchestratorEngine,
    ) -> None:
        self.remote_client = remote_client or WatsonxOrchestrateClient()
        self.local_engine_factory = local_engine_factory

    def execute(
        self,
        context: dict[str, Any],
        db: Session,
        report: Any,
    ) -> OrchestrationExecutionResult:
        mode_settings = resolve_orchestration_mode(settings)

        if not mode_settings.enabled or mode_settings.mode == "local":
            trace = self._run_local(context, execution_mode="local")
            return OrchestrationExecutionResult(
                trace=trace,
                processing_status=_determine_processing_status(trace),
                execution_mode="local",
                orchestrator_provider="local",
            )

        if mode_settings.mode == "remote":
            remote_result = self._run_remote(context)
            if remote_result.success:
                trace = self._remote_trace(remote_result)
                self._apply_remote_output(db, report, remote_result.output)
                return OrchestrationExecutionResult(
                    trace=trace,
                    processing_status=_remote_processing_status(trace),
                    execution_mode="remote",
                    orchestrator_provider="watsonx_orchestrate",
                )
            trace = self._remote_failure_trace(remote_result, mode="remote")
            return OrchestrationExecutionResult(
                trace=trace,
                processing_status="PROCESSED_WITH_REVIEW",
                execution_mode="remote",
                orchestrator_provider="watsonx_orchestrate",
            )

        if mode_settings.remote_configured:
            remote_result = self._run_remote(context)
            if remote_result.success:
                trace = self._remote_trace(remote_result)
                self._apply_remote_output(db, report, remote_result.output)
                return OrchestrationExecutionResult(
                    trace=trace,
                    processing_status=_remote_processing_status(trace),
                    execution_mode="remote",
                    orchestrator_provider="watsonx_orchestrate",
                )

            if mode_settings.fallback_to_local:
                trace = self._run_local(
                    {
                        **context,
                        "remote_orchestration_failed": True,
                        "remote_reason_code": remote_result.reason_code,
                    },
                    execution_mode="hybrid_fallback",
                    remote_result=remote_result,
                )
                return OrchestrationExecutionResult(
                    trace=trace,
                    processing_status=_fallback_processing_status(trace),
                    execution_mode="hybrid_fallback",
                    orchestrator_provider="local",
                    fallback_used=True,
                )

            trace = self._remote_failure_trace(remote_result, mode="remote")
            return OrchestrationExecutionResult(
                trace=trace,
                processing_status="PROCESSED_WITH_REVIEW",
                execution_mode="remote",
                orchestrator_provider="watsonx_orchestrate",
            )

        if mode_settings.fallback_to_local:
            trace = self._run_local(
                {
                    **context,
                    "remote_orchestration_failed": True,
                    "remote_reason_code": "remote_not_configured",
                },
                execution_mode="hybrid_fallback",
            )
            return OrchestrationExecutionResult(
                trace=trace,
                processing_status=_fallback_processing_status(trace),
                execution_mode="hybrid_fallback",
                orchestrator_provider="local",
                fallback_used=True,
            )

        remote_result = WatsonxOrchestrateResult(
            success=False,
            status="FAILED",
            reason_code="remote_not_configured",
            remote_workflow_id=mode_settings.workflow_id,
            error="watsonx Orchestrate is not configured",
        )
        trace = self._remote_failure_trace(remote_result, mode="remote")
        return OrchestrationExecutionResult(
            trace=trace,
            processing_status="PROCESSED_WITH_REVIEW",
            execution_mode="remote",
            orchestrator_provider="watsonx_orchestrate",
        )

    def _run_local(
        self,
        context: dict[str, Any],
        execution_mode: str,
        remote_result: WatsonxOrchestrateResult | None = None,
    ) -> PipelineExecutionTrace:
        trace = self.local_engine_factory().run(context)
        trace.mode = execution_mode  # type: ignore[assignment]
        trace.context["execution_mode"] = execution_mode
        trace.context["orchestrator_provider"] = "local"
        if context.get("remote_reason_code"):
            trace.context["remote_reason_code"] = context.get("remote_reason_code")
            trace.context["remote_orchestration_failed"] = bool(
                context.get("remote_orchestration_failed")
            )
        if remote_result:
            trace.context["remote_reason_code"] = remote_result.reason_code
            trace.context["remote_error"] = remote_result.error
        return trace

    def _run_remote(self, context: dict[str, Any]) -> WatsonxOrchestrateResult:
        result = self.remote_client.execute_report_workflow(context)
        if not result.success:
            logger.info("Remote orchestration failed safely: %s", result.reason_code)
        return result

    def _remote_trace(self, result: WatsonxOrchestrateResult) -> PipelineExecutionTrace:
        now = utc_now()
        output = mask_sensitive(result.output)
        context = {
            **output,
            "execution_mode": "remote",
            "orchestrator_provider": "watsonx_orchestrate",
            "remote_workflow_id": result.remote_workflow_id,
            "remote_run_id": result.remote_run_id,
            "remote_reason_code": result.reason_code,
            "latency_ms": result.latency_ms,
        }
        agent_result = AgentExecutionResult(
            agent_name="watsonx_orchestrate",
            status="SUCCESS",
            output=context,
            confidence=float(output.get("confidence", 0.0) or 0.0),
            errors=[],
            started_at=now,
            completed_at=now,
        )
        return PipelineExecutionTrace(
            pipeline_id=result.remote_workflow_id or settings.ORCHESTRATE_PIPELINE_ID,
            version="remote",
            mode="remote",
            status="SUCCESS",
            context=context,
            steps=[
                PipelineStepTrace(
                    agent_name="watsonx_orchestrate",
                    status="SUCCESS",
                    attempts=1,
                    result=agent_result,
                    errors=[],
                    started_at=now,
                    completed_at=now,
                )
            ],
            errors=[],
            started_at=now,
            completed_at=now,
        )

    def _remote_failure_trace(
        self,
        result: WatsonxOrchestrateResult,
        mode: str,
    ) -> PipelineExecutionTrace:
        now = utc_now()
        context = {
            "execution_mode": mode,
            "orchestrator_provider": "watsonx_orchestrate",
            "remote_workflow_id": result.remote_workflow_id,
            "remote_run_id": result.remote_run_id,
            "remote_reason_code": result.reason_code,
            "remote_error": result.error,
            "latency_ms": result.latency_ms,
            "admin_review_required": True,
        }
        agent_result = AgentExecutionResult(
            agent_name="watsonx_orchestrate",
            status="FAILED",
            output=context,
            confidence=0.0,
            errors=[result.reason_code or "remote_orchestration_failed"],
            started_at=now,
            completed_at=now,
        )
        return PipelineExecutionTrace(
            pipeline_id=result.remote_workflow_id or settings.ORCHESTRATE_PIPELINE_ID,
            version="remote",
            mode="remote",
            status="FAILED",
            context=context,
            steps=[
                PipelineStepTrace(
                    agent_name="watsonx_orchestrate",
                    status="FAILED",
                    attempts=1,
                    result=agent_result,
                    errors=[result.reason_code or "remote_orchestration_failed"],
                    started_at=now,
                    completed_at=now,
                )
            ],
            errors=[result.reason_code or "remote_orchestration_failed"],
            started_at=now,
            completed_at=now,
        )

    def _apply_remote_output(self, db: Session, report: Any, output: dict[str, Any]) -> None:
        status = _status_from_remote_output(output)
        if status is not None:
            report.status = status
        if output.get("confidence") is not None:
            report.confidence_score = Decimal(str(float(output["confidence"]) * 100))
        if output.get("severity_score") is not None:
            report.severity_score = Decimal(str(float(output["severity_score"])))
        if output.get("incident_id"):
            report.incident_id = str(output["incident_id"])
        try:
            db.commit()
            db.refresh(report)
        except Exception:
            db.rollback()
            logger.info("Remote orchestration state application was skipped")


def _status_from_remote_output(output: dict[str, Any]) -> IncidentStatus | None:
    if output.get("admin_review_required"):
        return IncidentStatus.PENDING_VERIFICATION
    decision = str(output.get("decision") or output.get("report_status") or "").upper()
    if decision in {"VERIFIED", "SUCCESS", "COMPLETED", "OK"}:
        return IncidentStatus.VERIFIED
    if decision in {"FALSE_REPORT", "REJECTED"}:
        return IncidentStatus.FALSE_REPORT
    return None


def _determine_processing_status(trace: PipelineExecutionTrace) -> str:
    if _trace_requires_review(trace):
        return "PROCESSED_WITH_REVIEW"
    return "PROCESSED"


def _remote_processing_status(trace: PipelineExecutionTrace) -> str:
    if _trace_requires_review(trace):
        return "PROCESSED_WITH_REVIEW"
    return "ORCHESTRATED_REMOTE"


def _fallback_processing_status(trace: PipelineExecutionTrace) -> str:
    if _trace_requires_review(trace):
        return "PROCESSED_WITH_REVIEW"
    return "ORCHESTRATED_LOCAL_FALLBACK"


def _trace_requires_review(trace: PipelineExecutionTrace) -> bool:
    context = trace.context or {}
    confidence = context.get("confidence")
    try:
        normalized_confidence = float(confidence)
    except (TypeError, ValueError):
        normalized_confidence = 0.0

    failed_or_partial = trace.status != "SUCCESS" or any(
        step.status == "FAILED" for step in trace.steps
    )
    skipped_critical_step = any(
        step.status == "SKIPPED"
        and step.agent_name in {"verification_agent", "clustering_agent", "priority_agent"}
        for step in trace.steps
    )
    review_required = bool(context.get("admin_review_required"))
    low_confidence = normalized_confidence < settings.AGENT_CONFIDENCE_THRESHOLD

    return failed_or_partial or skipped_critical_step or review_required or low_confidence

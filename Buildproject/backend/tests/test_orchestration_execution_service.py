"""Tests for local/remote/hybrid orchestration execution coordination."""

from types import SimpleNamespace

from app.core.config import settings
from app.schemas.agents import PipelineExecutionTrace
from app.schemas.common import IncidentStatus
from app.services.orchestration_execution_service import OrchestrationExecutionService
from app.services.watsonx_orchestrate_client import WatsonxOrchestrateResult
from app.utils.time import utc_now


class FakeDb:
    def __init__(self):
        self.committed = False
        self.refreshed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def refresh(self, _obj):
        self.refreshed = True

    def rollback(self):
        self.rolled_back = True


class FakeLocalEngine:
    calls = []

    def run(self, context):
        self.calls.append(context)
        now = utc_now()
        return PipelineExecutionTrace(
            pipeline_id="crisisgrid-main-pipeline",
            version="1.0",
            mode="local",
            status="SUCCESS",
            context={"confidence": 0.82, "admin_review_required": False},
            steps=[],
            errors=[],
            started_at=now,
            completed_at=now,
        )


class RemoteSuccessClient:
    def execute_report_workflow(self, context):
        return WatsonxOrchestrateResult(
            success=True,
            status="SUCCESS",
            output={
                "confidence": 0.9,
                "severity_score": 88,
                "decision": "VERIFIED",
                "incident_id": "incident_remote_1",
                "admin_review_required": False,
            },
            reason_code="remote_success",
            remote_run_id="remote-run-1",
            remote_workflow_id="crisisgrid-main-pipeline",
            latency_ms=25,
        )


class RemoteFailureClient:
    def execute_report_workflow(self, context):
        return WatsonxOrchestrateResult(
            success=False,
            status="FAILED",
            reason_code="remote_timeout",
            remote_workflow_id="crisisgrid-main-pipeline",
            latency_ms=30,
            error="watsonx Orchestrate request timed out",
        )


def _report():
    return SimpleNamespace(
        status=IncidentStatus.PENDING_VERIFICATION,
        confidence_score=0,
        severity_score=0,
        incident_id=None,
    )


def _configure(monkeypatch, mode, fallback=True, remote=True):
    monkeypatch.setattr(settings, "ORCHESTRATE_ENABLED", True)
    monkeypatch.setattr(settings, "ORCHESTRATE_MODE", mode)
    monkeypatch.setattr(settings, "ORCHESTRATE_FALLBACK_TO_LOCAL", fallback)
    monkeypatch.setattr(settings, "ORCHESTRATE_TIMEOUT_SECONDS", 15)
    monkeypatch.setattr(settings, "ORCHESTRATE_PIPELINE_ID", "crisisgrid-main-pipeline")
    monkeypatch.setattr(
        settings,
        "ORCHESTRATE_API_URL",
        "https://orchestrate.example.test/run" if remote else None,
    )
    monkeypatch.setattr(settings, "ORCHESTRATE_API_KEY", "secret" if remote else None)


def test_local_mode_uses_local_engine(monkeypatch):
    _configure(monkeypatch, "local", remote=True)
    FakeLocalEngine.calls = []

    result = OrchestrationExecutionService(
        remote_client=RemoteSuccessClient(),
        local_engine_factory=FakeLocalEngine,
    ).execute({}, FakeDb(), _report())

    assert result.execution_mode == "local"
    assert result.processing_status == "PROCESSED"
    assert len(FakeLocalEngine.calls) == 1


def test_remote_success_applies_safe_report_state(monkeypatch):
    _configure(monkeypatch, "remote", remote=True)
    report = _report()
    db = FakeDb()

    result = OrchestrationExecutionService(
        remote_client=RemoteSuccessClient(),
        local_engine_factory=FakeLocalEngine,
    ).execute({}, db, report)

    assert result.processing_status == "ORCHESTRATED_REMOTE"
    assert result.orchestrator_provider == "watsonx_orchestrate"
    assert report.status == IncidentStatus.VERIFIED
    assert float(report.confidence_score) == 90
    assert report.incident_id == "incident_remote_1"
    assert db.committed is True


def test_remote_failure_without_fallback_returns_review(monkeypatch):
    _configure(monkeypatch, "remote", fallback=False, remote=True)
    FakeLocalEngine.calls = []

    result = OrchestrationExecutionService(
        remote_client=RemoteFailureClient(),
        local_engine_factory=FakeLocalEngine,
    ).execute({}, FakeDb(), _report())

    assert result.processing_status == "PROCESSED_WITH_REVIEW"
    assert result.trace.context["admin_review_required"] is True
    assert result.trace.context["remote_reason_code"] == "remote_timeout"
    assert FakeLocalEngine.calls == []


def test_hybrid_remote_failure_falls_back_to_local(monkeypatch):
    _configure(monkeypatch, "hybrid", fallback=True, remote=True)
    FakeLocalEngine.calls = []

    result = OrchestrationExecutionService(
        remote_client=RemoteFailureClient(),
        local_engine_factory=FakeLocalEngine,
    ).execute({}, FakeDb(), _report())

    assert result.processing_status == "ORCHESTRATED_LOCAL_FALLBACK"
    assert result.execution_mode == "hybrid_fallback"
    assert result.fallback_used is True
    assert len(FakeLocalEngine.calls) == 1
    assert result.trace.context["remote_reason_code"] == "remote_timeout"


def test_hybrid_without_remote_config_uses_local_fallback(monkeypatch):
    _configure(monkeypatch, "hybrid", fallback=True, remote=False)
    FakeLocalEngine.calls = []

    result = OrchestrationExecutionService(
        remote_client=RemoteFailureClient(),
        local_engine_factory=FakeLocalEngine,
    ).execute({}, FakeDb(), _report())

    assert result.processing_status == "ORCHESTRATED_LOCAL_FALLBACK"
    assert len(FakeLocalEngine.calls) == 1
    assert result.trace.context["remote_reason_code"] == "remote_not_configured"


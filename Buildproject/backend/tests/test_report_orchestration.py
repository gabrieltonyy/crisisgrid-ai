"""Tests for report submission orchestration wiring."""

from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.api.routes import reports as reports_routes
from app.schemas.agents import PipelineExecutionTrace
from app.schemas.common import CrisisType, IncidentStatus, UserRole
from app.schemas.reports import CrisisReportCreateRequest
from app.utils.time import utc_now


class FakeDb:
    def __init__(self):
        self.refreshed = False

    def refresh(self, _obj):
        self.refreshed = True


def _fake_report(report_data, user_id=None):
    return SimpleNamespace(
        id=uuid4(),
        incident_id=None,
        user_id=user_id,
        crisis_type=report_data.crisis_type,
        description=report_data.description,
        image_url=report_data.image_url,
        video_url=report_data.video_url,
        latitude=report_data.latitude,
        longitude=report_data.longitude,
        location_text=report_data.location_text,
        status=IncidentStatus.VERIFIED,
        confidence_score=82.0,
        severity_score=85.0,
        source="CITIZEN_APP",
        is_anonymous=report_data.is_anonymous,
        created_at=datetime(2026, 5, 4, 12, 0, 0),
        updated_at=datetime(2026, 5, 4, 12, 0, 0),
    )


def _trace(status="SUCCESS", context=None, steps=None):
    now = utc_now()
    return PipelineExecutionTrace(
        pipeline_id="crisisgrid-main-pipeline",
        version="1.0",
        mode="local",
        status=status,
        context=context or {"confidence": 0.82, "admin_review_required": False},
        steps=steps or [],
        errors=[],
        started_at=now,
        completed_at=now,
    )


@pytest.fixture
def report_request():
    return CrisisReportCreateRequest(
        crisis_type=CrisisType.FIRE,
        description="Large fire with smoke near the central market warehouse",
        latitude=51.5074,
        longitude=-0.1278,
        location_text="Central market",
        is_anonymous=False,
    )


@pytest.mark.asyncio
async def test_create_report_invokes_orchestrator_and_persists_trace(
    monkeypatch,
    report_request,
):
    created_report = _fake_report(report_request, user_id=uuid4())
    created_contexts = []
    persisted = []

    class FakeReportRepository:
        def __init__(self, db):
            self.db = db

        def create(self, report_data, user_id=None):
            return created_report

        def get_by_id(self, report_id):
            return created_report if report_id == created_report.id else None

    class FakeOrchestratorEngine:
        def run(self, initial_context):
            created_contexts.append(initial_context)
            return _trace()

    def fake_persist_pipeline_trace(db, report_id, trace):
        persisted.append((db, report_id, trace.status))
        return {"postgres_agent_run_id": "run_orchestrator_1", "cloudant_log_id": None}

    monkeypatch.setattr(reports_routes, "ReportRepository", FakeReportRepository)
    monkeypatch.setattr(reports_routes, "OrchestratorEngine", FakeOrchestratorEngine)
    monkeypatch.setattr(reports_routes, "persist_pipeline_trace", fake_persist_pipeline_trace)
    monkeypatch.setattr(reports_routes.cloudant_service, "enabled", False)

    db = FakeDb()
    current_user = SimpleNamespace(id=created_report.user_id, role=UserRole.CITIZEN)

    response = await reports_routes.create_report(
        report_data=report_request,
        db=db,
        current_user=current_user,
    )

    assert response.processing_status == "PROCESSED"
    assert response.estimated_verification_time == 0
    assert created_contexts[0]["report"] == created_report
    assert created_contexts[0]["db"] == db
    assert created_contexts[0]["cloudant_enabled"] is False
    assert created_contexts[0]["user_context"] == {
        "authenticated": True,
        "user_id": str(current_user.id),
        "role": "CITIZEN",
    }
    assert persisted == [(db, created_report.id, "SUCCESS")]


@pytest.mark.asyncio
async def test_create_report_returns_review_status_for_admin_review_context(
    monkeypatch,
    report_request,
):
    created_report = _fake_report(report_request)

    class FakeReportRepository:
        def __init__(self, db):
            self.db = db

        def create(self, report_data, user_id=None):
            return created_report

        def get_by_id(self, report_id):
            return created_report

    class FakeOrchestratorEngine:
        def run(self, initial_context):
            return _trace(
                context={
                    "confidence": 0.4,
                    "admin_review_required": True,
                    "prompt_injection_detected": True,
                }
            )

    monkeypatch.setattr(reports_routes, "ReportRepository", FakeReportRepository)
    monkeypatch.setattr(reports_routes, "OrchestratorEngine", FakeOrchestratorEngine)
    monkeypatch.setattr(
        reports_routes,
        "persist_pipeline_trace",
        lambda db, report_id, trace: {"postgres_agent_run_id": "run_orchestrator_1"},
    )
    monkeypatch.setattr(reports_routes.cloudant_service, "enabled", False)

    response = await reports_routes.create_report(
        report_data=report_request,
        db=FakeDb(),
        current_user=None,
    )

    assert response.processing_status == "PROCESSED_WITH_REVIEW"


@pytest.mark.asyncio
async def test_create_report_treats_orchestrator_exception_as_review(
    monkeypatch,
    report_request,
):
    created_report = _fake_report(report_request)
    persisted = []

    class FakeReportRepository:
        def __init__(self, db):
            self.db = db

        def create(self, report_data, user_id=None):
            return created_report

        def get_by_id(self, report_id):
            return created_report

    class FakeOrchestratorEngine:
        def run(self, initial_context):
            raise RuntimeError("local orchestration unavailable")

    monkeypatch.setattr(reports_routes, "ReportRepository", FakeReportRepository)
    monkeypatch.setattr(reports_routes, "OrchestratorEngine", FakeOrchestratorEngine)
    monkeypatch.setattr(
        reports_routes,
        "persist_pipeline_trace",
        lambda db, report_id, trace: persisted.append((db, report_id, trace)),
    )
    monkeypatch.setattr(reports_routes.cloudant_service, "enabled", False)

    response = await reports_routes.create_report(
        report_data=report_request,
        db=FakeDb(),
        current_user=None,
    )

    assert response.processing_status == "PROCESSED_WITH_REVIEW"
    assert persisted == []

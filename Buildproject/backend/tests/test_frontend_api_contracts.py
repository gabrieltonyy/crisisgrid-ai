"""Tests for API response shapes consumed by the Next.js frontend."""

from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db.session import get_db
from app.main import app
from app.schemas.common import (
    AlertStatus,
    AuthorityType,
    CrisisType,
    DispatchStatus,
    IncidentStatus,
    SeverityLevel,
    UserRole,
)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: object()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_reports_list_matches_frontend_contract(client, monkeypatch):
    import app.api.routes.reports as reports_routes

    report_id = uuid4()
    admin_user = SimpleNamespace(
        id=uuid4(),
        role=UserRole.ADMIN,
        is_active=True,
    )

    class FakeReportRepository:
        def __init__(self, db):
            self.db = db

        def get_all(self, skip=0, limit=100, status=None):
            return [
                SimpleNamespace(
                    id=report_id,
                    incident_id=None,
                    user_id=None,
                    crisis_type=CrisisType.FIRE,
                    description="Smoke visible near the market",
                    image_url=None,
                    video_url=None,
                    latitude=51.5074,
                    longitude=-0.1278,
                    location_text="Central market",
                    status=IncidentStatus.PENDING_VERIFICATION,
                    confidence_score=0.0,
                    severity_score=0.0,
                    source="CITIZEN_APP",
                    is_anonymous=False,
                    created_at=datetime(2026, 5, 2, 12, 0, 0),
                    updated_at=None,
                )
            ]

    monkeypatch.setattr(reports_routes, "ReportRepository", FakeReportRepository)
    app.dependency_overrides[reports_routes.get_current_active_user] = lambda: admin_user

    response = client.get("/api/v1/reports")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body[0]["id"] == str(report_id)
    assert body[0]["crisis_type"] == "FIRE"
    assert body[0]["status"] == "PENDING_VERIFICATION"


def test_reports_list_sanitizes_database_unavailable_errors(client, monkeypatch):
    import app.api.routes.reports as reports_routes

    admin_user = SimpleNamespace(
        id=uuid4(),
        role=UserRole.ADMIN,
        is_active=True,
    )

    class UnavailableReportRepository:
        def __init__(self, db):
            self.db = db

        def get_all(self, skip=0, limit=100, status=None):
            raise OperationalError("SELECT reports", {}, Exception("connection refused"))

    monkeypatch.setattr(reports_routes, "ReportRepository", UnavailableReportRepository)
    app.dependency_overrides[reports_routes.get_current_active_user] = lambda: admin_user

    response = client.get("/api/v1/reports")

    assert response.status_code == 503
    body = response.json()
    assert "Database unavailable" in body["detail"]
    assert "connection refused" not in body["detail"]
    assert "psycopg2" not in body["detail"]


def test_anonymous_report_submission_does_not_require_auth(client, monkeypatch):
    import app.api.routes.reports as reports_routes

    report_id = uuid4()

    class FakeReportRepository:
        def __init__(self, db):
            self.db = db

        def create(self, report_data, user_id=None):
            return SimpleNamespace(
                id=report_id,
                incident_id=None,
                user_id=user_id,
                crisis_type=report_data.crisis_type,
                description=report_data.description,
                image_url=None,
                video_url=None,
                latitude=report_data.latitude,
                longitude=report_data.longitude,
                location_text=report_data.location_text,
                status=IncidentStatus.PENDING_VERIFICATION,
                confidence_score=0.0,
                severity_score=0.0,
                source="CITIZEN_APP",
                is_anonymous=report_data.is_anonymous,
                created_at=datetime(2026, 5, 2, 12, 0, 0),
                updated_at=datetime(2026, 5, 2, 12, 0, 0),
            )

    monkeypatch.setattr(reports_routes, "ReportRepository", FakeReportRepository)
    monkeypatch.setattr(
        reports_routes,
        "OrchestratorEngine",
        lambda: SimpleNamespace(
            run=lambda initial_context: SimpleNamespace(
                status="SUCCESS",
                context={"confidence": 0.8, "admin_review_required": False},
                steps=[],
            )
        ),
    )
    monkeypatch.setattr(
        reports_routes,
        "persist_pipeline_trace",
        lambda db, report_id, trace: {"postgres_agent_run_id": "run_orchestrator_1"},
    )
    monkeypatch.setattr(reports_routes.cloudant_service, "enabled", False)

    response = client.post(
        "/api/v1/reports",
        json={
            "crisis_type": "FIRE",
            "description": "Smoke visible near the market warehouse",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "location_text": "Central market",
            "is_anonymous": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["report"]["id"] == str(report_id)
    assert body["report"]["user_id"] is None
    assert body["report"]["is_anonymous"] is True
    assert body["processing_status"] == "PROCESSED"


def test_alerts_list_matches_frontend_contract(client, monkeypatch):
    import app.api.routes.alerts as alerts_routes

    alert = SimpleNamespace(
        alert_id="alert_fire_001",
        incident_id="incident_fire_001",
        crisis_type=CrisisType.FIRE,
        title="Fire Alert",
        message="Avoid the affected area.",
        severity=SeverityLevel.HIGH,
        affected_radius_meters=1000,
        latitude=51.5074,
        longitude=-0.1278,
        incident=None,
        status=AlertStatus.ACTIVE,
        issued_at=datetime(2026, 5, 2, 12, 0, 0),
        expires_at=None,
    )

    monkeypatch.setattr(
        alerts_routes.alert_repository,
        "get_all_active_alerts",
        lambda db, limit=100: [alert],
    )

    response = client.get("/api/v1/alerts")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body[0]["id"] == "alert_fire_001"
    assert body[0]["alert_title"] == "Fire Alert"
    assert body[0]["status"] == "ACTIVE"


def test_alerts_list_sanitizes_database_unavailable_errors(client, monkeypatch):
    import app.api.routes.alerts as alerts_routes

    def raise_database_unavailable(db, limit=100):
        raise OperationalError("SELECT alerts", {}, Exception("connection refused"))

    monkeypatch.setattr(
        alerts_routes.alert_repository,
        "get_all_active_alerts",
        raise_database_unavailable,
    )

    response = client.get("/api/v1/alerts")

    assert response.status_code == 503
    body = response.json()
    assert "Database unavailable" in body["detail"]
    assert "connection refused" not in body["detail"]
    assert "psycopg2" not in body["detail"]


def test_dispatch_logs_list_matches_frontend_contract(client, monkeypatch):
    import app.api.routes.dispatch as dispatch_routes

    dispatch = SimpleNamespace(
        dispatch_id="dispatch_fire_001",
        incident_id="incident_fire_001",
        authority_type=AuthorityType.FIRE_SERVICE,
        crisis_type=CrisisType.FIRE,
        message_sent="Dispatch fire service to Central market.",
        priority="HIGH",
        status=DispatchStatus.SIMULATED_SENT,
        latitude=51.5074,
        longitude=-0.1278,
        location_description="Central market",
        contact_method="SIMULATED",
        response_time_seconds=None,
        dispatched_at=datetime(2026, 5, 2, 12, 0, 0),
        acknowledged_at=None,
    )

    monkeypatch.setattr(
        dispatch_routes.dispatch_repository,
        "get_all_dispatches",
        lambda db, limit=100: [dispatch],
    )

    response = client.get("/api/v1/dispatch/logs")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body[0]["id"] == "dispatch_fire_001"
    assert body[0]["authority_type"] == "FIRE_SERVICE"
    assert body[0]["status"] == "SIMULATED_SENT"


def test_generic_advisory_matches_frontend_contract(client):
    response = client.get("/api/v1/advisory/FIRE")

    assert response.status_code == 200
    body = response.json()
    assert body["incident_id"] == "generic_fire"
    assert body["crisis_type"] == "FIRE"
    assert body["risk_level"] == "MODERATE"
    assert body["immediate_actions"]
    assert body["what_to_do"]
    assert body["emergency_contacts"]

"""
Unified CrisisGrid AI Demo Seed Script

Purpose:
    Seeds realistic hackathon demo data that shows the full CrisisGrid AI pipeline:

        Users -> Reports -> Confirmations -> Incidents -> Agent Runs -> Alerts -> Dispatch Logs

Run from Buildproject/backend:
    python scripts/seed_data.py

Recommended flow:
    python -m app.db.init_db
    python scripts/seed_data.py

Demo credentials:
    Citizen:   citizen.demo01@demo.crisisgrid.ai / Password123!
    Authority: authority.demo01@demo.crisisgrid.ai / Password123!
    Admin:     admin.demo01@demo.crisisgrid.ai / Password123!
"""

from __future__ import annotations

import random
import sys
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Iterable

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal, engine
from app.db.init_db import ensure_auth_columns
from app.models import Alert, AgentRun, Confirmation, DispatchLog, Incident, Report, User
from app.schemas.common import (
    AgentName,
    AgentRunStatus,
    AlertStatus,
    AuthorityType,
    ConfirmationType,
    CrisisType,
    DispatchStatus,
    IncidentStatus,
    SeverityLevel,
    UserRole,
)
from app.services.auth_service import hash_password


PASSWORD = "Password123!"
DEMO_DOMAIN = "demo.crisisgrid.ai"
SEED = 20260505

NAIROBI_LOCATIONS = [
    ("Nairobi CBD, Kenyatta Avenue", -1.2864, 36.8172),
    ("Westlands, Waiyaki Way", -1.2676, 36.8108),
    ("Kibera, Olympic", -1.3133, 36.7892),
    ("Eastleigh, First Avenue", -1.2762, 36.8497),
    ("Kasarani, Mwiki Road", -1.2260, 36.8992),
    ("Embakasi, Airport North Road", -1.3217, 36.8985),
    ("Langata, Mbagathi Way", -1.3530, 36.7657),
    ("Karen, Ngong Road", -1.3197, 36.7073),
    ("Rongai, Magadi Road", -1.3944, 36.7547),
    ("Thika Road, Roysambu", -1.2186, 36.8864),
    ("Mathare, Juja Road", -1.2619, 36.8571),
    ("Industrial Area, Enterprise Road", -1.3086, 36.8467),
    ("South B, Mombasa Road", -1.3193, 36.8422),
    ("Kawangware, Gitanga Road", -1.2858, 36.7465),
    ("Gikambura, Kikuyu Road", -1.2502, 36.6569),
]

CRISIS_DESCRIPTIONS = {
    CrisisType.FIRE: [
        "Heavy smoke and visible flames near a commercial building.",
        "Electrical fire reported inside a residential block.",
        "Market stall fire spreading toward nearby shops.",
    ],
    CrisisType.FLOOD: [
        "Road flooding after heavy rain, vehicles are stranded.",
        "Drainage overflow entering ground-floor homes.",
        "Rising water levels blocking pedestrian access.",
    ],
    CrisisType.WILDLIFE: [
        "Dangerous wildlife sighting close to a residential area.",
        "Stray animal causing panic near a school compound.",
        "Wildlife crossing has blocked traffic and pedestrians.",
    ],
    CrisisType.ACCIDENT: [
        "Multi-vehicle collision blocking one lane.",
        "Motorbike accident with injuries reported.",
        "Public transport vehicle crash causing traffic buildup.",
    ],
    CrisisType.SECURITY: [
        "Crowd safety concern reported near a busy junction.",
        "Security disturbance affecting access to the area.",
        "Suspicious activity creating public safety concerns.",
    ],
    CrisisType.HEALTH: [
        "Medical emergency requiring urgent response.",
        "Multiple people reporting breathing difficulty after exposure.",
        "Public health incident reported near a community facility.",
    ],
    CrisisType.LANDSLIDE: [
        "Soil collapse threatening nearby homes after rain.",
        "Debris flow blocking a local access road.",
        "Slope failure reported near informal housing.",
    ],
    CrisisType.HAZARDOUS_SPILL: [
        "Fuel spill on the roadway creating fire risk.",
        "Chemical smell reported after a container leak.",
        "Hazardous liquid spill near drainage channel.",
    ],
    CrisisType.OTHER: [
        "Emergency condition requiring assessment by responders.",
        "Community safety incident reported by residents.",
        "Unclear crisis report needing verification.",
    ],
}

AUTHORITY_BY_CRISIS = {
    CrisisType.FIRE: AuthorityType.FIRE_SERVICE,
    CrisisType.FLOOD: AuthorityType.DISASTER_RESPONSE,
    CrisisType.WILDLIFE: AuthorityType.WILDLIFE_SERVICE,
    CrisisType.ACCIDENT: AuthorityType.POLICE,
    CrisisType.SECURITY: AuthorityType.POLICE,
    CrisisType.HEALTH: AuthorityType.MEDICAL_SERVICE,
    CrisisType.LANDSLIDE: AuthorityType.DISASTER_RESPONSE,
    CrisisType.HAZARDOUS_SPILL: AuthorityType.DISASTER_RESPONSE,
    CrisisType.OTHER: AuthorityType.DISASTER_RESPONSE,
}


def decimal_value(value: float | int | str) -> Decimal:
    return Decimal(str(value))


def jitter(value: float, spread: float = 0.004) -> Decimal:
    return decimal_value(round(value + random.uniform(-spread, spread), 7))


def demo_email(role: str, index: int) -> str:
    return f"{role.lower()}.demo{index:02d}@{DEMO_DOMAIN}"


def upsert_user(db, *, name: str, email: str, phone_number: str, role: UserRole, trust_score: Decimal) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(email=email)
        db.add(user)

    user.name = name
    user.phone_number = phone_number
    user.role = role
    user.hashed_password = hash_password(PASSWORD)
    user.trust_score = trust_score
    user.status = "ACTIVE"
    user.is_active = True
    user.email_verified = True
    return user


def create_users(db) -> list[User]:
    users: list[User] = []

    for index in range(1, 41):
        users.append(
            upsert_user(
                db,
                name=f"Citizen Demo {index:02d}",
                email=demo_email("citizen", index),
                phone_number=f"254711{index:06d}",
                role=UserRole.CITIZEN,
                trust_score=decimal_value(round(random.uniform(0.45, 0.96), 2)),
            )
        )

    for index in range(1, 6):
        users.append(
            upsert_user(
                db,
                name=f"Authority Demo {index:02d}",
                email=demo_email("authority", index),
                phone_number=f"254722{index:06d}",
                role=UserRole.AUTHORITY,
                trust_score=decimal_value("1.00"),
            )
        )
        users.append(
            upsert_user(
                db,
                name=f"Admin Demo {index:02d}",
                email=demo_email("admin", index),
                phone_number=f"254733{index:06d}",
                role=UserRole.ADMIN,
                trust_score=decimal_value("1.00"),
            )
        )

    db.commit()
    for user in users:
        db.refresh(user)
    return users


def reset_demo_data(db, users: Iterable[User]) -> None:
    """Delete existing demo data only, not the whole database."""
    user_ids = [user.id for user in users]

    demo_report_ids = [row[0] for row in db.query(Report.id).filter(Report.user_id.in_(user_ids)).all()]
    demo_incident_ids = [
        row[0]
        for row in db.query(Incident.id)
        .filter(Incident.id.like("demo_incident_%"))
        .all()
    ]

    if demo_report_ids:
        db.query(Confirmation).filter(Confirmation.report_id.in_(demo_report_ids)).delete(synchronize_session=False)
        db.query(AgentRun).filter(AgentRun.report_id.in_(demo_report_ids)).delete(synchronize_session=False)
        db.query(Report).filter(Report.id.in_(demo_report_ids)).delete(synchronize_session=False)

    if demo_incident_ids:
        db.query(Alert).filter(Alert.incident_id.in_(demo_incident_ids)).delete(synchronize_session=False)
        db.query(DispatchLog).filter(DispatchLog.incident_id.in_(demo_incident_ids)).delete(synchronize_session=False)
        db.query(AgentRun).filter(AgentRun.incident_id.in_(demo_incident_ids)).delete(synchronize_session=False)
        db.query(Incident).filter(Incident.id.in_(demo_incident_ids)).delete(synchronize_session=False)

    db.commit()


def create_report(
    db,
    *,
    user: User,
    crisis_type: CrisisType,
    description: str,
    latitude: Decimal,
    longitude: Decimal,
    location_text: str,
    status: IncidentStatus,
    confidence_score: float,
    severity_score: float,
    created_at: datetime,
    is_anonymous: bool = False,
    image_url: str | None = None,
) -> Report:
    report = Report(
        user_id=user.id,
        crisis_type=crisis_type,
        description=description,
        latitude=latitude,
        longitude=longitude,
        location_text=location_text,
        status=status,
        confidence_score=decimal_value(confidence_score),
        severity_score=decimal_value(severity_score),
        source="CITIZEN_APP",
        is_anonymous=is_anonymous,
        image_url=image_url,
        video_url=None,
        created_at=created_at,
        updated_at=created_at + timedelta(minutes=random.randint(3, 90)),
    )
    db.add(report)
    return report


def create_showcase_reports(db, citizens: list[User], now: datetime) -> dict[str, list[Report]]:
    """Create guaranteed demo scenarios that make the product story obvious."""
    scenarios: dict[str, list[Report]] = defaultdict(list)

    westlands_lat, westlands_lng = -1.2676, 36.8108
    thika_lat, thika_lng = -1.2186, 36.8864
    karen_lat, karen_lng = -1.3197, 36.7073

    fire_descriptions = [
        "Large fire near Westlands mall. Thick smoke visible from the highway.",
        "Confirming heavy flames in Westlands. People are evacuating nearby shops.",
        "Smoke is spreading across Waiyaki Way. Emergency help needed urgently.",
        "Fire appears to be moving toward adjacent commercial buildings.",
        "Crowd is gathering near the fire scene, traffic is blocked.",
    ]
    for i, description in enumerate(fire_descriptions):
        scenarios["critical_fire"].append(
            create_report(
                db,
                user=citizens[i],
                crisis_type=CrisisType.FIRE,
                description=description,
                latitude=jitter(westlands_lat, 0.0015),
                longitude=jitter(westlands_lng, 0.0015),
                location_text="Westlands, Waiyaki Way",
                status=IncidentStatus.VERIFIED,
                confidence_score=random.uniform(86, 97),
                severity_score=random.uniform(88, 100),
                created_at=now - timedelta(minutes=30 - (i * 4)),
                image_url=f"https://example.com/demo/fire-westlands-{i + 1}.jpg",
            )
        )

    flood_descriptions = [
        "Thika Road flooding after heavy rain, cars are slowing down.",
        "Water is rising near Roysambu footbridge. Pedestrians are stuck.",
        "Drainage overflow is blocking one side of the road.",
    ]
    for i, description in enumerate(flood_descriptions):
        scenarios["developing_flood"].append(
            create_report(
                db,
                user=citizens[i + 8],
                crisis_type=CrisisType.FLOOD,
                description=description,
                latitude=jitter(thika_lat, 0.0018),
                longitude=jitter(thika_lng, 0.0018),
                location_text="Thika Road, Roysambu",
                status=IncidentStatus.NEEDS_CONFIRMATION,
                confidence_score=random.uniform(58, 76),
                severity_score=random.uniform(55, 74),
                created_at=now - timedelta(minutes=55 - (i * 8)),
            )
        )

    scenarios["false_wildlife"].append(
        create_report(
            db,
            user=citizens[-1],
            crisis_type=CrisisType.WILDLIFE,
            description="Unverified wildlife alert near Karen. No other witnesses yet.",
            latitude=jitter(karen_lat, 0.003),
            longitude=jitter(karen_lng, 0.003),
            location_text="Karen, Ngong Road",
            status=IncidentStatus.FALSE_REPORT,
            confidence_score=22,
            severity_score=30,
            created_at=now - timedelta(hours=2),
            is_anonymous=True,
        )
    )

    db.commit()
    for reports in scenarios.values():
        for report in reports:
            db.refresh(report)

    return scenarios


def create_random_reports(db, citizens: list[User], now: datetime, target_count: int = 291) -> list[Report]:
    crisis_types = list(CRISIS_DESCRIPTIONS.keys())
    statuses = [
        IncidentStatus.PENDING_VERIFICATION,
        IncidentStatus.NEEDS_CONFIRMATION,
        IncidentStatus.PROVISIONAL_CRITICAL,
        IncidentStatus.VERIFIED,
        IncidentStatus.DISPATCHED,
        IncidentStatus.RESOLVED,
        IncidentStatus.FALSE_REPORT,
    ]
    status_weights = [0.23, 0.16, 0.12, 0.24, 0.08, 0.12, 0.05]

    reports: list[Report] = []
    for _ in range(target_count):
        crisis_type = random.choice(crisis_types)
        location_text, latitude, longitude = random.choice(NAIROBI_LOCATIONS)
        status = random.choices(statuses, weights=status_weights, k=1)[0]
        created_at = now - timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        severity_floor = 65 if status == IncidentStatus.PROVISIONAL_CRITICAL else 20
        confidence_floor = 72 if status in {IncidentStatus.VERIFIED, IncidentStatus.DISPATCHED} else 35

        reports.append(
            create_report(
                db,
                user=random.choice(citizens),
                crisis_type=crisis_type,
                description=random.choice(CRISIS_DESCRIPTIONS[crisis_type]),
                latitude=jitter(latitude),
                longitude=jitter(longitude),
                location_text=location_text,
                status=status,
                confidence_score=round(random.uniform(confidence_floor, 98), 2),
                severity_score=round(random.uniform(severity_floor, 100), 2),
                created_at=created_at,
                is_anonymous=random.random() < 0.08,
            )
        )

    db.commit()
    for report in reports:
        db.refresh(report)
    return reports


def severity_from_score(score: float) -> SeverityLevel:
    if score >= 85:
        return SeverityLevel.CRITICAL
    if score >= 70:
        return SeverityLevel.HIGH
    if score >= 45:
        return SeverityLevel.MEDIUM
    return SeverityLevel.LOW


def incident_status_from_reports(reports: list[Report]) -> IncidentStatus:
    statuses = [report.status for report in reports]
    if IncidentStatus.FALSE_REPORT in statuses and len(reports) == 1:
        return IncidentStatus.FALSE_REPORT
    if IncidentStatus.DISPATCHED in statuses:
        return IncidentStatus.DISPATCHED
    if IncidentStatus.PROVISIONAL_CRITICAL in statuses:
        return IncidentStatus.PROVISIONAL_CRITICAL
    if IncidentStatus.VERIFIED in statuses or len(reports) >= 3:
        return IncidentStatus.VERIFIED
    if IncidentStatus.NEEDS_CONFIRMATION in statuses:
        return IncidentStatus.NEEDS_CONFIRMATION
    return IncidentStatus.PENDING_VERIFICATION


def create_incident_from_reports(db, incident_id: str, reports: list[Report], description: str | None = None) -> Incident:
    avg_lat = sum(float(report.latitude) for report in reports) / len(reports)
    avg_lng = sum(float(report.longitude) for report in reports) / len(reports)
    avg_confidence = sum(float(report.confidence_score or 0) for report in reports) / len(reports)
    avg_severity = sum(float(report.severity_score or 0) for report in reports) / len(reports)
    status = incident_status_from_reports(reports)
    first_reported_at = min(report.created_at for report in reports)
    last_updated_at = max(report.updated_at or report.created_at for report in reports)
    crisis_type = reports[0].crisis_type

    incident = Incident(
        id=incident_id,
        crisis_type=crisis_type,
        status=status,
        severity=severity_from_score(avg_severity),
        latitude=decimal_value(round(avg_lat, 7)),
        longitude=decimal_value(round(avg_lng, 7)),
        location_description=reports[0].location_text,
        confidence_score=decimal_value(round(avg_confidence, 2)),
        media_confidence=decimal_value(round(avg_confidence - random.uniform(0, 8), 2)),
        cross_report_confidence=decimal_value(min(98, round(avg_confidence + len(reports) * 2.5, 2))),
        external_signal_confidence=decimal_value(round(random.uniform(55, 90), 2)),
        reporter_trust_confidence=decimal_value(round(random.uniform(65, 96), 2)),
        geo_time_consistency=decimal_value(round(random.uniform(70, 98), 2)),
        report_count=len(reports),
        first_reported_at=first_reported_at,
        last_updated_at=last_updated_at,
        description=description or f"{crisis_type.value.title()} incident around {reports[0].location_text}",
        tags=[crisis_type.value.lower(), "demo", "clustered"],
    )
    db.add(incident)

    for report in reports:
        report.incident_id = incident.id

    db.commit()
    db.refresh(incident)
    return incident


def create_incidents(db, all_reports: list[Report], showcase: dict[str, list[Report]]) -> list[Incident]:
    incidents: list[Incident] = []

    incidents.append(
        create_incident_from_reports(
            db,
            "demo_incident_critical_fire_westlands",
            showcase["critical_fire"],
            "Confirmed multi-report fire incident near Westlands. High severity and active response required.",
        )
    )
    incidents.append(
        create_incident_from_reports(
            db,
            "demo_incident_developing_flood_thika_road",
            showcase["developing_flood"],
            "Developing flood risk along Thika Road. More confirmations requested before full dispatch.",
        )
    )
    incidents.append(
        create_incident_from_reports(
            db,
            "demo_incident_false_wildlife_karen",
            showcase["false_wildlife"],
            "Low-confidence wildlife report marked as likely false after verification.",
        )
    )

    grouped: dict[tuple[str, CrisisType], list[Report]] = defaultdict(list)
    linked_report_ids = {report.id for reports in showcase.values() for report in reports}

    for report in all_reports:
        if report.id in linked_report_ids or report.status == IncidentStatus.FALSE_REPORT:
            continue
        key = (report.location_text or "Unknown", report.crisis_type)
        grouped[key].append(report)

    index = 1
    for (_, _), group in grouped.items():
        if len(group) < 2:
            continue
        selected = group[: min(len(group), random.randint(2, 6))]
        incidents.append(create_incident_from_reports(db, f"demo_incident_auto_{index:03d}", selected))
        index += 1
        if index > 30:
            break

    return incidents


def create_confirmations(db, incidents: list[Incident], citizens: list[User]) -> list[Confirmation]:
    confirmations: list[Confirmation] = []
    now = datetime.now(UTC).replace(tzinfo=None)

    incident_reports = {
        incident.id: db.query(Report).filter(Report.incident_id == incident.id).all()
        for incident in incidents
    }

    counter = 1
    for incident in incidents[:18]:
        reports = incident_reports.get(incident.id, [])
        if not reports or incident.status == IncidentStatus.FALSE_REPORT:
            continue

        for report in reports[: random.randint(1, min(3, len(reports)))]:
            user = random.choice([citizen for citizen in citizens if citizen.id != report.user_id])
            confirmation = Confirmation(
                confirmation_id=f"demo_confirm_{counter:03d}",
                report_id=report.id,
                user_id=user.id,
                confirmation_type=ConfirmationType.CONFIRM,
                latitude=jitter(float(report.latitude), 0.0015),
                longitude=jitter(float(report.longitude), 0.0015),
                distance_from_report_meters=decimal_value(round(random.uniform(20, 220), 2)),
                notes="Nearby citizen confirmation added during demo simulation.",
                confirmed_at=(report.created_at or now) + timedelta(minutes=random.randint(5, 35)),
                trust_weight=decimal_value(round(random.uniform(0.55, 0.96), 2)),
            )
            confirmations.append(confirmation)
            db.add(confirmation)
            counter += 1

    db.commit()
    return confirmations


def create_agent_runs(db, incidents: list[Incident]) -> list[AgentRun]:
    agent_runs: list[AgentRun] = []
    counter = 1

    for incident in incidents:
        reports = db.query(Report).filter(Report.incident_id == incident.id).all()
        first_report = reports[0] if reports else None
        base_time = incident.first_reported_at or datetime.now(UTC).replace(tzinfo=None)

        verification = AgentRun(
            run_id=f"demo_run_verification_{counter:03d}",
            agent_name=AgentName.VERIFICATION_AGENT,
            status=AgentRunStatus.SUCCESS,
            report_id=first_report.id if first_report else None,
            incident_id=incident.id,
            started_at=base_time + timedelta(minutes=1),
            completed_at=base_time + timedelta(minutes=1, seconds=3),
            duration_seconds=decimal_value(round(random.uniform(1.5, 4.2), 2)),
            input_data={"incident_id": incident.id, "report_count": incident.report_count},
            output_data={
                "decision": incident.status.value,
                "confidence_score": float(incident.confidence_score or 0),
                "reason": "Cross-report similarity, reporter trust, geo-time consistency, and severity signals evaluated.",
            },
            confidence_score=incident.confidence_score,
            decision=incident.status.value,
            model_used="demo-ai-verification",
        )

        georisk = AgentRun(
            run_id=f"demo_run_georisk_{counter:03d}",
            agent_name=AgentName.GEORISK_AGENT,
            status=AgentRunStatus.SUCCESS,
            incident_id=incident.id,
            started_at=base_time + timedelta(minutes=2),
            completed_at=base_time + timedelta(minutes=2, seconds=2),
            duration_seconds=decimal_value(round(random.uniform(1.2, 3.8), 2)),
            input_data={"latitude": float(incident.latitude), "longitude": float(incident.longitude)},
            output_data={
                "risk_level": incident.severity.value,
                "affected_radius_meters": 750 if incident.severity == SeverityLevel.CRITICAL else 400,
                "recommended_action": "Generate alert" if incident.status in {IncidentStatus.VERIFIED, IncidentStatus.PROVISIONAL_CRITICAL, IncidentStatus.DISPATCHED} else "Request confirmation",
            },
            risk_level=incident.severity.value,
            decision="HIGH_RISK" if incident.severity in {SeverityLevel.HIGH, SeverityLevel.CRITICAL} else "MONITOR",
            model_used="demo-geospatial-risk",
        )

        db.add(verification)
        db.add(georisk)
        agent_runs.extend([verification, georisk])
        counter += 1

    db.commit()
    return agent_runs


def alert_message_for(incident: Incident) -> tuple[str, str, list[str]]:
    crisis = incident.crisis_type.value.replace("_", " ").title()
    title = f"{incident.severity.value}: {crisis} near {incident.location_description}"
    message = (
        f"CrisisGrid AI has verified a {crisis.lower()} incident near {incident.location_description}. "
        f"Avoid the area and follow official guidance."
    )
    instructions = [
        "Avoid the affected area",
        "Follow instructions from emergency responders",
        "Keep roads clear for response teams",
        "Share only verified updates",
    ]

    if incident.crisis_type == CrisisType.FIRE:
        instructions = [
            "Evacuate nearby buildings calmly",
            "Avoid smoke-filled areas",
            "Do not use elevators during evacuation",
            "Keep access roads open for fire engines",
        ]
    elif incident.crisis_type == CrisisType.FLOOD:
        instructions = [
            "Avoid walking or driving through flood water",
            "Move to higher ground if water levels rise",
            "Keep children away from drainage channels",
            "Follow traffic diversions",
        ]

    return title, message, instructions


def create_alerts(db, incidents: list[Incident]) -> list[Alert]:
    alerts: list[Alert] = []
    now = datetime.now(UTC).replace(tzinfo=None)
    eligible_statuses = {IncidentStatus.VERIFIED, IncidentStatus.PROVISIONAL_CRITICAL, IncidentStatus.DISPATCHED}

    counter = 1
    for incident in incidents:
        if incident.status not in eligible_statuses:
            continue
        if incident.severity not in {SeverityLevel.HIGH, SeverityLevel.CRITICAL} and random.random() > 0.35:
            continue

        title, message, instructions = alert_message_for(incident)
        alert = Alert(
            alert_id=f"demo_alert_{counter:03d}",
            incident_id=incident.id,
            crisis_type=incident.crisis_type,
            severity=incident.severity,
            status=AlertStatus.ACTIVE if incident.status != IncidentStatus.RESOLVED else AlertStatus.EXPIRED,
            latitude=incident.latitude,
            longitude=incident.longitude,
            affected_radius_meters=decimal_value(750 if incident.severity == SeverityLevel.CRITICAL else 400),
            title=title,
            message=message,
            safety_instructions=instructions,
            issued_at=incident.last_updated_at or now,
            expires_at=(incident.last_updated_at or now) + timedelta(hours=3),
            affected_population_estimate=decimal_value(random.randint(800, 7000)),
            priority_level=incident.severity.value,
            sms_sent_count=decimal_value(random.randint(120, 1800)),
            push_sent_count=decimal_value(random.randint(300, 4500)),
            tags=[incident.crisis_type.value.lower(), "demo", "ai-alert"],
        )
        db.add(alert)
        alerts.append(alert)
        counter += 1

    db.commit()
    return alerts


def create_dispatch_logs(db, incidents: list[Incident]) -> list[DispatchLog]:
    dispatches: list[DispatchLog] = []
    counter = 1

    for incident in incidents:
        if incident.status not in {IncidentStatus.VERIFIED, IncidentStatus.PROVISIONAL_CRITICAL, IncidentStatus.DISPATCHED}:
            continue
        if incident.severity not in {SeverityLevel.HIGH, SeverityLevel.CRITICAL} and random.random() > 0.25:
            continue

        dispatched_at = (incident.last_updated_at or datetime.now(UTC).replace(tzinfo=None)) + timedelta(minutes=2)
        eta = 6 if incident.severity == SeverityLevel.CRITICAL else random.randint(10, 25)
        status = DispatchStatus.ARRIVED if incident.severity == SeverityLevel.CRITICAL else DispatchStatus.DISPATCHED

        dispatch = DispatchLog(
            dispatch_id=f"demo_dispatch_{counter:03d}",
            incident_id=incident.id,
            crisis_type=incident.crisis_type,
            authority_type=AUTHORITY_BY_CRISIS.get(incident.crisis_type, AuthorityType.DISASTER_RESPONSE),
            status=status,
            latitude=incident.latitude,
            longitude=incident.longitude,
            location_description=incident.location_description,
            priority=incident.severity.value,
            units_dispatched=decimal_value(4 if incident.severity == SeverityLevel.CRITICAL else random.randint(1, 3)),
            estimated_arrival_minutes=decimal_value(eta),
            dispatched_at=dispatched_at,
            acknowledged_at=dispatched_at + timedelta(minutes=1),
            arrived_at=dispatched_at + timedelta(minutes=eta) if status == DispatchStatus.ARRIVED else None,
            contact_method="SIMULATED",
            message_sent=f"{incident.severity.value} {incident.crisis_type.value} incident at {incident.location_description}. Response team dispatched.",
            response_notes="Demo dispatch generated from AI incident severity and location analysis.",
            resources_deployed=["Response Unit 1", "Response Unit 2"] if incident.severity != SeverityLevel.CRITICAL else ["Command Unit", "Rescue Unit", "Engine 1", "Engine 2"],
            simulated=True,
            tags=[incident.crisis_type.value.lower(), "demo", "dispatch"],
        )
        db.add(dispatch)
        dispatches.append(dispatch)
        counter += 1

    db.commit()
    return dispatches


def print_credentials() -> None:
    print("\nDemo credentials")
    print("================")
    print(f"Citizen:   {demo_email('citizen', 1)} / {PASSWORD}")
    print(f"Authority: {demo_email('authority', 1)} / {PASSWORD}")
    print(f"Admin:     {demo_email('admin', 1)} / {PASSWORD}")


def main() -> int:
    random.seed(SEED)
    engine.echo = False

    if not ensure_auth_columns():
        print("Auth column verification failed. Run python -m app.db.init_db first.", file=sys.stderr)
        return 1

    db = SessionLocal()
    try:
        users = create_users(db)
        citizens = [user for user in users if user.role == UserRole.CITIZEN]
        reset_demo_data(db, users)

        now = datetime.now(UTC).replace(tzinfo=None)
        showcase = create_showcase_reports(db, citizens, now)
        random_reports = create_random_reports(db, citizens, now, target_count=291)
        all_reports = [report for group in showcase.values() for report in group] + random_reports

        incidents = create_incidents(db, all_reports, showcase)
        confirmations = create_confirmations(db, incidents, citizens)
        agent_runs = create_agent_runs(db, incidents)
        alerts = create_alerts(db, incidents)
        dispatches = create_dispatch_logs(db, incidents)

        print("\nUnified demo seed complete")
        print("==========================")
        print(f"Users:          {len(users)}")
        print(f"Reports:        {len(all_reports)}")
        print(f"Incidents:      {len(incidents)}")
        print(f"Confirmations:  {len(confirmations)}")
        print(f"Agent runs:     {len(agent_runs)}")
        print(f"Alerts:         {len(alerts)}")
        print(f"Dispatch logs:  {len(dispatches)}")
        print("\nShowcase scenarios")
        print("==================")
        print("1. CRITICAL verified fire: Westlands, Waiyaki Way")
        print("2. Developing flood needing confirmation: Thika Road, Roysambu")
        print("3. False/low-confidence wildlife report: Karen, Ngong Road")
        print_credentials()
        return 0

    except Exception as exc:
        db.rollback()
        print(f"Seed failed: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())

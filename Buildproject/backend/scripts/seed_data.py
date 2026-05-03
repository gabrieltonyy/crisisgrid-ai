"""
Seed CrisisGrid AI with hackathon demo users and reports.

Run from Buildproject/backend:
    python scripts/seed_data.py
"""

from __future__ import annotations

import random
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal, engine
from app.db.init_db import ensure_auth_columns
from app.models.report import Report
from app.models.user import User
from app.schemas.common import CrisisType, IncidentStatus, UserRole
from app.services.auth_service import hash_password


PASSWORD = "Password123!"
DEMO_DOMAIN = "demo.crisisgrid.ai"

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


def jitter(value: float, spread: float = 0.006) -> float:
    return round(value + random.uniform(-spread, spread), 7)


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
                phone_number=f"+254711{index:06d}",
                role=UserRole.CITIZEN,
                trust_score=Decimal(str(round(random.uniform(0.45, 0.92), 2))),
            )
        )

    for index in range(1, 6):
        users.append(
            upsert_user(
                db,
                name=f"Authority Demo {index:02d}",
                email=demo_email("authority", index),
                phone_number=f"+254722{index:06d}",
                role=UserRole.AUTHORITY,
                trust_score=Decimal("1.00"),
            )
        )
        users.append(
            upsert_user(
                db,
                name=f"Admin Demo {index:02d}",
                email=demo_email("admin", index),
                phone_number=f"+254733{index:06d}",
                role=UserRole.ADMIN,
                trust_score=Decimal("1.00"),
            )
        )

    db.commit()
    for user in users:
        db.refresh(user)
    return users


def reset_demo_reports(db, users: list[User]) -> None:
    user_ids = [user.id for user in users]
    db.query(Report).filter(Report.user_id.in_(user_ids)).delete(synchronize_session=False)
    db.commit()


def create_reports(db, users: list[User]) -> list[Report]:
    citizens = [user for user in users if user.role == UserRole.CITIZEN]
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
    status_weights = [0.22, 0.16, 0.14, 0.22, 0.08, 0.13, 0.05]

    reports: list[Report] = []
    now = datetime.now(UTC).replace(tzinfo=None)

    for _ in range(300):
        crisis_type = random.choice(crisis_types)
        location_text, latitude, longitude = random.choice(NAIROBI_LOCATIONS)
        status = random.choices(statuses, weights=status_weights, k=1)[0]
        created_at = now - timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        report = Report(
            user_id=random.choice(citizens).id,
            crisis_type=crisis_type,
            description=random.choice(CRISIS_DESCRIPTIONS[crisis_type]),
            latitude=Decimal(str(jitter(latitude))),
            longitude=Decimal(str(jitter(longitude))),
            location_text=location_text,
            status=status,
            confidence_score=Decimal(str(round(random.uniform(35, 98), 2))),
            severity_score=Decimal(str(round(random.uniform(20, 100), 2))),
            source="CITIZEN_APP",
            is_anonymous=random.random() < 0.08,
            image_url=None,
            video_url=None,
            created_at=created_at,
            updated_at=created_at + timedelta(minutes=random.randint(5, 240)),
        )
        reports.append(report)
        db.add(report)

    db.commit()
    return reports


def print_credentials() -> None:
    print("\nDemo credentials")
    print("================")
    print(f"Citizen:   {demo_email('citizen', 1)} / {PASSWORD}")
    print(f"Authority: {demo_email('authority', 1)} / {PASSWORD}")
    print(f"Admin:     {demo_email('admin', 1)} / {PASSWORD}")


def main() -> int:
    random.seed(20260503)
    engine.echo = False
    if not ensure_auth_columns():
        return 1

    db = SessionLocal()
    try:
        users = create_users(db)
        reset_demo_reports(db, users)
        reports = create_reports(db, users)
        print(f"Seed complete: {len(users)} users and {len(reports)} reports.")
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

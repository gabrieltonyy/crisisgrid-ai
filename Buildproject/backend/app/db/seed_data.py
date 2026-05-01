"""
Database Seed Data Script

Seeds the database with demo data for testing and demonstration.
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import User, Report, Incident, Alert, DispatchLog, AgentRun, Confirmation
from app.schemas.common import (
    CrisisType,
    IncidentStatus,
    SeverityLevel,
    UserRole,
    ConfirmationType,
    AlertStatus,
    DispatchStatus,
    AuthorityType,
    AgentName,
    AgentRunStatus,
)

logger = logging.getLogger(__name__)


def create_demo_users(db: Session) -> dict:
    """Create demo users."""
    logger.info("Creating demo users...")
    
    users = {
        "citizen1": User(
            name="John Doe",
            email="john@example.com",
            phone_number="+254712345678",
            role=UserRole.CITIZEN,
            trust_score=85.0,
            status="ACTIVE",
        ),
        "citizen2": User(
            name="Jane Smith",
            email="jane@example.com",
            phone_number="+254723456789",
            role=UserRole.CITIZEN,
            trust_score=92.0,
            status="ACTIVE",
        ),
        "authority": User(
            name="Fire Department Nairobi",
            email="fire@nairobi.gov.ke",
            phone_number="+254700000001",
            role=UserRole.AUTHORITY,
            trust_score=100.0,
            status="ACTIVE",
        ),
        "admin": User(
            name="Admin User",
            email="admin@crisisgrid.ai",
            phone_number="+254700000000",
            role=UserRole.ADMIN,
            trust_score=100.0,
            status="ACTIVE",
        ),
    }
    
    for user in users.values():
        db.add(user)
    
    db.commit()
    logger.info(f"✓ Created {len(users)} demo users")
    return users


def create_demo_reports(db: Session, users: dict) -> dict:
    """Create demo reports."""
    logger.info("Creating demo reports...")

    reports = {
        "fire1": Report(
            user_id=users["citizen1"].id,
            crisis_type=CrisisType.FIRE,
            latitude=-1.2921,
            longitude=36.8219,
            description="Large fire at Westlands shopping center. Heavy smoke visible.",
            confidence_score=75.0,
            severity_score=85.0,
            status=IncidentStatus.PENDING_VERIFICATION,
            source="CITIZEN_APP",
            is_anonymous=False,
            image_url="https://example.com/fire1.jpg",
        ),
        "fire2": Report(
            user_id=users["citizen2"].id,
            crisis_type=CrisisType.FIRE,
            latitude=-1.2925,
            longitude=36.8215,
            description="Confirming fire at Westlands. Multiple floors affected.",
            confidence_score=85.0,
            severity_score=95.0,
            status=IncidentStatus.VERIFIED,
            source="CITIZEN_APP",
            is_anonymous=False,
            image_url="https://example.com/fire2.jpg",
        ),
        "flood1": Report(
            user_id=users["citizen1"].id,
            crisis_type=CrisisType.FLOOD,
            latitude=-1.3167,
            longitude=36.8833,
            description="Heavy flooding on Thika Road. Water level rising rapidly.",
            confidence_score=65.0,
            severity_score=70.0,
            status=IncidentStatus.PENDING_VERIFICATION,
            source="CITIZEN_APP",
            is_anonymous=False,
        ),
    }
    
    for report in reports.values():
        db.add(report)
    
    db.commit()
    logger.info(f"✓ Created {len(reports)} demo reports")
    return reports


def create_demo_incidents(db: Session, reports: dict) -> dict:
    """Create demo incidents."""
    logger.info("Creating demo incidents...")
    
    now = datetime.utcnow()
    
    incidents = {
        "fire_westlands": Incident(
            id="incident_fire_001",
            crisis_type=CrisisType.FIRE,
            status=IncidentStatus.VERIFIED,
            severity=SeverityLevel.CRITICAL,
            latitude=-1.2923,
            longitude=36.8217,
            location_description="Westlands Shopping Center, Nairobi",
            confidence_score=82.5,
            media_confidence=85.0,
            cross_report_confidence=90.0,
            external_signal_confidence=75.0,
            reporter_trust_confidence=88.5,
            geo_time_consistency=80.0,
            report_count=2,
            first_reported_at=now - timedelta(minutes=15),
            last_updated_at=now - timedelta(minutes=5),
            description="Major fire incident at Westlands Shopping Center",
            tags=["commercial", "high-density", "urgent"],
        ),
        "flood_thika": Incident(
            id="incident_flood_001",
            crisis_type=CrisisType.FLOOD,
            status=IncidentStatus.PENDING_VERIFICATION,
            severity=SeverityLevel.MEDIUM,
            latitude=-1.3167,
            longitude=36.8833,
            location_description="Thika Road, Nairobi",
            confidence_score=65.0,
            media_confidence=50.0,
            cross_report_confidence=60.0,
            external_signal_confidence=70.0,
            reporter_trust_confidence=85.0,
            geo_time_consistency=75.0,
            report_count=1,
            first_reported_at=now - timedelta(hours=1),
            last_updated_at=now - timedelta(hours=1),
            description="Flooding reported on Thika Road",
            tags=["highway", "traffic"],
        ),
    }
    
    # Link reports to incidents
    reports["fire1"].incident_id = incidents["fire_westlands"].id
    reports["fire2"].incident_id = incidents["fire_westlands"].id
    reports["flood1"].incident_id = incidents["flood_thika"].id
    
    for incident in incidents.values():
        db.add(incident)
    
    db.commit()
    logger.info(f"✓ Created {len(incidents)} demo incidents")
    return incidents


def create_demo_alerts(db: Session, incidents: dict) -> dict:
    """Create demo alerts."""
    logger.info("Creating demo alerts...")
    
    now = datetime.utcnow()
    
    alerts = {
        "fire_alert": Alert(
            alert_id="alert_fire_001",
            incident_id=incidents["fire_westlands"].id,
            crisis_type=CrisisType.FIRE,
            severity=SeverityLevel.CRITICAL,
            status=AlertStatus.ACTIVE,
            latitude=-1.2923,
            longitude=36.8217,
            affected_radius_meters=500.0,
            title="CRITICAL: Major Fire at Westlands Shopping Center",
            message="A major fire has been confirmed at Westlands Shopping Center. Evacuate immediately if you are within 500 meters. Emergency services are responding.",
            safety_instructions=[
                "Evacuate the building immediately",
                "Use stairs, not elevators",
                "Stay low to avoid smoke",
                "Move at least 500 meters away",
                "Call 999 if you need assistance",
            ],
            issued_at=now - timedelta(minutes=5),
            expires_at=now + timedelta(hours=2),
            affected_population_estimate=5000.0,
            priority_level="CRITICAL",
            sms_sent_count=1250.0,
            push_sent_count=3800.0,
            tags=["fire", "evacuation", "critical"],
        ),
    }
    
    for alert in alerts.values():
        db.add(alert)
    
    db.commit()
    logger.info(f"✓ Created {len(alerts)} demo alerts")
    return alerts


def create_demo_dispatch_logs(db: Session, incidents: dict) -> dict:
    """Create demo dispatch logs."""
    logger.info("Creating demo dispatch logs...")
    
    now = datetime.utcnow()
    
    dispatch_logs = {
        "fire_dispatch": DispatchLog(
            dispatch_id="dispatch_fire_001",
            incident_id=incidents["fire_westlands"].id,
            crisis_type=CrisisType.FIRE,
            authority_type=AuthorityType.FIRE_SERVICE,
            status=DispatchStatus.ARRIVED,
            latitude=-1.2923,
            longitude=36.8217,
            location_description="Westlands Shopping Center, Nairobi",
            priority="CRITICAL",
            units_dispatched=4.0,
            estimated_arrival_minutes=8.0,
            dispatched_at=now - timedelta(minutes=10),
            acknowledged_at=now - timedelta(minutes=9),
            arrived_at=now - timedelta(minutes=2),
            contact_method="SIMULATED",
            message_sent="CRITICAL fire incident at Westlands Shopping Center. 4 units dispatched.",
            response_notes="Units arrived on scene. Fire suppression in progress.",
            resources_deployed=["Fire Engine 1", "Fire Engine 2", "Ladder Truck", "Rescue Unit"],
            simulated=True,
            tags=["fire", "critical", "commercial"],
        ),
    }
    
    for dispatch_log in dispatch_logs.values():
        db.add(dispatch_log)
    
    db.commit()
    logger.info(f"✓ Created {len(dispatch_logs)} demo dispatch logs")
    return dispatch_logs


def create_demo_agent_runs(db: Session, reports: dict, incidents: dict) -> dict:
    """Create demo agent runs."""
    logger.info("Creating demo agent runs...")
    
    now = datetime.utcnow()
    
    agent_runs = {
        "verification1": AgentRun(
            run_id="run_verification_001",
            agent_name=AgentName.VERIFICATION_AGENT,
            status=AgentRunStatus.SUCCESS,
            report_id=reports["fire1"].id,
            incident_id=incidents["fire_westlands"].id,
            started_at=now - timedelta(minutes=14),
            completed_at=now - timedelta(minutes=14, seconds=3),
            duration_seconds=3.2,
            input_data={"report_id": str(reports["fire1"].id)},
            output_data={"confidence": 75.0, "verified": True},
            confidence_score=75.0,
            decision="VERIFIED",
            model_used="rule-based",
        ),
        "georisk1": AgentRun(
            run_id="run_georisk_001",
            agent_name=AgentName.GEORISK_AGENT,
            status=AgentRunStatus.SUCCESS,
            incident_id=incidents["fire_westlands"].id,
            started_at=now - timedelta(minutes=13),
            completed_at=now - timedelta(minutes=13, seconds=2),
            duration_seconds=2.1,
            input_data={"incident_id": incidents["fire_westlands"].id},
            output_data={"risk_level": "HIGH", "affected_radius": 500},
            risk_level="HIGH",
            decision="HIGH_RISK",
            model_used="geospatial-analysis",
        ),
    }
    
    for agent_run in agent_runs.values():
        db.add(agent_run)
    
    db.commit()
    logger.info(f"✓ Created {len(agent_runs)} demo agent runs")
    return agent_runs


def create_demo_confirmations(db: Session, reports: dict, users: dict) -> dict:
    """Create demo confirmations."""
    logger.info("Creating demo confirmations...")
    
    now = datetime.utcnow()
    
    confirmations = {
        "confirm1": Confirmation(
            confirmation_id="confirm_001",
            report_id=reports["fire1"].id,
            user_id=users["citizen2"].id,
            confirmation_type=ConfirmationType.CONFIRM,
            latitude=-1.2925,
            longitude=36.8215,
            distance_from_report_meters=45.0,
            notes="I can see the fire from my location. Very large flames.",
            confirmed_at=now - timedelta(minutes=12),
            trust_weight=0.92,
        ),
    }
    
    for confirmation in confirmations.values():
        db.add(confirmation)
    
    db.commit()
    logger.info(f"✓ Created {len(confirmations)} demo confirmations")
    return confirmations


def seed_database() -> bool:
    """
    Seed database with demo data.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("DATABASE SEEDING")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Create demo data
        users = create_demo_users(db)
        reports = create_demo_reports(db, users)
        incidents = create_demo_incidents(db, reports)
        alerts = create_demo_alerts(db, incidents)
        dispatch_logs = create_demo_dispatch_logs(db, incidents)
        agent_runs = create_demo_agent_runs(db, reports, incidents)
        confirmations = create_demo_confirmations(db, reports, users)
        
        logger.info("=" * 60)
        logger.info("✓ DATABASE SEEDING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Users: {len(users)}")
        logger.info(f"Reports: {len(reports)}")
        logger.info(f"Incidents: {len(incidents)}")
        logger.info(f"Alerts: {len(alerts)}")
        logger.info(f"Dispatch Logs: {len(dispatch_logs)}")
        logger.info(f"Agent Runs: {len(agent_runs)}")
        logger.info(f"Confirmations: {len(confirmations)}")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to seed database: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Seed database
    import sys
    success = seed_database()
    sys.exit(0 if success else 1)

# Made with Bob

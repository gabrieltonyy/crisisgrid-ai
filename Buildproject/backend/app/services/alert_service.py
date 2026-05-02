"""
Alert service for generating and managing crisis alerts.
Implements alert generation logic based on verified incidents.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging
import random

from app.models.incident import Incident
from app.models.alert import Alert
from app.repositories.alert_repository import alert_repository
from app.schemas.common import (
    CrisisType, 
    IncidentStatus, 
    SeverityLevel, 
    AlertStatus,
    AgentName,
    AgentRunStatus
)
from app.services.georisk_service import get_alert_radius
from app.services.cloudant_service import cloudant_service
from app.utils.ids import generate_alert_id, generate_agent_run_id
from app.utils.time import utc_now
from datetime import timedelta

logger = logging.getLogger(__name__)


class AlertService:
    """Service for alert generation and management."""
    
    # Alert level thresholds based on risk score
    ALERT_THRESHOLDS = {
        "CRITICAL": 90.0,
        "HIGH": 80.0,
        "MEDIUM": 70.0,
        "LOW": 0.0
    }
    
    # Crisis-specific alert messages
    ALERT_MESSAGES = {
        CrisisType.FIRE: {
            "CRITICAL": "CRITICAL FIRE ALERT: Large fire reported. Evacuate immediately if in affected area.",
            "HIGH": "HIGH FIRE ALERT: Fire reported nearby. Avoid the area and follow official instructions.",
            "MEDIUM": "FIRE ALERT: Fire incident reported. Stay alert and monitor updates.",
            "LOW": "Fire incident reported in your area. Exercise caution."
        },
        CrisisType.FLOOD: {
            "CRITICAL": "CRITICAL FLOOD ALERT: Severe flooding reported. Evacuate to higher ground immediately.",
            "HIGH": "HIGH FLOOD ALERT: Flooding reported. Move to higher ground and avoid water.",
            "MEDIUM": "FLOOD ALERT: Flood risk in your area. Prepare for possible evacuation.",
            "LOW": "Flood incident reported. Monitor water levels and stay informed."
        },
        CrisisType.WILDLIFE: {
            "CRITICAL": "CRITICAL WILDLIFE ALERT: Dangerous animal sighting. Stay indoors and secure premises.",
            "HIGH": "HIGH WILDLIFE ALERT: Wildlife incident reported. Avoid the area and stay alert.",
            "MEDIUM": "WILDLIFE ALERT: Animal sighting reported. Exercise caution in the area.",
            "LOW": "Wildlife activity reported. Be aware of your surroundings."
        },
        CrisisType.ACCIDENT: {
            "CRITICAL": "CRITICAL ACCIDENT ALERT: Major accident reported. Avoid area, emergency services responding.",
            "HIGH": "HIGH ACCIDENT ALERT: Serious accident reported. Avoid the area if possible.",
            "MEDIUM": "ACCIDENT ALERT: Traffic accident reported. Expect delays in the area.",
            "LOW": "Minor accident reported. Exercise caution in the area."
        },
        CrisisType.SECURITY: {
            "CRITICAL": "CRITICAL SECURITY ALERT: Security threat reported. Shelter in place immediately.",
            "HIGH": "HIGH SECURITY ALERT: Security incident reported. Avoid the area and stay alert.",
            "MEDIUM": "SECURITY ALERT: Security concern reported. Exercise caution.",
            "LOW": "Security incident reported. Stay aware of your surroundings."
        },
        CrisisType.HEALTH: {
            "CRITICAL": "CRITICAL HEALTH ALERT: Health emergency reported. Avoid area and seek medical advice.",
            "HIGH": "HIGH HEALTH ALERT: Health incident reported. Follow health authority guidance.",
            "MEDIUM": "HEALTH ALERT: Health concern reported in your area. Take precautions.",
            "LOW": "Health incident reported. Follow standard health protocols."
        },
        CrisisType.LANDSLIDE: {
            "CRITICAL": "CRITICAL LANDSLIDE ALERT: Major landslide reported. Evacuate immediately if in path.",
            "HIGH": "HIGH LANDSLIDE ALERT: Landslide reported. Avoid slopes and unstable areas.",
            "MEDIUM": "LANDSLIDE ALERT: Ground instability reported. Exercise extreme caution.",
            "LOW": "Landslide risk reported. Avoid unstable terrain."
        },
        CrisisType.HAZARDOUS_SPILL: {
            "CRITICAL": "CRITICAL HAZMAT ALERT: Hazardous material spill. Evacuate area immediately.",
            "HIGH": "HIGH HAZMAT ALERT: Hazardous spill reported. Avoid area and stay upwind.",
            "MEDIUM": "HAZMAT ALERT: Chemical spill reported. Avoid the area.",
            "LOW": "Hazardous material incident reported. Exercise caution."
        },
        CrisisType.OTHER: {
            "CRITICAL": "CRITICAL ALERT: Emergency situation reported. Follow official instructions.",
            "HIGH": "HIGH ALERT: Crisis reported in your area. Stay alert and informed.",
            "MEDIUM": "ALERT: Incident reported. Exercise caution.",
            "LOW": "Incident reported in your area. Stay informed."
        }
    }
    
    def __init__(self):
        """Initialize alert service."""
        self.cloudant = cloudant_service
    
    def determine_alert_level(self, confidence_score: float) -> str:
        """
        Determine alert level based on confidence score.
        
        Args:
            confidence_score: Incident confidence score (0-100)
            
        Returns:
            Alert level: CRITICAL, HIGH, MEDIUM, or LOW
        """
        if confidence_score >= self.ALERT_THRESHOLDS["CRITICAL"]:
            return "CRITICAL"
        elif confidence_score >= self.ALERT_THRESHOLDS["HIGH"]:
            return "HIGH"
        elif confidence_score >= self.ALERT_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_alert_message(self, crisis_type: CrisisType, alert_level: str) -> str:
        """
        Generate human-readable alert message.
        
        Args:
            crisis_type: Type of crisis
            alert_level: Alert level (CRITICAL, HIGH, MEDIUM, LOW)
            
        Returns:
            Alert message string
        """
        messages = self.ALERT_MESSAGES.get(crisis_type, self.ALERT_MESSAGES[CrisisType.OTHER])
        return messages.get(alert_level, messages["LOW"])
    
    def generate_alert(
        self, 
        db: Session, 
        incident_id: str
    ) -> Optional[Alert]:
        """
        Generate alert for a verified incident.
        
        Business Rules:
        - Only VERIFIED incidents can trigger alerts
        - Risk score must be >= 0.7 (70%)
        - Prevents duplicate alerts for same incident
        - Logs to Cloudant for audit trail
        
        Args:
            db: Database session
            incident_id: Incident ID
            
        Returns:
            Created Alert object or None if conditions not met
        """
        agent_run_id = generate_agent_run_id("alert")
        
        try:
            # Get incident
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if not incident:
                logger.warning(f"Incident {incident_id} not found")
                return None
            
            # Validate incident is VERIFIED
            if incident.status != IncidentStatus.VERIFIED:
                logger.info(f"Incident {incident_id} not verified (status: {incident.status.value})")
                return None
            
            # Check risk score threshold (70%)
            if incident.confidence_score < 70.0:
                logger.info(f"Incident {incident_id} confidence too low: {incident.confidence_score}")
                return None
            
            # Check for duplicate alerts (idempotency)
            if alert_repository.check_duplicate_alert(db, incident_id):
                logger.info(f"Alert already exists for incident {incident_id}")
                existing_alerts = alert_repository.get_active_alerts_by_incident(db, incident_id)
                return existing_alerts[0] if existing_alerts else None
            
            # Determine alert level
            alert_level = self.determine_alert_level(incident.confidence_score)
            severity = SeverityLevel[alert_level]
            
            # Get affected radius from GeoRisk service
            radius_meters = get_alert_radius(incident.crisis_type)
            
            # Generate alert message
            message = self.generate_alert_message(incident.crisis_type, alert_level)
            
            # Generate alert ID
            alert_id = generate_alert_id(incident.crisis_type.value)
            
            # Create alert data
            alert_data = {
                "alert_id": alert_id,
                "incident_id": incident_id,
                "crisis_type": incident.crisis_type,
                "severity": severity,
                "status": AlertStatus.ACTIVE,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "affected_radius_meters": radius_meters,
                "title": f"{incident.crisis_type.value} ALERT",
                "message": message,
                "issued_at": utc_now(),
                "expires_at": utc_now() + timedelta(hours=24),  # 24-hour expiry
                "priority_level": alert_level
            }
            
            # Create alert in database
            alert = alert_repository.create_alert(db, alert_data)
            
            # Log to Cloudant for audit trail
            self._log_alert_generation(
                agent_run_id=agent_run_id,
                incident_id=incident_id,
                alert_id=alert_id,
                alert_level=alert_level,
                confidence_score=incident.confidence_score,
                radius_meters=radius_meters
            )
            
            logger.info(f"Generated {alert_level} alert {alert_id} for incident {incident_id}")
            return alert
            
        except Exception as e:
            logger.error(f"Error generating alert for incident {incident_id}: {e}")
            self._log_alert_generation(
                agent_run_id=agent_run_id,
                incident_id=incident_id,
                alert_id=None,
                alert_level=None,
                confidence_score=None,
                radius_meters=None,
                error=str(e)
            )
            return None
    
    def get_incident_alerts(self, db: Session, incident_id: str) -> List[Alert]:
        """
        Get all alerts for an incident.
        
        Args:
            db: Database session
            incident_id: Incident ID
            
        Returns:
            List of Alert objects
        """
        return alert_repository.get_alerts_by_incident(db, incident_id)
    
    def _log_alert_generation(
        self,
        agent_run_id: str,
        incident_id: str,
        alert_id: Optional[str],
        alert_level: Optional[str],
        confidence_score: Optional[float],
        radius_meters: Optional[int],
        error: Optional[str] = None
    ) -> None:
        """
        Log alert generation to Cloudant.
        
        Args:
            agent_run_id: Agent run ID
            incident_id: Incident ID
            alert_id: Generated alert ID
            alert_level: Alert level
            confidence_score: Incident confidence score
            radius_meters: Alert radius
            error: Error message if failed
        """
        try:
            log_data = {
                "agent_run_id": agent_run_id,
                "agent_name": AgentName.ALERT_AGENT.value,
                "incident_id": incident_id,
                "alert_id": alert_id,
                "alert_level": alert_level,
                "confidence_score": confidence_score,
                "radius_meters": radius_meters,
                "status": AgentRunStatus.FAILED.value if error else AgentRunStatus.SUCCESS.value,
                "error": error,
                "timestamp": utc_now().isoformat()
            }
            
            self.cloudant.store_audit_event(
                event_type="alert_generated",
                event_data=log_data,
                metadata={"agent_run_id": agent_run_id}
            )
        except Exception as e:
            logger.error(f"Failed to log alert generation to Cloudant: {e}")


# Singleton instance
alert_service = AlertService()

# Made with Bob
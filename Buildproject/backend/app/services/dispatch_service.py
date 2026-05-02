"""
Dispatch service for simulating emergency authority dispatch.
Maps crisis types to appropriate authorities and creates dispatch logs.
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session
import logging
import random

from app.models.incident import Incident
from app.models.dispatch_log import DispatchLog
from app.repositories.dispatch_repository import dispatch_repository
from app.schemas.common import (
    CrisisType,
    IncidentStatus,
    AuthorityType,
    DispatchStatus,
    AgentName,
    AgentRunStatus
)
from app.services.cloudant_service import cloudant_service
from app.utils.ids import generate_dispatch_id, generate_agent_run_id
from app.utils.time import utc_now

logger = logging.getLogger(__name__)


class DispatchService:
    """Service for emergency authority dispatch simulation."""
    
    # Crisis type to authority mapping
    AUTHORITY_MAPPING = {
        CrisisType.FIRE: [AuthorityType.FIRE_SERVICE],
        CrisisType.FLOOD: [AuthorityType.DISASTER_MANAGEMENT],
        CrisisType.ACCIDENT: [AuthorityType.AMBULANCE, AuthorityType.POLICE],
        CrisisType.SECURITY: [AuthorityType.POLICE],
        CrisisType.HEALTH: [AuthorityType.PUBLIC_HEALTH, AuthorityType.AMBULANCE],
        CrisisType.WILDLIFE: [AuthorityType.WILDLIFE_AUTHORITY],
        CrisisType.LANDSLIDE: [AuthorityType.DISASTER_MANAGEMENT],
        CrisisType.HAZARDOUS_SPILL: [AuthorityType.DISASTER_MANAGEMENT],
        CrisisType.OTHER: [AuthorityType.POLICE]
    }
    
    # Priority mapping based on confidence score
    PRIORITY_THRESHOLDS = {
        "CRITICAL": 90.0,
        "HIGH": 80.0,
        "MEDIUM": 70.0,
        "LOW": 0.0
    }
    
    def __init__(self):
        """Initialize dispatch service."""
        self.cloudant = cloudant_service
    
    def get_authorities_for_crisis(self, crisis_type: CrisisType) -> List[AuthorityType]:
        """
        Get appropriate authorities for a crisis type.
        
        Args:
            crisis_type: Type of crisis
            
        Returns:
            List of authority types to dispatch
        """
        return self.AUTHORITY_MAPPING.get(crisis_type, [AuthorityType.POLICE])
    
    def determine_priority(self, confidence_score: float) -> str:
        """
        Determine dispatch priority based on confidence score.
        
        Args:
            confidence_score: Incident confidence score (0-100)
            
        Returns:
            Priority level: CRITICAL, HIGH, MEDIUM, or LOW
        """
        if confidence_score >= self.PRIORITY_THRESHOLDS["CRITICAL"]:
            return "CRITICAL"
        elif confidence_score >= self.PRIORITY_THRESHOLDS["HIGH"]:
            return "HIGH"
        elif confidence_score >= self.PRIORITY_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_dispatch_message(
        self, 
        crisis_type: CrisisType, 
        priority: str,
        location: str,
        confidence_score: float
    ) -> str:
        """
        Generate dispatch message for authorities.
        
        Args:
            crisis_type: Type of crisis
            priority: Priority level
            location: Location description
            confidence_score: Confidence score
            
        Returns:
            Dispatch message string
        """
        return (
            f"{priority} priority {crisis_type.value} incident reported. "
            f"Location: {location}. "
            f"Confidence: {confidence_score:.1f}%. "
            f"Immediate response required."
        )
    
    def simulate_eta(self, priority: str) -> int:
        """
        Simulate estimated time of arrival based on priority.
        
        Args:
            priority: Priority level
            
        Returns:
            ETA in minutes
        """
        # Higher priority = faster response
        eta_ranges = {
            "CRITICAL": (3, 7),
            "HIGH": (5, 10),
            "MEDIUM": (8, 15),
            "LOW": (10, 20)
        }
        min_eta, max_eta = eta_ranges.get(priority, (10, 15))
        return random.randint(min_eta, max_eta)
    
    def dispatch_authority(
        self,
        db: Session,
        incident_id: str,
        alert_id: Optional[str] = None
    ) -> List[DispatchLog]:
        """
        Dispatch appropriate authorities for an incident.
        
        Business Rules:
        - Only dispatch for HIGH or CRITICAL priority incidents
        - Maps crisis type to appropriate authorities
        - Simulates ETA (5-15 minutes randomly)
        - Prevents duplicate dispatches
        - Logs to Cloudant for audit trail
        
        Args:
            db: Database session
            incident_id: Incident ID
            alert_id: Optional alert ID
            
        Returns:
            List of created DispatchLog objects
        """
        agent_run_id = generate_agent_run_id("dispatch")
        dispatches = []
        
        try:
            # Get incident
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if not incident:
                logger.warning(f"Incident {incident_id} not found")
                return []
            
            # Determine priority
            priority = self.determine_priority(incident.confidence_score)
            
            # Only dispatch for HIGH or CRITICAL priority
            if priority not in ["HIGH", "CRITICAL"]:
                logger.info(f"Incident {incident_id} priority too low for dispatch: {priority}")
                return []
            
            # Get authorities for crisis type
            authorities = self.get_authorities_for_crisis(incident.crisis_type)
            
            # Create dispatch for each authority
            for authority_type in authorities:
                # Check for duplicate dispatch (idempotency)
                if dispatch_repository.check_duplicate_dispatch(db, incident_id, authority_type.value):
                    logger.info(f"Dispatch already exists for incident {incident_id}, authority {authority_type.value}")
                    continue
                
                # Generate dispatch ID
                dispatch_id = generate_dispatch_id(incident.crisis_type.value)
                
                # Simulate ETA
                eta_minutes = self.simulate_eta(priority)
                
                # Generate dispatch message
                location = incident.location_description or f"{incident.latitude}, {incident.longitude}"
                message = self.generate_dispatch_message(
                    incident.crisis_type,
                    priority,
                    location,
                    incident.confidence_score
                )
                
                # Create dispatch data
                dispatch_data = {
                    "dispatch_id": dispatch_id,
                    "incident_id": incident_id,
                    "crisis_type": incident.crisis_type,
                    "authority_type": authority_type,
                    "status": DispatchStatus.SIMULATED_SENT,
                    "latitude": incident.latitude,
                    "longitude": incident.longitude,
                    "location_description": location,
                    "priority": priority,
                    "units_dispatched": 1,
                    "estimated_arrival_minutes": eta_minutes,
                    "dispatched_at": utc_now(),
                    "contact_method": "SIMULATED",
                    "message_sent": message,
                    "simulated": True
                }
                
                # Create dispatch in database
                dispatch = dispatch_repository.create_dispatch(db, dispatch_data)
                dispatches.append(dispatch)
                
                # Log to Cloudant
                self._log_dispatch(
                    agent_run_id=agent_run_id,
                    incident_id=incident_id,
                    dispatch_id=dispatch_id,
                    authority_type=authority_type.value,
                    priority=priority,
                    eta_minutes=eta_minutes
                )
                
                logger.info(
                    f"Dispatched {authority_type.value} for incident {incident_id} "
                    f"(priority: {priority}, ETA: {eta_minutes} min)"
                )
            
            return dispatches
            
        except Exception as e:
            logger.error(f"Error dispatching authorities for incident {incident_id}: {e}")
            self._log_dispatch(
                agent_run_id=agent_run_id,
                incident_id=incident_id,
                dispatch_id=None,
                authority_type=None,
                priority=None,
                eta_minutes=None,
                error=str(e)
            )
            return []
    
    def get_incident_dispatches(self, db: Session, incident_id: str) -> List[DispatchLog]:
        """
        Get all dispatches for an incident.
        
        Args:
            db: Database session
            incident_id: Incident ID
            
        Returns:
            List of DispatchLog objects
        """
        return dispatch_repository.get_dispatches_by_incident(db, incident_id)
    
    def _log_dispatch(
        self,
        agent_run_id: str,
        incident_id: str,
        dispatch_id: Optional[str],
        authority_type: Optional[str],
        priority: Optional[str],
        eta_minutes: Optional[int],
        error: Optional[str] = None
    ) -> None:
        """
        Log dispatch to Cloudant.
        
        Args:
            agent_run_id: Agent run ID
            incident_id: Incident ID
            dispatch_id: Generated dispatch ID
            authority_type: Authority type
            priority: Priority level
            eta_minutes: Estimated arrival time
            error: Error message if failed
        """
        try:
            log_data = {
                "agent_run_id": agent_run_id,
                "agent_name": AgentName.DISPATCH_AGENT.value,
                "incident_id": incident_id,
                "dispatch_id": dispatch_id,
                "authority_type": authority_type,
                "priority": priority,
                "eta_minutes": eta_minutes,
                "status": AgentRunStatus.FAILED.value if error else AgentRunStatus.SUCCESS.value,
                "error": error,
                "timestamp": utc_now().isoformat()
            }
            
            self.cloudant.store_agent_log(
                agent_name=AgentName.DISPATCH_AGENT.value,
                agent_run_id=agent_run_id,
                input_data={"incident_id": incident_id},
                output_data=log_data,
                status=AgentRunStatus.FAILED.value if error else AgentRunStatus.SUCCESS.value
            )
        except Exception as e:
            logger.error(f"Failed to log dispatch to Cloudant: {e}")


# Singleton instance
dispatch_service = DispatchService()

# Made with Bob
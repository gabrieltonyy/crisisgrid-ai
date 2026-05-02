"""
GeoRisk service for assessing geographic risk and clustering incidents.
Implements crisis-specific radius rules and spatial analysis.
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.schemas.common import CrisisType, SeverityLevel, AgentName, AgentRunStatus
from app.utils.geo import haversine_distance, is_within_radius, calculate_centroid, get_bounding_box
from app.utils.time import utc_now
from app.utils.ids import generate_agent_run_id
from app.services.cloudant_service import cloudant_service

logger = logging.getLogger(__name__)


# Crisis-specific radius rules (in meters)
CRISIS_RADIUS_CONFIG = {
    CrisisType.FIRE: {
        "clustering_radius": 500,  # Reports within 500m are same incident
        "alert_radius": 1000,      # Alert citizens within 1km
        "evacuation_radius": 2000, # Evacuation zone for severe fires
        "description": "Fire spreads rapidly, tight clustering needed"
    },
    CrisisType.FLOOD: {
        "clustering_radius": 1000,  # Floods affect larger areas
        "alert_radius": 2000,       # Alert wider area due to water flow
        "evacuation_radius": 3000,  # Large evacuation zones
        "description": "Floods affect large areas, wider clustering"
    },
    CrisisType.WILDLIFE: {
        "clustering_radius": 1500,  # Animals can move between reports
        "alert_radius": 2500,       # Wide alert for animal movement
        "evacuation_radius": 1000,  # Smaller evacuation for wildlife
        "description": "Wildlife can move, wider clustering radius"
    },
    CrisisType.ACCIDENT: {
        "clustering_radius": 300,   # Accidents are localized
        "alert_radius": 500,        # Alert immediate area
        "evacuation_radius": 200,   # Small evacuation if needed
        "description": "Accidents are point events, tight clustering"
    },
    CrisisType.SECURITY: {
        "clustering_radius": 700,   # Security incidents can span blocks
        "alert_radius": 1500,       # Wide alert for safety
        "evacuation_radius": 1000,  # Moderate evacuation zone
        "description": "Security incidents need moderate clustering"
    },
    CrisisType.HEALTH: {
        "clustering_radius": 500,   # Health incidents localized
        "alert_radius": 1000,       # Alert for potential spread
        "evacuation_radius": 500,   # Small evacuation zone
        "description": "Health incidents localized but need alerts"
    },
    CrisisType.LANDSLIDE: {
        "clustering_radius": 800,   # Landslides affect slopes
        "alert_radius": 1500,       # Alert downslope areas
        "evacuation_radius": 2000,  # Large evacuation for safety
        "description": "Landslides affect slopes and downslope areas"
    },
    CrisisType.HAZARDOUS_SPILL: {
        "clustering_radius": 1000,  # Spills can spread
        "alert_radius": 2000,       # Wide alert for contamination
        "evacuation_radius": 1500,  # Moderate evacuation zone
        "description": "Hazardous materials need wide safety zones"
    },
    CrisisType.OTHER: {
        "clustering_radius": 500,   # Default moderate clustering
        "alert_radius": 1000,       # Default alert radius
        "evacuation_radius": 1000,  # Default evacuation zone
        "description": "Default configuration for unknown crisis types"
    }
}


def get_clustering_radius(crisis_type: CrisisType) -> int:
    """
    Get clustering radius for a crisis type.
    
    Args:
        crisis_type: Type of crisis
        
    Returns:
        Clustering radius in meters
    """
    return CRISIS_RADIUS_CONFIG.get(crisis_type, CRISIS_RADIUS_CONFIG[CrisisType.OTHER])["clustering_radius"]


def get_alert_radius(crisis_type: CrisisType) -> int:
    """
    Get alert radius for a crisis type.
    
    Args:
        crisis_type: Type of crisis
        
    Returns:
        Alert radius in meters
    """
    return CRISIS_RADIUS_CONFIG.get(crisis_type, CRISIS_RADIUS_CONFIG[CrisisType.OTHER])["alert_radius"]


def get_evacuation_radius(crisis_type: CrisisType) -> int:
    """
    Get evacuation radius for a crisis type.
    
    Args:
        crisis_type: Type of crisis
        
    Returns:
        Evacuation radius in meters
    """
    return CRISIS_RADIUS_CONFIG.get(crisis_type, CRISIS_RADIUS_CONFIG[CrisisType.OTHER])["evacuation_radius"]


class GeoRiskService:
    """Service for geographic risk assessment and spatial analysis."""
    
    def __init__(self, db: Session):
        """
        Initialize GeoRisk service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def assess_geographic_risk(
        self,
        latitude: float,
        longitude: float,
        crisis_type: CrisisType,
        severity: SeverityLevel = SeverityLevel.MEDIUM
    ) -> Dict[str, Any]:
        """
        Assess geographic risk for a location and crisis type.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            crisis_type: Type of crisis
            severity: Severity level of the crisis
            
        Returns:
            Dictionary with risk assessment results
        """
        agent_run_id = generate_agent_run_id("georisk")
        
        logger.info(
            f"Assessing geographic risk at ({latitude}, {longitude}) "
            f"for {crisis_type.value}"
        )
        
        # Get crisis-specific radii
        clustering_radius = get_clustering_radius(crisis_type)
        alert_radius = get_alert_radius(crisis_type)
        evacuation_radius = get_evacuation_radius(crisis_type)
        
        # Calculate risk zones
        risk_zones = self._calculate_risk_zones(
            latitude, longitude, crisis_type, severity
        )
        
        # Find nearby incidents
        nearby_incidents = self._find_nearby_incidents(
            latitude, longitude, crisis_type, clustering_radius
        )
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(
            crisis_type, severity, len(nearby_incidents)
        )
        
        # Determine recommended actions
        recommended_actions = self._get_recommended_actions(
            crisis_type, severity, risk_score
        )
        
        result = {
            "agent_run_id": agent_run_id,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "crisis_type": crisis_type.value,
            "severity": severity.value,
            "risk_score": risk_score,
            "radii": {
                "clustering_radius_meters": clustering_radius,
                "alert_radius_meters": alert_radius,
                "evacuation_radius_meters": evacuation_radius
            },
            "risk_zones": risk_zones,
            "nearby_incidents_count": len(nearby_incidents),
            "nearby_incidents": nearby_incidents,
            "recommended_actions": recommended_actions,
            "assessed_at": utc_now().isoformat()
        }
        
        # Log to Cloudant
        self._log_to_cloudant(agent_run_id, result)
        
        return result
    
    def _calculate_risk_zones(
        self,
        latitude: float,
        longitude: float,
        crisis_type: CrisisType,
        severity: SeverityLevel
    ) -> List[Dict[str, Any]]:
        """
        Calculate risk zones around the incident location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            crisis_type: Type of crisis
            severity: Severity level
            
        Returns:
            List of risk zone definitions
        """
        clustering_radius = get_clustering_radius(crisis_type)
        alert_radius = get_alert_radius(crisis_type)
        evacuation_radius = get_evacuation_radius(crisis_type)
        
        zones = [
            {
                "zone_type": "immediate_danger",
                "radius_meters": clustering_radius,
                "description": "Immediate danger zone - incident clustering area",
                "action": "Avoid area, emergency response only"
            },
            {
                "zone_type": "alert_zone",
                "radius_meters": alert_radius,
                "description": "Alert zone - citizens should be notified",
                "action": "Stay alert, follow safety guidelines"
            }
        ]
        
        # Add evacuation zone for high severity incidents
        if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            zones.append({
                "zone_type": "evacuation_zone",
                "radius_meters": evacuation_radius,
                "description": "Potential evacuation zone for severe incidents",
                "action": "Prepare for possible evacuation"
            })
        
        return zones
    
    def _find_nearby_incidents(
        self,
        latitude: float,
        longitude: float,
        crisis_type: CrisisType,
        radius_meters: float,
        time_window_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Find nearby incidents of the same type within time window.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            crisis_type: Type of crisis
            radius_meters: Search radius in meters
            time_window_hours: Time window in hours
            
        Returns:
            List of nearby incident summaries
        """
        from app.models.incident import Incident
        
        # Calculate time threshold
        time_threshold = utc_now() - timedelta(hours=time_window_hours)
        
        # Get bounding box for efficient query
        bbox = get_bounding_box(latitude, longitude, radius_meters)
        
        # Query incidents within bounding box
        incidents = self.db.query(Incident).filter(
            Incident.crisis_type == crisis_type,
            Incident.latitude >= bbox["min_lat"],
            Incident.latitude <= bbox["max_lat"],
            Incident.longitude >= bbox["min_lon"],
            Incident.longitude <= bbox["max_lon"],
            Incident.created_at >= time_threshold
        ).all()
        
        # Filter by exact distance and format results
        nearby = []
        for incident in incidents:
            # SQLAlchemy returns Float values at runtime, type checker doesn't know this
            distance = haversine_distance(
                latitude, longitude,
                float(incident.latitude),  # type: ignore
                float(incident.longitude)  # type: ignore
            )
            
            if distance <= radius_meters:
                nearby.append({
                    "incident_id": incident.id,
                    "distance_meters": round(distance, 2),
                    "confidence_score": incident.confidence_score,
                    "severity": incident.severity.value,
                    "status": incident.status.value,
                    "created_at": incident.created_at.isoformat()
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x["distance_meters"])
        
        return nearby
    
    def _calculate_risk_score(
        self,
        crisis_type: CrisisType,
        severity: SeverityLevel,
        nearby_count: int
    ) -> float:
        """
        Calculate overall risk score (0-100).
        
        Args:
            crisis_type: Type of crisis
            severity: Severity level
            nearby_count: Number of nearby incidents
            
        Returns:
            Risk score (0-100)
        """
        # Base score from severity
        severity_scores = {
            SeverityLevel.LOW: 25,
            SeverityLevel.MEDIUM: 50,
            SeverityLevel.HIGH: 75,
            SeverityLevel.CRITICAL: 90
        }
        base_score = severity_scores.get(severity, 50)
        
        # Adjust for crisis type urgency
        urgency_multipliers = {
            CrisisType.FIRE: 1.2,
            CrisisType.FLOOD: 1.15,
            CrisisType.WILDLIFE: 1.0,
            CrisisType.ACCIDENT: 1.1,
            CrisisType.SECURITY: 1.15,
            CrisisType.HEALTH: 1.1,
            CrisisType.LANDSLIDE: 1.2,
            CrisisType.HAZARDOUS_SPILL: 1.25,
            CrisisType.OTHER: 1.0
        }
        multiplier = urgency_multipliers.get(crisis_type, 1.0)
        
        # Adjust for nearby incidents (clustering increases risk)
        cluster_bonus = min(20, nearby_count * 5)
        
        # Calculate final score
        risk_score = min(100, (base_score * multiplier) + cluster_bonus)
        
        return round(risk_score, 2)
    
    def _get_recommended_actions(
        self,
        crisis_type: CrisisType,
        severity: SeverityLevel,
        risk_score: float
    ) -> List[str]:
        """
        Get recommended actions based on risk assessment.
        
        Args:
            crisis_type: Type of crisis
            severity: Severity level
            risk_score: Calculated risk score
            
        Returns:
            List of recommended actions
        """
        actions = []
        
        # High risk actions
        if risk_score >= 75:
            actions.append("IMMEDIATE: Dispatch emergency services")
            actions.append("IMMEDIATE: Issue public alert")
            if severity == SeverityLevel.CRITICAL:
                actions.append("IMMEDIATE: Consider evacuation orders")
        
        # Medium risk actions
        elif risk_score >= 50:
            actions.append("Dispatch emergency services")
            actions.append("Issue public advisory")
            actions.append("Monitor situation closely")
        
        # Lower risk actions
        else:
            actions.append("Verify incident details")
            actions.append("Prepare emergency services for potential dispatch")
            actions.append("Monitor for additional reports")
        
        # Crisis-specific actions
        crisis_actions = {
            CrisisType.FIRE: ["Alert fire department", "Check wind conditions"],
            CrisisType.FLOOD: ["Alert disaster management", "Monitor water levels"],
            CrisisType.WILDLIFE: ["Alert wildlife authority", "Issue safety guidelines"],
            CrisisType.HEALTH: ["Alert public health", "Implement containment measures"],
            CrisisType.HAZARDOUS_SPILL: ["Alert hazmat team", "Establish containment zone"]
        }
        
        if crisis_type in crisis_actions:
            actions.extend(crisis_actions[crisis_type])
        
        return actions
    
    def _log_to_cloudant(self, agent_run_id: str, result: Dict[str, Any]) -> None:
        """
        Log GeoRisk assessment to Cloudant.
        
        Args:
            agent_run_id: Agent run ID
            result: Assessment result
        """
        if not cloudant_service.enabled:
            return
        
        try:
            cloudant_service.store_agent_log(
                agent_run_id=agent_run_id,
                agent_type="georisk_agent",
                payload=result
            )
        except Exception as e:
            logger.error(f"Failed to log to Cloudant: {e}")


def get_georisk_service(db: Session) -> GeoRiskService:
    """
    Factory function to get GeoRisk service instance.
    
    Args:
        db: Database session
        
    Returns:
        GeoRiskService instance
    """
    return GeoRiskService(db)

# Made with Bob
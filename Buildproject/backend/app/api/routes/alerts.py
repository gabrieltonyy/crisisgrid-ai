"""
Alert API routes for CrisisGrid AI.
Handles alert generation and retrieval endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.services.alert_service import alert_service
from app.schemas.alerts import AlertResponse
from app.schemas.common import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post(
    "/generate/{incident_id}",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate alert for incident",
    description="Generate a public safety alert for a verified incident"
)
async def generate_alert(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate alert for a verified incident.
    
    Business Rules:
    - Only VERIFIED incidents can trigger alerts
    - Risk score must be >= 0.7 (70%)
    - Prevents duplicate alerts for same incident
    - Logs to Cloudant for audit trail
    
    Args:
        incident_id: Incident ID
        db: Database session
        
    Returns:
        API response with alert data
        
    Raises:
        404: Incident not found or doesn't meet alert criteria
    """
    try:
        alert = alert_service.generate_alert(db, incident_id)
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot generate alert for incident {incident_id}. "
                       "Incident must be VERIFIED with confidence >= 70%"
            )
        
        # Convert to response schema
        alert_response = AlertResponse(
            id=alert.alert_id,
            incident_id=alert.incident_id,
            crisis_type=alert.crisis_type,
            alert_title=alert.title,
            alert_message=alert.message,
            severity=alert.severity,
            target_radius_meters=alert.affected_radius_meters,
            latitude=alert.latitude,
            longitude=alert.longitude,
            location_text=alert.incident.location_description if alert.incident else None,
            status=alert.status,
            created_at=alert.issued_at,
            expires_at=alert.expires_at
        )
        
        return APIResponse(
            success=True,
            message=f"Alert generated successfully for incident {incident_id}",
            data=alert_response.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating alert for incident {incident_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate alert: {str(e)}"
        )


@router.get(
    "/{incident_id}",
    response_model=APIResponse,
    summary="Get alerts for incident",
    description="Retrieve all alerts associated with an incident"
)
async def get_incident_alerts(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all alerts for an incident.
    
    Args:
        incident_id: Incident ID
        db: Database session
        
    Returns:
        API response with list of alerts
    """
    try:
        alerts = alert_service.get_incident_alerts(db, incident_id)
        
        # Convert to response schemas
        alert_responses = [
            AlertResponse(
                id=alert.alert_id,
                incident_id=alert.incident_id,
                crisis_type=alert.crisis_type,
                alert_title=alert.title,
                alert_message=alert.message,
                severity=alert.severity,
                target_radius_meters=alert.affected_radius_meters,
                latitude=alert.latitude,
                longitude=alert.longitude,
                location_text=alert.incident.location_description if alert.incident else None,
                status=alert.status,
                created_at=alert.issued_at,
                expires_at=alert.expires_at
            )
            for alert in alerts
        ]
        
        return APIResponse(
            success=True,
            message=f"Found {len(alerts)} alert(s) for incident {incident_id}",
            data={
                "alerts": [a.model_dump() for a in alert_responses],
                "count": len(alerts)
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving alerts for incident {incident_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alerts: {str(e)}"
        )


# Made with Bob
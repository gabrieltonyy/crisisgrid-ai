"""
Advisory API routes for CrisisGrid AI.
Handles safety advisory generation and retrieval endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.services.advisory_service import advisory_service
from app.schemas.advisory import AdvisoryRequest, AdvisoryResponse
from app.schemas.common import APIResponse, CrisisType, SeverityLevel
from app.utils.time import utc_now

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advisory", tags=["advisory"])


@router.get(
    "/{crisis_type}",
    response_model=AdvisoryResponse,
    summary="Get safety advisory by crisis type",
    description="Generate generic crisis-type advisory content for the citizen portal"
)
async def get_advisory_by_crisis_type(
    crisis_type: CrisisType
) -> AdvisoryResponse:
    """
    Return a generic advisory by crisis type.

    This supports the citizen UI flow where no verified incident has been
    selected yet, but the user needs crisis-specific guidance.
    """
    playbook = advisory_service.get_playbook(crisis_type)
    risk_level = "MODERATE"
    immediate_actions = [
        action if hasattr(action, "priority") else action
        for action in playbook["immediate_actions"]
    ]

    return AdvisoryResponse(
        incident_id=f"generic_{crisis_type.value.lower()}",
        crisis_type=crisis_type,
        severity=SeverityLevel.MEDIUM,
        distance_meters=None,
        risk_level=risk_level,
        primary_advice=advisory_service.generate_primary_advice(
            crisis_type,
            risk_level,
            None
        ),
        immediate_actions=immediate_actions,
        what_to_do=playbook["what_to_do"],
        what_not_to_do=playbook["what_not_to_do"],
        evacuation_advice=playbook["evacuation_template"].format(radius=1000),
        emergency_contacts=playbook["emergency_contacts"],
        additional_resources=[],
        generated_at=utc_now(),
        playbook_used=playbook["playbook_id"],
        ai_enhanced=False
    )


@router.post(
    "/{incident_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Get safety advisory for incident",
    description="Generate personalized safety advice based on incident and user location"
)
async def get_advisory(
    incident_id: str,
    user_latitude: Optional[float] = Query(None, ge=-90, le=90, description="User's current latitude"),
    user_longitude: Optional[float] = Query(None, ge=-180, le=180, description="User's current longitude"),
    user_context: Optional[str] = Query(None, max_length=500, description="User context (e.g., 'at home')"),
    db: Session = Depends(get_db)
):
    """
    Get safety advisory for an incident.
    
    Provides:
    - Crisis-specific safety playbooks
    - Distance-based risk assessment
    - Immediate action recommendations
    - Evacuation guidance
    - Emergency contacts
    - AI-enhanced advice (if available)
    
    Args:
        incident_id: Incident ID
        user_latitude: User's latitude (optional)
        user_longitude: User's longitude (optional)
        user_context: User's context (optional)
        db: Database session
        
    Returns:
        API response with safety advisory
        
    Raises:
        404: Incident not found
        500: Internal server error
    """
    try:
        advisory = advisory_service.generate_advisory(
            db=db,
            incident_id=incident_id,
            user_latitude=user_latitude,
            user_longitude=user_longitude,
            user_context=user_context
        )
        
        if not advisory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        
        return APIResponse(
            success=True,
            message=f"Safety advisory generated for incident {incident_id}",
            data=advisory.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating advisory for incident {incident_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate advisory: {str(e)}"
        )


@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Get safety advisory (POST)",
    description="Generate personalized safety advice using POST body"
)
async def get_advisory_post(
    request: AdvisoryRequest,
    db: Session = Depends(get_db)
):
    """
    Get safety advisory for an incident using POST request.
    
    Alternative endpoint that accepts request body instead of query parameters.
    Useful for more complex requests or when query parameters are not preferred.
    
    Args:
        request: Advisory request with incident ID and optional user location
        db: Database session
        
    Returns:
        API response with safety advisory
        
    Raises:
        404: Incident not found
        500: Internal server error
    """
    try:
        advisory = advisory_service.generate_advisory(
            db=db,
            incident_id=request.incident_id,
            user_latitude=request.user_latitude,
            user_longitude=request.user_longitude,
            user_context=request.user_context
        )
        
        if not advisory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {request.incident_id} not found"
            )
        
        return APIResponse(
            success=True,
            message=f"Safety advisory generated for incident {request.incident_id}",
            data=advisory.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating advisory for incident {request.incident_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate advisory: {str(e)}"
        )


# Made with Bob

"""
Dispatch API routes for CrisisGrid AI.
Handles authority dispatch simulation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.services.dispatch_service import dispatch_service
from app.schemas.dispatch import DispatchLogResponse
from app.schemas.common import APIResponse
from app.repositories.dispatch_repository import dispatch_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


def _to_dispatch_response(dispatch) -> DispatchLogResponse:
    """Convert a DispatchLog model to the public frontend response shape."""
    return DispatchLogResponse(
        id=dispatch.dispatch_id,
        incident_id=dispatch.incident_id,
        authority_type=dispatch.authority_type,
        crisis_type=dispatch.crisis_type,
        message=dispatch.message_sent,
        priority=dispatch.priority,
        status=dispatch.status,
        latitude=dispatch.latitude,
        longitude=dispatch.longitude,
        location_text=dispatch.location_description,
        contact_method=dispatch.contact_method,
        response_time_seconds=dispatch.response_time_seconds,
        created_at=dispatch.dispatched_at,
        acknowledged_at=dispatch.acknowledged_at
    )


@router.get(
    "/logs",
    response_model=list[DispatchLogResponse],
    summary="List dispatch logs",
    description="Retrieve dispatch logs for the admin coordination view"
)
async def list_dispatch_logs(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
) -> list[DispatchLogResponse]:
    """List dispatch logs in newest-first order."""
    try:
        dispatches = dispatch_repository.get_all_dispatches(db, limit=limit)
        return [_to_dispatch_response(dispatch) for dispatch in dispatches]
    except Exception as e:
        logger.error(f"Error listing dispatch logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list dispatch logs: {str(e)}"
        )


@router.post(
    "/{incident_id}",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dispatch authorities for incident",
    description="Dispatch appropriate emergency authorities for a high-priority incident"
)
async def dispatch_authorities(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Dispatch appropriate authorities for an incident.
    
    Business Rules:
    - Only dispatch for HIGH or CRITICAL priority incidents
    - Maps crisis type to appropriate authorities
    - Simulates ETA (5-15 minutes randomly)
    - Prevents duplicate dispatches
    - Logs to Cloudant for audit trail
    
    Args:
        incident_id: Incident ID
        db: Database session
        
    Returns:
        API response with dispatch data
        
    Raises:
        404: Incident not found or doesn't meet dispatch criteria
    """
    try:
        dispatches = dispatch_service.dispatch_authority(db, incident_id)
        
        if not dispatches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot dispatch authorities for incident {incident_id}. "
                       "Incident must have HIGH or CRITICAL priority (confidence >= 80%)"
            )
        
        # Convert to response schemas
        dispatch_responses = [_to_dispatch_response(dispatch) for dispatch in dispatches]
        
        return APIResponse(
            success=True,
            message=f"Dispatched {len(dispatches)} authority/authorities for incident {incident_id}",
            data={
                "dispatches": [d.model_dump() for d in dispatch_responses],
                "count": len(dispatches)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error dispatching authorities for incident {incident_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch authorities: {str(e)}"
        )


@router.get(
    "/{incident_id}",
    response_model=APIResponse,
    summary="Get dispatches for incident",
    description="Retrieve all dispatch logs associated with an incident"
)
async def get_incident_dispatches(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all dispatch logs for an incident.
    
    Args:
        incident_id: Incident ID
        db: Database session
        
    Returns:
        API response with list of dispatches
    """
    try:
        dispatches = dispatch_service.get_incident_dispatches(db, incident_id)
        
        # Convert to response schemas
        dispatch_responses = [_to_dispatch_response(dispatch) for dispatch in dispatches]
        
        return APIResponse(
            success=True,
            message=f"Found {len(dispatches)} dispatch(es) for incident {incident_id}",
            data={
                "dispatches": [d.model_dump() for d in dispatch_responses],
                "count": len(dispatches)
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving dispatches for incident {incident_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dispatches: {str(e)}"
        )


# Made with Bob

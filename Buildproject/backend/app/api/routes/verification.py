"""
Verification API routes for CrisisGrid AI.
Handles report verification, verification history, and pending verifications.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.verification import (
    VerificationRequest,
    VerificationResponse,
    VerificationHistoryResponse,
    VerificationHistoryItem,
    AgentRunSummary,
    PendingVerificationResponse,
    PendingVerificationItem,
    VerificationStatsResponse
)
from app.schemas.common import CrisisType
from app.services.verification_service import get_verification_service
from app.repositories.verification_repository import VerificationRepository
from app.utils.http_errors import (
    database_unavailable_exception,
    is_database_unavailable_error,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/verification", tags=["verification"])


@router.post(
    "/reports/{report_id}/verify",
    response_model=VerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify a crisis report",
    description="Trigger AI-powered verification for a specific report"
)
async def verify_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    request: VerificationRequest = VerificationRequest(force_revalidation=False)
) -> VerificationResponse:
    """
    Verify a crisis report using AI analysis.
    
    This endpoint:
    - Analyzes the report using watsonx.ai
    - Calculates credibility and severity scores
    - Updates report status (VERIFIED or FALSE_REPORT)
    - Creates audit trail in Cloudant
    - Returns detailed verification results
    
    Args:
        report_id: UUID of the report to verify
        request: Verification request options
        db: Database session
        
    Returns:
        VerificationResponse with verification results
        
    Raises:
        HTTPException 404: If report not found
        HTTPException 400: If report already verified (unless force_revalidation)
        HTTPException 500: If verification fails
    """
    try:
        logger.info(f"Verification requested for report {report_id}")
        
        # Get verification service
        verification_service = get_verification_service(db)
        
        # Perform verification
        result = verification_service.verify_report(
            report_id=report_id,
            force_revalidation=request.force_revalidation
        )
        
        logger.info(
            f"Verification complete for {report_id}: "
            f"verified={result.verified}, confidence={result.final_confidence_score}"
        )
        
        return result
        
    except ValueError as e:
        # Report not found or already verified
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    except Exception as e:
        logger.error(f"Verification failed for report {report_id}: {e}")
        if is_database_unavailable_error(e):
            raise database_unavailable_exception()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed"
        )


@router.get(
    "/reports/{report_id}",
    response_model=VerificationHistoryResponse,
    summary="Get verification history",
    description="Retrieve verification history and details for a specific report"
)
async def get_verification_history(
    report_id: UUID,
    db: Session = Depends(get_db)
) -> VerificationHistoryResponse:
    """
    Get verification history for a report.
    
    Returns all verification attempts and their results for the specified report.
    
    Args:
        report_id: UUID of the report
        db: Database session
        
    Returns:
        VerificationHistoryResponse with verification history
        
    Raises:
        HTTPException 404: If report not found
    """
    try:
        repo = VerificationRepository(db)
        
        # Get report
        report = repo.get_report_by_id(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found"
            )
        
        # Get verification history
        agent_runs = repo.get_verification_history(report_id)
        
        # Build history items
        history_items = []
        for agent_run in agent_runs:
            # Extract verification result from output_data if available
            verification_result = None
            if agent_run.output_data and "verification_result" in agent_run.output_data:
                from app.schemas.verification import VerificationResult
                verification_result = VerificationResult(**agent_run.output_data["verification_result"])
            
            history_items.append(
                VerificationHistoryItem(
                    agent_run=AgentRunSummary.model_validate(agent_run),
                    verification_result=verification_result
                )
            )
        
        return VerificationHistoryResponse(
            report_id=report_id,
            current_status=report.status,
            verification_count=len(agent_runs),
            history=history_items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get verification history for {report_id}: {e}")
        if is_database_unavailable_error(e):
            raise database_unavailable_exception()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve verification history"
        )


@router.get(
    "/pending",
    response_model=PendingVerificationResponse,
    summary="List pending verifications",
    description="Get list of reports pending verification with optional filters"
)
async def get_pending_verifications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    crisis_type: Optional[CrisisType] = Query(None, description="Filter by crisis type"),
    created_after: Optional[datetime] = Query(None, description="Filter by creation date"),
    db: Session = Depends(get_db)
) -> PendingVerificationResponse:
    """
    Get list of reports pending verification.
    
    Returns paginated list of reports with PENDING_VERIFICATION status.
    Supports filtering by crisis type and creation date.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        crisis_type: Optional filter by crisis type
        created_after: Optional filter by creation date
        db: Database session
        
    Returns:
        PendingVerificationResponse with paginated results
    """
    try:
        repo = VerificationRepository(db)
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get pending reports
        reports, total = repo.get_pending_verifications(
            skip=skip,
            limit=page_size,
            crisis_type=crisis_type.value if crisis_type else None,
            created_after=created_after
        )
        
        # Build response items
        items = []
        for report in reports:
            items.append(
                PendingVerificationItem(
                    id=report.id,
                    crisis_type=report.crisis_type,
                    description=report.description,
                    latitude=float(report.latitude),
                    longitude=float(report.longitude),
                    location_text=report.location_text,
                    status=report.status,
                    created_at=report.created_at,
                    has_media=bool(report.image_url or report.video_url)
                )
            )
        
        return PendingVerificationResponse(
            total=total,
            items=items,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Failed to get pending verifications: {e}")
        if is_database_unavailable_error(e):
            raise database_unavailable_exception()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pending verifications"
        )


@router.get(
    "/stats",
    response_model=VerificationStatsResponse,
    summary="Get verification statistics",
    description="Get overall verification statistics and metrics"
)
async def get_verification_stats(
    db: Session = Depends(get_db)
) -> VerificationStatsResponse:
    """
    Get verification statistics.
    
    Returns overall metrics about verification operations including:
    - Total verified/rejected/pending reports
    - Average confidence scores
    - Average verification time
    - Verification rate
    
    Args:
        db: Database session
        
    Returns:
        VerificationStatsResponse with statistics
    """
    try:
        repo = VerificationRepository(db)
        stats = repo.get_verification_stats()
        
        return VerificationStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get verification stats: {e}")
        if is_database_unavailable_error(e):
            raise database_unavailable_exception()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve verification statistics"
        )

# Made with Bob

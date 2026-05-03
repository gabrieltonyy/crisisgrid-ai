"""
Reports API routes for CrisisGrid AI.
Handles crisis report submission and retrieval.
"""

from typing import Optional
from uuid import UUID
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.reports import (
    CrisisReportCreateRequest,
    ReportSubmissionResponse,
    ReportResponse
)
from app.repositories.report_repository import ReportRepository
from app.services.cloudant_service import cloudant_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post(
    "",
    response_model=ReportSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a crisis report",
    description="Submit a new crisis report. Supports both anonymous and authenticated submissions."
)
async def create_report(
    report_data: CrisisReportCreateRequest,
    db: Session = Depends(get_db)
) -> ReportSubmissionResponse:
    """
    Create a new crisis report.
    
    This endpoint:
    1. Validates the report data (via Pydantic schema)
    2. Generates a unique report ID
    3. Stores the report in PostgreSQL
    4. Optionally stores raw payload in Cloudant for audit trail
    5. Returns the created report with processing status
    
    Args:
        report_data: Validated crisis report data
        db: Database session
        
    Returns:
        ReportSubmissionResponse with created report and processing status
        
    Raises:
        HTTPException: If report creation fails
    """
    try:
        logger.info(f"Received crisis report: {report_data.crisis_type}")
        
        # Create repository instance
        repo = ReportRepository(db)
        
        # For Phase 3, we don't have authentication yet
        # In future phases, extract user_id from JWT token
        user_id: Optional[UUID] = None
        
        # Create report in PostgreSQL
        report = repo.create(
            report_data=report_data,
            user_id=user_id
        )
        
        logger.info(f"Report created successfully: {report.id}")
        
        # Store raw payload in Cloudant for audit trail (if enabled)
        if cloudant_service.enabled:
            try:
                cloudant_doc_id = cloudant_service.store_raw_report(
                    report_id=str(report.id),
                    report_data=report_data.model_dump(),
                    metadata={
                        "source": "api",
                        "endpoint": "/api/v1/reports",
                        "is_anonymous": report_data.is_anonymous
                    }
                )
                logger.info(f"Raw report stored in Cloudant: {cloudant_doc_id}")
            except Exception as e:
                # Don't fail the request if Cloudant storage fails
                logger.error(f"Failed to store in Cloudant: {e}")
        
        # Store audit event in Cloudant
        if cloudant_service.enabled:
            try:
                cloudant_service.store_audit_event(
                    event_type="report_created",
                    entity_id=str(report.id),
                    entity_type="report",
                    action="create",
                    details={
                        "crisis_type": report_data.crisis_type.value,
                        "is_anonymous": report_data.is_anonymous,
                        "has_image": bool(report_data.image_url),
                        "has_video": bool(report_data.video_url)
                    }
                )
            except Exception as e:
                logger.error(f"Failed to store audit event: {e}")
        
        # Convert SQLAlchemy model to Pydantic response
        report_response = ReportResponse.model_validate(report)
        
        # Build response
        response = ReportSubmissionResponse(
            report=report_response,
            processing_status="QUEUED_FOR_VERIFICATION",
            estimated_verification_time=30  # seconds
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to create report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create report: {str(e)}"
        )


@router.get(
    "",
    response_model=list[ReportResponse],
    summary="List reports",
    description="Retrieve reports for dashboard and citizen tracking views"
)
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
) -> list[ReportResponse]:
    """List reports in newest-first order."""
    try:
        repo = ReportRepository(db)
        reports = repo.get_all(skip=skip, limit=limit, status=status_filter)
        return [ReportResponse.model_validate(report) for report in reports]
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reports: {str(e)}"
        )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report by ID",
    description="Retrieve a specific report by its UUID"
)
async def get_report(
    report_id: UUID,
    db: Session = Depends(get_db)
) -> ReportResponse:
    """
    Get a report by its ID.
    
    Args:
        report_id: Report UUID
        db: Database session
        
    Returns:
        ReportResponse with report details
        
    Raises:
        HTTPException: If report not found
    """
    repo = ReportRepository(db)
    report = repo.get_by_id(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found"
        )
    
    return ReportResponse.model_validate(report)


# Made with Bob

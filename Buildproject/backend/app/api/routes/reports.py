"""
Reports API routes for CrisisGrid AI.
Handles crisis report submission and retrieval.
"""

from typing import Optional, List
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
from app.schemas.common import IncidentStatus
from app.core.config import settings
from app.repositories.report_repository import ReportRepository
from app.services.cloudant_service import cloudant_service
from app.services.orchestration_log_service import persist_pipeline_trace
from app.services.orchestrator_engine import OrchestratorEngine
from app.dependencies.auth import get_current_active_user, get_optional_user
from app.models.user import User

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
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
) -> ReportSubmissionResponse:
    """
    Create a new crisis report.

    This endpoint:
    1. Validates the report data (via Pydantic schema)
    2. Generates a unique report ID
    3. Stores the report in PostgreSQL
    4. Optionally stores raw payload in Cloudant for audit trail
    5. Returns the created report with processing status
    """
    try:
        logger.info(f"Received crisis report: {report_data.crisis_type}")

        # Create repository instance
        repo = ReportRepository(db)

        # Extract user_id from authenticated user, unless report is anonymous
        user_id: Optional[UUID] = None
        if current_user and not report_data.is_anonymous:
            user_id = current_user.id
            logger.info(f"Report submitted by authenticated user: {user_id}")
        else:
            logger.info("Anonymous report submission")

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

        processing_status = "PROCESSED_WITH_REVIEW"
        try:
            orchestrator = OrchestratorEngine()
            trace = orchestrator.run(
                {
                    "report": report,
                    "db": db,
                    "cloudant_enabled": cloudant_service.enabled,
                    "source": "api",
                    "user_context": _build_safe_user_context(current_user),
                }
            )
            persist_pipeline_trace(db=db, report_id=report.id, trace=trace)
            processing_status = _determine_processing_status(trace)

            try:
                db.refresh(report)
            except Exception:
                logger.debug("Report refresh after orchestration was skipped")

            if hasattr(repo, "get_by_id"):
                latest_report = repo.get_by_id(report.id)
                if latest_report:
                    report = latest_report

        except Exception as e:
            logger.error("Local orchestration failed for report %s: %s", report.id, e)
            if cloudant_service.enabled:
                try:
                    cloudant_service.store_audit_event(
                        event_type="report_orchestration_review",
                        entity_id=str(report.id),
                        entity_type="report",
                        action="orchestration_failed",
                        details={
                            "reason": "local_orchestration_failed",
                            "processing_status": processing_status,
                        },
                    )
                except Exception as audit_error:
                    logger.error(f"Failed to store orchestration audit event: {audit_error}")

        # Convert SQLAlchemy model to Pydantic response
        report_response = ReportResponse.model_validate(report)

        # Build response
        response = ReportSubmissionResponse(
            report=report_response,
            processing_status=processing_status,
            estimated_verification_time=0
        )

        return response

    except Exception as e:
        logger.error(f"Failed to create report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report. Please try again."
        )


def _build_safe_user_context(current_user: Optional[User]) -> dict:
    if not current_user:
        return {
            "authenticated": False,
            "user_id": None,
            "role": None,
        }

    role = getattr(current_user, "role", None)
    return {
        "authenticated": True,
        "user_id": str(current_user.id),
        "role": role.value if hasattr(role, "value") else role,
    }


def _determine_processing_status(trace) -> str:
    context = trace.context or {}
    confidence = context.get("confidence")
    try:
        normalized_confidence = float(confidence)
    except (TypeError, ValueError):
        normalized_confidence = 0.0

    failed_or_partial = trace.status != "SUCCESS" or any(
        step.status == "FAILED" for step in trace.steps
    )
    skipped_critical_step = any(
        step.status == "SKIPPED"
        and step.agent_name in {"verification_agent", "clustering_agent", "priority_agent"}
        for step in trace.steps
    )
    review_required = bool(context.get("admin_review_required"))
    low_confidence = normalized_confidence < settings.AGENT_CONFIDENCE_THRESHOLD

    if failed_or_partial or skipped_critical_step or review_required or low_confidence:
        return "PROCESSED_WITH_REVIEW"

    return "PROCESSED"


@router.get(
    "/me",
    response_model=List[ReportResponse],
    summary="Get my reports",
    description="Retrieve reports created by the current authenticated user"
)
async def get_my_reports(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status_filter: Optional[IncidentStatus] = Query(None, alias="status")
) -> List[ReportResponse]:
    """
    Get all reports created by the current authenticated user.
    """
    try:
        repo = ReportRepository(db)
        reports = repo.get_by_user_id(current_user.id, status=status_filter)
        return [ReportResponse.model_validate(report) for report in reports]
    except Exception as e:
        logger.error(f"Failed to get user reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reports"
        )


@router.get(
    "",
    response_model=list[ReportResponse],
    summary="List reports",
    description="Retrieve reports for dashboard and authority views (requires ADMIN or AUTHORITY role)"
)
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> list[ReportResponse]:
    """
    List reports in newest-first order.

    Access control:
    - ADMIN and AUTHORITY: Can view all reports
    - CITIZEN: Can only view their own reports (use /reports/me endpoint instead)
    """
    from app.schemas.common import UserRole

    # Check role authorization
    if current_user.role not in [UserRole.ADMIN, UserRole.AUTHORITY]:
        logger.warning(
            f"Unauthorized access attempt to list all reports by user {current_user.id} with role {current_user.role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Only ADMIN and AUTHORITY roles can view all reports."
        )

    try:
        repo = ReportRepository(db)
        reports = repo.get_all(skip=skip, limit=limit, status=status_filter)
        return [ReportResponse.model_validate(report) for report in reports]
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reports"
        )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report by ID",
    description="Retrieve a specific report by its UUID (requires authentication)"
)
async def get_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ReportResponse:
    """
    Get a report by its ID.

    Access control:
    - ADMIN and AUTHORITY: Can view any report
    - CITIZEN: Can only view their own reports
    """
    from app.schemas.common import UserRole

    repo = ReportRepository(db)
    report = repo.get_by_id(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found"
        )

    # Check authorization
    if current_user.role not in [UserRole.ADMIN, UserRole.AUTHORITY]:
        # Citizen role - check ownership
        if report.user_id != current_user.id:
            logger.warning(
                f"Unauthorized access attempt to report {report_id} by user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this report"
            )

    return ReportResponse.model_validate(report)

# Made with Bob

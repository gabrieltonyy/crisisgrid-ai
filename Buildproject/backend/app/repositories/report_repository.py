"""Repository for Report database operations."""

from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.report import Report
from app.schemas.reports import CrisisReportCreateRequest
from app.schemas.common import IncidentStatus
from app.utils.ids import generate_report_id
from app.utils.time import utc_now


class ReportRepository:
    """Repository for Report database operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def create(
        self,
        report_data: CrisisReportCreateRequest,
        user_id: Optional[UUID] = None
    ) -> Report:
        """
        Create a new report in the database.
        
        Args:
            report_data: Validated report creation request
            user_id: Optional user ID if authenticated
            
        Returns:
            Created Report model instance
        """
        # Create report instance
        report = Report(
            id=generate_report_id(),
            user_id=user_id if not report_data.is_anonymous else None,
            crisis_type=report_data.crisis_type,
            description=report_data.description,
            latitude=report_data.latitude,
            longitude=report_data.longitude,
            location_text=report_data.location_text,
            image_url=report_data.image_url,
            video_url=report_data.video_url,
            is_anonymous=report_data.is_anonymous,
            status=IncidentStatus.PENDING_VERIFICATION,  # Default status
            confidence_score=Decimal("0.00"),
            severity_score=Decimal("0.00"),
            source="CITIZEN_APP",
            created_at=utc_now(),
            updated_at=utc_now()
        )
        
        # Add to session and commit
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_by_id(self, report_id: UUID) -> Optional[Report]:
        """Get a report by its ID."""
        stmt = select(Report).where(Report.id == report_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Report]:
        """
        Get all reports with optional filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter
            
        Returns:
            List of Report instances
        """
        stmt = select(Report)
        
        if status:
            stmt = stmt.where(Report.status == status)
        
        stmt = stmt.offset(skip).limit(limit).order_by(Report.created_at.desc())
        
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def update_status(
        self,
        report_id: UUID,
        status: IncidentStatus,
        confidence_score: Optional[float] = None,
        severity_score: Optional[float] = None
    ) -> Optional[Report]:
        """
        Update report status and scores.
        
        Args:
            report_id: Report UUID
            status: New status (IncidentStatus enum)
            confidence_score: Optional confidence score (0-100)
            severity_score: Optional severity score (0-100)
            
        Returns:
            Updated Report instance or None if not found
        """
        report = self.get_by_id(report_id)
        
        if not report:
            return None
        
        report.status = status
        report.updated_at = utc_now()
        
        if confidence_score is not None:
            report.confidence_score = Decimal(str(confidence_score))
        
        if severity_score is not None:
            report.severity_score = Decimal(str(severity_score))
        
        self.db.commit()
        self.db.refresh(report)
        
        return report

# Made with Bob

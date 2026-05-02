"""Repository for verification database operations."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.report import Report
from app.models.agent_run import AgentRun
from app.schemas.common import IncidentStatus, AgentName, AgentRunStatus
from app.utils.ids import generate_agent_run_id
from app.utils.time import utc_now


class VerificationRepository:
    """Repository for verification-related database operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def update_report_verification(
        self,
        report_id: UUID,
        confidence_score: float,
        severity_score: float,
        status: IncidentStatus
    ) -> Optional[Report]:
        """
        Update report with verification results.
        
        Args:
            report_id: Report UUID
            confidence_score: Confidence score (0-100)
            severity_score: Severity score (0-100)
            status: New status (VERIFIED or FALSE_REPORT)
            
        Returns:
            Updated Report instance or None if not found
        """
        stmt = select(Report).where(Report.id == report_id)
        result = self.db.execute(stmt)
        report = result.scalar_one_or_none()
        
        if not report:
            return None
        
        # Update report fields
        report.confidence_score = Decimal(str(confidence_score))
        report.severity_score = Decimal(str(severity_score))
        report.status = status
        report.updated_at = utc_now()
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def create_agent_run(
        self,
        report_id: UUID,
        agent_type: AgentName,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        status: AgentRunStatus = AgentRunStatus.PENDING,
        confidence_score: Optional[float] = None,
        decision: Optional[str] = None,
        model_used: Optional[str] = None
    ) -> AgentRun:
        """
        Create an agent run record for audit trail.
        
        Args:
            report_id: Report UUID
            agent_type: Type of agent (AgentName enum)
            input_data: Input data for the agent
            output_data: Output data from the agent
            status: Run status
            confidence_score: Optional confidence score
            decision: Optional decision/recommendation
            model_used: Optional model identifier
            
        Returns:
            Created AgentRun instance
        """
        agent_run = AgentRun(
            run_id=generate_agent_run_id(agent_type.value),
            agent_name=agent_type,
            report_id=report_id,
            status=status,
            input_data=input_data,
            output_data=output_data,
            confidence_score=confidence_score,
            decision=decision,
            model_used=model_used,
            started_at=utc_now(),
            created_at=utc_now(),
            updated_at=utc_now()
        )
        
        self.db.add(agent_run)
        self.db.commit()
        self.db.refresh(agent_run)
        
        return agent_run
    
    def update_agent_run(
        self,
        run_id: str,
        output_data: Dict[str, Any],
        status: AgentRunStatus,
        confidence_score: Optional[float] = None,
        decision: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[AgentRun]:
        """
        Update an agent run with results.
        
        Args:
            run_id: Agent run ID
            output_data: Output data from the agent
            status: Final status
            confidence_score: Optional confidence score
            decision: Optional decision
            error_message: Optional error message if failed
            
        Returns:
            Updated AgentRun instance or None if not found
        """
        stmt = select(AgentRun).where(AgentRun.run_id == run_id)
        result = self.db.execute(stmt)
        agent_run = result.scalar_one_or_none()
        
        if not agent_run:
            return None
        
        # Update fields
        agent_run.output_data = output_data
        agent_run.status = status
        completed_time = utc_now()
        agent_run.completed_at = completed_time
        agent_run.updated_at = completed_time
        
        if confidence_score is not None:
            agent_run.confidence_score = confidence_score
        
        if decision:
            agent_run.decision = decision
        
        if error_message:
            agent_run.error_message = error_message
        
        # Calculate duration - ensure both datetimes are timezone-aware
        if agent_run.started_at:
            # Make started_at timezone-aware if it isn't
            started = agent_run.started_at
            if started.tzinfo is None:
                from datetime import timezone
                started = started.replace(tzinfo=timezone.utc)
            delta = completed_time - started
            agent_run.duration_seconds = delta.total_seconds()
        
        self.db.commit()
        self.db.refresh(agent_run)
        
        return agent_run
    
    def get_pending_verifications(
        self,
        skip: int = 0,
        limit: int = 100,
        crisis_type: Optional[str] = None,
        created_after: Optional[datetime] = None
    ) -> tuple[List[Report], int]:
        """
        Get reports with PENDING_VERIFICATION status.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            crisis_type: Optional filter by crisis type
            created_after: Optional filter by creation date
            
        Returns:
            Tuple of (list of Report instances, total count)
        """
        # Build query
        stmt = select(Report).where(Report.status == IncidentStatus.PENDING_VERIFICATION)
        
        if crisis_type:
            stmt = stmt.where(Report.crisis_type == crisis_type)
        
        if created_after:
            stmt = stmt.where(Report.created_at >= created_after)
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0
        
        # Get paginated results
        stmt = stmt.offset(skip).limit(limit).order_by(Report.created_at.desc())
        result = self.db.execute(stmt)
        reports = list(result.scalars().all())
        
        return reports, total
    
    def get_verification_history(self, report_id: UUID) -> List[AgentRun]:
        """
        Get all agent runs for a report (verification history).
        
        Args:
            report_id: Report UUID
            
        Returns:
            List of AgentRun instances
        """
        stmt = (
            select(AgentRun)
            .where(AgentRun.report_id == report_id)
            .where(AgentRun.agent_name == AgentName.VERIFICATION_AGENT)
            .order_by(AgentRun.started_at.desc())
        )
        
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_report_by_id(self, report_id: UUID) -> Optional[Report]:
        """
        Get a report by its ID.
        
        Args:
            report_id: Report UUID
            
        Returns:
            Report instance or None if not found
        """
        stmt = select(Report).where(Report.id == report_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """
        Get verification statistics.
        
        Returns:
            Dictionary with verification statistics
        """
        # Count by status
        verified_count = self.db.execute(
            select(func.count()).select_from(Report).where(Report.status == IncidentStatus.VERIFIED)
        ).scalar() or 0
        
        rejected_count = self.db.execute(
            select(func.count()).select_from(Report).where(Report.status == IncidentStatus.FALSE_REPORT)
        ).scalar() or 0
        
        pending_count = self.db.execute(
            select(func.count()).select_from(Report).where(Report.status == IncidentStatus.PENDING_VERIFICATION)
        ).scalar() or 0
        
        # Average confidence score for verified reports
        avg_confidence = self.db.execute(
            select(func.avg(Report.confidence_score))
            .where(Report.status == IncidentStatus.VERIFIED)
        ).scalar() or 0.0
        
        # Average verification time (from agent runs)
        avg_duration = self.db.execute(
            select(func.avg(AgentRun.duration_seconds))
            .where(AgentRun.agent_name == AgentName.VERIFICATION_AGENT)
            .where(AgentRun.status == AgentRunStatus.COMPLETED)
        ).scalar() or 0.0
        
        # Calculate verification rate
        total_processed = verified_count + rejected_count
        verification_rate = (verified_count / total_processed * 100) if total_processed > 0 else 0.0
        
        return {
            "total_verified": verified_count,
            "total_rejected": rejected_count,
            "total_pending": pending_count,
            "average_confidence": float(avg_confidence),
            "average_verification_time": float(avg_duration),
            "verification_rate": verification_rate
        }

# Made with Bob
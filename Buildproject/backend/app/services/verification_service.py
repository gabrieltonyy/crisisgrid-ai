"""
Verification service for orchestrating report verification process.
Coordinates watsonx.ai analysis, database updates, and audit logging.
"""

from typing import Dict, Any, Optional
from uuid import UUID
import logging
from sqlalchemy.orm import Session

from app.services.watsonx_service import watsonx_service
from app.services.cloudant_service import cloudant_service
from app.repositories.verification_repository import VerificationRepository
from app.schemas.common import IncidentStatus, AgentName, AgentRunStatus
from app.schemas.verification import VerificationResult, VerificationResponse
from app.core.config import settings
from app.utils.time import utc_now

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for orchestrating report verification."""
    
    # Verification threshold - reports above this are verified
    VERIFICATION_THRESHOLD = 60.0
    
    def __init__(self, db: Session):
        """
        Initialize verification service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.repo = VerificationRepository(db)
    
    def verify_report(
        self,
        report_id: UUID,
        force_revalidation: bool = False
    ) -> VerificationResponse:
        """
        Verify a crisis report using AI analysis.
        
        This method:
        1. Retrieves the report from database
        2. Checks if already verified (unless force_revalidation)
        3. Calls watsonx.ai for AI analysis
        4. Calculates final scores
        5. Updates report status in database
        6. Creates agent run record
        7. Logs to Cloudant for audit trail
        8. Returns verification result
        
        Args:
            report_id: UUID of the report to verify
            force_revalidation: Force re-verification even if already verified
            
        Returns:
            VerificationResponse with verification results
            
        Raises:
            ValueError: If report not found or invalid state
        """
        # Get report
        report = self.repo.get_report_by_id(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        # Check if already verified
        if not force_revalidation and report.status in [
            IncidentStatus.VERIFIED,
            IncidentStatus.FALSE_REPORT
        ]:
            raise ValueError(
                f"Report {report_id} already verified with status {report.status}. "
                "Use force_revalidation=true to re-verify."
            )
        
        logger.info(f"Starting verification for report {report_id}")
        
        # Prepare input data for AI analysis
        input_data = self._prepare_input_data(report)
        
        # Create agent run record (PENDING)
        agent_run = self.repo.create_agent_run(
            report_id=report_id,
            agent_type=AgentName.VERIFICATION_AGENT,
            input_data=input_data,
            status=AgentRunStatus.PENDING,
            model_used=settings.WATSONX_MODEL_ID if settings.WATSONX_ENABLED else "fallback"
        )
        
        try:
            # Call watsonx.ai for analysis
            ai_analysis = watsonx_service.analyze_report(input_data)
            
            # Parse AI analysis into VerificationResult
            verification_result = VerificationResult(
                credibility_score=ai_analysis["credibility_score"],
                crisis_category=ai_analysis["crisis_category"],
                severity_score=ai_analysis["severity_score"],
                urgency_level=ai_analysis["urgency_level"],
                recommended_action=ai_analysis["recommended_action"],
                reasoning=ai_analysis["reasoning"]
            )
            
            # Calculate final scores (can combine AI + other factors)
            final_confidence = self._calculate_final_confidence(
                ai_credibility=ai_analysis["credibility_score"],
                report=report
            )
            final_severity = ai_analysis["severity_score"]
            
            # Determine if report passes verification threshold
            verified = final_confidence >= self.VERIFICATION_THRESHOLD
            
            # Determine new status
            if verified:
                new_status = IncidentStatus.VERIFIED
                decision = "VERIFIED"
            else:
                new_status = IncidentStatus.FALSE_REPORT
                decision = "REJECTED"
            
            logger.info(
                f"Verification complete for {report_id}: "
                f"confidence={final_confidence:.2f}, decision={decision}"
            )
            
            # Update report in database
            updated_report = self.repo.update_report_verification(
                report_id=report_id,
                confidence_score=final_confidence,
                severity_score=final_severity,
                status=new_status
            )
            
            if not updated_report:
                raise ValueError(f"Failed to update report {report_id}")
            
            # Update agent run with results
            output_data = {
                "verification_result": verification_result.model_dump(),
                "final_confidence_score": final_confidence,
                "final_severity_score": final_severity,
                "decision": decision,
                "status": new_status.value
            }
            
            self.repo.update_agent_run(
                run_id=agent_run.run_id,
                output_data=output_data,
                status=AgentRunStatus.COMPLETED,
                confidence_score=final_confidence,
                decision=decision
            )
            
            # Log to Cloudant for audit trail
            self._log_to_cloudant(
                report_id=report_id,
                agent_run_id=agent_run.run_id,
                verification_result=verification_result,
                final_confidence=final_confidence,
                decision=decision
            )
            
            # Build response
            response = VerificationResponse(
                report_id=report_id,
                status=new_status,
                verification_result=verification_result,
                final_confidence_score=final_confidence,
                final_severity_score=final_severity,
                verified=verified,
                agent_run_id=agent_run.run_id,
                verified_at=utc_now()
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Verification failed for report {report_id}: {e}")
            
            # Update agent run as failed
            self.repo.update_agent_run(
                run_id=agent_run.run_id,
                output_data={"error": str(e)},
                status=AgentRunStatus.FAILED,
                error_message=str(e)
            )
            
            raise
    
    def _prepare_input_data(self, report) -> Dict[str, Any]:
        """
        Prepare input data for AI analysis.
        
        Args:
            report: Report model instance
            
        Returns:
            Dictionary with report data for AI analysis
        """
        return {
            "crisis_type": report.crisis_type.value,
            "description": report.description,
            "latitude": float(report.latitude),
            "longitude": float(report.longitude),
            "location_text": report.location_text,
            "image_url": report.image_url,
            "video_url": report.video_url,
            "is_anonymous": report.is_anonymous,
            "source": report.source
        }
    
    def _calculate_final_confidence(
        self,
        ai_credibility: float,
        report
    ) -> float:
        """
        Calculate final confidence score.
        
        Can combine AI credibility with other factors like:
        - Media presence
        - User reputation (if not anonymous)
        - Similar nearby reports
        - Historical patterns
        
        For now, we use AI credibility as the primary factor.
        
        Args:
            ai_credibility: Credibility score from AI (0-100)
            report: Report model instance
            
        Returns:
            Final confidence score (0-100)
        """
        confidence = ai_credibility
        
        # Boost confidence if media is present
        if report.image_url or report.video_url:
            confidence = min(100, confidence + 5)
        
        # Slight penalty for anonymous reports
        if report.is_anonymous:
            confidence = max(0, confidence - 3)
        
        return confidence
    
    def _log_to_cloudant(
        self,
        report_id: UUID,
        agent_run_id: str,
        verification_result: VerificationResult,
        final_confidence: float,
        decision: str
    ) -> None:
        """
        Log verification event to Cloudant for audit trail.
        
        Args:
            report_id: Report UUID
            agent_run_id: Agent run ID
            verification_result: Verification result
            final_confidence: Final confidence score
            decision: Verification decision
        """
        if not cloudant_service.enabled:
            return
        
        try:
            # Log agent execution
            cloudant_service.store_agent_log(
                agent_run_id=agent_run_id,
                agent_type="verification_agent",
                payload={
                    "report_id": str(report_id),
                    "verification_result": verification_result.model_dump(),
                    "final_confidence_score": final_confidence,
                    "decision": decision
                }
            )
            
            # Log audit event
            cloudant_service.store_audit_event(
                event_type="report_verified",
                entity_id=str(report_id),
                entity_type="report",
                action="verify",
                details={
                    "agent_run_id": agent_run_id,
                    "decision": decision,
                    "confidence_score": final_confidence,
                    "urgency_level": verification_result.urgency_level
                }
            )
            
        except Exception as e:
            # Don't fail verification if Cloudant logging fails
            logger.error(f"Failed to log to Cloudant: {e}")


def get_verification_service(db: Session) -> VerificationService:
    """
    Factory function to get verification service instance.
    
    Args:
        db: Database session
        
    Returns:
        VerificationService instance
    """
    return VerificationService(db)

# Made with Bob
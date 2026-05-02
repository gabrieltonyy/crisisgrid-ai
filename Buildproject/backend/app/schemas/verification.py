"""
Verification schemas for CrisisGrid AI.
Defines Pydantic models for report verification requests and responses.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from app.schemas.common import CrisisType, IncidentStatus, AgentName, AgentRunStatus


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class VerificationRequest(BaseModel):
    """Request schema for triggering report verification."""
    
    force_revalidation: bool = Field(
        False,
        description="Force re-verification even if already verified"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "force_revalidation": False
            }
        }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class VerificationResult(BaseModel):
    """AI analysis output structure from watsonx.ai."""
    
    credibility_score: float = Field(..., ge=0, le=100, description="Credibility score (0-100)")
    crisis_category: CrisisType = Field(..., description="Validated crisis category")
    severity_score: float = Field(..., ge=0, le=100, description="Severity score (0-100)")
    urgency_level: str = Field(..., description="Urgency level: LOW, MEDIUM, HIGH, CRITICAL")
    recommended_action: str = Field(..., description="Recommended action")
    reasoning: str = Field(..., description="Explanation of the decision")
    
    class Config:
        json_schema_extra = {
            "example": {
                "credibility_score": 78.5,
                "crisis_category": "FIRE",
                "severity_score": 82.0,
                "urgency_level": "HIGH",
                "recommended_action": "Rapid verification and potential dispatch",
                "reasoning": "Report contains detailed description with specific location. High severity due to fire type."
            }
        }


class AgentRunSummary(BaseModel):
    """Summary of an agent run for verification history."""
    
    run_id: str = Field(..., description="Agent run ID")
    agent_name: AgentName = Field(..., description="Agent name")
    status: AgentRunStatus = Field(..., description="Run status")
    confidence_score: Optional[float] = Field(None, description="Confidence score if applicable")
    decision: Optional[str] = Field(None, description="Agent decision")
    started_at: datetime = Field(..., description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    duration_seconds: Optional[float] = Field(None, description="Duration in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "run_id": "run_ver_abc123",
                "agent_name": "verification_agent",
                "status": "COMPLETED",
                "confidence_score": 78.5,
                "decision": "VERIFIED",
                "started_at": "2026-05-01T10:30:00Z",
                "completed_at": "2026-05-01T10:30:02Z",
                "duration_seconds": 2.5
            }
        }


class VerificationResponse(BaseModel):
    """Response after verification is complete."""
    
    report_id: UUID = Field(..., description="Report ID")
    status: IncidentStatus = Field(..., description="Updated report status")
    verification_result: VerificationResult = Field(..., description="AI analysis results")
    final_confidence_score: float = Field(..., ge=0, le=100, description="Final confidence score")
    final_severity_score: float = Field(..., ge=0, le=100, description="Final severity score")
    verified: bool = Field(..., description="Whether report passed verification threshold")
    agent_run_id: str = Field(..., description="Agent run ID for this verification")
    verified_at: datetime = Field(..., description="Verification timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "VERIFIED",
                "verification_result": {
                    "credibility_score": 78.5,
                    "crisis_category": "FIRE",
                    "severity_score": 82.0,
                    "urgency_level": "HIGH",
                    "recommended_action": "Rapid verification and potential dispatch",
                    "reasoning": "Report contains detailed description"
                },
                "final_confidence_score": 78.5,
                "final_severity_score": 82.0,
                "verified": True,
                "agent_run_id": "run_ver_abc123",
                "verified_at": "2026-05-01T10:30:02Z"
            }
        }


class VerificationHistoryItem(BaseModel):
    """Single verification history entry."""
    
    agent_run: AgentRunSummary = Field(..., description="Agent run details")
    verification_result: Optional[VerificationResult] = Field(None, description="Verification result if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_run": {
                    "run_id": "run_ver_abc123",
                    "agent_name": "verification_agent",
                    "status": "COMPLETED",
                    "confidence_score": 78.5
                },
                "verification_result": {
                    "credibility_score": 78.5,
                    "crisis_category": "FIRE",
                    "severity_score": 82.0,
                    "urgency_level": "HIGH"
                }
            }
        }


class VerificationHistoryResponse(BaseModel):
    """Response containing verification history for a report."""
    
    report_id: UUID = Field(..., description="Report ID")
    current_status: IncidentStatus = Field(..., description="Current report status")
    verification_count: int = Field(..., description="Number of verification attempts")
    history: List[VerificationHistoryItem] = Field(..., description="Verification history")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_status": "VERIFIED",
                "verification_count": 1,
                "history": [
                    {
                        "agent_run": {
                            "run_id": "run_ver_abc123",
                            "agent_name": "verification_agent",
                            "status": "COMPLETED"
                        }
                    }
                ]
            }
        }


class PendingVerificationItem(BaseModel):
    """Single pending verification item."""
    
    id: UUID = Field(..., description="Report ID")
    crisis_type: CrisisType = Field(..., description="Crisis type")
    description: str = Field(..., description="Report description")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    location_text: Optional[str] = Field(None, description="Location text")
    status: IncidentStatus = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Creation timestamp")
    has_media: bool = Field(..., description="Whether report has image or video")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "crisis_type": "FIRE",
                "description": "Large fire visible with smoke",
                "latitude": -1.2921,
                "longitude": 36.8219,
                "location_text": "Nairobi CBD",
                "status": "PENDING_VERIFICATION",
                "created_at": "2026-05-01T10:30:00Z",
                "has_media": True
            }
        }


class PendingVerificationResponse(BaseModel):
    """Response containing list of reports pending verification."""
    
    total: int = Field(..., description="Total number of pending reports")
    items: List[PendingVerificationItem] = Field(..., description="Pending reports")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 15,
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "crisis_type": "FIRE",
                        "description": "Large fire visible",
                        "status": "PENDING_VERIFICATION"
                    }
                ],
                "page": 1,
                "page_size": 20
            }
        }


class VerificationStatsResponse(BaseModel):
    """Statistics about verification operations."""
    
    total_verified: int = Field(..., description="Total verified reports")
    total_rejected: int = Field(..., description="Total rejected reports")
    total_pending: int = Field(..., description="Total pending verification")
    average_confidence: float = Field(..., description="Average confidence score")
    average_verification_time: float = Field(..., description="Average verification time in seconds")
    verification_rate: float = Field(..., description="Percentage of reports verified")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_verified": 120,
                "total_rejected": 15,
                "total_pending": 8,
                "average_confidence": 76.5,
                "average_verification_time": 2.3,
                "verification_rate": 88.9
            }
        }

# Made with Bob
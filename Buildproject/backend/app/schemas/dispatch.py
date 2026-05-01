"""
Dispatch schemas for CrisisGrid AI.
Defines Pydantic models for authority dispatch and notifications.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.common import (
    CrisisType,
    AuthorityType,
    DispatchStatus
)


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class DispatchLogResponse(BaseModel):
    """Response schema for a dispatch log."""
    
    id: str = Field(..., description="Unique dispatch log identifier")
    incident_id: str = Field(..., description="Associated incident ID")
    authority_type: AuthorityType = Field(..., description="Type of authority")
    crisis_type: CrisisType = Field(..., description="Crisis type")
    message: Optional[str] = Field(None, description="Dispatch message")
    priority: str = Field(..., description="Priority level: LOW, MEDIUM, HIGH, CRITICAL")
    status: DispatchStatus = Field(..., description="Dispatch status")
    latitude: float = Field(..., description="Incident latitude")
    longitude: float = Field(..., description="Incident longitude")
    location_text: Optional[str] = Field(None, description="Location text")
    contact_method: str = Field(default="SIMULATED", description="Contact method used")
    response_time_seconds: Optional[int] = Field(None, description="Response time if acknowledged")
    created_at: datetime = Field(..., description="Dispatch timestamp")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgment timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "dispatch_fire_001",
                "incident_id": "incident_fire_001",
                "authority_type": "FIRE_SERVICE",
                "crisis_type": "FIRE",
                "message": "High-confidence fire incident reported near Nairobi CBD. Immediate response required.",
                "priority": "HIGH",
                "status": "SIMULATED_SENT",
                "latitude": -1.2921,
                "longitude": 36.8219,
                "location_text": "Nairobi CBD",
                "contact_method": "SIMULATED",
                "created_at": "2026-05-01T10:35:00Z"
            }
        }


class DispatchDetailResponse(DispatchLogResponse):
    """Detailed dispatch response with additional information."""
    
    incident_confidence: float = Field(..., description="Incident confidence score")
    incident_severity: float = Field(..., description="Incident severity score")
    report_count: int = Field(..., description="Number of reports in incident")
    estimated_response_time_minutes: Optional[int] = Field(None, description="Estimated response time")
    
    class Config:
        from_attributes = True


class DispatchStatistics(BaseModel):
    """Statistics about dispatches."""
    
    total_dispatches: int = Field(..., description="Total number of dispatches")
    by_authority_type: dict = Field(..., description="Count by authority type")
    by_status: dict = Field(..., description="Count by status")
    by_priority: dict = Field(..., description="Count by priority")
    average_response_time_seconds: Optional[float] = Field(None, description="Average response time")
    simulated_count: int = Field(..., description="Number of simulated dispatches")
    real_count: int = Field(0, description="Number of real dispatches")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_dispatches": 85,
                "by_authority_type": {
                    "FIRE_SERVICE": 30,
                    "DISASTER_MANAGEMENT": 35,
                    "WILDLIFE_AUTHORITY": 15,
                    "POLICE": 5
                },
                "by_status": {
                    "SIMULATED_SENT": 80,
                    "SENT": 5
                },
                "by_priority": {
                    "CRITICAL": 15,
                    "HIGH": 40,
                    "MEDIUM": 25,
                    "LOW": 5
                },
                "average_response_time_seconds": 180,
                "simulated_count": 80,
                "real_count": 5
            }
        }


class DispatchListResponse(BaseModel):
    """List of dispatch logs."""
    
    dispatches: list = Field(..., description="List of dispatch logs")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dispatches": [],
                "total": 85,
                "page": 1,
                "page_size": 20
            }
        }

# Made with Bob

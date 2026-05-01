"""
Incident schemas for CrisisGrid AI.
Defines Pydantic models for clustered crisis incidents.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from app.schemas.common import (
    CrisisType,
    IncidentStatus,
)


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class IncidentResponse(BaseModel):
    """Response schema for an incident."""
    
    id: str = Field(..., description="Unique incident identifier")
    primary_report_id: Optional[UUID] = Field(None, description="ID of the first report")
    crisis_type: CrisisType = Field(..., description="Type of crisis")
    title: str = Field(..., description="Incident title")
    description: Optional[str] = Field(None, description="Incident description")
    latitude: float = Field(..., description="Incident latitude")
    longitude: float = Field(..., description="Incident longitude")
    location_text: Optional[str] = Field(None, description="Location text")
    status: IncidentStatus = Field(..., description="Current status")
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence score")
    severity_score: float = Field(..., ge=0, le=100, description="Severity score")
    risk_radius_meters: int = Field(..., description="Risk radius in meters")
    report_count: int = Field(..., description="Number of associated reports")
    confirmation_count: int = Field(0, description="Number of confirmations")
    dispute_count: int = Field(0, description="Number of disputes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "incident_fire_001",
                "primary_report_id": "550e8400-e29b-41d4-a716-446655440000",
                "crisis_type": "FIRE",
                "title": "Fire Incident - Nairobi CBD",
                "latitude": -1.2921,
                "longitude": 36.8219,
                "location_text": "Nairobi CBD",
                "status": "VERIFIED",
                "confidence_score": 85.0,
                "severity_score": 90.0,
                "risk_radius_meters": 500,
                "report_count": 3,
                "confirmation_count": 5,
                "dispute_count": 0,
                "created_at": "2026-05-01T10:30:00Z"
            }
        }


class IncidentDetailResponse(IncidentResponse):
    """Detailed incident response with scoring breakdown."""
    
    external_signal_score: float = Field(0.0, ge=0, le=100, description="External signal score")
    cross_report_score: float = Field(0.0, ge=0, le=100, description="Cross-report score")
    reporter_trust_score: float = Field(0.0, ge=0, le=100, description="Reporter trust score")
    media_evidence_score: float = Field(0.0, ge=0, le=100, description="Media evidence score")
    geo_time_consistency_score: float = Field(0.0, ge=0, le=100, description="Geo-time consistency score")
    
    class Config:
        from_attributes = True


class IncidentWithReports(IncidentDetailResponse):
    """Incident with associated reports."""
    
    reports: List[dict] = Field(default_factory=list, description="Associated reports")
    alerts: List[dict] = Field(default_factory=list, description="Generated alerts")
    dispatch_logs: List[dict] = Field(default_factory=list, description="Dispatch logs")
    
    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    """List of incidents with pagination."""
    
    incidents: List[IncidentResponse] = Field(..., description="List of incidents")
    total: int = Field(..., description="Total number of incidents")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "incidents": [],
                "total": 50,
                "page": 1,
                "page_size": 20
            }
        }


class IncidentFilterRequest(BaseModel):
    """Request schema for filtering incidents."""
    
    crisis_type: Optional[CrisisType] = Field(None, description="Filter by crisis type")
    status: Optional[IncidentStatus] = Field(None, description="Filter by status")
    min_confidence: Optional[float] = Field(None, ge=0, le=100, description="Minimum confidence")
    min_severity: Optional[float] = Field(None, ge=0, le=100, description="Minimum severity")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Center latitude for radius search")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Center longitude for radius search")
    radius_meters: Optional[int] = Field(None, ge=100, le=50000, description="Search radius")
    from_date: Optional[datetime] = Field(None, description="Filter from date")
    to_date: Optional[datetime] = Field(None, description="Filter to date")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "crisis_type": "FIRE",
                "status": "VERIFIED",
                "min_confidence": 70.0,
                "page": 1,
                "page_size": 20
            }
        }


class IncidentStatistics(BaseModel):
    """Statistics about incidents."""
    
    total_incidents: int = Field(..., description="Total number of incidents")
    active_incidents: int = Field(..., description="Number of active incidents")
    resolved_incidents: int = Field(..., description="Number of resolved incidents")
    by_crisis_type: dict = Field(..., description="Count by crisis type")
    by_status: dict = Field(..., description="Count by status")
    by_severity: dict = Field(..., description="Count by severity level")
    average_confidence: float = Field(..., description="Average confidence score")
    average_response_time_minutes: Optional[float] = Field(None, description="Average response time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_incidents": 75,
                "active_incidents": 15,
                "resolved_incidents": 60,
                "by_crisis_type": {
                    "FIRE": 25,
                    "FLOOD": 30,
                    "WILDLIFE": 15,
                    "ACCIDENT": 5
                },
                "by_status": {
                    "VERIFIED": 40,
                    "DISPATCHED": 20,
                    "RESOLVED": 15
                },
                "by_severity": {
                    "CRITICAL": 10,
                    "HIGH": 25,
                    "MEDIUM": 30,
                    "LOW": 10
                },
                "average_confidence": 0.78,
                "average_response_time_minutes": 12.5
            }
        }

# Made with Bob

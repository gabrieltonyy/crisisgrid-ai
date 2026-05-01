"""
Report schemas for CrisisGrid AI.
Defines Pydantic models for crisis report submission and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from app.schemas.common import (
    CrisisType,
    IncidentStatus,
)


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class CrisisReportCreateRequest(BaseModel):
    """Request schema for creating a new crisis report."""
    
    crisis_type: CrisisType = Field(..., description="Type of crisis being reported")
    description: str = Field(..., min_length=10, max_length=1000, description="Detailed description of the crisis")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    location_text: Optional[str] = Field(None, max_length=255, description="Human-readable location")
    image_url: Optional[str] = Field(None, description="URL to uploaded image")
    video_url: Optional[str] = Field(None, description="URL to uploaded video")
    is_anonymous: bool = Field(False, description="Whether the report is anonymous")
    
    class Config:
        json_schema_extra = {
            "example": {
                "crisis_type": "FIRE",
                "description": "Large fire visible with smoke and flames near residential building",
                "latitude": -1.2921,
                "longitude": 36.8219,
                "location_text": "Nairobi CBD, near Kenyatta Avenue",
                "image_url": "/uploads/fire_123.jpg",
                "is_anonymous": False
            }
        }


class ReportConfirmationRequest(BaseModel):
    """Request schema for confirming or disputing a report."""
    
    confirmation_type: str = Field(..., description="Type of confirmation: CONFIRM, DISPUTE, UPDATE_LOCATION, RESOLVED")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    updated_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Updated latitude if location correction")
    updated_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Updated longitude if location correction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "confirmation_type": "CONFIRM",
                "notes": "I can also see the fire from my location"
            }
        }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ReportResponse(BaseModel):
    """Response schema for a crisis report."""
    
    id: UUID = Field(..., description="Unique report identifier")
    incident_id: Optional[str] = Field(None, description="Associated incident ID if clustered")
    user_id: Optional[UUID] = Field(None, description="Reporter user ID")
    crisis_type: CrisisType = Field(..., description="Type of crisis")
    description: str = Field(..., description="Report description")
    image_url: Optional[str] = Field(None, description="Image URL")
    video_url: Optional[str] = Field(None, description="Video URL")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    location_text: Optional[str] = Field(None, description="Location text")
    status: IncidentStatus = Field(..., description="Current status")
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence score (0-100)")
    severity_score: float = Field(..., ge=0, le=100, description="Severity score (0-100)")
    source: str = Field(default="CITIZEN_APP", description="Report source")
    is_anonymous: bool = Field(..., description="Whether anonymous")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "incident_id": "incident_fire_001",
                "crisis_type": "FIRE",
                "description": "Large fire visible with smoke",
                "latitude": -1.2921,
                "longitude": 36.8219,
                "location_text": "Nairobi CBD",
                "status": "PROVISIONAL_CRITICAL",
                "confidence_score": 72.0,
                "severity_score": 85.0,
                "source": "CITIZEN_APP",
                "is_anonymous": False,
                "created_at": "2026-05-01T10:30:00Z"
            }
        }


class ReportDetailResponse(ReportResponse):
    """Detailed report response with additional information."""
    
    verification_summary: Optional[str] = Field(None, description="Verification agent summary")
    nearby_reports_count: int = Field(0, description="Number of nearby similar reports")
    confirmation_count: int = Field(0, description="Number of confirmations")
    dispute_count: int = Field(0, description="Number of disputes")
    
    class Config:
        from_attributes = True


class ReportSubmissionResponse(BaseModel):
    """Response after submitting a report."""
    
    report: ReportResponse = Field(..., description="Created report")
    processing_status: str = Field(..., description="Processing status")
    estimated_verification_time: int = Field(..., description="Estimated verification time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "crisis_type": "FIRE",
                    "status": "PENDING_VERIFICATION",
                    "confidence_score": 0.0
                },
                "processing_status": "QUEUED_FOR_VERIFICATION",
                "estimated_verification_time": 5
            }
        }


class NearbyReportsRequest(BaseModel):
    """Request schema for finding nearby reports."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Center latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Center longitude")
    radius_meters: int = Field(5000, ge=100, le=50000, description="Search radius in meters")
    crisis_type: Optional[CrisisType] = Field(None, description="Filter by crisis type")
    min_confidence: Optional[float] = Field(None, ge=0, le=1, description="Minimum confidence score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": -1.2921,
                "longitude": 36.8219,
                "radius_meters": 5000,
                "crisis_type": "FIRE",
                "min_confidence": 0.6
            }
        }


class ReportStatistics(BaseModel):
    """Statistics about reports."""
    
    total_reports: int = Field(..., description="Total number of reports")
    by_crisis_type: dict = Field(..., description="Count by crisis type")
    by_status: dict = Field(..., description="Count by status")
    average_confidence: float = Field(..., description="Average confidence score")
    verified_count: int = Field(..., description="Number of verified reports")
    pending_count: int = Field(..., description="Number of pending reports")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_reports": 150,
                "by_crisis_type": {
                    "FIRE": 45,
                    "FLOOD": 60,
                    "WILDLIFE": 25,
                    "ACCIDENT": 20
                },
                "by_status": {
                    "VERIFIED": 80,
                    "PENDING_VERIFICATION": 40,
                    "PROVISIONAL_CRITICAL": 20,
                    "FALSE_REPORT": 10
                },
                "average_confidence": 0.72,
                "verified_count": 80,
                "pending_count": 40
            }
        }

# Made with Bob

"""
Alert schemas for CrisisGrid AI.
Defines Pydantic models for crisis alerts and notifications.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.common import (
    CrisisType,
    SeverityLevel,
    AlertStatus
)


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class AlertResponse(BaseModel):
    """Response schema for an alert."""
    
    id: str = Field(..., description="Unique alert identifier")
    incident_id: str = Field(..., description="Associated incident ID")
    crisis_type: CrisisType = Field(..., description="Type of crisis")
    alert_title: str = Field(..., max_length=180, description="Alert title")
    alert_message: str = Field(..., description="Alert message")
    severity: SeverityLevel = Field(..., description="Alert severity")
    target_radius_meters: float = Field(..., description="Target radius for alert")
    latitude: float = Field(..., description="Alert center latitude")
    longitude: float = Field(..., description="Alert center longitude")
    location_text: Optional[str] = Field(None, description="Location text")
    status: AlertStatus = Field(..., description="Alert status")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "alert_fire_001",
                "incident_id": "incident_fire_001",
                "crisis_type": "FIRE",
                "alert_title": "FIRE ALERT",
                "alert_message": "Fire reported nearby. Avoid the area and follow official instructions.",
                "severity": "HIGH",
                "target_radius_meters": 500,
                "latitude": -1.2921,
                "longitude": 36.8219,
                "location_text": "Nairobi CBD",
                "status": "ACTIVE",
                "created_at": "2026-05-01T10:35:00Z"
            }
        }


class AlertDetailResponse(AlertResponse):
    """Detailed alert response with additional information."""
    
    affected_users_estimate: int = Field(0, description="Estimated number of affected users")
    delivery_status: str = Field("PENDING", description="Delivery status")
    safety_advice: Optional[str] = Field(None, description="Safety advice")
    
    class Config:
        from_attributes = True


class NearbyAlertsRequest(BaseModel):
    """Request schema for finding nearby alerts."""
    
    latitude: float = Field(..., ge=-90, le=90, description="User latitude")
    longitude: float = Field(..., ge=-180, le=180, description="User longitude")
    radius_meters: int = Field(5000, ge=100, le=50000, description="Search radius")
    crisis_type: Optional[CrisisType] = Field(None, description="Filter by crisis type")
    active_only: bool = Field(True, description="Only return active alerts")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": -1.2921,
                "longitude": 36.8219,
                "radius_meters": 5000,
                "active_only": True
            }
        }


class AlertStatistics(BaseModel):
    """Statistics about alerts."""
    
    total_alerts: int = Field(..., description="Total number of alerts")
    active_alerts: int = Field(..., description="Number of active alerts")
    expired_alerts: int = Field(..., description="Number of expired alerts")
    by_crisis_type: dict = Field(..., description="Count by crisis type")
    by_severity: dict = Field(..., description="Count by severity")
    average_response_time_seconds: Optional[float] = Field(None, description="Average time from report to alert")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_alerts": 120,
                "active_alerts": 25,
                "expired_alerts": 95,
                "by_crisis_type": {
                    "FIRE": 40,
                    "FLOOD": 50,
                    "WILDLIFE": 20,
                    "ACCIDENT": 10
                },
                "by_severity": {
                    "CRITICAL": 15,
                    "HIGH": 45,
                    "MEDIUM": 50,
                    "LOW": 10
                },
                "average_response_time_seconds": 45.5
            }
        }

# Made with Bob

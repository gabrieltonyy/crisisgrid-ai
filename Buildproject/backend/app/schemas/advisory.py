"""
Advisory schemas for CrisisGrid AI.
Defines Pydantic models for safety advisory requests and responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.common import CrisisType, SeverityLevel


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class AdvisoryRequest(BaseModel):
    """Request schema for safety advisory."""
    
    incident_id: str = Field(..., description="Incident ID to get advice for")
    user_latitude: Optional[float] = Field(None, ge=-90, le=90, description="User's current latitude")
    user_longitude: Optional[float] = Field(None, ge=-180, le=180, description="User's current longitude")
    user_context: Optional[str] = Field(None, max_length=500, description="Additional user context (e.g., 'at home', 'in car')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "incident_id": "incident_fire_001",
                "user_latitude": -1.2921,
                "user_longitude": 36.8219,
                "user_context": "at home with family"
            }
        }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class SafetyAction(BaseModel):
    """Individual safety action recommendation."""
    
    priority: int = Field(..., ge=1, le=10, description="Action priority (1=highest)")
    action: str = Field(..., description="Action to take")
    rationale: str = Field(..., description="Why this action is important")
    
    class Config:
        json_schema_extra = {
            "example": {
                "priority": 1,
                "action": "Evacuate immediately to a safe location",
                "rationale": "Fire is spreading rapidly and poses immediate danger"
            }
        }


class AdvisoryResponse(BaseModel):
    """Response schema for safety advisory."""
    
    incident_id: str = Field(..., description="Incident ID")
    crisis_type: CrisisType = Field(..., description="Type of crisis")
    severity: SeverityLevel = Field(..., description="Incident severity")
    distance_meters: Optional[float] = Field(None, description="Distance from user to incident")
    risk_level: str = Field(..., description="Risk level: IMMEDIATE, HIGH, MODERATE, LOW")
    
    # Primary advisory
    primary_advice: str = Field(..., description="Main safety advice")
    immediate_actions: List[SafetyAction] = Field(..., description="Immediate actions to take")
    
    # Additional guidance
    what_to_do: List[str] = Field(..., description="What to do")
    what_not_to_do: List[str] = Field(..., description="What NOT to do")
    evacuation_advice: Optional[str] = Field(None, description="Evacuation guidance")
    
    # Resources
    emergency_contacts: List[Dict[str, str]] = Field(..., description="Emergency contact information")
    additional_resources: List[str] = Field(default_factory=list, description="Additional resources")
    
    # Metadata
    generated_at: datetime = Field(..., description="When advice was generated")
    playbook_used: str = Field(..., description="Safety playbook used")
    ai_enhanced: bool = Field(False, description="Whether AI enhanced the advice")
    
    class Config:
        json_schema_extra = {
            "example": {
                "incident_id": "incident_fire_001",
                "crisis_type": "FIRE",
                "severity": "HIGH",
                "distance_meters": 250.5,
                "risk_level": "IMMEDIATE",
                "primary_advice": "Evacuate immediately. Fire is within 500 meters of your location.",
                "immediate_actions": [
                    {
                        "priority": 1,
                        "action": "Leave the building immediately",
                        "rationale": "Fire spreads rapidly and smoke inhalation is deadly"
                    },
                    {
                        "priority": 2,
                        "action": "Stay low to avoid smoke",
                        "rationale": "Smoke rises and cleaner air is near the floor"
                    }
                ],
                "what_to_do": [
                    "Alert others in the building",
                    "Use stairs, not elevators",
                    "Close doors behind you to slow fire spread"
                ],
                "what_not_to_do": [
                    "Do not stop to collect belongings",
                    "Do not use elevators",
                    "Do not re-enter the building"
                ],
                "evacuation_advice": "Move at least 500 meters away from the fire. Head upwind if possible.",
                "emergency_contacts": [
                    {"service": "Fire Service", "number": "999"},
                    {"service": "Emergency Hotline", "number": "112"}
                ],
                "generated_at": "2026-05-02T10:00:00Z",
                "playbook_used": "FIRE_STANDARD",
                "ai_enhanced": True
            }
        }


class AdvisoryStatistics(BaseModel):
    """Statistics about advisory requests."""
    
    total_advisories: int = Field(..., description="Total advisories generated")
    by_crisis_type: Dict[str, int] = Field(..., description="Count by crisis type")
    by_risk_level: Dict[str, int] = Field(..., description="Count by risk level")
    ai_enhanced_count: int = Field(..., description="Number of AI-enhanced advisories")
    average_response_time_ms: Optional[float] = Field(None, description="Average generation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_advisories": 150,
                "by_crisis_type": {
                    "FIRE": 45,
                    "FLOOD": 50,
                    "WILDLIFE": 30,
                    "ACCIDENT": 25
                },
                "by_risk_level": {
                    "IMMEDIATE": 20,
                    "HIGH": 50,
                    "MODERATE": 60,
                    "LOW": 20
                },
                "ai_enhanced_count": 120,
                "average_response_time_ms": 250.5
            }
        }


# Made with Bob
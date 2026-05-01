"""
Agent schemas for CrisisGrid AI.
Defines Pydantic models for agent execution and logging.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from app.schemas.common import AgentName, AgentRunStatus


# ============================================================================
# AGENT INPUT/OUTPUT SCHEMAS
# ============================================================================

class AgentInput(BaseModel):
    """Base schema for agent inputs."""
    
    report_id: UUID = Field(..., description="Report being processed")
    crisis_type: str = Field(..., description="Crisis type")
    description: str = Field(..., description="Report description")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    image_url: Optional[str] = Field(None, description="Image URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentOutput(BaseModel):
    """Base schema for agent outputs."""
    
    agent_name: AgentName = Field(..., description="Name of the agent")
    status: AgentRunStatus = Field(..., description="Execution status")
    output_data: Dict[str, Any] = Field(..., description="Agent output data")
    summary: str = Field(..., description="Human-readable summary")
    duration_ms: int = Field(..., description="Execution duration in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")


# ============================================================================
# VERIFICATION AGENT SCHEMAS
# ============================================================================

class VerificationAgentOutput(BaseModel):
    """Output from verification agent."""
    
    agent_name: str = Field(default="verification_agent", description="Agent name")
    crisis_type: str = Field(..., description="Classified crisis type")
    media_validity_score: float = Field(..., ge=0, le=1, description="Media validity score")
    description_match_score: float = Field(..., ge=0, le=1, description="Description match score")
    initial_confidence_score: float = Field(..., ge=0, le=1, description="Initial confidence")
    verification_summary: str = Field(..., description="Verification summary")
    keywords_found: list = Field(default_factory=list, description="Keywords found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "verification_agent",
                "crisis_type": "FIRE",
                "media_validity_score": 0.80,
                "description_match_score": 0.75,
                "initial_confidence_score": 0.68,
                "verification_summary": "Image and description strongly indicate a fire incident.",
                "keywords_found": ["fire", "smoke", "flames"]
            }
        }


# ============================================================================
# GEORISK AGENT SCHEMAS
# ============================================================================

class GeoRiskAgentOutput(BaseModel):
    """Output from GeoRisk agent."""
    
    agent_name: str = Field(default="georisk_agent", description="Agent name")
    risk_radius_meters: int = Field(..., description="Risk radius")
    matched_incident_id: Optional[UUID] = Field(None, description="Matched incident ID")
    is_clustered: bool = Field(..., description="Whether report was clustered")
    cluster_report_count: int = Field(0, description="Number of reports in cluster")
    nearby_reports: list = Field(default_factory=list, description="Nearby report IDs")
    geospatial_summary: str = Field(..., description="Geospatial analysis summary")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "georisk_agent",
                "risk_radius_meters": 500,
                "matched_incident_id": "660e8400-e29b-41d4-a716-446655440001",
                "is_clustered": True,
                "cluster_report_count": 3,
                "geospatial_summary": "Report is within 300m of an active fire incident."
            }
        }


# ============================================================================
# ALERT AGENT SCHEMAS
# ============================================================================

class AlertAgentOutput(BaseModel):
    """Output from alert agent."""
    
    agent_name: str = Field(default="alert_agent", description="Agent name")
    alert_title: str = Field(..., description="Alert title")
    alert_message: str = Field(..., description="Alert message")
    target_radius_meters: int = Field(..., description="Target radius")
    alert_status: str = Field(..., description="Alert status")
    estimated_affected_users: int = Field(0, description="Estimated affected users")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "alert_agent",
                "alert_title": "FIRE ALERT",
                "alert_message": "Fire reported nearby. Avoid the area.",
                "target_radius_meters": 500,
                "alert_status": "CREATED",
                "estimated_affected_users": 150
            }
        }


# ============================================================================
# DISPATCH AGENT SCHEMAS
# ============================================================================

class DispatchAgentOutput(BaseModel):
    """Output from dispatch agent."""
    
    agent_name: str = Field(default="dispatch_agent", description="Agent name")
    authority_type: str = Field(..., description="Authority type")
    dispatch_status: str = Field(..., description="Dispatch status")
    message: str = Field(..., description="Dispatch message")
    priority: str = Field(..., description="Priority level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "dispatch_agent",
                "authority_type": "FIRE_SERVICE",
                "dispatch_status": "SIMULATED_SENT",
                "message": "High-confidence fire incident reported near Nairobi CBD.",
                "priority": "HIGH"
            }
        }


# ============================================================================
# ADVISORY AGENT SCHEMAS
# ============================================================================

class AdvisoryAgentOutput(BaseModel):
    """Output from advisory agent."""
    
    agent_name: str = Field(default="advisory_agent", description="Agent name")
    safety_steps: list = Field(..., description="Safety steps")
    avoid_actions: list = Field(..., description="Actions to avoid")
    emergency_note: Optional[str] = Field(None, description="Emergency note")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "advisory_agent",
                "safety_steps": [
                    "Move away from the affected area.",
                    "Avoid smoke exposure.",
                    "Follow official emergency instructions."
                ],
                "avoid_actions": [
                    "Do not enter the building.",
                    "Do not block emergency access routes."
                ],
                "emergency_note": "Call 999 if you see flames or need immediate assistance."
            }
        }


# ============================================================================
# AGENT RUN LOG SCHEMAS
# ============================================================================

class AgentRunResponse(BaseModel):
    """Response schema for agent run log."""
    
    id: UUID = Field(..., description="Agent run ID")
    report_id: UUID = Field(..., description="Associated report ID")
    agent_name: AgentName = Field(..., description="Agent name")
    input_summary: str = Field(..., description="Input summary")
    output_summary: str = Field(..., description="Output summary")
    status: AgentRunStatus = Field(..., description="Execution status")
    duration_ms: int = Field(..., description="Duration in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Execution timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440003",
                "report_id": "550e8400-e29b-41d4-a716-446655440000",
                "agent_name": "verification_agent",
                "input_summary": "Fire report with image and GPS",
                "output_summary": "Confidence 0.72, crisis_type FIRE",
                "status": "SUCCESS",
                "duration_ms": 240,
                "created_at": "2026-05-01T10:30:05Z"
            }
        }


class AgentRunListResponse(BaseModel):
    """List of agent runs."""
    
    agent_runs: list = Field(..., description="List of agent runs")
    total: int = Field(..., description="Total count")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_runs": [],
                "total": 50
            }
        }

# Made with Bob

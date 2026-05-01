"""
Common schemas and enums used across CrisisGrid AI.
Defines shared data types, enums, and base response models.
"""

from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# ENUMS
# ============================================================================

class CrisisType(str, Enum):
    """Types of crisis events that can be reported."""
    FIRE = "FIRE"
    FLOOD = "FLOOD"
    WILDLIFE = "WILDLIFE"
    ACCIDENT = "ACCIDENT"
    SECURITY = "SECURITY"
    HEALTH = "HEALTH"
    LANDSLIDE = "LANDSLIDE"
    HAZARDOUS_SPILL = "HAZARDOUS_SPILL"
    OTHER = "OTHER"


class IncidentStatus(str, Enum):
    """Status of an incident through its lifecycle."""
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
    PROVISIONAL_CRITICAL = "PROVISIONAL_CRITICAL"
    VERIFIED = "VERIFIED"
    DISPATCHED = "DISPATCHED"
    RESOLVED = "RESOLVED"
    FALSE_REPORT = "FALSE_REPORT"


class SeverityLevel(str, Enum):
    """Severity levels for incidents."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UserRole(str, Enum):
    """User roles in the system."""
    CITIZEN = "CITIZEN"
    AUTHORITY = "AUTHORITY"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"


class ConfirmationType(str, Enum):
    """Types of confirmations users can provide."""
    CONFIRM = "CONFIRM"
    CONFIRMED = "CONFIRMED"  # Alias for CONFIRM
    DISPUTE = "DISPUTE"
    DISPUTED = "DISPUTED"  # Alias for DISPUTE
    UPDATE_LOCATION = "UPDATE_LOCATION"
    RESOLVED = "RESOLVED"


class DispatchStatus(str, Enum):
    """Status of dispatch notifications."""
    PENDING = "PENDING"
    SIMULATED_SENT = "SIMULATED_SENT"
    SENT = "SENT"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    ARRIVED = "ARRIVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class AlertStatus(str, Enum):
    """Status of alerts."""
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class AuthorityType(str, Enum):
    """Types of authorities that can be dispatched."""
    FIRE_SERVICE = "FIRE_SERVICE"
    FIRE_DEPARTMENT = "FIRE_DEPARTMENT"  # Alias for FIRE_SERVICE
    DISASTER_MANAGEMENT = "DISASTER_MANAGEMENT"
    WILDLIFE_AUTHORITY = "WILDLIFE_AUTHORITY"
    POLICE = "POLICE"
    AMBULANCE = "AMBULANCE"
    PUBLIC_HEALTH = "PUBLIC_HEALTH"


class AgentName(str, Enum):
    """Names of AI agents in the system."""
    VERIFICATION_AGENT = "verification_agent"
    GEORISK_AGENT = "georisk_agent"
    WEATHER_CONTEXT_AGENT = "weather_context_agent"
    WILDLIFE_AGENT = "wildlife_agent"
    ALERT_AGENT = "alert_agent"
    DISPATCH_AGENT = "dispatch_agent"
    ADVISORY_AGENT = "advisory_agent"
    ANALYTICS_AGENT = "analytics_agent"


class AgentRunStatus(str, Enum):
    """Status of agent execution."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    COMPLETED = "COMPLETED"  # Alias for SUCCESS
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# ============================================================================
# BASE MODELS
# ============================================================================

class LocationSchema(BaseModel):
    """Geographic location information."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    location_text: Optional[str] = Field(None, max_length=255, description="Human-readable location")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": -1.2921,
                "longitude": 36.8219,
                "location_text": "Nairobi CBD"
            }
        }


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Any] = Field(None, description="Response data")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {}
            }
        }


class APIError(BaseModel):
    """Standard API error response."""
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    error: Dict[str, Any] = Field(..., description="Error details")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Validation failed",
                "error": {
                    "code": "VALIDATION_ERROR",
                    "details": "Latitude is required"
                }
            }
        }


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: list = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    @classmethod
    def create(cls, items: list, total: int, page: int, page_size: int):
        """Create paginated response."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_authority_for_crisis(crisis_type: CrisisType) -> AuthorityType:
    """
    Map crisis type to appropriate authority type.
    
    Args:
        crisis_type: Type of crisis
        
    Returns:
        Appropriate authority type
    """
    mapping = {
        CrisisType.FIRE: AuthorityType.FIRE_SERVICE,
        CrisisType.FLOOD: AuthorityType.DISASTER_MANAGEMENT,
        CrisisType.WILDLIFE: AuthorityType.WILDLIFE_AUTHORITY,
        CrisisType.ACCIDENT: AuthorityType.POLICE,
        CrisisType.SECURITY: AuthorityType.POLICE,
        CrisisType.HEALTH: AuthorityType.PUBLIC_HEALTH,
        CrisisType.LANDSLIDE: AuthorityType.DISASTER_MANAGEMENT,
        CrisisType.HAZARDOUS_SPILL: AuthorityType.DISASTER_MANAGEMENT,
        CrisisType.OTHER: AuthorityType.DISASTER_MANAGEMENT,
    }
    return mapping.get(crisis_type, AuthorityType.DISASTER_MANAGEMENT)


def get_risk_radius_meters(crisis_type: CrisisType) -> int:
    """
    Get default risk radius for crisis type.
    
    Args:
        crisis_type: Type of crisis
        
    Returns:
        Risk radius in meters
    """
    radius_mapping = {
        CrisisType.FIRE: 500,
        CrisisType.FLOOD: 1000,
        CrisisType.WILDLIFE: 1500,
        CrisisType.ACCIDENT: 300,
        CrisisType.SECURITY: 700,
        CrisisType.HEALTH: 500,
        CrisisType.LANDSLIDE: 800,
        CrisisType.HAZARDOUS_SPILL: 1000,
        CrisisType.OTHER: 500,
    }
    return radius_mapping.get(crisis_type, 500)


def get_severity_from_confidence(confidence_score: float) -> SeverityLevel:
    """
    Determine severity level from confidence score.
    
    Args:
        confidence_score: Confidence score (0.0 to 100.0). Values from
        0.0 to 1.0 are accepted for backwards compatibility.
        
    Returns:
        Severity level
    """
    normalized_score = confidence_score * 100 if confidence_score <= 1 else confidence_score

    if normalized_score >= 85:
        return SeverityLevel.CRITICAL
    elif normalized_score >= 70:
        return SeverityLevel.HIGH
    elif normalized_score >= 50:
        return SeverityLevel.MEDIUM
    else:
        return SeverityLevel.LOW

# Made with Bob

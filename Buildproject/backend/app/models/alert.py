"""
Alert SQLAlchemy Model

Represents public safety alerts generated from verified incidents.
"""

from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel
from app.schemas.common import CrisisType, SeverityLevel, AlertStatus


class Alert(BaseModel):
    """
    Alert model representing public safety notifications.
    
    Generated when incidents reach crisis-specific confidence thresholds.
    """
    __tablename__ = "alerts"

    # Core identification
    alert_id = Column(String(50), primary_key=True, unique=True, nullable=False, index=True)
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=False, index=True)
    
    # Alert details
    crisis_type = Column(SQLEnum(CrisisType), nullable=False, index=True)
    severity = Column(SQLEnum(SeverityLevel), nullable=False, index=True)
    status = Column(SQLEnum(AlertStatus), nullable=False, default=AlertStatus.ACTIVE, index=True)
    
    # Location
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    affected_radius_meters = Column(Float, nullable=False)  # Alert coverage radius
    
    # Alert content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    safety_instructions = Column(JSON, nullable=True)  # List of safety instructions
    
    # Timing
    issued_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Metadata
    affected_population_estimate = Column(Float, nullable=True)  # Estimated people in radius
    priority_level = Column(String(20), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Delivery tracking
    sms_sent_count = Column(Float, nullable=False, default=0)
    push_sent_count = Column(Float, nullable=False, default=0)
    
    # Additional context
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Relationships
    incident = relationship("Incident", back_populates="alerts")

    @property
    def id(self) -> str:
        """Expose alert_id under the generic API response ID name."""
        return self.alert_id

    @property
    def alert_title(self) -> str:
        """Expose title under the public API response field name."""
        return self.title

    @property
    def alert_message(self) -> str:
        """Expose message under the public API response field name."""
        return self.message

    @property
    def target_radius_meters(self) -> float:
        """Expose affected_radius_meters under the public API response field name."""
        return self.affected_radius_meters

    @property
    def location_text(self) -> str:
        """Expose related incident location text when available."""
        return self.incident.location_description if self.incident else None
    
    def is_active(self) -> bool:
        """Check if alert is currently active."""
        if self.status != AlertStatus.ACTIVE:
            return False
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        return True
    
    def cancel(self) -> None:
        """Cancel the alert."""
        self.status = AlertStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
    
    def expire(self) -> None:
        """Mark alert as expired."""
        self.status = AlertStatus.EXPIRED
    
    def __repr__(self) -> str:
        return f"<Alert {self.alert_id} {self.crisis_type.value} {self.severity.value}>"

# Made with Bob

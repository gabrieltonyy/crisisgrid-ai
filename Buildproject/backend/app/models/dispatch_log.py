"""
DispatchLog SQLAlchemy Model

Represents emergency service dispatch records for incidents.
"""

from typing import Optional

from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel
from app.schemas.common import CrisisType, AuthorityType, DispatchStatus


class DispatchLog(BaseModel):
    """
    DispatchLog model representing emergency service dispatch records.
    
    Tracks dispatch of emergency services to verified incidents.
    """
    __tablename__ = "dispatch_logs"

    # Core identification
    dispatch_id = Column(String(50), primary_key=True, unique=True, nullable=False, index=True)
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=False, index=True)
    
    # Dispatch details
    crisis_type = Column(SQLEnum(CrisisType), nullable=False, index=True)
    authority_type = Column(SQLEnum(AuthorityType), nullable=False, index=True)
    status = Column(SQLEnum(DispatchStatus), nullable=False, default=DispatchStatus.PENDING, index=True)
    
    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_description = Column(Text, nullable=True)
    
    # Dispatch information
    priority = Column(String(20), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    units_dispatched = Column(Float, nullable=False, default=1)
    estimated_arrival_minutes = Column(Float, nullable=True)
    
    # Timing
    dispatched_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    arrived_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Communication
    contact_method = Column(String(50), nullable=False, default="SIMULATED")  # SMS, PHONE, RADIO, SIMULATED
    contact_number = Column(String(50), nullable=True)
    message_sent = Column(Text, nullable=True)
    
    # Response details
    response_notes = Column(Text, nullable=True)
    resources_deployed = Column(JSON, nullable=True)  # List of resources
    
    # Metadata
    simulated = Column(Boolean, nullable=False, default=True)  # True for demo/testing
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Relationships
    incident = relationship("Incident", back_populates="dispatch_logs")

    @property
    def id(self) -> str:
        """Expose dispatch_id under the generic API response ID name."""
        return self.dispatch_id

    @property
    def message(self) -> str:
        """Expose message_sent under the public API response field name."""
        return self.message_sent

    @property
    def location_text(self) -> str:
        """Expose location_description under the public API response field name."""
        return self.location_description

    @property
    def response_time_seconds(self) -> Optional[int]:
        """Return response time in seconds when the dispatch has arrived."""
        minutes = self.get_response_time_minutes()
        return int(minutes * 60) if minutes is not None else None
    
    def acknowledge(self) -> None:
        """Mark dispatch as acknowledged by authority."""
        self.status = DispatchStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.utcnow()
    
    def mark_arrived(self) -> None:
        """Mark dispatch units as arrived on scene."""
        self.status = DispatchStatus.ARRIVED
        self.arrived_at = datetime.utcnow()
    
    def complete(self, notes: Optional[str] = None) -> None:
        """Mark dispatch as completed."""
        self.status = DispatchStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if notes:
            self.response_notes = notes
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the dispatch."""
        self.status = DispatchStatus.CANCELLED
        if reason:
            self.response_notes = f"Cancelled: {reason}"
    
    def get_response_time_minutes(self) -> Optional[float]:
        """
        Calculate response time from dispatch to arrival.
        
        Returns:
            float: Response time in minutes, or None if not arrived
        """
        if not self.arrived_at:
            return None
        
        delta = self.arrived_at - self.dispatched_at
        return delta.total_seconds() / 60.0
    
    def __repr__(self) -> str:
        return f"<DispatchLog {self.dispatch_id} {self.authority_type.value} {self.status.value}>"

# Made with Bob

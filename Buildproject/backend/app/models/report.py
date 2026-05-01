"""
Report model for CrisisGrid AI.
Stores individual crisis reports submitted by citizens.
"""

from sqlalchemy import Column, String, Text, Numeric, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import BaseModel
from app.schemas.common import CrisisType, IncidentStatus


class Report(BaseModel):
    """Report model for storing individual crisis reports."""
    
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    crisis_type = Column(
        SQLEnum(CrisisType, name="crisis_type", create_type=False),
        nullable=False
    )
    description = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    location_text = Column(String(255), nullable=True)
    
    status = Column(
        SQLEnum(IncidentStatus, name="incident_status", create_type=False),
        nullable=False,
        default=IncidentStatus.PENDING_VERIFICATION
    )
    confidence_score = Column(Numeric(5, 2), nullable=False, default=0.00)
    severity_score = Column(Numeric(5, 2), nullable=False, default=0.00)
    
    source = Column(String(50), nullable=False, default="CITIZEN_APP")
    is_anonymous = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="reports", foreign_keys=[incident_id])
    user = relationship("User", foreign_keys=[user_id])
    agent_runs = relationship("AgentRun", back_populates="report", cascade="all, delete-orphan")
    confirmations = relationship("Confirmation", back_populates="report")
    
    def __repr__(self):
        return f"<Report {self.id} - {self.crisis_type} at ({self.latitude}, {self.longitude})>"

# Made with Bob

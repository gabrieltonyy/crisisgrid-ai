"""
AgentRun SQLAlchemy Model

Represents execution logs for AI agents processing reports and incidents.
"""

from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel
from app.schemas.common import AgentName, AgentRunStatus


class AgentRun(BaseModel):
    """
    AgentRun model representing AI agent execution logs.
    
    Tracks agent processing for explainability and debugging.
    """
    __tablename__ = "agent_runs"

    # Core identification
    run_id = Column(String(50), primary_key=True, unique=True, nullable=False, index=True)
    agent_name = Column(SQLEnum(AgentName), nullable=False, index=True)
    status = Column(SQLEnum(AgentRunStatus), nullable=False, default=AgentRunStatus.PENDING, index=True)
    
    # Context
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=True, index=True)
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=True, index=True)
    
    # Execution details
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Input/Output
    input_data = Column(JSON, nullable=True)  # Agent input payload
    output_data = Column(JSON, nullable=True)  # Agent output payload
    
    # Results
    confidence_score = Column(Float, nullable=True)  # For verification agent
    risk_level = Column(String(20), nullable=True)  # For georisk agent
    decision = Column(String(100), nullable=True)  # Agent decision/recommendation
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Float, nullable=False, default=0)
    
    # Metadata
    model_used = Column(String(100), nullable=True)  # watsonx.ai model if used
    tokens_used = Column(Float, nullable=True)  # Token count if applicable
    cost_estimate = Column(Float, nullable=True)  # Cost in USD if applicable
    
    # Additional context
    tags = Column(JSON, nullable=True)  # List of tags
    notes = Column(Text, nullable=True)
    
    # Relationships
    report = relationship("Report", back_populates="agent_runs")
    incident = relationship("Incident", backref="agent_runs")

    @property
    def id(self) -> str:
        """Expose run_id under the generic API response ID name."""
        return self.run_id

    @property
    def input_summary(self) -> str:
        """Return a compact representation of the agent input."""
        return str(self.input_data or {})

    @property
    def output_summary(self) -> str:
        """Return a compact representation of the agent output."""
        return str(self.output_data or {})

    @property
    def duration_ms(self) -> int:
        """Expose duration_seconds as integer milliseconds."""
        return int((self.duration_seconds or 0) * 1000)
    
    def complete(self, output_data: dict, confidence_score: float = None) -> None:
        """
        Mark agent run as completed successfully.
        
        Args:
            output_data: Agent output payload
            confidence_score: Optional confidence score
        """
        self.status = AgentRunStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.output_data = output_data
        
        if confidence_score is not None:
            self.confidence_score = confidence_score
        
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = delta.total_seconds()
    
    def fail(self, error_message: str) -> None:
        """
        Mark agent run as failed.
        
        Args:
            error_message: Error description
        """
        self.status = AgentRunStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = delta.total_seconds()
    
    def retry(self) -> None:
        """Increment retry count and reset status."""
        self.retry_count += 1
        self.status = AgentRunStatus.PENDING
        self.error_message = None
    
    def get_execution_summary(self) -> dict:
        """
        Get execution summary for logging/debugging.
        
        Returns:
            dict: Execution summary
        """
        return {
            "run_id": self.run_id,
            "agent_name": self.agent_name.value if self.agent_name else None,
            "status": self.status.value if self.status else None,
            "duration_seconds": self.duration_seconds,
            "confidence_score": self.confidence_score,
            "decision": self.decision,
            "retry_count": self.retry_count,
            "error": self.error_message
        }
    
    def __repr__(self) -> str:
        return f"<AgentRun {self.run_id} {self.agent_name.value if self.agent_name else 'Unknown'} {self.status.value if self.status else 'Unknown'}>"

# Made with Bob

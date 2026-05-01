"""
Incident SQLAlchemy Model

Represents a clustered crisis event aggregated from multiple reports.
Includes confidence scoring breakdown and relationships to reports, alerts, and dispatch logs.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any

from app.models.base import BaseModel
from app.schemas.common import CrisisType, IncidentStatus, SeverityLevel, get_risk_radius_meters


class Incident(BaseModel):
    """
    Incident model representing a clustered crisis event.
    
    Aggregates multiple reports into a single incident with confidence scoring.
    """
    __tablename__ = "incidents"

    # Core identification
    id = Column(String(50), primary_key=True, unique=True, nullable=False, index=True)
    crisis_type = Column(SQLEnum(CrisisType), nullable=False, index=True)
    status = Column(SQLEnum(IncidentStatus), nullable=False, default=IncidentStatus.PENDING_VERIFICATION, index=True)
    severity = Column(SQLEnum(SeverityLevel), nullable=False, default=SeverityLevel.LOW)
    
    # Location
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    location_description = Column(Text, nullable=True)
    
    # Confidence scoring (0-100)
    confidence_score = Column(Float, nullable=False, default=0.0, index=True)
    
    # Confidence breakdown (weighted components)
    media_confidence = Column(Float, nullable=False, default=0.0)  # 25% weight
    cross_report_confidence = Column(Float, nullable=False, default=0.0)  # 25% weight
    external_signal_confidence = Column(Float, nullable=False, default=0.0)  # 20% weight
    reporter_trust_confidence = Column(Float, nullable=False, default=0.0)  # 15% weight
    geo_time_consistency = Column(Float, nullable=False, default=0.0)  # 15% weight
    
    # Metadata
    report_count = Column(Integer, nullable=False, default=1)
    first_reported_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Agent analysis results (JSON)
    verification_result = Column(JSON, nullable=True)
    georisk_result = Column(JSON, nullable=True)
    weather_context = Column(JSON, nullable=True)
    wildlife_context = Column(JSON, nullable=True)
    
    # Alert and dispatch tracking
    alert_generated = Column(String(50), nullable=True)  # Alert ID if generated
    dispatched_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Additional context
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Relationships
    reports = relationship("Report", back_populates="incident", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="incident", cascade="all, delete-orphan")
    dispatch_logs = relationship("DispatchLog", back_populates="incident", cascade="all, delete-orphan")

    @property
    def primary_report_id(self):
        """Return the first related report ID when reports are loaded."""
        return self.reports[0].id if self.reports else None

    @property
    def title(self) -> str:
        """Return a compact display title for API responses."""
        crisis_type = self.crisis_type.value if self.crisis_type else "CRISIS"
        location = self.location_description or f"{self.latitude}, {self.longitude}"
        return f"{crisis_type.title()} Incident - {location}"

    @property
    def location_text(self) -> str:
        """Expose location_description under the response schema's location_text name."""
        return self.location_description

    @property
    def risk_radius_meters(self) -> int:
        """Return the default alert radius for this incident's crisis type."""
        return get_risk_radius_meters(self.crisis_type)

    @property
    def severity_score(self) -> float:
        """Map severity enum to a 0-100 numeric score for API responses."""
        scores = {
            SeverityLevel.LOW: 25.0,
            SeverityLevel.MEDIUM: 50.0,
            SeverityLevel.HIGH: 75.0,
            SeverityLevel.CRITICAL: 100.0,
        }
        return scores.get(self.severity, 0.0)
    
    def update_confidence_score(self) -> float:
        """
        Calculate weighted confidence score from components.
        
        Weights:
        - Media confidence: 25%
        - Cross-report confidence: 25%
        - External signal confidence: 20%
        - Reporter trust confidence: 15%
        - Geo-time consistency: 15%
        
        Returns:
            float: Calculated confidence score (0-100)
        """
        self.confidence_score = (
            (self.media_confidence * 0.25) +
            (self.cross_report_confidence * 0.25) +
            (self.external_signal_confidence * 0.20) +
            (self.reporter_trust_confidence * 0.15) +
            (self.geo_time_consistency * 0.15)
        )
        
        # Update severity based on confidence
        if self.confidence_score >= 80:
            self.severity = SeverityLevel.CRITICAL
        elif self.confidence_score >= 60:
            self.severity = SeverityLevel.HIGH
        elif self.confidence_score >= 40:
            self.severity = SeverityLevel.MEDIUM
        else:
            self.severity = SeverityLevel.LOW
        
        return self.confidence_score
    
    def get_confidence_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed confidence score breakdown.
        
        Returns:
            Dict with component scores and weights
        """
        return {
            "total_confidence": self.confidence_score,
            "components": {
                "media_confidence": {
                    "score": self.media_confidence,
                    "weight": 0.25,
                    "contribution": self.media_confidence * 0.25
                },
                "cross_report_confidence": {
                    "score": self.cross_report_confidence,
                    "weight": 0.25,
                    "contribution": self.cross_report_confidence * 0.25
                },
                "external_signal_confidence": {
                    "score": self.external_signal_confidence,
                    "weight": 0.20,
                    "contribution": self.external_signal_confidence * 0.20
                },
                "reporter_trust_confidence": {
                    "score": self.reporter_trust_confidence,
                    "weight": 0.15,
                    "contribution": self.reporter_trust_confidence * 0.15
                },
                "geo_time_consistency": {
                    "score": self.geo_time_consistency,
                    "weight": 0.15,
                    "contribution": self.geo_time_consistency * 0.15
                }
            }
        }
    
    def should_generate_alert(self) -> bool:
        """
        Determine if incident should trigger an alert based on crisis-specific thresholds.
        
        Thresholds:
        - FIRE: 60% confidence
        - FLOOD: 70% confidence
        - WILDLIFE: 65% confidence
        - Others: 70% confidence
        
        Returns:
            bool: True if alert should be generated
        """
        thresholds = {
            CrisisType.FIRE: 60.0,
            CrisisType.FLOOD: 70.0,
            CrisisType.WILDLIFE: 65.0
        }
        
        threshold = thresholds.get(self.crisis_type, 70.0)
        return self.confidence_score >= threshold
    
    def __repr__(self) -> str:
        return f"<Incident {self.id} {self.crisis_type.value} confidence={self.confidence_score:.1f}%>"

# Made with Bob

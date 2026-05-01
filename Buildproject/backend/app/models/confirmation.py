"""
Confirmation SQLAlchemy Model

Represents confirmations or disputes of crisis reports by other users.
"""

from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel
from app.schemas.common import ConfirmationType


class Confirmation(BaseModel):
    """
    Confirmation model representing user confirmations or disputes of reports.
    
    Enables community-based verification through cross-reporting.
    """
    __tablename__ = "confirmations"

    # Core identification
    confirmation_id = Column(String(50), primary_key=True, unique=True, nullable=False, index=True)
    report_id = Column(String(50), ForeignKey("reports.report_id"), nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    
    # Confirmation details
    confirmation_type = Column(SQLEnum(ConfirmationType), nullable=False, index=True)
    
    # Location (for proximity verification)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    distance_from_report_meters = Column(Float, nullable=True)
    
    # Content
    notes = Column(Text, nullable=True)
    
    # Timing
    confirmed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Trust impact
    trust_weight = Column(Float, nullable=False, default=1.0)  # Based on user's trust score
    
    # Relationships
    report = relationship("Report", back_populates="confirmations")
    user = relationship("User", back_populates="confirmations")
    
    def is_confirmation(self) -> bool:
        """Check if this is a confirmation (not a dispute)."""
        return self.confirmation_type == ConfirmationType.CONFIRMED
    
    def is_dispute(self) -> bool:
        """Check if this is a dispute."""
        return self.confirmation_type == ConfirmationType.DISPUTED
    
    def calculate_distance_from_report(self, report_lat: float, report_lon: float) -> float:
        """
        Calculate distance from report location using Haversine formula.
        
        Args:
            report_lat: Report latitude
            report_lon: Report longitude
            
        Returns:
            float: Distance in meters
        """
        if not self.latitude or not self.longitude:
            return None
        
        from math import radians, sin, cos, sqrt, atan2
        
        # Earth radius in meters
        R = 6371000
        
        lat1 = radians(report_lat)
        lon1 = radians(report_lon)
        lat2 = radians(self.latitude)
        lon2 = radians(self.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance = R * c
        self.distance_from_report_meters = distance
        
        return distance
    
    def __repr__(self) -> str:
        return f"<Confirmation {self.confirmation_id} {self.confirmation_type.value if self.confirmation_type else 'Unknown'}>"

# Made with Bob

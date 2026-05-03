"""
User model for CrisisGrid AI.
Stores user information and trust scores.
"""

from sqlalchemy import Column, String, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import BaseModel
from app.schemas.common import UserRole


class User(BaseModel):
    """User model for storing citizen and authority user information."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=True)
    email = Column(String(180), unique=True, nullable=True)
    phone_number = Column(String(50), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        SQLEnum(UserRole, name="user_role", create_type=False),
        nullable=False,
        default=UserRole.CITIZEN
    )
    trust_score = Column(Numeric(5, 2), nullable=False, default=0.50)
    status = Column(String(30), nullable=False, default="ACTIVE")
    is_active = Column(Boolean, nullable=False, default=True)
    email_verified = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    confirmations = relationship("Confirmation", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.id} - {self.name or 'Anonymous'} ({self.role})>"

# Made with Bob

"""
Base model for SQLAlchemy models.
Provides common fields and utilities for all database models.
"""

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

from app.db.session import Base


class TimestampMixin:
    """Mixin to add timestamp fields to models."""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now())


class BaseModel(Base, TimestampMixin):
    """
    Base model class that includes timestamp fields.
    All models should inherit from this.
    """
    
    __abstract__ = True
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: dict):
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

# Made with Bob

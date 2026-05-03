"""
User schemas for authentication and user management.
Defines Pydantic models for user registration, login, and responses.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

from app.schemas.common import UserRole


class UserCreate(BaseModel):
    """Schema for user registration."""
    name: str = Field(..., min_length=1, max_length=120, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")
    phone_number: Optional[str] = Field(None, max_length=50, description="User's phone number")
    role: UserRole = Field(default=UserRole.CITIZEN, description="User's role in the system")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "SecurePass123!",
                "phone_number": "+254712345678",
                "role": "CITIZEN"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass123!"
            }
        }


class UserResponse(BaseModel):
    """Schema for user data in responses (excludes sensitive information)."""
    id: UUID = Field(..., description="User's unique identifier")
    name: Optional[str] = Field(None, description="User's full name")
    email: Optional[str] = Field(None, description="User's email address")
    phone_number: Optional[str] = Field(None, description="User's phone number")
    role: UserRole = Field(..., description="User's role in the system")
    trust_score: float = Field(..., description="User's trust score (0.0 to 1.0)")
    is_active: bool = Field(..., description="Whether the user account is active")
    email_verified: bool = Field(..., description="Whether the user's email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone_number": "+254712345678",
                "role": "CITIZEN",
                "trust_score": 0.75,
                "is_active": True,
                "email_verified": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z"
            }
        }


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "role": "CITIZEN",
                    "trust_score": 0.75,
                    "is_active": True,
                    "email_verified": True,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-20T14:45:00Z"
                }
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    phone_number: Optional[str] = Field(None, max_length=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Updated Doe",
                "phone_number": "+254712345679"
            }
        }


class PasswordChange(BaseModel):
    """Schema for changing user password."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPass123!",
                "new_password": "NewSecurePass456!"
            }
        }

# Made with Bob
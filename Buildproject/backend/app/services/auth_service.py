"""
Authentication service for CrisisGrid AI.
Handles password hashing, JWT token generation, and token validation.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing token payload data (user_id, email, role)
        expires_delta: Optional custom expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRES_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode the JWT token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Dictionary containing token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Could not validate credentials: {str(e)}")


def create_user_token(user_id: str, email: str, role: str) -> str:
    """
    Create a JWT token for a user with standard claims.
    
    Args:
        user_id: User's unique identifier
        email: User's email address
        role: User's role in the system
        
    Returns:
        Encoded JWT token string
    """
    token_data = {
        "sub": str(user_id),  # Subject (user ID)
        "email": email,
        "role": role,
        "iat": datetime.utcnow()  # Issued at
    }
    
    return create_access_token(token_data)


def verify_token_payload(payload: Dict[str, Any]) -> bool:
    """
    Verify that a token payload contains required fields.
    
    Args:
        payload: Decoded token payload
        
    Returns:
        True if payload is valid, False otherwise
    """
    required_fields = ["sub", "email", "role", "exp"]
    return all(field in payload for field in required_fields)

# Made with Bob
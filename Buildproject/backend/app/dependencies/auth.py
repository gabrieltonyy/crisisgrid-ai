"""
Authentication dependencies for CrisisGrid AI.
Provides FastAPI dependencies for JWT authentication and authorization.
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.session import get_db
from app.models.user import User
from app.schemas.common import UserRole
from app.services.auth_service import decode_access_token


# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate current user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object for the authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = decode_access_token(token)
        user_id: Optional[str] = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    try:
        user = db.query(User).filter(User.id == UUID(user_id)).first()
    except ValueError:
        # Invalid UUID format
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensure the current user is active.
    
    Args:
        current_user: User object from get_current_user
        
    Returns:
        User object if active
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory to check if user has required role.
    
    Args:
        *allowed_roles: One or more UserRole values that are allowed
        
    Returns:
        Dependency function that validates user role
        
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: User = Depends(require_role(UserRole.ADMIN))
        ):
            return {"message": "Admin access granted"}
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """Check if current user has one of the allowed roles."""
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    
    return role_checker


def require_authority():
    """
    Dependency to require AUTHORITY or ADMIN role.
    Convenience wrapper for common authority check.
    
    Returns:
        Dependency function that validates authority access
    """
    return require_role(UserRole.AUTHORITY, UserRole.ADMIN)


def require_admin():
    """
    Dependency to require ADMIN role.
    Convenience wrapper for admin-only endpoints.
    
    Returns:
        Dependency function that validates admin access
    """
    return require_role(UserRole.ADMIN)


async def get_optional_user(
    token: Optional[str] = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Useful for endpoints that work with or without authentication.
    
    Args:
        token: Optional JWT token from Authorization header
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not token:
        return None
    
    try:
        payload = decode_access_token(token)
        user_id: Optional[str] = payload.get("sub")
        
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        return user
        
    except (JWTError, ValueError):
        return None

# Made with Bob

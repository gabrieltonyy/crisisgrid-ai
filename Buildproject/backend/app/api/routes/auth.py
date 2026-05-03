"""
Authentication routes for CrisisGrid AI.
Handles user registration, login, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.user import User
from app.schemas.users import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserUpdate,
)
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_user_token,
)
from app.dependencies.auth import get_current_active_user


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    - **name**: User's full name
    - **email**: User's email address (must be unique)
    - **password**: User's password (minimum 8 characters)
    - **phone_number**: Optional phone number
    - **role**: User role (defaults to CITIZEN)
    
    Returns the created user data (without password).
    User must login separately to receive an access token.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=True,
        email_verified=False,
        trust_score=0.50,  # Default trust score
        status="ACTIVE"
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed. Email may already be in use."
        )
    
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns an access token and user information.
    Include the token in subsequent requests as: `Authorization: Bearer <token>`
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_user_token(
        user_id=str(user.id),
        email=user.email,
        role=user.role.value
    )
    
    # Return token and user data
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.
    
    Requires authentication via JWT token in Authorization header.
    Returns the user's profile data.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    
    - **name**: Updated full name (optional)
    - **phone_number**: Updated phone number (optional)
    
    Requires authentication. Returns updated user data.
    """
    # Update fields if provided
    if user_update.name is not None:
        current_user.name = user_update.name
    
    if user_update.phone_number is not None:
        current_user.phone_number = user_update.phone_number
    
    try:
        db.commit()
        db.refresh(current_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user profile"
        )
    
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout endpoint.
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token from storage. This endpoint is provided for
    consistency and can be extended for token blacklisting if needed.
    
    Requires authentication.
    """
    return {
        "success": True,
        "message": "Successfully logged out. Please remove the token from client storage."
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Refresh the access token for the current user.
    
    Requires a valid (non-expired) token. Returns a new token
    with extended expiration time.
    """
    # Create new access token
    access_token = create_user_token(
        user_id=str(current_user.id),
        email=current_user.email,
        role=current_user.role.value
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(current_user)
    )

# Made with Bob
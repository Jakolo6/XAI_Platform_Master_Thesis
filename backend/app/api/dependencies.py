"""
API dependencies for authentication and authorization.
NOTE: Using Supabase Auth, not custom SQLAlchemy auth.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog
from typing import Optional

# from app.core.database import get_db  # Not used - Supabase only
from app.core.security import decode_token
from app.core.config import settings
from app.models.user import User, UserRole

logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)  # Don't auto-error, we'll handle it


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token.
    In development mode without PostgreSQL, returns a mock user.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Development bypass: If no credentials and in development, return mock user
    if not credentials and settings.ENVIRONMENT == "development":
        logger.warning("Using development bypass - no authentication required")
        # Return a mock user object
        mock_user = User(
            id="dev-user-123",
            email="dev@example.com",
            full_name="Development User",
            role=UserRole.RESEARCHER,
            is_active=True,
            hashed_password=""
        )
        return mock_user
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # NOTE: Using Supabase Auth - no database lookup needed
    # In development, return mock user
    if settings.ENVIRONMENT == "development":
        logger.info("Development mode - returning mock user", user_id=user_id)
        mock_user = User(
            id=user_id,
            email="dev@example.com",
            full_name="Development User",
            role=UserRole.RESEARCHER,
            is_active=True,
            hashed_password=""
        )
        return mock_user
    
    # In production, trust the JWT token from Supabase
    # Create a user object from the token payload
    mock_user = User(
        id=user_id,
        email=payload.get("email", "user@example.com"),
        full_name=payload.get("name", "User"),
        role=UserRole.RESEARCHER,
        is_active=True,
        hashed_password=""
    )
    return mock_user


async def get_current_researcher(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify current user is a researcher or admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not a researcher or admin
    """
    if current_user.role not in [UserRole.RESEARCHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify current user is an admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

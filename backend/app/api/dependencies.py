"""
API dependencies for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_token
from app.core.config import settings
from app.models.user import User, UserRole

logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)  # Don't auto-error, we'll handle it


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
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
    
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
    except Exception as e:
        # If database query fails (no PostgreSQL), use development bypass
        if settings.ENVIRONMENT == "development":
            logger.warning("Database query failed, using development bypass", error=str(e))
            mock_user = User(
                id="dev-user-123",
                email="dev@example.com",
                full_name="Development User",
                role=UserRole.RESEARCHER,
                is_active=True,
                hashed_password=""
            )
            return mock_user
        raise


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

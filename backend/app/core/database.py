"""
Database configuration and session management.
NOTE: This platform uses Supabase as the primary database.
SQLAlchemy is kept for potential future use but not actively used.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# SQLAlchemy engine - NOT USED (we use Supabase)
# Kept for backwards compatibility only
engine = None
AsyncSessionLocal = None

# Create declarative base (for potential future use)
Base = declarative_base()

logger.info("Database module loaded (using Supabase for all operations)")


async def get_db() -> AsyncSession:
    """
    Dependency for getting async database sessions.
    NOTE: Not used - all database operations go through Supabase DAL.
    
    Yields:
        AsyncSession: Database session
    """
    raise RuntimeError("SQLAlchemy sessions not available. Use Supabase DAL instead.")


async def init_db():
    """
    Initialize database tables.
    NOTE: Not used - Supabase schema is managed via SQL migrations.
    """
    logger.info("✅ Database initialization skipped (using Supabase)")
    logger.info("   All tables managed via Supabase SQL migrations")
    logger.info("   See: backend/migrations/FINAL_supabase_schema.sql")


async def close_db():
    """
    Close database connections.
    NOTE: Not used - Supabase connections managed by supabase-py client.
    """
    logger.info("✅ Database cleanup skipped (using Supabase)")

"""
Database configuration and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Create async engine (optional - we primarily use Supabase)
try:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
        poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
    )
    logger.info("PostgreSQL engine created")
except Exception as e:
    logger.warning("PostgreSQL engine creation failed, using Supabase only", error=str(e))
    engine = None

# Create async session factory (only if engine exists)
if engine:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
else:
    AsyncSessionLocal = None

# Create declarative base
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency for getting async database sessions.
    
    Yields:
        AsyncSession: Database session
    """
    if not AsyncSessionLocal:
        raise RuntimeError("Database not available. Using Supabase instead.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Database session error", exc_info=e)
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    if not engine:
        logger.info("Skipping PostgreSQL initialization (using Supabase)")
        return
    
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            from app.models import dataset, model, explanation, user, study
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
    except Exception as e:
        logger.warning("Database table creation failed", error=str(e))


async def close_db():
    """Close database connections."""
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")
    else:
        logger.info("No database connections to close")

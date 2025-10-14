"""
Health check endpoints.
NOTE: Using Supabase, not SQLAlchemy database checks.
"""

from fastapi import APIRouter
import structlog

from app.utils.supabase_client import supabase_db
from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger()


@router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with service status."""
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check Supabase
    try:
        if supabase_db.is_available():
            # Try a simple query
            supabase_db.client.table('datasets').select('id').limit(1).execute()
            health_status["services"]["supabase"] = {"status": "healthy"}
        else:
            health_status["services"]["supabase"] = {"status": "unavailable"}
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error("Supabase health check failed", exc_info=e)
        health_status["services"]["supabase"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    return health_status


@router.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe."""
    try:
        if supabase_db.is_available():
            supabase_db.client.table('datasets').select('id').limit(1).execute()
            return {"status": "ready"}
        return {"status": "not ready"}
    except Exception:
        return {"status": "not ready"}


@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}

"""
Main API router.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, explanations, study, reports, benchmarks, humanstudy, datasets, models

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(explanations.router, prefix="/explanations", tags=["explanations"])
api_router.include_router(benchmarks.router, prefix="/benchmarks", tags=["benchmarks"])
api_router.include_router(study.router, prefix="/study", tags=["study"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(humanstudy.router, prefix="/humanstudy", tags=["humanstudy"])

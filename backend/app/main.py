"""
FastAPI main application.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1.api import api_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting application", app_name=settings.APP_NAME, version=settings.APP_VERSION)
    logger.info("CORS origins configured", origins=settings.BACKEND_CORS_ORIGINS)
    
    # Try to initialize database, but don't fail if PostgreSQL is not available
    # (We're using Supabase for metadata storage)
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning("Database initialization failed (using Supabase instead)", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.warning("Database close failed", error=str(e))


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="XAI Finance Benchmark Platform - Master's Thesis Project",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# CORS middleware - Parse origins properly
# Check ALLOWED_ORIGINS first (Railway), then BACKEND_CORS_ORIGINS
if settings.ALLOWED_ORIGINS:
    cors_origins = settings.ALLOWED_ORIGINS
    logger.info("Using ALLOWED_ORIGINS from environment")
else:
    cors_origins = settings.BACKEND_CORS_ORIGINS
    logger.info("Using BACKEND_CORS_ORIGINS from config")

if isinstance(cors_origins, str):
    # If it's still a string, split by comma
    cors_origins = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]

logger.info("Setting up CORS middleware", origins=cors_origins, origins_count=len(cors_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Global exception handler to ensure CORS headers on errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure CORS headers are present even on unhandled exceptions."""
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
    
    # Manually add CORS headers
    origin = request.headers.get("origin")
    if origin and origin in cors_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


@app.get("/health")
async def health():
    """Basic health check."""
    return {"status": "healthy"}


@app.get("/docs")
async def docs_redirect():
    """Redirect to API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"{settings.API_V1_PREFIX}/docs")


@app.get("/redoc")
async def redoc_redirect():
    """Redirect to ReDoc documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"{settings.API_V1_PREFIX}/redoc")
# Force redeploy - Sun Oct 12 19:38:44 CEST 2025

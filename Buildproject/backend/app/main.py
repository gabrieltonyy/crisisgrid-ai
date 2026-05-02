"""
CrisisGrid AI - Main FastAPI Application
Multi-agent crisis intelligence platform for the IBM Bob Dev Day Hackathon.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys

from app.core.config import settings
from app.api.routes import health, reports, verification
from app.db.session import check_db_connection

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="CrisisGrid AI API",
    description="Multi-agent crisis intelligence, community reporting, verification, alerting, and emergency coordination platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:8000",  # Backend itself
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    Performs initialization tasks and validates configuration.
    """
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug mode: {settings.APP_DEBUG}")
    
    # Check database connection
    if check_db_connection():
        logger.info("✓ PostgreSQL connection successful")
    else:
        logger.error("✗ PostgreSQL connection failed")
        logger.warning("Application starting with database connection issues")
    
    # Log optional service status
    service_status = settings.validate_required_services()
    
    if service_status["cloudant"]:
        logger.info("✓ IBM Cloudant configured")
    else:
        logger.info("○ IBM Cloudant not configured (optional)")
    
    if service_status["watsonx"]:
        logger.info("✓ IBM watsonx.ai configured")
    else:
        logger.info("○ IBM watsonx.ai not configured (optional)")
    
    if service_status["weather"]:
        logger.info("✓ Weather API configured")
    else:
        logger.info("○ Weather API not configured (optional)")
    
    if service_status["sms"]:
        logger.info("✓ SMS service configured")
    else:
        logger.info("○ SMS service not configured (using simulated dispatch)")
    
    logger.info(f"Agent mode: {settings.AGENT_MODE}")
    logger.info(f"Simulated verification: {settings.ENABLE_SIMULATED_VERIFICATION}")
    logger.info(f"Simulated dispatch: {settings.ENABLE_SIMULATED_DISPATCH}")
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    Performs cleanup tasks.
    """
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "environment": settings.APP_ENV,
        "docs": "/docs",
        "health": "/health",
        "api_health": "/api/v1/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Don't expose internal errors in production
    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "An internal error occurred",
                "error": {
                    "code": "INTERNAL_ERROR"
                }
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "An internal error occurred",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "detail": str(exc)
                }
            }
        )


# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(reports.router, prefix="/api/v1")
app.include_router(verification.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )

# Made with Bob

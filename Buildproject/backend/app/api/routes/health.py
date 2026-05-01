"""
Health check endpoints for CrisisGrid AI backend.
Provides system status and service connectivity information.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging

from app.core.config import Settings, get_settings
from app.db.session import check_db_connection, get_db_info

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=Dict[str, Any])
async def health_check(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns system status and connectivity information for:
    - PostgreSQL database
    - IBM Cloudant (if enabled)
    - IBM watsonx.ai (if enabled)
    
    Returns:
        dict: Health status information
        
    Example Response:
        {
            "status": "ok",
            "app": "CrisisGrid AI",
            "environment": "local",
            "services": {
                "postgres": "connected",
                "cloudant": "configured",
                "watsonx": "configured"
            }
        }
    """
    # Check PostgreSQL connection
    postgres_status = "connected" if check_db_connection() else "disconnected"
    
    # Check Cloudant configuration
    cloudant_status = "not_configured"
    if settings.CLOUDANT_ENABLED:
        if settings.CLOUDANT_URL and settings.CLOUDANT_API_KEY:
            cloudant_status = "configured"
        else:
            cloudant_status = "misconfigured"
    
    # Check watsonx.ai configuration
    watsonx_status = "not_configured"
    if settings.WATSONX_ENABLED:
        if settings.WATSONX_API_KEY and settings.WATSONX_PROJECT_ID:
            watsonx_status = "configured"
        else:
            watsonx_status = "misconfigured"
    
    # Determine overall status
    overall_status = "ok" if postgres_status == "connected" else "degraded"
    
    return {
        "status": overall_status,
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "services": {
            "postgres": postgres_status,
            "cloudant": cloudant_status,
            "watsonx": watsonx_status,
        }
    }


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    """
    Detailed health check endpoint with additional system information.
    
    Returns:
        dict: Detailed health status and configuration
        
    Example Response:
        {
            "status": "ok",
            "app": "CrisisGrid AI",
            "environment": "local",
            "database": {
                "connected": true,
                "database": "crisisgrid",
                "version": "PostgreSQL 14.x"
            },
            "features": {
                "cloudant_enabled": false,
                "watsonx_enabled": true,
                "weather_enabled": false,
                "sms_enabled": false
            },
            "agent_settings": {
                "mode": "local",
                "simulated_verification": true,
                "simulated_dispatch": true
            }
        }
    """
    # Get database info
    db_info = get_db_info()
    
    # Get service validation status
    service_status = settings.validate_required_services()
    
    return {
        "status": "ok" if db_info.get("connected") else "degraded",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": db_info,
        "features": {
            "cloudant_enabled": settings.CLOUDANT_ENABLED,
            "watsonx_enabled": settings.WATSONX_ENABLED,
            "weather_enabled": settings.WEATHER_ENABLED,
            "sms_enabled": settings.SMS_ENABLED,
        },
        "agent_settings": {
            "mode": settings.AGENT_MODE,
            "simulated_verification": settings.ENABLE_SIMULATED_VERIFICATION,
            "simulated_dispatch": settings.ENABLE_SIMULATED_DISPATCH,
            "agent_run_logs": settings.ENABLE_AGENT_RUN_LOGS,
        },
        "service_status": service_status,
    }


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint for basic connectivity check.
    
    Returns:
        dict: Simple pong response
    """
    return {"message": "pong"}

# Made with Bob

"""
Configuration management for CrisisGrid AI backend.
Loads environment variables and provides typed configuration access.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "CrisisGrid AI"
    APP_ENV: str = "local"
    APP_DEBUG: bool = True
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_BASE_URL: str = "http://localhost:8000/api/v1"
    FRONTEND_ORIGINS: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:8000,"
        "http://127.0.0.1:8000,"
        "https://crisisgrid-ai.vercel.app"
    )
    
    # Database - PostgreSQL
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    
    # IBM Cloudant (Optional)
    CLOUDANT_ENABLED: bool = False
    CLOUDANT_URL: Optional[str] = None
    CLOUDANT_API_KEY: Optional[str] = None
    CLOUDANT_DB_REPORTS: str = "crisis_reports_raw"
    CLOUDANT_DB_AGENT_LOGS: str = "agent_payload_logs"
    CLOUDANT_DB_AUDIT_EVENTS: str = "audit_events"
    
    # IBM watsonx.ai (Optional)
    WATSONX_ENABLED: bool = False
    WATSONX_API_KEY: Optional[str] = None
    WATSONX_PROJECT_ID: Optional[str] = None
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    WATSONX_MODEL_ID: str = "ibm/granite-13b-chat-v2"
    
    # IBM Cloud (Optional)
    IBM_CLOUD_API_KEY: Optional[str] = None
    IBM_CLOUD_REGION: str = "us-south"
    IBM_CODE_ENGINE_PROJECT: Optional[str] = None
    
    # Weather API (Optional)
    WEATHER_ENABLED: bool = False
    WEATHER_API_PROVIDER: str = "openweathermap"
    WEATHER_API_KEY: Optional[str] = None
    WEATHER_API_BASE_URL: Optional[str] = None
    
    # Maps
    MAPS_PROVIDER: str = "google"
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    MAPBOX_ACCESS_TOKEN: Optional[str] = None
    
    # SMS / Dispatch (Optional)
    SMS_ENABLED: bool = False
    SMS_PROVIDER: str = "simulated"
    SMS_API_KEY: Optional[str] = None
    SMS_SENDER_ID: str = "CrisisGrid"
    AFRICAS_TALKING_USERNAME: Optional[str] = None
    AFRICAS_TALKING_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Authentication
    AUTH_MODE: str = "demo"
    JWT_SECRET: str = Field(..., description="JWT secret key")
    JWT_EXPIRES_MINUTES: int = 1440
    
    # File Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"
    
    # Agent Settings
    AGENT_MODE: str = "local"
    ENABLE_AGENT_RUN_LOGS: bool = True
    ENABLE_SIMULATED_VERIFICATION: bool = True
    ENABLE_SIMULATED_DISPATCH: bool = True
    ENABLE_DEMO_SEED_DATA: bool = True
    
    # Crisis Thresholds
    FIRE_ALERT_THRESHOLD: float = 0.60
    FIRE_DISPATCH_THRESHOLD: float = 0.65
    FLOOD_ALERT_THRESHOLD: float = 0.70
    FLOOD_DISPATCH_THRESHOLD: float = 0.75
    WILDLIFE_ALERT_THRESHOLD: float = 0.65
    WILDLIFE_DISPATCH_THRESHOLD: float = 0.70
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env that aren't defined in Settings
    
    def validate_required_services(self) -> dict:
        """
        Validate that required services are configured.
        Returns status of optional services.
        """
        status = {
            "postgres": bool(self.DATABASE_URL),
            "cloudant": self.CLOUDANT_ENABLED and bool(self.CLOUDANT_URL) and bool(self.CLOUDANT_API_KEY),
            "watsonx": self.WATSONX_ENABLED and bool(self.WATSONX_API_KEY) and bool(self.WATSONX_PROJECT_ID),
            "weather": self.WEATHER_ENABLED and bool(self.WEATHER_API_KEY),
            "sms": self.SMS_ENABLED and bool(self.SMS_API_KEY),
        }
        return status
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.APP_ENV in ["local", "development", "dev"]
    
    @property
    def is_demo(self) -> bool:
        """Check if running in demo mode."""
        return self.APP_ENV == "demo"

    @property
    def frontend_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins from FRONTEND_ORIGINS."""
        return [
            origin.strip()
            for origin in self.FRONTEND_ORIGINS.split(",")
            if origin.strip()
        ]


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency function to get settings instance.
    Can be used with FastAPI's Depends().
    """
    return settings

# Made with Bob

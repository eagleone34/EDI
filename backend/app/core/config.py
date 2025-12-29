"""
Application configuration settings.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "ReadableEDI"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    
    # CORS - Allow localhost and production domains
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://readableedi.com",
        "https://www.readableedi.com",
        "https://*.vercel.app",
    ]
    
    # Email (Resend)
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "hello@readableedi.com"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/edi_email"
    
    # Redis  
    REDIS_URL: str = "redis://localhost:6379"
    
    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "edi-email-files"
    AWS_SES_FROM_EMAIL: str = "noreply@readableedi.com"
    
    # File Storage
    MAX_FILE_SIZE_MB: int = 10
    TEMP_FILE_DIR: str = "/tmp/edi-files"
    
    # Conversion Settings
    CONVERSION_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

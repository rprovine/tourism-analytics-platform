from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Tourism Analytics Platform"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/tourism_analytics"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # HubSpot
    HUBSPOT_API_KEY: Optional[str] = None
    HUBSPOT_PORTAL_ID: Optional[str] = None
    
    # External APIs
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None
    
    # ML Models
    SENTIMENT_MODEL_PATH: str = "models/sentiment"
    FORECASTING_MODEL_PATH: str = "models/forecasting"
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
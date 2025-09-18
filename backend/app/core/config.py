from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/instadmin"
    TEST_DATABASE_URL: str = "postgresql://username:password@localhost:5432/instadmin_test"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Meta Graph API
    META_APP_ID: str
    META_APP_SECRET: str
    META_REDIRECT_URI: str = "http://localhost:8000/api/v1/instagram/auth/callback"
    META_GRAPH_API_URL: str = "https://graph.facebook.com/v18.0"
    
    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin Credentials
    ADMIN_EMAIL: str = "admin@instadmin.com"
    ADMIN_PASSWORD: str
    
    # Storage
    MEDIA_STORAGE_PATH: str = "/app/media"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "video/mp4", "video/mpeg"]
    # Public base URL for serving media files
    PUBLIC_MEDIA_BASE_URL: str = "http://localhost:8000/media/"
    
    # API Configuration
    RATE_LIMIT_PER_MINUTE: int = 60
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Instagram API Limits
    INSTAGRAM_API_REQUESTS_PER_HOUR: int = 200
    INSTAGRAM_BATCH_SIZE: int = 50
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "/app/logs/instadmin.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Istanza globale delle impostazioni
settings = Settings()

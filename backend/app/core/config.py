"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "Supplier Consumer Platform"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/scp_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]
    
    # Languages
    SUPPORTED_LANGUAGES: List[str] = ["kk", "ru", "en"]  # Kazakh, Russian, English
    DEFAULT_LANGUAGE: str = "en"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


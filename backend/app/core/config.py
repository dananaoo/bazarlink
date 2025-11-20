"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


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
    
    # CORS - accept string or list, will be parsed
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    
    # Languages - accept string or list, will be parsed
    SUPPORTED_LANGUAGES: Union[str, List[str]] = "kk,ru,en"
    DEFAULT_LANGUAGE: str = "en"
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_FILE_TYPES: List[str] = [
        # Images
        "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp",
        # Documents
        "application/pdf", "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        # Audio
        "audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg", "audio/aac", "audio/webm",
        # Video (optional)
        "video/mp4", "video/webm", "video/ogg"
    ]
    
    @field_validator("CORS_ORIGINS", "SUPPORTED_LANGUAGES", mode="after")
    @classmethod
    def parse_comma_separated(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated string into list"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


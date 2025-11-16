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


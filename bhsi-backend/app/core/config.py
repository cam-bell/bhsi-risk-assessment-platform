from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator
import secrets
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "BHSI Risk Assessment"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432",
            path="/bhsi_db",
        )
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # External APIs
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = None
    BING_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # News API Keys
    ELPAIS_API_KEY: Optional[str] = None
    ELMUNDO_API_KEY: Optional[str] = None
    EXPANSION_API_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings() 
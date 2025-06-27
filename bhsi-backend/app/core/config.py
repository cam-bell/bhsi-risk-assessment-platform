from typing import Optional
from pydantic_settings import BaseSettings
import secrets
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "BHSI Risk Assessment"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - SQLite configuration with absolute path
    @property
    def DATABASE_URL(self) -> str:
        # Get absolute path to database file
        backend_dir = Path(__file__).parent.parent  # Go up to bhsi-backend
        db_path = backend_dir / "app" / "db" / "queue.db"
        return f"sqlite:///{db_path}"
    
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
    
    # NewsAPI settings
    NEWS_API_KEY: str = "d191eaacfc0c47118a582d23e35e9c63"  # Your NewsAPI key
    NEWS_API_RATE_LIMIT: int = 100  # Maximum requests per day
    NEWS_API_CACHE_TTL: int = 3600  # Cache time in seconds
    
    # LLM settings
    USE_OLLAMA: bool = True
    OLLAMA_MODEL: str = "llama3:latest"
    OLLAMA_HOST: str = "http://localhost:11434"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from environment


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings() 
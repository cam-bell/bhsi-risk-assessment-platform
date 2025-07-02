from typing import Optional
from pydantic_settings import BaseSettings
import secrets
from functools import lru_cache
from pathlib import Path
import os


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
    
    # Cloud Service URLs
    GEMINI_SERVICE_URL: str = (
        "https://gemini-service-185303190462.europe-west1.run.app"
    )
    EMBEDDER_SERVICE_URL: str = (
        "https://embedder-service-185303190462.europe-west1.run.app"
    )
    VECTOR_SEARCH_SERVICE_URL: str = (
        "https://vector-search-185303190462.europe-west1.run.app"
    )
    BIGQUERY_ANALYTICS_SERVICE_URL: str = (
        "https://bigquery-analytics-185303190462.europe-west1.run.app"
    )
    
    # Demo Configuration
    USE_MOCK_DATA: bool = False  # Set to True for demo mode, False for production
    MOCK_MODE_ENABLED: bool = False  # Enable mock data system for demo
    USE_MOCK_ORCHESTRATOR: bool = (
        os.getenv("USE_MOCK_ORCHESTRATOR", "false").lower() 
        in ("1", "true", "yes")
    )
    
    # BigQuery
    BIGQUERY_PROJECT: str = "solid-topic-443216-b2"
    BIGQUERY_DATASET: str = "risk_monitoring"
    BIGQUERY_RAW_DOCS_TABLE: str = "raw_docs"

    # Database selection logic
    USE_BIGQUERY: bool = (
        os.getenv("USE_BIGQUERY", "0").lower() in ("1", "true", "yes")
    )

    def is_bigquery_enabled(self) -> bool:
        return self.USE_BIGQUERY
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from environment


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings() 
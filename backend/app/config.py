"""
Application Configuration
Loads settings from .env file with sensible defaults.
"""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "Decision Intelligence System"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-this-to-a-random-secret-key"

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./data/intelligence.db"

    # --- Gemini ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"
    gemini_embedding_model: str = "models/text-embedding-004"

    # --- ML ---
    ml_models_dir: str = "./ml/models"
    ml_retrain_schedule: str = "daily"

    # --- Vector Store ---
    vector_store_path: str = "./data/vector_store"

    # --- Rate Limiting ---
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.gemini_api_key) and self.gemini_api_key != "your-gemini-api-key-here"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()

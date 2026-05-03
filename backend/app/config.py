"""
Application configuration using Pydantic settings.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================
    # Application
    # =========================
    APP_NAME: str = "Azure Cost Intelligence Simulator"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # =========================
    # Database
    # =========================
    DATABASE_URL: str

    # =========================
    # Redis
    # =========================
    REDIS_URL: str = "redis://localhost:6379/0"

    # =========================
    # Celery
    # =========================
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # =========================
    # Analytics
    # =========================
    ANOMALY_THRESHOLD: float = 2.5
    FORECAST_DAYS: int = 7

    # =========================
    # CORS
    # =========================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # =========================
    # Pydantic Settings Config
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",")]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
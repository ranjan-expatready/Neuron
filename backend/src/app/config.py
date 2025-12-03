"""
Centralized configuration management for Canada Immigration OS.

This module provides a single source of truth for all application configuration,
following FAANG-level best practices for configuration management.
"""
import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Canada Immigration OS API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    database_echo: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # CORS
    frontend_url: Optional[str] = os.getenv("FRONTEND_URL")
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://localhost:3000",
        "https://localhost:3001",
    ]

    # File Storage
    document_storage_path: str = os.getenv("DOCUMENT_STORAGE_PATH", "./uploads")
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    # OCR
    ocr_enabled: bool = os.getenv("OCR_ENABLED", "true").lower() == "true"
    tesseract_path: Optional[str] = os.getenv("TESSERACT_PATH")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")

    def get_cors_origins(self) -> list[str]:
        """Get CORS origins with environment-specific additions."""
        origins = self.cors_origins.copy()
        if self.frontend_url:
            origins.append(self.frontend_url)
        return origins

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "testing"


# Global settings instance
settings = Settings()

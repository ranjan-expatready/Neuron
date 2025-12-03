"""
Unit tests for configuration management.

Tests the centralized configuration system.
"""
import os
from unittest.mock import patch

from src.app.config import Settings, settings


class TestSettings:
    """Test Settings class."""

    def test_settings_defaults(self):
        """Test that settings have sensible defaults."""
        assert settings.app_name == "Canada Immigration OS API"
        assert settings.app_version == "1.0.0"
        assert isinstance(settings.database_url, str)
        assert isinstance(settings.secret_key, str)

    def test_settings_environment_detection(self):
        """Test environment detection."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            test_settings = Settings()
            assert test_settings.is_production is True
            assert test_settings.is_development is False

    def test_settings_cors_origins(self):
        """Test CORS origins configuration."""
        origins = settings.get_cors_origins()
        assert isinstance(origins, list)
        assert "http://localhost:3000" in origins

    def test_settings_cors_with_frontend_url(self):
        """Test CORS origins with frontend URL."""
        with patch.dict(os.environ, {"FRONTEND_URL": "https://example.com"}):
            test_settings = Settings()
            origins = test_settings.get_cors_origins()
            assert "https://example.com" in origins

    def test_settings_properties(self):
        """Test settings properties."""
        with patch.dict(os.environ, {"ENVIRONMENT": "testing"}):
            test_settings = Settings()
            assert test_settings.is_testing is True
            assert test_settings.is_production is False
            assert test_settings.is_development is False

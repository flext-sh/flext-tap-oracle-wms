"""Unit tests for configuration validation.

Tests FlextTapOracleWmsSettings validation and domain rules.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from tests.typings import t


class TestsFlextTapOracleWmsConfigValidation:
    """Test configuration validation."""

    def test_minimal_valid_config(self) -> None:
        """Test minimal valid configuration."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="test_user",
            password="test_password",
        )
        assert str(settings.base_url).rstrip("/") == "https://wms.example.com"
        assert settings.username == "test_user"
        assert isinstance(settings.password, (str, t.SecretStr))
        assert settings.api_version == "V1"
        assert settings.page_size == 10

    def test_url_accepts_trailing_slash(self) -> None:
        """Test URL with trailing slash is accepted."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com/",
            username="user",
            password="pass",
        )
        assert "wms.example.com" in str(settings.base_url)

    def test_page_size_custom_value(self) -> None:
        """Test custom page size is accepted."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            page_size=500,
        )
        assert settings.page_size == 500

    def test_entity_selection_fields(self) -> None:
        """Test entity include/exclude fields are stored correctly."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            include_entities=["inventory", "locations"],
            exclude_entities=["orders"],
        )
        assert settings.include_entities == ["inventory", "locations"]
        assert settings.exclude_entities == ["orders"]

    def test_date_fields(self) -> None:
        """Test date fields are accepted."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-12-31T23:59:59Z",
        )
        assert settings.start_date == "2024-01-01T00:00:00Z"
        assert settings.end_date == "2024-12-31T23:59:59Z"

    def test_model_serialization(self) -> None:
        """Test configuration model serialization."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )
        data = settings.model_dump()
        assert isinstance(data, dict)
        assert data["username"] == "user"
        assert "base_url" in data

    def test_domain_rules_valid(self) -> None:
        """Test domain-specific validation rules pass for valid settings."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )
        result = settings.validate_domain_rules()
        assert result.success

    def test_business_rules_valid(self) -> None:
        """Test business rules validation passes for valid settings."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )
        result = settings.validate_business_rules()
        assert result.success

    def test_stream_related_config_fields(self) -> None:
        """Test stream-related configuration fields are accessible."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            page_size=50,
            column_mappings={"inventory": {"old_col": "new_col"}},
            ignored_columns=["internal_id"],
        )
        assert settings.page_size == 50
        assert settings.column_mappings == {"inventory": {"old_col": "new_col"}}
        assert settings.ignored_columns == ["internal_id"]

    def test_parallel_extraction_config(self) -> None:
        """Test parallel extraction configuration fields."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            enable_parallel_extraction=True,
            max_parallel_streams=6,
            enable_rate_limiting=True,
        )
        assert settings.enable_parallel_extraction is True
        assert settings.max_parallel_streams == 6
        assert settings.enable_rate_limiting is True

    def test_ssl_config(self) -> None:
        """Test SSL configuration fields."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            verify_ssl=False,
            ssl_cert_path="/path/to/cert.pem",
        )
        assert settings.verify_ssl is False
        assert settings.ssl_cert_path == "/path/to/cert.pem"

    def test_rate_limiting_config(self) -> None:
        """Test rate limiting configuration."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            enable_rate_limiting=True,
            max_requests_per_minute=120,
        )
        assert settings.enable_rate_limiting is True
        assert settings.max_requests_per_minute == 120

    def test_password_is_secret(self) -> None:
        """Test password field stores password value."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="super_secret",
        )
        password_value = (
            settings.password.get_secret_value()
            if isinstance(settings.password, t.SecretStr)
            else settings.password
        )
        assert password_value == "super_secret"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

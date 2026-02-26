"""Unit tests for configuration validation.

Tests FlextTapOracleWmsSettings validation and domain rules.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from pydantic import SecretStr


@pytest.fixture(autouse=True)
def _reset_settings_singleton() -> None:
    """Reset global settings singleton to avoid cross-test pollution."""
    FlextTapOracleWmsSettings.reset_global_instance()


class TestConfigValidation:
    """Test configuration validation."""

    def test_minimal_valid_config(self) -> None:
        """Test minimal valid configuration."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="test_user",
            password="test_password",
        )

        assert str(config.base_url).rstrip("/") == "https://wms.example.com"
        assert config.username == "test_user"
        assert isinstance(config.password, SecretStr)
        assert config.api_version == "v1"
        assert config.page_size == 10

    def test_url_accepts_trailing_slash(self) -> None:
        """Test URL with trailing slash is accepted."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com/",
            username="user",
            password="pass",
        )
        assert "wms.example.com" in str(config.base_url)

    def test_page_size_custom_value(self) -> None:
        """Test custom page size is accepted."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            page_size=500,
        )
        assert config.page_size == 500

    def test_entity_selection_fields(self) -> None:
        """Test entity include/exclude fields are stored correctly."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            include_entities=["inventory", "locations"],
            exclude_entities=["orders"],
        )

        assert config.include_entities == ["inventory", "locations"]
        assert config.exclude_entities == ["orders"]

    def test_date_fields(self) -> None:
        """Test date fields are accepted."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-12-31T23:59:59Z",
        )

        assert config.start_date == "2024-01-01T00:00:00Z"
        assert config.end_date == "2024-12-31T23:59:59Z"

    def test_model_serialization(self) -> None:
        """Test configuration model serialization."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )

        data = config.model_dump()
        assert isinstance(data, dict)
        assert data["username"] == "user"
        assert "base_url" in data

    def test_domain_rules_valid(self) -> None:
        """Test domain-specific validation rules pass for valid config."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )

        result = config.validate_domain_rules()
        assert result.is_success

    def test_business_rules_valid(self) -> None:
        """Test business rules validation passes for valid config."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )

        result = config.validate_business_rules()
        assert result.is_success

    def test_stream_related_config_fields(self) -> None:
        """Test stream-related configuration fields are accessible."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            page_size=50,
            column_mappings={
                "inventory": {"old_col": "new_col"},
            },
            ignored_columns=["internal_id"],
        )

        assert config.page_size == 50
        assert config.column_mappings == {"inventory": {"old_col": "new_col"}}
        assert config.ignored_columns == ["internal_id"]

    def test_parallel_extraction_config(self) -> None:
        """Test parallel extraction configuration fields."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            enable_parallel_extraction=True,
            max_parallel_streams=6,
            enable_rate_limiting=True,
        )

        assert config.enable_parallel_extraction is True
        assert config.max_parallel_streams == 6
        assert config.enable_rate_limiting is True

    def test_ssl_config(self) -> None:
        """Test SSL configuration fields."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            verify_ssl=False,
            ssl_cert_path="/path/to/cert.pem",
        )

        assert config.verify_ssl is False
        assert config.ssl_cert_path == "/path/to/cert.pem"

    def test_rate_limiting_config(self) -> None:
        """Test rate limiting configuration."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            enable_rate_limiting=True,
            max_requests_per_minute=120,
        )

        assert config.enable_rate_limiting is True
        assert config.max_requests_per_minute == 120

    def test_password_is_secret(self) -> None:
        """Test password field is SecretStr type."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="super_secret",
        )

        assert isinstance(config.password, SecretStr)
        assert config.password.get_secret_value() == "super_secret"
        assert "super_secret" not in repr(config.password)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

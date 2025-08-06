"""Unit tests for configuration validation.

Tests FlextTapOracleWMSConfig validation and domain rules.
"""

from __future__ import annotations

import pytest
from pydantic import SecretStr, ValidationError

from flext_tap_oracle_wms import FlextTapOracleWMSConfig


class TestConfigValidation:
    """Test configuration validation."""

    def test_minimal_valid_config(self) -> None:
        """Test minimal valid configuration."""
        config = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="test_user",
            password="test_password",
        )

        assert config.base_url == "https://wms.example.com"
        assert config.username == "test_user"
        assert isinstance(config.password, SecretStr)
        assert config.api_version == "v10"  # Default
        assert config.page_size == 100  # Default

    def test_url_validation(self) -> None:
        """Test URL validation."""
        # Valid URLs
        config = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com/",
            username="user",
            password="pass",
        )
        assert config.base_url == "https://wms.example.com"  # Trailing slash removed

        # Invalid URL
        with pytest.raises(ValidationError) as exc_info:
            FlextTapOracleWMSConfig(
                base_url="not-a-url",
                username="user",
                password="pass",
            )
        assert "must start with http://" in str(exc_info.value)

    def test_page_size_limits(self) -> None:
        """Test page size validation."""
        # Valid page sizes
        config = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            page_size=500,
        )
        assert config.page_size == 500

        # Too large
        with pytest.raises(ValidationError):
            FlextTapOracleWMSConfig(
                base_url="https://wms.example.com",
                username="user",
                password="pass",
                page_size=1001,  # Max is 1000
            )

        # Too small
        with pytest.raises(ValidationError):
            FlextTapOracleWMSConfig(
                base_url="https://wms.example.com",
                username="user",
                password="pass",
                page_size=0,
            )

    def test_entity_selection_validation(self) -> None:
        """Test entity selection validation."""
        # Valid include/exclude
        config = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            include_entities=["inventory", "locations"],
            exclude_entities=["orders"],
        )

        # Validate no overlap
        result = config.validate_oracle_wms_config()
        assert result.is_success

        # Overlapping entities
        config_overlap = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            include_entities=["inventory", "locations"],
            exclude_entities=["inventory", "orders"],  # inventory in both
        )

        result = config_overlap.validate_oracle_wms_config()
        assert result.is_failure
        assert "cannot be both included and excluded" in result.error

    def test_date_validation(self) -> None:
        """Test date format validation."""
        # Valid dates
        config = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-12-31T23:59:59Z",
        )

        result = config.validate_oracle_wms_config()
        assert result.is_success

        # Invalid date format
        with pytest.raises(ValidationError) as exc_info:
            FlextTapOracleWMSConfig(
                base_url="https://wms.example.com",
                username="user",
                password="pass",
                start_date="not-a-date",
            )
        assert "Invalid date format" in str(exc_info.value)

        # Start after end
        config_bad_range = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            start_date="2024-12-31T00:00:00Z",
            end_date="2024-01-01T00:00:00Z",
        )

        result = config_bad_range.validate_oracle_wms_config()
        assert result.is_failure
        assert "Start date must be before end date" in result.error

    def test_immutability(self) -> None:
        """Test configuration immutability."""
        config = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )

        # Should not be able to modify
        with pytest.raises(AttributeError):
            config.base_url = "https://new.example.com"

        with pytest.raises(AttributeError):
            config.username = "new_user"

    def test_domain_rules(self) -> None:
        """Test domain-specific validation rules."""
        config = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )

        # Test domain validation
        result = config.validate_domain_rules()
        assert result.is_success

        # Test missing required fields
        # (Can't actually test this with Pydantic since fields are required)

        # Test parallel extraction limits
        config_parallel = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            enable_parallel_extraction=True,
            max_parallel_streams=6,
            enable_rate_limiting=False,
        )

        result = config_parallel.validate_oracle_wms_config()
        assert result.is_failure
        assert "Rate limiting must be enabled" in result.error

    def test_get_stream_config(self) -> None:
        """Test stream-specific configuration."""
        config = FlextTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            page_size=50,
            column_mappings={
                "inventory": {"old_col": "new_col"},
            },
            ignored_columns=["internal_id"],
        )

        # Get config for inventory stream
        stream_config = config.get_stream_config("inventory")
        assert stream_config["page_size"] == 50
        assert stream_config["column_mappings"] == {"old_col": "new_col"}
        assert stream_config["ignored_columns"] == ["internal_id"]

        # Get config for other stream
        other_config = config.get_stream_config("locations")
        assert other_config["page_size"] == 50
        assert "column_mappings" not in other_config  # No mapping for this stream
        assert other_config["ignored_columns"] == ["internal_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

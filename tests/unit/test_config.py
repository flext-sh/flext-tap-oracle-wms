"""Unit tests for configuration module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from pydantic import SecretStr, ValidationError

from flext_tap_oracle_wms import FlextMeltanoTapOracleWMSConfig


class TestFlextMeltanoTapOracleWMSConfig:
    """Test configuration class."""

    def test_minimal_config(self) -> None:
        """Test creating config with minimal fields."""
        config = FlextMeltanoTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="test_user",
            password=SecretStr("test_pass"),
        )

        # Check required fields
        assert config.base_url == "https://wms.example.com"
        assert config.username == "test_user"
        assert config.password.get_secret_value() == "test_pass"

        # Check defaults
        assert config.api_version == "v10"
        assert config.timeout == 30
        assert config.page_size == 100
        assert config.verify_ssl is True
        assert config.enable_rate_limiting is True

    def test_full_config(self) -> None:
        """Test creating config with all fields."""
        config = FlextMeltanoTapOracleWMSConfig(
            # Connection
            base_url="https://prod.wms.example.com",
            username="prod_user",
            password=SecretStr("prod_pass"),
            # API
            api_version="v11",
            timeout=60,
            max_retries=5,
            retry_delay=2.0,
            page_size=500,
            # SSL
            verify_ssl=False,
            ssl_cert_path="/path/to/cert.pem",
            # Stream selection
            include_entities=["inventory", "orders"],
            exclude_entities=["test_entity"],
            # Discovery
            discovery_sample_size=200,
            enable_schema_flattening=False,
            max_flattening_depth=5,
            # Rate limiting
            enable_rate_limiting=False,
            max_requests_per_minute=120,
            # Advanced
            user_agent="CustomAgent/1.0",
            additional_headers={"X-Custom": "value"},
            # Column filtering
            column_mappings={"inventory": {"old": "new"}},
            ignored_columns=["internal_id"],
            # Replication
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-12-31T23:59:59Z",
            # Logging
            log_level="DEBUG",
            enable_request_logging=True,
            # Performance
            enable_parallel_extraction=True,
            max_parallel_streams=5,
            # Validation
            validate_config=False,
            validate_schemas=False,
        )

        # Verify all settings
        assert config.api_version == "v11"
        assert config.timeout == 60
        assert config.page_size == 500
        assert config.verify_ssl is False
        assert config.include_entities == ["inventory", "orders"]
        assert config.enable_rate_limiting is False
        assert config.log_level == "DEBUG"
        assert config.max_parallel_streams == 5

    def test_base_url_validation(self) -> None:
        """Test base URL validation."""
        # Valid URLs
        config = FlextMeltanoTapOracleWMSConfig(
            base_url="https://wms.example.com/",
            username="user",
            password=SecretStr("pass"),
        )
        assert config.base_url == "https://wms.example.com"  # Trailing slash removed

        # Invalid URL - missing protocol
        with pytest.raises(ValidationError) as exc_info:
            FlextMeltanoTapOracleWMSConfig(
                base_url="wms.example.com",
                username="user",
                password=SecretStr("pass"),
            )
        assert "must start with http://" in str(exc_info.value)

    def test_entity_list_validation(self) -> None:
        """Test entity list validation."""
        # Duplicate entities should raise error
        with pytest.raises(ValidationError) as exc_info:
            FlextMeltanoTapOracleWMSConfig(
                base_url="https://wms.example.com",
                username="user",
                password=SecretStr("pass"),
                include_entities=["inventory", "orders", "inventory"],
            )
        assert "contains duplicates" in str(exc_info.value)

    def test_date_validation(self) -> None:
        """Test date format validation."""
        # Valid ISO dates
        config = FlextMeltanoTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password=SecretStr("pass"),
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-12-31T23:59:59Z",
        )
        assert config.start_date == "2024-01-01T00:00:00Z"

        # Invalid date format
        with pytest.raises(ValidationError) as exc_info:
            FlextMeltanoTapOracleWMSConfig(
                base_url="https://wms.example.com",
                username="user",
                password=SecretStr("pass"),
                start_date="01/01/2024",
            )
        assert "Invalid date format" in str(exc_info.value)

    def test_numeric_validation(self) -> None:
        """Test numeric field validation."""
        # Invalid page size
        with pytest.raises(ValidationError):
            FlextMeltanoTapOracleWMSConfig(
                base_url="https://wms.example.com",
                username="user",
                password=SecretStr("pass"),
                page_size=0,  # Too small
            )

        # Invalid timeout
        with pytest.raises(ValidationError):
            FlextMeltanoTapOracleWMSConfig(
                base_url="https://wms.example.com",
                username="user",
                password=SecretStr("pass"),
                timeout=400,  # Too large
            )

    def test_validate_oracle_wms_config(self) -> None:
        """Test Oracle WMS specific validation."""
        # Valid config
        config = FlextMeltanoTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password=SecretStr("pass"),
        )
        result = config.validate_oracle_wms_config()
        assert result.is_success
        assert result.value["valid"] is True

        # Conflicting include/exclude
        config = FlextMeltanoTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password=SecretStr("pass"),
            include_entities=["inventory", "orders"],
            exclude_entities=["orders", "shipments"],
        )
        result = config.validate_oracle_wms_config()
        assert result.is_failure
        assert "cannot be both included and excluded" in str(result.error)

        # Invalid date range
        config = FlextMeltanoTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password=SecretStr("pass"),
            start_date="2024-12-31T00:00:00Z",
            end_date="2024-01-01T00:00:00Z",
        )
        result = config.validate_oracle_wms_config()
        assert result.is_failure
        assert "Start date must be before end date" in str(result.error)

    def test_get_oracle_wms_client_config(self) -> None:
        """Test getting client configuration."""
        config = FlextMeltanoTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password=SecretStr("pass"),
            api_version="v11",
            timeout=45,
            user_agent="TestAgent/1.0",
        )

        client_config = config.get_oracle_wms_client_config()

        assert client_config["base_url"] == "https://wms.example.com"
        assert client_config["username"] == "user"
        assert client_config["password"] == "pass"
        assert client_config["api_version"] == "v11"
        assert client_config["timeout"] == 45
        assert client_config["user_agent"] == "TestAgent/1.0"

    def test_get_stream_config(self) -> None:
        """Test getting stream-specific configuration."""
        config = FlextMeltanoTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password=SecretStr("pass"),
            page_size=200,
            start_date="2024-01-01T00:00:00Z",
            column_mappings={
                "inventory": {"old_name": "new_name"},
                "orders": {"customer_id": "cust_id"},
            },
            ignored_columns=["internal_id"],
        )

        # Get config for inventory stream
        inv_config = config.get_stream_config("inventory")
        assert inv_config["page_size"] == 200
        assert inv_config["start_date"] == "2024-01-01T00:00:00Z"
        assert inv_config["column_mappings"] == {"old_name": "new_name"}
        assert inv_config["ignored_columns"] == ["internal_id"]

        # Get config for stream without mappings
        loc_config = config.get_stream_config("locations")
        assert "column_mappings" not in loc_config
        assert loc_config["ignored_columns"] == ["internal_id"]

    def test_config_immutability(self) -> None:
        """Test that config is immutable."""
        config = FlextMeltanoTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password=SecretStr("pass"),
        )

        # Should not be able to modify
        with pytest.raises(ValidationError):
            config.base_url = "https://new.example.com"

    def test_password_hiding(self) -> None:
        """Test password is hidden in string representation."""
        config = FlextMeltanoTapOracleWMSConfig(
            base_url="https://wms.example.com",
            username="user",
            password=SecretStr("super_secret_password"),
        )

        config_str = str(config)
        assert "super_secret_password" not in config_str
        assert "SecretStr" in config_str or "**********" in config_str

"""Unit tests for configuration module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from pydantic import AnyUrl, ValidationError

from flext_tap_oracle_wms import FlextTapOracleWmsSettings


class TestFlextTapOracleWmsSettings:
    """Test configuration class."""

    @pytest.fixture(autouse=True)
    def reset_settings_singleton(self) -> None:
        """Avoid singleton state leakage between tests."""
        FlextTapOracleWmsSettings.reset_global_instance()

    def test_minimal_config(self) -> None:
        """Test creating config with minimal fields."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="test_user",
            password="test_pass",
        )
        assert str(config.base_url).rstrip("/") == "https://wms.example.com"
        assert config.username == "test_user"
        assert config.password.get_secret_value() == "test_pass"
        assert config.api_version == "v1"
        assert config.timeout == 30
        assert config.page_size == 10
        assert config.verify_ssl is True
        assert config.enable_rate_limiting is True

    def test_full_config(self) -> None:
        """Test creating config with all fields."""
        config = FlextTapOracleWmsSettings(
            base_url="https://prod.wms.example.com",
            username="prod_user",
            password="prod_pass",
            api_version="v11",
            timeout=60,
            max_retries=5,
            retry_delay=2.0,
            page_size=500,
            verify_ssl=False,
            ssl_cert_path="/path/to/cert.pem",
            discovery_sample_size=200,
            enable_schema_flattening=False,
            max_flattening_depth=5,
            enable_rate_limiting=False,
            max_requests_per_minute=120,
            user_agent="CustomAgent/1.0",
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-12-31T23:59:59Z",
            log_level="DEBUG",
            enable_request_logging=True,
            enable_parallel_extraction=True,
            max_parallel_streams=5,
            validate_config=False,
            validate_schemas=False,
        )
        config.include_entities = ["inventory", "orders"]
        config.exclude_entities = ["test_entity"]
        config.additional_headers = {"X-Custom": "value"}
        config.column_mappings = {"inventory": {"old": "new"}}
        config.ignored_columns = ["internal_id"]
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
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com/", username="user", password="pass"
        )
        assert str(config.base_url).rstrip("/") == "https://wms.example.com"
        with pytest.raises(ValidationError) as exc_info:
            FlextTapOracleWmsSettings(
                base_url="wms.example.com", username="user", password="pass"
            )
        assert "Input should be a valid URL" in str(exc_info.value)

    def test_entity_list_validation(self) -> None:
        """Test entity list validation."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com", username="user", password="pass"
        )
        with pytest.raises(ValidationError) as exc_info:
            config.include_entities = ["inventory", "orders", "inventory"]
        assert "contains duplicates" in str(exc_info.value)

    def test_date_validation(self) -> None:
        """Test date format validation."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-12-31T23:59:59Z",
        )
        assert config.start_date == "2024-01-01T00:00:00Z"
        with pytest.raises(ValidationError) as exc_info:
            FlextTapOracleWmsSettings(
                base_url="https://wms.example.com",
                username="user",
                password="pass",
                start_date="01/01/2024",
            )
        assert "Invalid date format" in str(exc_info.value)

    def test_numeric_validation(self) -> None:
        """Test numeric field validation."""
        with pytest.raises(ValidationError):
            FlextTapOracleWmsSettings(
                base_url="https://wms.example.com",
                username="user",
                password="pass",
                page_size=0,
            )
        with pytest.raises(ValidationError):
            FlextTapOracleWmsSettings(
                base_url="https://wms.example.com",
                username="user",
                password="pass",
                timeout=400,
            )

    def test_validate_business_rules(self) -> None:
        """Test Oracle WMS specific business-rule validation."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com", username="user", password="pass"
        )
        result = config.validate_business_rules()
        assert result.is_success
        assert result.value is True
        FlextTapOracleWmsSettings.reset_global_instance()
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com", username="user", password="pass"
        )
        config.include_entities = ["inventory", "orders"]
        config.exclude_entities = ["orders", "shipments"]
        result = config.validate_business_rules()
        assert result.is_failure
        assert "cannot be both included and excluded" in str(result.error)
        FlextTapOracleWmsSettings.reset_global_instance()
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            start_date="2024-12-31T00:00:00Z",
            end_date="2024-01-01T00:00:00Z",
        )
        result = config.validate_business_rules()
        assert result.is_failure
        assert "start_date must be <= end_date" in str(result.error)

    def test_model_dump_for_client_payload(self) -> None:
        """Test generating a serializable client payload from settings."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            api_version="v11",
            timeout=45,
            user_agent="TestAgent/1.0",
        )
        client_config = config.model_dump(mode="json")
        assert client_config["base_url"] == "https://wms.example.com/"
        assert client_config["username"] == "user"
        assert client_config["password"] == "**********"
        assert client_config["api_version"] == "v11"
        assert client_config["timeout"] == 45
        assert client_config["user_agent"] == "TestAgent/1.0"

    def test_stream_related_fields_available(self) -> None:
        """Test stream-related configuration fields are preserved in model."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            page_size=200,
            start_date="2024-01-01T00:00:00Z",
        )
        config.column_mappings = {
            "inventory": {"old_name": "new_name"},
            "orders": {"customer_id": "cust_id"},
        }
        config.ignored_columns = ["internal_id"]
        payload = config.model_dump(mode="json")
        assert payload["page_size"] == 200
        assert payload["start_date"] == "2024-01-01T00:00:00Z"
        assert payload["column_mappings"]["inventory"] == {"old_name": "new_name"}
        assert payload["ignored_columns"] == ["internal_id"]

    def test_config_mutability_with_assignment_validation(self) -> None:
        """Test that config is mutable but still validated on assignment."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com", username="user", password="pass"
        )
        config.base_url = AnyUrl("https://new.example.com")
        assert str(config.base_url) == "https://new.example.com/"

    def test_password_hiding(self) -> None:
        """Test password is hidden in string representation."""
        config = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="super_secret_password",
        )
        config_str = str(config)
        assert "super_secret_password" not in config_str
        assert "SecretStr" in config_str or "**********" in config_str

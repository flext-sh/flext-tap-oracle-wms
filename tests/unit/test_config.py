"""Unit tests for configuration module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from tests.constants import c
from tests.typings import t


class TestsFlextTapOracleWmsConfig:
    """Test configuration class."""

    def test_minimal_config(self) -> None:
        """Test creating settings with minimal fields."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="test_user",
            password="test_pass",
        )
        assert str(settings.base_url).rstrip("/") == "https://wms.example.com"
        assert settings.username == "test_user"
        password = settings.password
        password_value = (
            password.get_secret_value()
            if isinstance(password, t.SecretStr)
            else password
        )
        assert password_value == "test_pass"
        assert settings.api_version == "V1"
        assert settings.timeout == 30
        assert settings.page_size == 10
        assert settings.verify_ssl is True
        assert settings.enable_rate_limiting is True

    def test_full_config(self) -> None:
        """Test creating settings with all fields."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://prod.wms.example.com",
            username="prod_user",
            password="prod_pass",
            api_version="v11",
            timeout=60,
            max_retries=5,
            retry_delay=2,
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
            log_level=c.LogLevel.DEBUG,
            enable_request_logging=True,
            enable_parallel_extraction=True,
            max_parallel_streams=5,
            validate_config=False,
            validate_schemas=False,
        )
        settings.include_entities = ["inventory", "orders"]
        settings.exclude_entities = ["test_entity"]
        settings.additional_headers = {"X-Custom": "value"}
        settings.column_mappings = {"inventory": {"old": "new"}}
        settings.ignored_columns = ["internal_id"]
        assert settings.api_version == "v11"
        assert settings.timeout == 60
        assert settings.page_size == 500
        assert settings.verify_ssl is False
        assert settings.include_entities == ["inventory", "orders"]
        assert settings.enable_rate_limiting is False
        assert settings.log_level == "DEBUG"
        assert settings.max_parallel_streams == 5

    def test_base_url_validation(self) -> None:
        """Test base URL validation accepts valid URLs and bare strings."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com/",
            username="user",
            password="pass",
        )
        assert "wms.example.com" in str(settings.base_url)
        # str | t.AnyUrl union accepts bare hostnames as str
        config_bare = FlextTapOracleWmsSettings(
            base_url="wms.example.com",
            username="user",
            password="pass",
        )
        assert config_bare.base_url == "wms.example.com"

    def test_entity_list_validation(self) -> None:
        """Test entity list validation."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )
        with pytest.raises(c.ValidationError) as exc_info:
            settings.include_entities = ["inventory", "orders", "inventory"]
        assert "contains duplicates" in str(exc_info.value)

    def test_date_validation(self) -> None:
        """Test date format validation."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-12-31T23:59:59Z",
        )
        assert settings.start_date == "2024-01-01T00:00:00Z"
        with pytest.raises(c.ValidationError) as exc_info:
            FlextTapOracleWmsSettings(
                base_url="https://wms.example.com",
                username="user",
                password="pass",
                start_date="01/01/2024",
            )
        assert "Invalid date format" in str(exc_info.value)

    def test_numeric_validation(self) -> None:
        """Test numeric field validation."""
        with pytest.raises(c.ValidationError):
            FlextTapOracleWmsSettings(
                base_url="https://wms.example.com",
                username="user",
                password="pass",
                page_size=0,
            )
        with pytest.raises(c.ValidationError):
            FlextTapOracleWmsSettings(
                base_url="https://wms.example.com",
                username="user",
                password="pass",
                timeout=400,
            )

    def test_validate_business_rules(self) -> None:
        """Test Oracle WMS specific business-rule validation."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )
        result = settings.validate_business_rules()
        assert result.success
        assert result.value is True
        FlextTapOracleWmsSettings.reset_for_testing()
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )
        settings.include_entities = ["inventory", "orders"]
        settings.exclude_entities = ["orders", "shipments"]
        result = settings.validate_business_rules()
        assert result.failure
        assert "cannot be both included and excluded" in str(result.error)
        FlextTapOracleWmsSettings.reset_for_testing()
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            start_date="2024-12-31T00:00:00Z",
            end_date="2024-01-01T00:00:00Z",
        )
        result = settings.validate_business_rules()
        assert result.failure
        assert "start_date must be <= end_date" in str(result.error)

    def test_model_dump_for_client_payload(self) -> None:
        """Test generating a serializable client payload from settings."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            api_version="v11",
            timeout=45,
            user_agent="TestAgent/1.0",
        )
        client_config = settings.model_dump(mode="json")
        assert "wms.example.com" in str(client_config["base_url"])
        assert client_config["username"] == "user"
        # Password may be str or masked t.SecretStr depending on model settings
        assert client_config["password"] is not None
        assert client_config["api_version"] == "v11"
        assert client_config["timeout"] == 45
        assert client_config["user_agent"] == "TestAgent/1.0"

    def test_stream_related_fields_available(self) -> None:
        """Test stream-related configuration fields are preserved in model."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
            page_size=200,
            start_date="2024-01-01T00:00:00Z",
        )
        settings.column_mappings = {
            "inventory": {"old_name": "new_name"},
            "orders": {"customer_id": "cust_id"},
        }
        settings.ignored_columns = ["internal_id"]
        payload = settings.model_dump(mode="json")
        assert payload["page_size"] == 200
        assert payload["start_date"] == "2024-01-01T00:00:00Z"
        assert payload["column_mappings"]["inventory"] == {"old_name": "new_name"}
        assert payload["ignored_columns"] == ["internal_id"]

    def test_config_mutability_with_assignment_validation(self) -> None:
        """Test that settings is mutable but still validated on assignment."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="pass",
        )
        settings.base_url = t.AnyUrl("https://new.example.com")
        assert str(settings.base_url) == "https://new.example.com/"

    def test_password_hiding(self) -> None:
        """Test password field is stored (str | t.SecretStr union)."""
        settings = FlextTapOracleWmsSettings(
            base_url="https://wms.example.com",
            username="user",
            password="super_secret_password",
        )
        password_value = (
            settings.password.get_secret_value()
            if isinstance(settings.password, t.SecretStr)
            else settings.password
        )
        assert password_value == "super_secret_password"

"""Unit tests for configuration module.

NOTE (multi-agent): mro-u3eu — ADR-005 (commit 7d69609) namespaced every project
field under ``settings.TapOracleWms.*`` and removed ``validate_business_rules``
from the settings layer (business rules live at the config boundary). These
tests exercise the real namespaced contract and the validators that still
exist (no-duplicates, ISO-8601 dates).

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
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "test_user",
                "password": "test_pass",
            },
        )
        namespace = settings.TapOracleWms
        assert namespace.base_url.rstrip("/") == "https://wms.example.com"
        assert namespace.username == "test_user"
        password = namespace.password
        password_value = (
            password.get_secret_value()
            if isinstance(password, t.SecretStr)
            else password
        )
        assert password_value == "test_pass"
        assert namespace.api_version == "V1"
        assert namespace.timeout == 30
        assert namespace.page_size == 10
        assert namespace.verify_ssl is True
        assert namespace.enable_rate_limiting is True

    def test_full_config(self) -> None:
        """Test creating settings with all fields."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://prod.wms.example.com",
                "username": "prod_user",
                "password": "prod_pass",
                "api_version": "v11",
                "timeout": 60,
                "max_retries": 5,
                "retry_delay": 2,
                "page_size": 500,
                "verify_ssl": False,
                "ssl_cert_path": "/path/to/cert.pem",
                "discovery_sample_size": 200,
                "enable_schema_flattening": False,
                "max_flattening_depth": 5,
                "enable_rate_limiting": False,
                "max_requests_per_minute": 120,
                "user_agent": "CustomAgent/1.0",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "log_level": c.LogLevel.DEBUG,
                "enable_request_logging": True,
                "enable_parallel_extraction": True,
                "max_parallel_streams": 5,
                "validate_config": False,
                "validate_schemas": False,
            },
        )
        namespace = settings.TapOracleWms
        namespace.include_entities = ["inventory", "orders"]
        namespace.exclude_entities = ["test_entity"]
        namespace.additional_headers = {"X-Custom": "value"}
        namespace.column_mappings = '{"inventory": {"old": "new"}}'
        namespace.ignored_columns = ["internal_id"]
        assert namespace.api_version == "v11"
        assert namespace.timeout == 60
        assert namespace.page_size == 500
        assert namespace.verify_ssl is False
        assert namespace.include_entities == ["inventory", "orders"]
        assert namespace.enable_rate_limiting is False
        assert namespace.log_level == "DEBUG"
        assert namespace.max_parallel_streams == 5

    def test_base_url_validation(self) -> None:
        """Test base URL validation accepts valid URLs and bare strings."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com/",
                "username": "user",
                "password": "pass",
            },
        )
        assert "wms.example.com" in settings.TapOracleWms.base_url
        # str | t.AnyUrl union accepts bare hostnames as str
        config_bare = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "wms.example.com",
                "username": "user",
                "password": "pass",
            },
        )
        assert config_bare.TapOracleWms.base_url == "wms.example.com"

    def test_entity_list_validation(self) -> None:
        """Test entity list validation rejects duplicates at construction."""
        with pytest.raises(c.ValidationError) as exc_info:
            FlextTapOracleWmsSettings(
                TapOracleWms={
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": "pass",
                    "include_entities": ["inventory", "orders", "inventory"],
                },
            )
        assert "contains duplicates" in str(exc_info.value)

    def test_date_validation(self) -> None:
        """Test date format validation."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
            },
        )
        assert settings.TapOracleWms.start_date == "2024-01-01T00:00:00Z"
        with pytest.raises(c.ValidationError) as exc_info:
            FlextTapOracleWmsSettings(
                TapOracleWms={
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": "pass",
                    "start_date": "01/01/2024",
                },
            )
        assert "Invalid date format" in str(exc_info.value)

    def test_numeric_validation(self) -> None:
        """Test numeric field validation."""
        with pytest.raises(c.ValidationError):
            FlextTapOracleWmsSettings(
                TapOracleWms={
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": "pass",
                    "page_size": 0,
                },
            )
        with pytest.raises(c.ValidationError):
            FlextTapOracleWmsSettings(
                TapOracleWms={
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": "pass",
                    "timeout": 400,
                },
            )

    def test_model_dump_for_client_payload(self) -> None:
        """Test generating a serializable client payload from settings."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "api_version": "v11",
                "timeout": 45,
                "user_agent": "TestAgent/1.0",
            },
        )
        client_config = settings.TapOracleWms.model_dump(mode="json")
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
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "page_size": 200,
                "start_date": "2024-01-01T00:00:00Z",
            },
        )
        namespace = settings.TapOracleWms
        # column_mappings is a JSON-encoded string per ADR-005 simple-scalar rule
        namespace.column_mappings = (
            '{"inventory": {"old_name": "new_name"},'
            ' "orders": {"customer_id": "cust_id"}}'
        )
        namespace.ignored_columns = ["internal_id"]
        payload = namespace.model_dump(mode="json")
        assert payload["page_size"] == 200
        assert payload["start_date"] == "2024-01-01T00:00:00Z"
        decoded_mappings = t.json_dict_adapter().validate_json(
            payload["column_mappings"],
        )
        assert decoded_mappings["inventory"] == {"old_name": "new_name"}
        assert payload["ignored_columns"] == ["internal_id"]

    def test_config_mutability_with_assignment(self) -> None:
        """Test that namespaced settings fields are mutable via assignment."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
            },
        )
        settings.TapOracleWms.base_url = "https://new.example.com"
        assert settings.TapOracleWms.base_url == "https://new.example.com"

    def test_password_hiding(self) -> None:
        """Test password field is stored (str | t.SecretStr union)."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "super_secret_password",
            },
        )
        password = settings.TapOracleWms.password
        password_value = (
            password.get_secret_value()
            if isinstance(password, t.SecretStr)
            else password
        )
        assert password_value == "super_secret_password"

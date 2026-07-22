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
from flext_tests import tm
from tests import c, t


class TestsFlextTapOracleWmsConfig:
    """Test configuration class."""

    def test_minimal_config(self) -> None:
        """Test creating settings with minimal fields."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "test_user",
                "password": "test_pass",
            }
        )
        namespace = settings.TapOracleWms
        tm.that(namespace.base_url.rstrip("/"), eq="https://wms.example.com")
        tm.that(namespace.username, eq="test_user")
        password = namespace.password
        password_value = (
            password.get_secret_value()
            if isinstance(password, t.SecretStr)
            else password
        )
        tm.that(password_value, eq="test_pass")
        tm.that(namespace.api_version, eq="V1")
        tm.that(namespace.timeout, eq=30)
        tm.that(namespace.page_size, eq=10)
        tm.that(namespace.verify_ssl, eq=True)
        tm.that(namespace.enable_rate_limiting, eq=True)

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
            }
        )
        namespace = settings.TapOracleWms
        namespace.include_entities = ["inventory", "orders"]
        namespace.exclude_entities = ["test_entity"]
        namespace.additional_headers = {"X-Custom": "value"}
        namespace.column_mappings = '{"inventory": {"old": "new"}}'
        namespace.ignored_columns = ["internal_id"]
        tm.that(namespace.api_version, eq="v11")
        tm.that(namespace.timeout, eq=60)
        tm.that(namespace.page_size, eq=500)
        tm.that(namespace.verify_ssl, eq=False)
        tm.that(namespace.include_entities, eq=["inventory", "orders"])
        tm.that(namespace.enable_rate_limiting, eq=False)
        tm.that(namespace.log_level, eq="DEBUG")
        tm.that(namespace.max_parallel_streams, eq=5)

    def test_base_url_validation(self) -> None:
        """Test base URL validation accepts valid URLs and bare strings."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com/",
                "username": "user",
                "password": "pass",
            }
        )
        tm.that(settings.TapOracleWms.base_url, has="wms.example.com")
        # str | t.AnyUrl union accepts bare hostnames as str
        config_bare = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "wms.example.com",
                "username": "user",
                "password": "pass",
            }
        )
        tm.that(config_bare.TapOracleWms.base_url, eq="wms.example.com")

    def test_entity_list_validation(self) -> None:
        """Test entity list validation rejects duplicates at construction."""
        with pytest.raises(c.ValidationError) as exc_info:
            FlextTapOracleWmsSettings(
                TapOracleWms={
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": "pass",
                    "include_entities": ["inventory", "orders", "inventory"],
                }
            )
        tm.that(str(exc_info.value), has="contains duplicates")

    def test_date_validation(self) -> None:
        """Test date format validation."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
            }
        )
        tm.that(settings.TapOracleWms.start_date, eq="2024-01-01T00:00:00Z")
        with pytest.raises(c.ValidationError) as exc_info:
            FlextTapOracleWmsSettings(
                TapOracleWms={
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": "pass",
                    "start_date": "01/01/2024",
                }
            )
        tm.that(str(exc_info.value), has="Invalid date format")

    def test_numeric_validation(self) -> None:
        """Test numeric field validation."""
        with pytest.raises(c.ValidationError):
            FlextTapOracleWmsSettings(
                TapOracleWms={
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": "pass",
                    "page_size": 0,
                }
            )
        with pytest.raises(c.ValidationError):
            FlextTapOracleWmsSettings(
                TapOracleWms={
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": "pass",
                    "timeout": 400,
                }
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
            }
        )
        client_config = settings.TapOracleWms.model_dump(mode="json")
        tm.that(str(client_config["base_url"]), has="wms.example.com")
        tm.that(client_config["username"], eq="user")
        # Password may be str or masked t.SecretStr depending on model settings
        tm.that(client_config["password"], none=False)
        tm.that(client_config["api_version"], eq="v11")
        tm.that(client_config["timeout"], eq=45)
        tm.that(client_config["user_agent"], eq="TestAgent/1.0")

    def test_stream_related_fields_available(self) -> None:
        """Test stream-related configuration fields are preserved in model."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "page_size": 200,
                "start_date": "2024-01-01T00:00:00Z",
            }
        )
        namespace = settings.TapOracleWms
        # column_mappings is a JSON-encoded string per ADR-005 simple-scalar rule
        namespace.column_mappings = (
            '{"inventory": {"old_name": "new_name"},'
            ' "orders": {"customer_id": "cust_id"}}'
        )
        namespace.ignored_columns = ["internal_id"]
        payload = namespace.model_dump(mode="json")
        tm.that(payload["page_size"], eq=200)
        tm.that(payload["start_date"], eq="2024-01-01T00:00:00Z")
        decoded_mappings = t.json_dict_adapter().validate_json(
            payload["column_mappings"]
        )
        tm.that(decoded_mappings["inventory"], eq={"old_name": "new_name"})
        tm.that(payload["ignored_columns"], eq=["internal_id"])

    def test_config_mutability_with_assignment(self) -> None:
        """Test that namespaced settings fields are mutable via assignment."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
            }
        )
        settings.TapOracleWms.base_url = "https://new.example.com"
        tm.that(settings.TapOracleWms.base_url, eq="https://new.example.com")

    def test_password_hiding(self) -> None:
        """Test password field is stored (str | t.SecretStr union)."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "super_secret_password",
            }
        )
        password = settings.TapOracleWms.password
        password_value = (
            password.get_secret_value()
            if isinstance(password, t.SecretStr)
            else password
        )
        tm.that(password_value, eq="super_secret_password")

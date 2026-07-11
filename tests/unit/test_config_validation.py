"""Unit tests for configuration validation.

Tests FlextTapOracleWmsSettings validation through the namespaced
``settings.TapOracleWms.*`` contract (ADR-005). The former
``validate_domain_rules``/``validate_business_rules`` helpers were removed
from the settings layer by ADR-005, so these tests exercise the validators
that still exist on the namespace model.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from tests.constants import c
from tests.typings import t


class TestsFlextTapOracleWmsConfigValidation:
    """Test configuration validation."""

    def test_minimal_valid_config(self) -> None:
        """Test minimal valid configuration."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "test_user",
                "password": "test_password",
            },
        )
        namespace = settings.TapOracleWms
        assert namespace.base_url.rstrip("/") == "https://wms.example.com"
        assert namespace.username == "test_user"
        assert isinstance(namespace.password, (str, t.SecretStr))
        assert namespace.api_version == "V1"
        assert namespace.page_size == 10

    def test_url_accepts_trailing_slash(self) -> None:
        """Test URL with trailing slash is accepted."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com/",
                "username": "user",
                "password": "pass",
            },
        )
        assert "wms.example.com" in settings.TapOracleWms.base_url

    def test_page_size_custom_value(self) -> None:
        """Test custom page size is accepted."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "page_size": 500,
            },
        )
        assert settings.TapOracleWms.page_size == 500

    def test_entity_selection_fields(self) -> None:
        """Test entity include/exclude fields are stored correctly."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "include_entities": ["inventory", "locations"],
                "exclude_entities": ["orders"],
            },
        )
        assert settings.TapOracleWms.include_entities == ["inventory", "locations"]
        assert settings.TapOracleWms.exclude_entities == ["orders"]

    def test_duplicate_entities_rejected(self) -> None:
        """Test namespace validator rejects duplicate entity entries."""
        with pytest.raises(c.ValidationError):
            FlextTapOracleWmsSettings(
                TapOracleWms={
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": "pass",
                    "exclude_entities": ["orders", "orders"],
                },
            )

    def test_date_fields(self) -> None:
        """Test date fields are accepted."""
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
        assert settings.TapOracleWms.end_date == "2024-12-31T23:59:59Z"

    def test_invalid_date_rejected(self) -> None:
        """Test namespace validator rejects non-ISO date values."""
        with pytest.raises(c.ValidationError):
            FlextTapOracleWmsSettings(
                TapOracleWms={
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": "pass",
                    "end_date": "31/12/2024",
                },
            )

    def test_model_serialization(self) -> None:
        """Test configuration model serialization."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
            },
        )
        data = settings.TapOracleWms.model_dump()
        assert isinstance(data, dict)
        assert data["username"] == "user"
        assert "base_url" in data

    def test_stream_related_config_fields(self) -> None:
        """Test stream-related configuration fields are accessible."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "page_size": 50,
                "column_mappings": '{"inventory": {"old_col": "new_col"}}',
                "ignored_columns": ["internal_id"],
            },
        )
        namespace = settings.TapOracleWms
        assert namespace.page_size == 50
        # column_mappings is a JSON-encoded string per ADR-005 simple-scalar rule
        decoded_mappings = t.json_dict_adapter().validate_json(
            namespace.column_mappings,
        )
        assert decoded_mappings == {"inventory": {"old_col": "new_col"}}
        assert namespace.ignored_columns == ["internal_id"]

    def test_parallel_extraction_config(self) -> None:
        """Test parallel extraction configuration fields."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "enable_parallel_extraction": True,
                "max_parallel_streams": 6,
                "enable_rate_limiting": True,
            },
        )
        namespace = settings.TapOracleWms
        assert namespace.enable_parallel_extraction is True
        assert namespace.max_parallel_streams == 6
        assert namespace.enable_rate_limiting is True

    def test_ssl_config(self) -> None:
        """Test SSL configuration fields."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "verify_ssl": False,
                "ssl_cert_path": "/path/to/cert.pem",
            },
        )
        assert settings.TapOracleWms.verify_ssl is False
        assert settings.TapOracleWms.ssl_cert_path == "/path/to/cert.pem"

    def test_rate_limiting_config(self) -> None:
        """Test rate limiting configuration."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "pass",
                "enable_rate_limiting": True,
                "max_requests_per_minute": 120,
            },
        )
        assert settings.TapOracleWms.enable_rate_limiting is True
        assert settings.TapOracleWms.max_requests_per_minute == 120

    def test_password_is_secret(self) -> None:
        """Test password field stores password value."""
        settings = FlextTapOracleWmsSettings(
            TapOracleWms={
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": "super_secret",
            },
        )
        password = settings.TapOracleWms.password
        password_value = (
            password.get_secret_value()
            if isinstance(password, t.SecretStr)
            else password
        )
        assert password_value == "super_secret"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

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

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from tests import TestsFlextTapOracleWmsHelpers, c, tm, u


class TestsFlextTapOracleWmsConfigValidation(TestsFlextTapOracleWmsHelpers):
    """Test configuration validation."""

    def test_url_accepts_trailing_slash(self) -> None:
        """Test URL with trailing slash is accepted."""
        settings = self._tap_settings({"base_url": "https://wms.example.com/"})
        tm.that(settings.TapOracleWms.base_url, has="wms.example.com")

    @staticmethod
    def test_page_size_custom_value() -> None:
        """Test custom page size is accepted."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": c.TapOracleWms.Tests.CREDENTIAL,
                "page_size": 500,
            },
        })
        tm.that(settings.TapOracleWms.page_size, eq=500)

    @staticmethod
    def test_entity_selection_fields() -> None:
        """Test entity include/exclude fields are stored correctly."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": c.TapOracleWms.Tests.CREDENTIAL,
                "include_entities": ["inventory", "locations"],
                "exclude_entities": ["orders"],
            },
        })
        tm.that(settings.TapOracleWms.include_entities, eq=["inventory", "locations"])
        tm.that(settings.TapOracleWms.exclude_entities, eq=["orders"])

    def test_date_fields(self) -> None:
        """Test date fields are accepted."""
        settings = self._tap_settings({
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-12-31T23:59:59Z",
        })
        tm.that(settings.TapOracleWms.start_date, eq="2024-01-01T00:00:00Z")
        tm.that(settings.TapOracleWms.end_date, eq="2024-12-31T23:59:59Z")

    @staticmethod
    def test_invalid_date_rejected() -> None:
        """Test namespace validator rejects non-ISO date values."""
        with u.Tests.raises(c.ValidationError):
            FlextTapOracleWmsSettings.model_validate({
                "TapOracleWms": {
                    "base_url": "https://wms.example.com",
                    "username": "user",
                    "password": c.TapOracleWms.Tests.CREDENTIAL,
                    "end_date": "31/12/2024",
                },
            })

    @staticmethod
    def test_model_serialization() -> None:
        """Test configuration model serialization."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": c.TapOracleWms.Tests.CREDENTIAL,
            },
        })
        data = settings.TapOracleWms.model_dump()
        tm.that(data, is_=dict)
        tm.that(data["username"], eq="user")
        tm.that(data, has="base_url")

    @staticmethod
    def test_parallel_extraction_config() -> None:
        """Test parallel extraction configuration fields."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": c.TapOracleWms.Tests.CREDENTIAL,
                "enable_parallel_extraction": True,
                "max_parallel_streams": 6,
                "enable_rate_limiting": True,
            },
        })
        namespace = settings.TapOracleWms
        tm.ok(namespace.enable_parallel_extraction)
        tm.that(namespace.max_parallel_streams, eq=6)
        tm.ok(namespace.enable_rate_limiting)

    @staticmethod
    def test_ssl_config() -> None:
        """Test SSL configuration fields."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": c.TapOracleWms.Tests.CREDENTIAL,
                "verify_ssl": False,
                "ssl_cert_path": "/path/to/cert.pem",
            },
        })
        tm.fail(settings.TapOracleWms.verify_ssl)
        tm.that(settings.TapOracleWms.ssl_cert_path, eq="/path/to/cert.pem")

    @staticmethod
    def test_rate_limiting_config() -> None:
        """Test rate limiting configuration."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                "base_url": "https://wms.example.com",
                "username": "user",
                "password": c.TapOracleWms.Tests.CREDENTIAL,
                "enable_rate_limiting": True,
                "max_requests_per_minute": 120,
            },
        })
        tm.ok(settings.TapOracleWms.enable_rate_limiting)
        tm.that(settings.TapOracleWms.max_requests_per_minute, eq=120)

    def test_password_is_secret(self) -> None:
        """Test password field stores password value."""
        settings = self._tap_settings({"password": "p" + c.ParserBooleanToken.ONE * 12})
        tm.that(self._password_value(settings), eq="p" + c.ParserBooleanToken.ONE * 12)


if __name__ == "__main__":
    u.Tests.main([__file__, "-v"])

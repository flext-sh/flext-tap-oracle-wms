"""Comprehensive test suite for config_mapper module covering all 41 methods."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from flext_tap_oracle_wms.config_mapper import (
    MAX_PAGE_SIZE,
    MAX_REQUEST_TIMEOUT,
    ConfigMapper,
)

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_TOTAL_PAGES = 8
EXPECTED_DATA_COUNT = 3


class TestConfigMapperInitialization:
    """Test ConfigMapper initialization and basic functionality."""

    def test_init_without_profile_config(self) -> None:
        """Test initialization without profile configuration."""
        mapper = ConfigMapper()
        if mapper.profile_config != {}:
            msg = f"Expected {{}}, got {mapper.profile_config}"
            raise AssertionError(msg)
        assert mapper._config_cache == {}

    def test_init_with_profile_config(self) -> None:
        """Test initialization with profile configuration."""
        profile = {"key": "value", "api": {"base_url": "https://test.com"}}
        mapper = ConfigMapper(profile)
        if mapper.profile_config != profile:
            msg = f"Expected {profile}, got {mapper.profile_config}"
            raise AssertionError(msg)
        assert mapper._config_cache == {}

    def test_init_with_none_profile_config(self) -> None:
        """Test initialization with None profile configuration."""
        mapper = ConfigMapper(None)
        if mapper.profile_config != {}:
            msg = f"Expected {{}}, got {mapper.profile_config}"
            raise AssertionError(msg)
        assert mapper._config_cache == {}


class TestConnectionConfiguration:
    """Test connection-related configuration methods."""

    def test_get_base_url_default(self) -> None:
        """Test get_base_url with default value."""
        with patch.dict(os.environ, {}, clear=True):
            mapper = ConfigMapper()
            if mapper.get_base_url() != "":
                msg = f"Expected {''}, got {mapper.get_base_url()}"
                raise AssertionError(msg)

    def test_get_base_url_from_env(self) -> None:
        """Test get_base_url from environment variable."""
        with patch.dict(
            os.environ,
            {"TAP_ORACLE_WMS_BASE_URL": "https://env.example.com"},
        ):
            mapper = ConfigMapper()
            if mapper.get_base_url() != "https://env.example.com":
                msg = f"Expected {'https://env.example.com'}, got {mapper.get_base_url()}"
                raise AssertionError(
                    msg,
                )

    def test_get_base_url_from_profile(self) -> None:
        """Test get_base_url from profile configuration."""
        profile = {"api": {"base_url": "https://profile.example.com"}}
        mapper = ConfigMapper(profile)
        if mapper.get_base_url() != "https://profile.example.com":
            msg = f"Expected {'https://profile.example.com'}, got {mapper.get_base_url()}"
            raise AssertionError(
                msg,
            )

    def test_get_base_url_env_overrides_profile(self) -> None:
        """Test that environment variable overrides profile configuration."""
        profile = {"api": {"base_url": "https://profile.example.com"}}
        with patch.dict(
            os.environ,
            {"TAP_ORACLE_WMS_BASE_URL": "https://env.example.com"},
        ):
            mapper = ConfigMapper(profile)
            if mapper.get_base_url() != "https://env.example.com":
                msg = f"Expected {'https://env.example.com'}, got {mapper.get_base_url()}"
                raise AssertionError(
                    msg,
                )

    def test_get_username_default(self) -> None:
        """Test get_username with default value."""
        # Clear environment to test default
        with patch.dict(os.environ, {}, clear=True):
            mapper = ConfigMapper()
            if mapper.get_username() != "":
                msg = f"Expected {''}, got {mapper.get_username()}"
                raise AssertionError(msg)

    def test_get_username_from_env(self) -> None:
        """Test get_username from environment variable."""
        with patch.dict(os.environ, {"TAP_ORACLE_WMS_USERNAME": "testuser"}):
            mapper = ConfigMapper()
            if mapper.get_username() != "testuser":
                msg = f"Expected {'testuser'}, got {mapper.get_username()}"
                raise AssertionError(
                    msg,
                )

    def test_get_username_from_profile(self) -> None:
        """Test get_username from profile configuration."""
        profile = {"api": {"username": "profileuser"}}
        with patch.dict(os.environ, {}, clear=True):
            mapper = ConfigMapper(profile)
            if mapper.get_username() != "profileuser":
                msg = f"Expected {'profileuser'}, got {mapper.get_username()}"
                raise AssertionError(
                    msg,
                )

    def test_get_password_default(self) -> None:
        """Test get_password with default value."""
        with patch.dict(os.environ, {}, clear=True):
            mapper = ConfigMapper()
            if mapper.get_password() != "":
                msg = f"Expected {''}, got {mapper.get_password()}"
                raise AssertionError(msg)

    def test_get_password_from_env(self) -> None:
        """Test get_password from environment variable."""
        with patch.dict(os.environ, {"TAP_ORACLE_WMS_PASSWORD": "testpass"}):
            mapper = ConfigMapper()
            if mapper.get_password() != "testpass":
                msg = f"Expected {'testpass'}, got {mapper.get_password()}"
                raise AssertionError(
                    msg,
                )

    def test_get_password_from_profile(self) -> None:
        """Test get_password from profile configuration."""
        profile = {"api": {"password": "profilepass"}}
        with patch.dict(os.environ, {}, clear=True):
            mapper = ConfigMapper(profile)
            if mapper.get_password() != "profilepass":
                msg = f"Expected {'profilepass'}, got {mapper.get_password()}"
                raise AssertionError(
                    msg,
                )


class TestAPIConfiguration:
    """Test API-related configuration methods."""

    def test_get_api_version_default(self) -> None:
        """Test get_api_version with default value."""
        with patch.dict(os.environ, {}, clear=True):
            mapper = ConfigMapper()
            if mapper.get_api_version() != "v10":
                msg = f"Expected {'v10'}, got {mapper.get_api_version()}"
                raise AssertionError(
                    msg,
                )

    def test_get_api_version_from_env(self) -> None:
        """Test get_api_version from environment variable."""
        with patch.dict(os.environ, {"WMS_API_VERSION": "v11"}):
            mapper = ConfigMapper()
            if mapper.get_api_version() != "v11":
                msg = f"Expected {'v11'}, got {mapper.get_api_version()}"
                raise AssertionError(
                    msg,
                )

    def test_get_endpoint_prefix_default(self) -> None:
        """Test get_endpoint_prefix with default value."""
        with patch.dict(os.environ, {}, clear=True):
            mapper = ConfigMapper()
            if mapper.get_endpoint_prefix() != "/wms/lgfapi":
                msg = f"Expected {'/wms/lgfapi'}, got {mapper.get_endpoint_prefix()}"
                raise AssertionError(
                    msg,
                )

    def test_get_endpoint_prefix_from_env(self) -> None:
        """Test get_endpoint_prefix from environment variable."""
        with patch.dict(os.environ, {"WMS_ENDPOINT_PREFIX": "/custom/api"}):
            mapper = ConfigMapper()
            if mapper.get_endpoint_prefix() != "/custom/api":
                msg = f"Expected {'/custom/api'}, got {mapper.get_endpoint_prefix()}"
                raise AssertionError(
                    msg,
                )

    def test_get_entity_endpoint_pattern_default(self) -> None:
        """Test get_entity_endpoint_pattern with default value."""
        mapper = ConfigMapper()
        assert (
            mapper.get_entity_endpoint_pattern()
            == "/{prefix}/{version}/entity/{entity}"
        )

    def test_get_entity_endpoint_pattern_from_env(self) -> None:
        """Test get_entity_endpoint_pattern from environment variable."""
        pattern = "/custom/{prefix}/{version}/{entity}"
        with patch.dict(os.environ, {"WMS_ENTITY_ENDPOINT_PATTERN": pattern}):
            mapper = ConfigMapper()
            if mapper.get_entity_endpoint_pattern() != pattern:
                msg = f"Expected {pattern}, got {mapper.get_entity_endpoint_pattern()}"
                raise AssertionError(
                    msg,
                )

    def test_get_authentication_method_default(self) -> None:
        """Test get_authentication_method with default value."""
        mapper = ConfigMapper()
        if mapper.get_authentication_method() != "basic":
            msg = f"Expected {'basic'}, got {mapper.get_authentication_method()}"
            raise AssertionError(
                msg,
            )

    def test_get_authentication_method_from_env(self) -> None:
        """Test get_authentication_method from environment variable."""
        with patch.dict(os.environ, {"WMS_AUTH_METHOD": "oauth"}):
            mapper = ConfigMapper()
            if mapper.get_authentication_method() != "oauth":
                msg = f"Expected {'oauth'}, got {mapper.get_authentication_method()}"
                raise AssertionError(
                    msg,
                )


class TestPerformanceConfiguration:
    """Test performance-related configuration methods."""

    def test_get_page_size_default(self) -> None:
        """Test get_page_size with default value."""
        mapper = ConfigMapper()
        if mapper.get_page_size() != 500:
            msg = f"Expected {500}, got {mapper.get_page_size()}"
            raise AssertionError(msg)

    def test_get_page_size_from_env(self) -> None:
        """Test get_page_size from environment variable."""
        with patch.dict(os.environ, {"WMS_PAGE_SIZE": "1000"}):
            mapper = ConfigMapper()
            if mapper.get_page_size() != 1000:
                msg = f"Expected {1000}, got {mapper.get_page_size()}"
                raise AssertionError(msg)

    def test_get_page_size_exceeds_max(self) -> None:
        """Test get_page_size when value exceeds maximum."""
        with patch.dict(os.environ, {"WMS_PAGE_SIZE": "2000"}):
            mapper = ConfigMapper()
            if mapper.get_page_size() != MAX_PAGE_SIZE:
                msg = f"Expected {MAX_PAGE_SIZE}, got {mapper.get_page_size()}"
                raise AssertionError(
                    msg,
                )

    def test_get_max_page_size_constant(self) -> None:
        """Test get_max_page_size returns constant."""
        mapper = ConfigMapper()
        if mapper.get_max_page_size() != MAX_PAGE_SIZE:
            msg = f"Expected {MAX_PAGE_SIZE}, got {mapper.get_max_page_size()}"
            raise AssertionError(
                msg,
            )

    def test_get_request_timeout_default(self) -> None:
        """Test get_request_timeout with default value."""
        mapper = ConfigMapper()
        if mapper.get_request_timeout() != MAX_REQUEST_TIMEOUT:
            msg = f"Expected {MAX_REQUEST_TIMEOUT}, got {mapper.get_request_timeout()}"
            raise AssertionError(
                msg,
            )

    def test_get_request_timeout_from_env(self) -> None:
        """Test get_request_timeout from environment variable."""
        with patch.dict(os.environ, {"WMS_REQUEST_TIMEOUT": "300"}):
            mapper = ConfigMapper()
            if mapper.get_request_timeout() != 300:
                msg = f"Expected {300}, got {mapper.get_request_timeout()}"
                raise AssertionError(
                    msg,
                )

    def test_get_max_retries_default(self) -> None:
        """Test get_max_retries with default value."""
        mapper = ConfigMapper()
        if mapper.get_max_retries() != EXPECTED_DATA_COUNT:
            msg = f"Expected {3}, got {mapper.get_max_retries()}"
            raise AssertionError(msg)

    def test_get_max_retries_from_env_string(self) -> None:
        """Test get_max_retries from environment variable as string."""
        with patch.dict(os.environ, {"WMS_MAX_RETRIES": "5"}):
            mapper = ConfigMapper()
            if mapper.get_max_retries() != 5:
                msg = f"Expected {5}, got {mapper.get_max_retries()}"
                raise AssertionError(msg)

    def test_get_max_retries_from_profile_int(self) -> None:
        """Test get_max_retries from profile as integer."""
        profile = {"performance": {"max_retries": 7}}
        mapper = ConfigMapper(profile)
        if mapper.get_max_retries() != 7:
            msg = f"Expected {7}, got {mapper.get_max_retries()}"
            raise AssertionError(msg)

    def test_get_max_retries_from_profile_float(self) -> None:
        """Test get_max_retries from profile as float."""
        profile = {"performance": {"max_retries": 8.5}}
        mapper = ConfigMapper(profile)
        if mapper.get_max_retries() != EXPECTED_TOTAL_PAGES:
            msg = f"Expected {8}, got {mapper.get_max_retries()}"
            raise AssertionError(msg)

    def test_get_max_retries_invalid_value(self) -> None:
        """Test get_max_retries with invalid value falls back to default."""
        profile = {"performance": {"max_retries": "invalid"}}
        mapper = ConfigMapper(profile)
        if mapper.get_max_retries() != EXPECTED_DATA_COUNT:
            msg = f"Expected {3}, got {mapper.get_max_retries()}"
            raise AssertionError(msg)

    def test_get_retry_backoff_factor_default(self) -> None:
        """Test get_retry_backoff_factor with default value."""
        mapper = ConfigMapper()
        if mapper.get_retry_backoff_factor() != 1.5:
            msg = f"Expected {1.5}, got {mapper.get_retry_backoff_factor()}"
            raise AssertionError(
                msg,
            )

    def test_get_retry_backoff_factor_from_env_string(self) -> None:
        """Test get_retry_backoff_factor from environment variable as string."""
        with patch.dict(os.environ, {"WMS_RETRY_BACKOFF_FACTOR": "2.0"}):
            mapper = ConfigMapper()
            if mapper.get_retry_backoff_factor() != 2.0:
                msg = f"Expected {2.0}, got {mapper.get_retry_backoff_factor()}"
                raise AssertionError(
                    msg,
                )

    def test_get_retry_backoff_factor_from_profile_int(self) -> None:
        """Test get_retry_backoff_factor from profile as integer."""
        profile = {"performance": {"retry_backoff_factor": 3}}
        mapper = ConfigMapper(profile)
        if mapper.get_retry_backoff_factor() != 3.0:
            msg = f"Expected {3.0}, got {mapper.get_retry_backoff_factor()}"
            raise AssertionError(
                msg,
            )

    def test_get_retry_backoff_factor_invalid_string(self) -> None:
        """Test get_retry_backoff_factor with invalid string falls back to default."""
        profile = {"performance": {"retry_backoff_factor": "invalid"}}
        mapper = ConfigMapper(profile)
        if mapper.get_retry_backoff_factor() != 1.5:
            msg = f"Expected {1.5}, got {mapper.get_retry_backoff_factor()}"
            raise AssertionError(
                msg,
            )

    def test_get_cache_ttl_seconds_default(self) -> None:
        """Test get_cache_ttl_seconds with default value."""
        mapper = ConfigMapper()
        if mapper.get_cache_ttl_seconds() != 3600:
            msg = f"Expected {3600}, got {mapper.get_cache_ttl_seconds()}"
            raise AssertionError(
                msg,
            )

    def test_get_cache_ttl_seconds_from_env(self) -> None:
        """Test get_cache_ttl_seconds from environment variable."""
        with patch.dict(os.environ, {"WMS_CACHE_TTL_SECONDS": "7200"}):
            mapper = ConfigMapper()
            if mapper.get_cache_ttl_seconds() != 7200:
                msg = f"Expected {7200}, got {mapper.get_cache_ttl_seconds()}"
                raise AssertionError(
                    msg,
                )

    def test_get_cache_ttl_seconds_from_profile_float(self) -> None:
        """Test get_cache_ttl_seconds from profile as float."""
        profile = {"performance": {"cache_ttl_seconds": 1800.5}}
        mapper = ConfigMapper(profile)
        if mapper.get_cache_ttl_seconds() != 1800:
            msg = f"Expected {1800}, got {mapper.get_cache_ttl_seconds()}"
            raise AssertionError(
                msg,
            )

    def test_get_cache_ttl_seconds_invalid_value(self) -> None:
        """Test get_cache_ttl_seconds with invalid value falls back to default."""
        profile = {"performance": {"cache_ttl_seconds": "invalid"}}
        mapper = ConfigMapper(profile)
        if mapper.get_cache_ttl_seconds() != 3600:
            msg = f"Expected {3600}, got {mapper.get_cache_ttl_seconds()}"
            raise AssertionError(
                msg,
            )

    def test_get_connection_pool_size_default(self) -> None:
        """Test get_connection_pool_size with default value."""
        mapper = ConfigMapper()
        if mapper.get_connection_pool_size() != 5:
            msg = f"Expected {5}, got {mapper.get_connection_pool_size()}"
            raise AssertionError(
                msg,
            )

    def test_get_connection_pool_size_from_env(self) -> None:
        """Test get_connection_pool_size from environment variable."""
        with patch.dict(os.environ, {"WMS_CONNECTION_POOL_SIZE": "10"}):
            mapper = ConfigMapper()
            if mapper.get_connection_pool_size() != 10:
                msg = f"Expected {10}, got {mapper.get_connection_pool_size()}"
                raise AssertionError(
                    msg,
                )


class TestSafeIntConversion:
    """Test _safe_int_conversion static method."""

    def test_safe_int_conversion_with_int(self) -> None:
        """Test _safe_int_conversion with integer input."""
        result = ConfigMapper._safe_int_conversion(42, 100)
        if result != 42:
            msg = f"Expected {42}, got {result}"
            raise AssertionError(msg)

    def test_safe_int_conversion_with_string_digit(self) -> None:
        """Test _safe_int_conversion with digit string input."""
        result = ConfigMapper._safe_int_conversion("123", 100)
        if result != 123:
            msg = f"Expected {123}, got {result}"
            raise AssertionError(msg)

    def test_safe_int_conversion_with_float(self) -> None:
        """Test _safe_int_conversion with float input."""
        result = ConfigMapper._safe_int_conversion(45.7, 100)
        if result != 45:
            msg = f"Expected {45}, got {result}"
            raise AssertionError(msg)

    def test_safe_int_conversion_with_invalid_string(self) -> None:
        """Test _safe_int_conversion with invalid string returns default."""
        result = ConfigMapper._safe_int_conversion("invalid", 100)
        if result != 100:
            msg = f"Expected {100}, got {result}"
            raise AssertionError(msg)

    def test_safe_int_conversion_with_none(self) -> None:
        """Test _safe_int_conversion with None returns default."""
        result = ConfigMapper._safe_int_conversion(None, 100)
        if result != 100:
            msg = f"Expected {100}, got {result}"
            raise AssertionError(msg)

    def test_safe_int_conversion_with_list(self) -> None:
        """Test _safe_int_conversion with list returns default."""
        result = ConfigMapper._safe_int_conversion([1, 2, 3], 100)
        if result != 100:
            msg = f"Expected {100}, got {result}"
            raise AssertionError(msg)


class TestConfigCaching:
    """Test configuration value caching functionality."""

    def test_config_value_cached(self) -> None:
        """Test that configuration values are cached."""
        mapper = ConfigMapper()

        # First call should compute and cache
        with patch.dict(os.environ, {"TAP_ORACLE_WMS_BASE_URL": "https://test.com"}):
            result1 = mapper.get_base_url()

        # Second call should use cache (env var changed but result should be same)
        with patch.dict(os.environ, {"TAP_ORACLE_WMS_BASE_URL": "https://changed.com"}):
            result2 = mapper.get_base_url()

        if result1 == result2 != "https://test.com":
            msg = f"Expected {'https://test.com'}, got {result1 == result2}"
            raise AssertionError(
                msg,
            )

    def test_cache_key_generation(self) -> None:
        """Test that different cache keys work correctly."""
        mapper = ConfigMapper()

        with patch.dict(
            os.environ,
            {
                "TAP_ORACLE_WMS_BASE_URL": "https://test.com",
                "TAP_ORACLE_WMS_USERNAME": "testuser",
            },
        ):
            base_url = mapper.get_base_url()
            username = mapper.get_username()

        if base_url != "https://test.com":
            msg = f"Expected {'https://test.com'}, got {base_url}"
            raise AssertionError(msg)
        assert username == "testuser"
        if len(mapper._config_cache) != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {len(mapper._config_cache)}"
            raise AssertionError(msg)


class TestNestedProfileConfiguration:
    """Test nested profile configuration path handling."""

    def test_nested_profile_configuration(self) -> None:
        """Test nested profile configuration paths work correctly."""
        profile = {
            "api": {
                "base_url": "https://nested.example.com",
                "username": "nesteduser",
                "connection": {
                    "timeout": 300,
                },
            },
            "performance": {
                "page_size": 1000,
                "cache_ttl_seconds": 7200,
            },
        }
        # Clear environment to test profile configuration only
        with patch.dict(os.environ, {}, clear=True):
            mapper = ConfigMapper(profile)

            if mapper.get_base_url() != "https://nested.example.com":
                msg = f"Expected {'https://nested.example.com'}, got {mapper.get_base_url()}"
                raise AssertionError(
                    msg,
                )
            assert mapper.get_username() == "nesteduser"
            if mapper.get_page_size() != 1000:
                msg = f"Expected {1000}, got {mapper.get_page_size()}"
                raise AssertionError(msg)
            assert mapper.get_cache_ttl_seconds() == 7200

    def test_direct_key_overrides_nested_path(self) -> None:
        """Test that direct keys override nested paths."""
        profile = {
            "base_url": "https://direct.example.com",
            "api": {
                "base_url": "https://nested.example.com",
            },
        }
        mapper = ConfigMapper(profile)
        if mapper.get_base_url() != "https://direct.example.com":
            msg = f"Expected {'https://direct.example.com'}, got {mapper.get_base_url()}"
            raise AssertionError(
                msg,
            )


class TestConfigMapperAllMethods:
    """Test all remaining methods in ConfigMapper to achieve full coverage."""

    def test_get_replication_key(self) -> None:
        """Test get_replication_key method."""
        mapper = ConfigMapper()
        # Default should be "mod_ts" based on implementation
        if mapper.get_replication_key() != "mod_ts":
            msg = f"Expected {'mod_ts'}, got {mapper.get_replication_key()}"
            raise AssertionError(
                msg,
            )

        with patch.dict(os.environ, {"WMS_REPLICATION_KEY": "updated_at"}):
            mapper = ConfigMapper()
            if mapper.get_replication_key() != "updated_at":
                msg = f"Expected {'updated_at'}, got {mapper.get_replication_key()}"
                raise AssertionError(
                    msg,
                )

    def test_get_pagination_mode(self) -> None:
        """Test get_pagination_mode method."""
        mapper = ConfigMapper()
        # Test with default
        if mapper.get_pagination_mode() != "sequenced":
            msg = f"Expected {'sequenced'}, got {mapper.get_pagination_mode()}"
            raise AssertionError(
                msg,
            )

        with patch.dict(os.environ, {"WMS_PAGE_MODE": "cursor"}):
            mapper = ConfigMapper()
            if mapper.get_pagination_mode() != "cursor":
                msg = f"Expected {'cursor'}, got {mapper.get_pagination_mode()}"
                raise AssertionError(
                    msg,
                )

    def test_get_incremental_overlap_minutes(self) -> None:
        """Test get_incremental_overlap_minutes method."""
        mapper = ConfigMapper()
        if mapper.get_incremental_overlap_minutes() != 5:  # default:
            msg = f"Expected {5}, got {mapper.get_incremental_overlap_minutes()}"
            raise AssertionError(
                msg,
            )

        with patch.dict(os.environ, {"WMS_INCREMENTAL_OVERLAP_MINUTES": "10"}):
            mapper = ConfigMapper()
            if mapper.get_incremental_overlap_minutes() != 10:
                msg = f"Expected {10}, got {mapper.get_incremental_overlap_minutes()}"
                raise AssertionError(
                    msg,
                )

    def test_get_lookback_minutes(self) -> None:
        """Test get_lookback_minutes method."""
        mapper = ConfigMapper()
        if mapper.get_lookback_minutes() != 60:  # default:
            msg = f"Expected {60}, got {mapper.get_lookback_minutes()}"
            raise AssertionError(msg)

        profile = {"business_rules": {"lookback_minutes": 120}}
        mapper = ConfigMapper(profile)
        if mapper.get_lookback_minutes() != 120:
            msg = f"Expected {120}, got {mapper.get_lookback_minutes()}"
            raise AssertionError(msg)

    def test_profile_config_with_complex_data(self) -> None:
        """Test profile configuration with complex nested data."""
        complex_profile = {
            "api": {
                "base_url": "https://complex.example.com",
                "version": "v12",
                "auth": {
                    "method": "oauth",
                    "token_url": "https://auth.example.com/token",
                },
            },
            "performance": {
                "timeouts": {
                    "request": 600,
                    "connection": 30,
                },
                "retries": {
                    "max": 5,
                    "backoff": 2.0,
                },
            },
            "features": {
                "caching": True,
                "compression": False,
                "ssl_verify": True,
            },
        }

        mapper = ConfigMapper(complex_profile)

        # Test that complex nested access works
        if mapper.get_base_url() != "https://complex.example.com":
            msg = f"Expected {'https://complex.example.com'}, got {mapper.get_base_url()}"
            raise AssertionError(
                msg,
            )
        assert mapper.get_api_version() == "v12"

    def test_environment_precedence_over_all(self) -> None:
        """Test that environment variables have highest precedence."""
        profile = {
            "base_url": "https://profile-direct.com",
            "api": {
                "base_url": "https://profile-nested.com",
            },
        }

        with patch.dict(os.environ, {"TAP_ORACLE_WMS_BASE_URL": "https://env.com"}):
            mapper = ConfigMapper(profile)
            if mapper.get_base_url() != "https://env.com":
                msg = f"Expected {'https://env.com'}, got {mapper.get_base_url()}"
                raise AssertionError(
                    msg,
                )

    def test_string_type_conversion(self) -> None:
        """Test that all getter methods return strings when expected."""
        mapper = ConfigMapper()

        # All string methods should return strings even with empty values
        assert isinstance(mapper.get_base_url(), str)
        assert isinstance(mapper.get_username(), str)
        assert isinstance(mapper.get_password(), str)
        assert isinstance(mapper.get_api_version(), str)
        assert isinstance(mapper.get_endpoint_prefix(), str)
        assert isinstance(mapper.get_entity_endpoint_pattern(), str)
        assert isinstance(mapper.get_authentication_method(), str)
        assert isinstance(mapper.get_replication_key(), str)
        assert isinstance(mapper.get_pagination_mode(), str)

    def test_integer_type_conversion(self) -> None:
        """Test that all integer methods return integers."""
        mapper = ConfigMapper()

        # All integer methods should return integers
        assert isinstance(mapper.get_page_size(), int)
        assert isinstance(mapper.get_max_page_size(), int)
        assert isinstance(mapper.get_request_timeout(), int)
        assert isinstance(mapper.get_max_retries(), int)
        assert isinstance(mapper.get_cache_ttl_seconds(), int)
        assert isinstance(mapper.get_connection_pool_size(), int)
        assert isinstance(mapper.get_incremental_overlap_minutes(), int)
        assert isinstance(mapper.get_lookback_minutes(), int)

    def test_float_type_conversion(self) -> None:
        """Test that float methods return floats."""
        mapper = ConfigMapper()

        # Float method should return float
        assert isinstance(mapper.get_retry_backoff_factor(), float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

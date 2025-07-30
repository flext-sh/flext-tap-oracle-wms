"""Test simple API functionality."""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License
from __future__ import annotations

from unittest.mock import Mock

import pytest
from flext_core import FlextResult

from flext_tap_oracle_wms import simple_api
from flext_tap_oracle_wms.config import TapOracleWMSConfig
from flext_tap_oracle_wms.simple_api import (
    create_development_wms_config,
    create_production_wms_config,
    setup_wms_tap,
    validate_wms_config,
)

# Constants
EXPECTED_DATA_COUNT = 3


class TestSimpleAPI:
    """Test simple API functionality."""

    def test_setup_wms_tap_without_config(self) -> None:
        """Test setup WMS tap without providing config."""
        result = setup_wms_tap()
        assert isinstance(result, FlextResult)
        assert result.success
        assert isinstance(result.data, TapOracleWMSConfig)

    def test_setup_wms_tap_with_config(self) -> None:
        """Test setup WMS tap with provided config."""
        config = create_development_wms_config(
            username="test_user",
            password="test_pass",
        )
        result = setup_wms_tap(config)
        assert result.success
        if result.data != config:
            msg = f"Expected {config}, got {result.data}"
            raise AssertionError(msg)

    def test_setup_wms_tap_missing_username(self) -> None:
        """Test setup WMS tap fails with missing username."""
        config = TapOracleWMSConfig.from_singer_config(
            {
                "username": "",  # Empty username
                "password": "test_pass",
                "auth_method": "basic",
                "base_url": "https://test.com",
                "timeout": 30,
                "max_retries": 3,
                "verify_ssl": False,
            },
        )
        result = setup_wms_tap(config)
        assert not result.success
        assert result.error is not None
        if "Username is required" not in result.error:
            msg = f"Expected {'Username is required'} in {result.error}"
            raise AssertionError(msg)

    def test_setup_wms_tap_exception_handling(self) -> None:
        """Test setup WMS tap handles exceptions."""
        # Create an invalid config that will cause an exception
        invalid_config = object()  # Not a TapOracleWMSConfig
        result = setup_wms_tap(invalid_config)
        assert not result.success
        assert result.error is not None
        if "Failed to setup WMS tap" not in result.error:
            msg = f"Expected {'Failed to setup WMS tap'} in {result.error}"
            raise AssertionError(
                msg,
            )

    def test_create_development_wms_config_defaults(self) -> None:
        """Test creating development config with defaults."""
        config = create_development_wms_config()
        if config.auth.username != "test_user":
            msg = f"Expected {'test_user'}, got {config.auth.username}"
            raise AssertionError(msg)
        assert config.auth.password == "test_password"
        if config.auth.auth_method != "basic":
            msg = f"Expected {'basic'}, got {config.auth.auth_method}"
            raise AssertionError(msg)
        if "test-wms.oracle.com" not in config.connection.base_url:
            msg = f"Expected {'test-wms.oracle.com'} in {config.connection.base_url}"
            raise AssertionError(
                msg,
            )
        if config.connection.timeout != 30:
            msg = f"Expected {30}, got {config.connection.timeout}"
            raise AssertionError(msg)
        assert config.connection.max_retries == EXPECTED_DATA_COUNT
        if config.connection.verify_ssl:
            msg = f"Expected False, got {config.connection.verify_ssl}"
            raise AssertionError(msg)
        if not (config.debug):
            msg = f"Expected True, got {config.debug}"
            raise AssertionError(msg)
        if config.log_level != "DEBUG":
            msg = f"Expected {'DEBUG'}, got {config.log_level}"
            raise AssertionError(msg)

    def test_create_development_wms_config_overrides(self) -> None:
        """Test creating development config with overrides."""
        config = create_development_wms_config(
            username="custom_user",
            password="custom_pass",
            base_url="https://custom.com",
            debug=False,
            log_level="INFO",
        )
        if config.auth.username != "custom_user":
            msg = f"Expected {'custom_user'}, got {config.auth.username}"
            raise AssertionError(
                msg,
            )
        assert config.auth.password == "custom_pass"
        if config.connection.base_url != "https://custom.com":
            msg = f"Expected {'https://custom.com'}, got {config.connection.base_url}"
            raise AssertionError(
                msg,
            )
        if config.debug:
            msg = f"Expected False, got {config.debug}"
            raise AssertionError(msg)
        assert config.log_level == "INFO"

    def test_create_development_wms_config_partial_overrides(self) -> None:
        """Test creating development config with partial overrides."""
        config = create_development_wms_config(
            username="partial_user",
            custom_field="custom_value",
        )
        if config.auth.username != "partial_user":
            msg = f"Expected {'partial_user'}, got {config.auth.username}"
            raise AssertionError(
                msg,
            )
        assert config.auth.password == "test_password"  # Default preserved
        # Custom fields are not preserved in config structure
        config_dict = config.model_dump()
        if "custom_field" not in config_dict:
            msg = f"Expected {'custom_field'} in {config_dict}"
            raise AssertionError(msg)

    def test_create_production_wms_config_defaults(self) -> None:
        """Test creating production config with defaults."""
        # Production config with empty base_url should fail validation
        with pytest.raises(ValueError, match=".*base_url.*"):
            create_production_wms_config()

    def test_create_production_wms_config_overrides(self) -> None:
        """Test creating production config with overrides."""
        config = create_production_wms_config(
            username="prod_user",
            password="prod_pass",
            base_url="https://prod.oracle.com",
            debug=True,
            log_level="DEBUG",
        )
        if config.auth.username != "prod_user":
            msg = f"Expected {'prod_user'}, got {config.auth.username}"
            raise AssertionError(msg)
        assert config.auth.password == "prod_pass"
        if config.connection.base_url != "https://prod.oracle.com":
            msg = f"Expected {'https://prod.oracle.com'}, got {config.connection.base_url}"
            raise AssertionError(
                msg,
            )
        if not (config.debug):
            msg = f"Expected True, got {config.debug}"
            raise AssertionError(msg)
        if config.log_level != "DEBUG":
            msg = f"Expected {'DEBUG'}, got {config.log_level}"
            raise AssertionError(msg)

    def test_create_production_wms_config_security_defaults(self) -> None:
        """Test production config has secure defaults."""
        config = create_production_wms_config(
            username="prod_user",
            password="prod_pass",
            base_url="https://prod.oracle.com",
        )
        # Production should have secure defaults
        if not (config.connection.verify_ssl):
            msg = f"Expected True, got {config.connection.verify_ssl}"
            raise AssertionError(msg)
        if config.debug:
            msg = f"Expected False, got {config.debug}"
            raise AssertionError(msg)
        assert config.connection.timeout == 60  # Higher timeout for production
        if config.connection.max_retries != 5:  # More retries for production:
            msg = f"Expected {5}, got {config.connection.max_retries}"
            raise AssertionError(msg)

    def test_validate_wms_config_valid(self) -> None:
        """Test validation of valid WMS config."""
        config = create_development_wms_config(
            username="valid_user",
            password="valid_pass",
            base_url="https://valid.com",
        )
        result = validate_wms_config(config)
        assert result.success
        if not (result.data):
            msg = f"Expected True, got {result.data}"
            raise AssertionError(msg)

    def test_validate_wms_config_missing_username(self) -> None:
        """Test validation fails for missing username."""
        config = TapOracleWMSConfig.from_singer_config(
            {
                "username": "",
                "password": "valid_pass",
                "auth_method": "basic",
                "base_url": "https://valid.com",
                "timeout": 30,
                "max_retries": 3,
                "verify_ssl": False,
            },
        )
        result = validate_wms_config(config)
        assert not result.success
        assert result.error is not None
        if "Username is required" not in result.error:
            msg = f"Expected {'Username is required'} in {result.error}"
            raise AssertionError(msg)

    def test_validate_wms_config_missing_password(self) -> None:
        """Test validation fails for missing password."""
        config = TapOracleWMSConfig.from_singer_config(
            {
                "username": "valid_user",
                "password": "",
                "auth_method": "basic",
                "base_url": "https://valid.com",
                "timeout": 30,
                "max_retries": 3,
                "verify_ssl": False,
            },
        )
        result = validate_wms_config(config)
        assert not result.success
        assert result.error is not None
        if "Password is required" not in result.error:
            msg = f"Expected {'Password is required'} in {result.error}"
            raise AssertionError(msg)

    def test_validate_wms_config_missing_base_url(self) -> None:
        """Test validation fails for missing base URL."""
        # Create a valid config first
        config = TapOracleWMSConfig.from_singer_config(
            {
                "username": "valid_user",
                "password": "valid_pass",
                "auth_method": "basic",
                "base_url": "https://valid.com",
                "timeout": 30,
                "max_retries": 3,
                "verify_ssl": False,
            },
        )
        # Now test that validation catches empty base_url by modifying the config
        # Test validation logic with mock config since model is frozen

        mock_config = Mock()
        mock_config.auth.username = "valid_user"
        mock_config.auth.password = "valid_pass"
        mock_config.connection.base_url = ""
        config = mock_config
        result = validate_wms_config(config)
        assert not result.success
        assert result.error is not None
        if "Base URL is required" not in result.error:
            msg = f"Expected {'Base URL is required'} in {result.error}"
            raise AssertionError(msg)

    def test_validate_wms_config_exception_handling(self) -> None:
        """Test validation handles exceptions."""
        # Create a mock config that will cause validation to fail
        invalid_config = object()  # Not a TapOracleWMSConfig
        result = validate_wms_config(invalid_config)
        assert not result.success
        assert result.error is not None
        if "Configuration validation failed" not in result.error:
            msg = f"Expected {'Configuration validation failed'} in {result.error}"
            raise AssertionError(
                msg,
            )

    def test_simple_api_exports(self) -> None:
        """Test that simple API exports expected functions."""
        # Check that all expected functions are exported
        assert hasattr(simple_api, "setup_wms_tap")
        assert hasattr(simple_api, "create_development_wms_config")
        assert hasattr(simple_api, "create_production_wms_config")
        assert hasattr(simple_api, "validate_wms_config")
        assert hasattr(simple_api, "FlextResult")
        # Check __all__ list
        expected_exports = [
            "FlextResult",
            "create_development_wms_config",
            "create_production_wms_config",
            "setup_wms_tap",
            "validate_wms_config",
        ]
        for export in expected_exports:
            if export not in simple_api.__all__:
                msg = f"Expected {export} in {simple_api.__all__}"
                raise AssertionError(msg)

    def test_service_result_integration(self) -> None:
        """Test integration with FlextResult from flext-core."""
        # Test success case
        success_result = FlextResult.ok("test_data")
        assert success_result.success
        if success_result.data != "test_data":
            msg = f"Expected {'test_data'}, got {success_result.data}"
            raise AssertionError(msg)
        # Test failure case
        fail_result: FlextResult[None] = FlextResult.fail(
            "test_error",
        )
        assert not fail_result.success
        if fail_result.error != "test_error":
            msg = f"Expected {'test_error'}, got {fail_result.error}"
            raise AssertionError(msg)

    def test_config_from_singer_integration(self) -> None:
        """Test integration with Singer config format."""
        singer_config = {
            "username": "singer_user",
            "password": "singer_pass",
            "auth_method": "basic",
            "base_url": "https://singer.oracle.com",
            "timeout": 45,
            "max_retries": 4,
            "verify_ssl": True,
            "debug": True,
            "log_level": "INFO",
        }
        config = TapOracleWMSConfig.from_singer_config(singer_config)
        if config.auth.username != "singer_user":
            msg = f"Expected {'singer_user'}, got {config.auth.username}"
            raise AssertionError(
                msg,
            )
        assert config.auth.password == "singer_pass"
        if config.connection.base_url != "https://singer.oracle.com":
            msg = f"Expected {'https://singer.oracle.com'}, got {config.connection.base_url}"
            raise AssertionError(
                msg,
            )
        assert config.connection.timeout == 45
        if not (config.debug):
            msg = f"Expected True, got {config.debug}"
            raise AssertionError(msg)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

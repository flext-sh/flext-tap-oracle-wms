"""Test simple API functionality."""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License
from __future__ import annotations

import pytest
from flext_core import ServiceResult

from flext_tap_oracle_wms.config import TapOracleWMSConfig
from flext_tap_oracle_wms.simple_api import (
    create_development_wms_config,
    create_production_wms_config,
    setup_wms_tap,
    validate_wms_config,
)


class TestSimpleAPI:
    """Test simple API functionality."""

    def test_setup_wms_tap_without_config(self) -> None:
        """Test setup WMS tap without providing config."""
        result = setup_wms_tap()
        assert isinstance(result, ServiceResult)
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
        assert result.data == config

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
        assert "Username is required" in result.error

    def test_setup_wms_tap_exception_handling(self) -> None:
        """Test setup WMS tap handles exceptions."""
        # Create an invalid config that will cause an exception
        invalid_config = object()  # Not a TapOracleWMSConfig
        result = setup_wms_tap(invalid_config)
        assert not result.success
        assert result.error is not None
        assert "Failed to setup WMS tap" in result.error

    def test_create_development_wms_config_defaults(self) -> None:
        """Test creating development config with defaults."""
        config = create_development_wms_config()
        assert config.auth.username == "test_user"
        assert config.auth.password == "test_password"
        assert config.auth.auth_method == "basic"
        assert "test-wms.oracle.com" in config.connection.base_url
        assert config.connection.timeout == 30
        assert config.connection.max_retries == 3
        assert config.connection.verify_ssl is False
        assert config.debug is True
        assert config.log_level == "DEBUG"

    def test_create_development_wms_config_overrides(self) -> None:
        """Test creating development config with overrides."""
        config = create_development_wms_config(
            username="custom_user",
            password="custom_pass",
            base_url="https://custom.com",
            debug=False,
            log_level="INFO",
        )
        assert config.auth.username == "custom_user"
        assert config.auth.password == "custom_pass"
        assert config.connection.base_url == "https://custom.com"
        assert config.debug is False
        assert config.log_level == "INFO"

    def test_create_development_wms_config_partial_overrides(self) -> None:
        """Test creating development config with partial overrides."""
        config = create_development_wms_config(
            username="partial_user",
            custom_field="custom_value",
        )
        assert config.auth.username == "partial_user"
        assert config.auth.password == "test_password"  # Default preserved
        # Custom fields are not preserved in config structure
        config_dict = config.model_dump()
        assert "custom_field" not in config_dict

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
        assert config.auth.username == "prod_user"
        assert config.auth.password == "prod_pass"
        assert config.connection.base_url == "https://prod.oracle.com"
        assert config.debug is True
        assert config.log_level == "DEBUG"

    def test_create_production_wms_config_security_defaults(self) -> None:
        """Test production config has secure defaults."""
        config = create_production_wms_config(
            username="prod_user",
            password="prod_pass",
            base_url="https://prod.oracle.com",
        )
        # Production should have secure defaults
        assert config.connection.verify_ssl is True
        assert config.debug is False
        assert config.connection.timeout == 60  # Higher timeout for production
        assert config.connection.max_retries == 5  # More retries for production

    def test_validate_wms_config_valid(self) -> None:
        """Test validation of valid WMS config."""
        config = create_development_wms_config(
            username="valid_user",
            password="valid_pass",
            base_url="https://valid.com",
        )
        result = validate_wms_config(config)
        assert result.success
        assert result.data is True

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
        assert "Username is required" in result.error

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
        assert "Password is required" in result.error

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
        from unittest.mock import Mock

        mock_config = Mock()
        mock_config.auth.username = "valid_user"
        mock_config.auth.password = "valid_pass"
        mock_config.connection.base_url = ""
        config = mock_config
        result = validate_wms_config(config)
        assert not result.success
        assert result.error is not None
        assert "Base URL is required" in result.error

    def test_validate_wms_config_exception_handling(self) -> None:
        """Test validation handles exceptions."""
        # Create a mock config that will cause validation to fail
        invalid_config = object()  # Not a TapOracleWMSConfig
        result = validate_wms_config(invalid_config)
        assert not result.success
        assert result.error is not None
        assert "Configuration validation failed" in result.error

    def test_simple_api_exports(self) -> None:
        """Test that simple API exports expected functions."""
        from flext_tap_oracle_wms import simple_api

        # Check that all expected functions are exported
        assert hasattr(simple_api, "setup_wms_tap")
        assert hasattr(simple_api, "create_development_wms_config")
        assert hasattr(simple_api, "create_production_wms_config")
        assert hasattr(simple_api, "validate_wms_config")
        assert hasattr(simple_api, "ServiceResult")
        # Check __all__ list
        expected_exports = [
            "ServiceResult",
            "create_development_wms_config",
            "create_production_wms_config",
            "setup_wms_tap",
            "validate_wms_config",
        ]
        for export in expected_exports:
            assert export in simple_api.__all__

    def test_service_result_integration(self) -> None:
        """Test integration with ServiceResult from flext-core."""
        # Test success case
        success_result = ServiceResult.ok("test_data")
        assert success_result.success
        assert success_result.data == "test_data"
        # Test failure case
        fail_result: ServiceResult[None] = ServiceResult.fail("test_error",
        )
        assert not fail_result.success
        assert fail_result.error == "test_error"

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
        assert config.auth.username == "singer_user"
        assert config.auth.password == "singer_pass"
        assert config.connection.base_url == "https://singer.oracle.com"
        assert config.connection.timeout == 45
        assert config.debug is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

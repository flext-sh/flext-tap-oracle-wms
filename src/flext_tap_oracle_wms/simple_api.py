"""Simple API for FLEXT tap-oracle-wms setup and configuration.

Provides a simple interface for setting up Oracle WMS data extraction.
"""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

# Use centralized ServiceResult from flext-core - ELIMINATE DUPLICATION
from flext_core.domain.types import ServiceResult

from flext_tap_oracle_wms.config import TapOracleWMSConfig
from flext_tap_oracle_wms.config import WMSAuthConfig
from flext_tap_oracle_wms.config import WMSConnectionConfig


def setup_wms_tap(
    config: TapOracleWMSConfig | None = None,
) -> ServiceResult[TapOracleWMSConfig]:
    """Set up WMS tap with configuration.

    Args:
        config: WMS tap configuration

    Returns:
        ServiceResult containing the configuration

    """
    try:
        if config is None:
            # Create default configuration
            config = create_development_wms_config()

        # Basic validation
        config_dict = config.model_dump()
        if not config_dict.get("auth", {}).get("username"):
            return ServiceResult.fail("Username is required for WMS authentication")

        return ServiceResult.ok(config)

    except (ValueError, TypeError, AttributeError) as e:
        return ServiceResult.fail(f"Failed to setup WMS tap: {e}")


def create_development_wms_config(**overrides: object) -> TapOracleWMSConfig:
    """Create development configuration for WMS tap.

    Args:
        **overrides: Configuration overrides

    Returns:
        Configured TapOracleWMSConfig for development use

    """
    # Development defaults
    defaults = {
        "auth": WMSAuthConfig(
            username=str(overrides.get("username", "test_user")),
            password=str(overrides.get("password", "test_password")),
            auth_method="basic",
        ),
        "connection": WMSConnectionConfig(
            base_url=str(overrides.get("base_url", "https://test-wms.oracle.com")),
            timeout=30,
            max_retries=3,
            verify_ssl=False,  # Development setting
        ),
        "debug": True,
        "log_level": "DEBUG",
    }

    # Override with provided values
    # These are handled above
    defaults.update(
        {
            key: value
            for key, value in overrides.items()
            if key not in {"username", "password", "base_url"}
        },
    )

    return TapOracleWMSConfig.from_singer_config(defaults)


def create_production_wms_config(**overrides: object) -> TapOracleWMSConfig:
    """Create production configuration for WMS tap.

    Args:
        **overrides: Configuration overrides

    Returns:
        Configured TapOracleWMSConfig for production use

    """
    # Production defaults
    defaults = {
        "auth": WMSAuthConfig(
            username=str(overrides.get("username", "")),
            password=str(overrides.get("password", "")),
            auth_method="basic",
        ),
        "connection": WMSConnectionConfig(
            base_url=str(overrides.get("base_url", "")),
            timeout=60,
            max_retries=5,
            verify_ssl=True,  # Production setting
        ),
        "debug": False,
        "log_level": "INFO",
    }

    # Override with provided values
    # These are handled above
    defaults.update(
        {
            key: value
            for key, value in overrides.items()
            if key not in {"username", "password", "base_url"}
        },
    )

    return TapOracleWMSConfig.from_singer_config(defaults)


def validate_wms_config(config: TapOracleWMSConfig) -> ServiceResult[bool]:
    """Validate WMS configuration.

    Args:
        config: Configuration to validate

    Returns:
        ServiceResult indicating validation success

    """
    try:
        # Validate using Pydantic validation
        config.model_validate(config.model_dump())

        # Additional business validation
        if not config.auth.username:
            return ServiceResult.fail("Username is required")

        if not config.auth.password:
            return ServiceResult.fail("Password is required")

        if not config.connection.base_url:
            return ServiceResult.fail("Base URL is required")

        return ServiceResult.ok(data=True)

    except (ValueError, TypeError, AttributeError) as e:
        return ServiceResult.fail(f"Configuration validation failed: {e}")


# Export convenience functions
__all__ = [
    "ServiceResult",
    "create_development_wms_config",
    "create_production_wms_config",
    "setup_wms_tap",
    "validate_wms_config",
]

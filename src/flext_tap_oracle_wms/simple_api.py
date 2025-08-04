"""Simple API for FLEXT tap-oracle-wms setup and configuration.

Copyright (c) 2025 FLEXT Team
Licensed under the MIT License

Provides a simple interface for setting up Oracle WMS data extraction.
"""

from __future__ import annotations

from typing import Any, cast

from flext_core import (
    FlextResult,
    TAnyDict,
)

from flext_tap_oracle_wms.config import TapOracleWMSConfig


def setup_wms_tap(
    config: TapOracleWMSConfig | None = None,
) -> FlextResult[Any]:
    """Set up WMS tap with configuration.

    Args:
        config: WMS tap configuration

    Returns:
        FlextResult containing the configuration

    """
    try:
        if config is None:
            # Create default configuration
            config = create_development_wms_config()

        # Basic validation
        config_dict = config.model_dump()
        if not config_dict.get("auth", {}).get("username"):
            return FlextResult.fail(
                "Username is required for WMS authentication",
            )

        return FlextResult.ok(config)

    except (ValueError, TypeError, AttributeError) as e:
        return FlextResult.fail(f"Failed to setup WMS tap: {e}")


def create_development_wms_config(**overrides: object) -> TapOracleWMSConfig:
    """Create development configuration for WMS tap.

    Args:
        **overrides: Configuration overrides

    Returns:
        Configured TapOracleWMSConfig for development use

    """
    # Development defaults
    defaults = {
        "username": str(overrides.get("username", "test_user")),
        "password": str(overrides.get("password", "test_password")),
        "base_url": str(overrides.get("base_url", "https://test-wms.oracle.com")),
        "auth_method": "basic",
        "timeout": 30,
        "max_retries": 3,
        "verify_ssl": False,  # Development setting
        "debug": True,
        "log_level": "DEBUG",
    }

    # Override with provided values
    defaults.update(overrides)

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
        "username": str(overrides.get("username", "")),
        "password": str(overrides.get("password", "")),
        "base_url": str(overrides.get("base_url", "")),
        "auth_method": "basic",
        "timeout": 60,
        "max_retries": 5,
        "verify_ssl": True,  # Production setting
        "debug": False,
        "log_level": "INFO",
    }

    # Override with provided values
    defaults.update(
        dict(overrides.items()),
    )

    return TapOracleWMSConfig.from_singer_config(defaults)


def validate_wms_config(config: TapOracleWMSConfig) -> FlextResult[Any]:
    """Validate WMS configuration.

    Args:
        config: Configuration to validate

    Returns:
        FlextResult indicating validation success

    """
    try:
        # Validate using Pydantic validation
        config.model_validate(config.model_dump())

        # Additional business validation
        if not config.username:
            return FlextResult.fail("Username is required")

        if not config.password:
            return FlextResult.fail("Password is required")

        if not config.host:
            return FlextResult.fail("Host is required")

        return FlextResult.ok(data=True)

    except (ValueError, TypeError, AttributeError) as e:
        return FlextResult.fail(
            f"Configuration validation failed: {e}",
        )


# Export convenience functions
__all__: list[str] = [
    "FlextResult",
    "create_development_wms_config",
    "create_production_wms_config",
    "setup_wms_tap",
    "validate_wms_config",
]

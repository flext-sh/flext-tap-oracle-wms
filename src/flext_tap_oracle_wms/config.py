"""Configuration for tap-oracle-wms using flext-core centralized models.

REFACTORED from original config.py to use flext-core semantic models:
- Uses FlextOracleConfig, FlextSingerConfig, FlextDatabaseConfig from flext-core
- Eliminates code duplication through centralized configuration patterns
- Provides type-safe configuration with comprehensive validation
- Implements factory functions for configuration creation
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from typing import cast

# Import centralized configuration models from flext-core
from flext_core import (
    FlextDataIntegrationConfig,
    # Configuration models from flext-core
    FlextOracleConfig,
    FlextSingerConfig,
    # TypedDict definitions
    TAnyDict,
    create_oracle_config,
)
from pydantic import Field, field_validator

# =============================================================================
# ORACLE WMS SPECIFIC CONFIGURATION - Extends flext-core patterns
# =============================================================================


class OracleWMSTapConfig(FlextDataIntegrationConfig):
    """Oracle WMS Tap configuration extending flext-core data integration patterns.

    REFACTORED: Extends FlextDataIntegrationConfig instead of defining custom classes.
    Eliminates duplication by using centralized configuration patterns from flext-core.
    """

    # Oracle WMS specific configuration
    company_code: str = Field(default="*", description="WMS company code filter")
    facility_code: str = Field(default="*", description="WMS facility code filter")
    wms_api_version: str = Field(default="v10", description="Oracle WMS API version")

    # Entity configuration - extends base configuration
    entities: list[str] = Field(
        default_factory=list,
        description="List of WMS entities to extract",
    )
    entity_filters: dict[str, dict[str, str]] = Field(
        default_factory=dict,
        description="Entity-specific filtering criteria",
    )

    # WMS pagination and extraction settings
    page_mode: str = Field(
        default="sequenced",
        description="WMS pagination mode (sequenced or paged)",
    )

    @field_validator("page_mode")
    @classmethod
    def validate_page_mode(cls, v: str) -> str:
        """Validate page mode is supported by Oracle WMS."""
        valid_modes = ["sequenced", "paged"]
        if v not in valid_modes:
            msg = f"Page mode must be one of: {valid_modes}"
            raise ValueError(msg)
        return v

    @field_validator("wms_api_version")
    @classmethod
    def validate_api_version(cls, v: str) -> str:
        """Validate WMS API version format."""
        if not v.startswith("v") or not v[1:].isdigit():
            msg = "API version must be in format 'v{number}' (e.g., 'v10')"
            raise ValueError(msg)
        return v


# =============================================================================
# MAIN CONFIGURATION CLASS - Uses flext-core semantic models
# =============================================================================


class TapOracleWMSConfig(OracleWMSTapConfig):
    """Main configuration for Oracle WMS tap using flext-core centralized patterns.

    REFACTORED: Inherits from OracleWMSTapConfig which extends FlextDataIntegrationConfig.
    Eliminates all configuration duplication by using flext-core semantic models.
    """

    # WMS connection details
    host: str = Field(description="Oracle WMS host")
    username: str = Field(description="Oracle WMS username")
    password: str = Field(description="Oracle WMS password")
    port: int = Field(default=1521, description="Oracle port")
    service_name: str = Field(description="Oracle service name")

    def get_oracle_config(self) -> FlextOracleConfig:
        """Get Oracle configuration using flext-core factory patterns.

        Returns:
            FlextOracleConfig instance for Oracle connectivity

        """
        return create_oracle_config(
            host=self.host,
            username=self.username,
            password=self.password,
            service_name=self.service_name,
            port=self.port,
        )

    def get_wms_specific_config(self) -> dict[str, object]:
        """Get WMS-specific configuration parameters.

        Returns:
            Dictionary containing WMS-specific configuration

        """
        return {
            "company_code": self.company_code,
            "facility_code": self.facility_code,
            "wms_api_version": self.wms_api_version,
            "page_mode": self.page_mode,
            "entities": self.entities,
            "entity_filters": self.entity_filters,
        }

    def to_singer_config(self) -> TAnyDict:
        """Convert to Singer protocol configuration format using flext-core patterns.

        Returns:
            Dictionary containing Singer-compatible configuration

        """
        # Use flext-core configuration serialization patterns
        self.model_dump()

        # Create Singer-compatible configuration
        singer_config: TAnyDict = {
            "host": self.host,
            "username": self.username,
            "password": self.password,
            "port": self.port,
            "service_name": self.service_name,
            "company_code": self.company_code,
            "facility_code": self.facility_code,
            "wms_api_version": self.wms_api_version,
            "page_mode": self.page_mode,
            "entities": self.entities,
            "entity_filters": self.entity_filters,
            "batch_size": self.batch_size,
            "parallel_workers": self.parallel_workers,
        }

        return singer_config

    @classmethod
    def from_singer_config(cls, config: TAnyDict) -> TapOracleWMSConfig:
        """Create configuration from Singer protocol format using flext-core patterns.

        Args:
            config: Dictionary containing Singer configuration

        Returns:
            TapOracleWMSConfig instance created from Singer config

        REFACTORED: Uses flext-core configuration creation patterns instead of manual construction.

        """
        # Use flext-core factory patterns for Oracle configuration
        oracle_config = create_oracle_config(
            {
                "host": cast("str", config["base_url"]),
                "username": cast("str", config["username"]),
                "password": cast("str", config["password"]),
                "timeout": cast("int", config.get("timeout", 30)),
                "max_retries": cast("int", config.get("max_retries", 3)),
                "verify_ssl": cast("bool", config.get("verify_ssl", True)),
            },
        )

        # Create Singer configuration using flext-core patterns
        singer_config = FlextSingerConfig(
            state_file=cast("str", config.get("state_file"))
            if config.get("state_file")
            else None,
            catalog_file=cast("str", config.get("catalog_file"))
            if config.get("catalog_file")
            else None,
        )

        # Create main configuration using centralized patterns
        return cls(
            # Connection from Oracle config
            connection=oracle_config.connection,
            authentication=oracle_config.authentication,
            # WMS-specific configuration
            company_code=cast("str", config.get("company_code", "*")),
            facility_code=cast("str", config.get("facility_code", "*")),
            wms_api_version=cast("str", config.get("wms_api_version", "v10")),
            page_mode=cast("str", config.get("page_mode", "sequenced")),
            entities=cast("list[str]", config.get("entities", [])),
            entity_filters=cast(
                "dict[str, dict[str, str]]",
                config.get("entity_filters", {}),
            ),
            # Extraction configuration
            extraction={
                "page_size": cast("int", config.get("page_size", 1000)),
                "batch_size": cast("int", config.get("batch_size", 1000)),
                "start_date": cast("str", config.get("start_date"))
                if config.get("start_date")
                else None,
            },
            # Singer protocol configuration
            singer_config=singer_config,
        )


# =============================================================================
# FACTORY FUNCTIONS - Using flext-core patterns
# =============================================================================


def create_wms_tap_config(config_dict: TAnyDict) -> TapOracleWMSConfig:
    """Factory function to create Oracle WMS tap configuration using flext-core patterns.

    Args:
        config_dict: Configuration dictionary

    Returns:
        Validated Oracle WMS tap configuration

    REFACTORED: Uses flext-core factory patterns instead of manual construction.

    """
    return TapOracleWMSConfig.from_singer_config(config_dict)


def get_wms_config_schema() -> dict[str, object]:
    """Get JSON schema for Oracle WMS tap configuration.

    Returns:
        JSON schema dictionary for configuration validation

    """
    return TapOracleWMSConfig.model_json_schema()


# =============================================================================
# EXPORTS - Centralized configuration classes
# =============================================================================

__all__ = [
    "OracleWMSTapConfig",
    # Main configuration class
    "TapOracleWMSConfig",
    # Factory functions
    "create_wms_tap_config",
    "get_wms_config_schema",
]

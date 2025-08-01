"""Configuration for tap-oracle-wms using flext-core patterns.

REFACTORED:
Uses flext-core base models for declarative configuration.
Zero tolerance for code duplication.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from typing import Any

# Use FlextBaseSettings from flext-core
from flext_core import FlextBaseSettings
from pydantic import BaseModel, Field, field_validator


def _default_discovery_config() -> WMSDiscoveryConfig:
    """Create default discovery configuration.

    Returns:
        Default WMSDiscoveryConfig instance

    """
    return WMSDiscoveryConfig()


def _default_extraction_config() -> WMSExtractionConfig:
    """Create default extraction configuration.

    Returns:
        Default WMSExtractionConfig instance with start_date=None

    """
    return WMSExtractionConfig(start_date=None)


# Simple auth config using BaseModel
class WMSAuthConfig(BaseModel):
    """WMS authentication configuration using consolidated patterns."""

    username: str = Field(..., description="WMS username")
    password: str = Field(..., description="WMS password")
    auth_method: str = Field(default="basic", description="Authentication method")


# Simple connection config using BaseModel
class WMSConnectionConfig(BaseModel):
    """WMS connection configuration using consolidated patterns."""

    base_url: str = Field(
        ...,
        description="Oracle WMS base URL",
    )
    verify_ssl: bool = Field(
        default=True,
        description="Verify SSL certificates",
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries",
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url_field(cls, v: str) -> str:
        """Validate base URL format."""
        if not v.startswith(("http://", "https://")):
            msg = "Base URL must start with http:// or https://"
            raise ValueError(msg)
        return v


class WMSDiscoveryConfig(BaseModel):
    """WMS entity discovery configuration value object."""

    auto_discover: bool = Field(
        default=True,
        description="Enable automatic entity discovery",
    )
    entity_filter: list[str] = Field(
        default_factory=list,
        description="List of entities to include (empty = all)",
    )
    exclude_entities: list[str] = Field(
        default_factory=list,
        description="List of entities to exclude",
    )
    include_metadata: bool = Field(
        default=True,
        description="Include entity metadata in discovery",
    )
    max_entities: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum entities to discover",
    )


class WMSExtractionConfig(BaseModel):
    """WMS data extraction configuration value object."""

    page_size: int = Field(
        default=500,
        ge=1,
        le=10000,
        description="Records per page",
    )
    company_code: str = Field(
        default="*",
        description="WMS company code filter",
    )
    facility_code: str = Field(
        default="*",
        description="WMS facility code filter",
    )
    start_date: str | None = Field(
        None,
        description="Start date for incremental extraction (ISO format)",
    )
    batch_size: int = Field(
        default=1000,
        ge=1,
        le=50000,
        description="Batch size for bulk operations",
    )


class TapOracleWMSConfig(FlextBaseSettings):
    """Main configuration for Oracle WMS tap using flext-core patterns."""

    # Authentication
    auth: WMSAuthConfig = Field(
        ...,
        description="Authentication configuration",
    )

    # Connection
    connection: WMSConnectionConfig = Field(
        ...,
        description="Connection configuration",
    )

    # Discovery
    discovery: WMSDiscoveryConfig = Field(
        default_factory=_default_discovery_config,
        description="Entity discovery configuration",
    )

    # Extraction
    extraction: WMSExtractionConfig = Field(
        default_factory=_default_extraction_config,
        description="Data extraction configuration",
    )

    # Singer protocol settings
    state_file: str | None = Field(
        None,
        description="Path to state file for incremental sync",
    )
    catalog_file: str | None = Field(
        None,
        description="Path to catalog file",
    )

    # Debugging and logging
    debug: bool = Field(
        default=False,
        description="Enable debug logging",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level_field(cls, v: str) -> str:
        """Validate log level format."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            msg = f"Invalid log level: {v}. Must be one of: {valid_levels}"
            raise ValueError(msg)
        return v.upper()

    def to_singer_config(self) -> dict[str, object]:
        """Convert to Singer protocol configuration format.

        Returns:
            Dictionary containing Singer-compatible configuration

        """
        return {
            "base_url": self.connection.base_url,
            "username": self.auth.username,
            "password": self.auth.password,
            "auth_method": self.auth.auth_method,
            "timeout": self.connection.timeout,
            "max_retries": self.connection.max_retries,
            "verify_ssl": self.connection.verify_ssl,
            "page_size": self.extraction.page_size,
            "company_code": self.extraction.company_code,
            "facility_code": self.extraction.facility_code,
            "auto_discover": self.discovery.auto_discover,
            "entity_filter": self.discovery.entity_filter,
            "exclude_entities": self.discovery.exclude_entities,
            "include_metadata": self.discovery.include_metadata,
            "max_entities": self.discovery.max_entities,
            "start_date": self.extraction.start_date,
            "batch_size": self.extraction.batch_size,
            "debug": self.debug,
            "log_level": self.log_level,
        }

    @classmethod
    def from_singer_config(cls, config: dict[str, object]) -> TapOracleWMSConfig:
        """Create configuration from Singer protocol format.

        Args:
            config: Dictionary containing Singer configuration

        Returns:
            TapOracleWMSConfig instance created from Singer config

        """
        return cls(
            auth=WMSAuthConfig(
                username=config["username"],
                password=config["password"],
                auth_method=config.get("auth_method", "basic"),
            ),
            connection=WMSConnectionConfig(
                base_url=config["base_url"],
                timeout=config.get("timeout", 30),
                max_retries=config.get("max_retries", 3),
                verify_ssl=config.get("verify_ssl", True),
            ),
            discovery=WMSDiscoveryConfig(
                auto_discover=config.get("auto_discover", True),
                entity_filter=config.get("entity_filter", []),
                exclude_entities=config.get("exclude_entities", []),
                include_metadata=config.get("include_metadata", True),
                max_entities=config.get("max_entities", 100),
            ),
            extraction=WMSExtractionConfig(
                page_size=config.get("page_size", 500),
                company_code=config.get("company_code", "*"),
                facility_code=config.get("facility_code", "*"),
                batch_size=config.get("batch_size", 1000),
                start_date=config.get("start_date") if "start_date" in config else None,
            ),
            state_file=config.get("state_file"),
            catalog_file=config.get("catalog_file"),
            debug=config.get("debug", False),
            log_level=config.get("log_level", "INFO"),
        )


# Export configuration classes
__all__ = [
    "TapOracleWMSConfig",
    "WMSAuthConfig",
    "WMSConnectionConfig",
    "WMSDiscoveryConfig",
    "WMSExtractionConfig",
]

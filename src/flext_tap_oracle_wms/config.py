"""Configuration for tap-oracle-wms using flext-core patterns.

REFACTORED:
Uses flext-core base models for declarative configuration.
Zero tolerance for code duplication.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from typing import Any

# 🚨 ARCHITECTURAL COMPLIANCE: Using DI container
from flext_tap_oracle_wms.infrastructure.di_container import (
    get_base_config,
    get_domain_entity,
    get_domain_value_object,
    get_field,
    get_service_result,
)

ServiceResult = get_service_result()
DomainEntity = get_domain_entity()
Field = get_field()
DomainValueObject = get_domain_value_object()
BaseConfig = get_base_config()
from pydantic import Field, field_validator


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


class WMSAuthConfig(DomainValueObject):
    """WMS authentication configuration value object."""

    username: str = Field(
        ...,
        description="Authentication username",
    )
    password: str = Field(
        ...,
        description="Authentication password",
        json_schema_extra={"secret": True},
    )
    auth_method: str = Field(
        "basic",
        description="Authentication method (basic, token, oauth)",
    )

    @field_validator("auth_method")
    @classmethod
    def validate_auth_method(cls, v: str) -> str:
        """Validate authentication method.

        Args:
            v: Authentication method to validate

        Returns:
            Validated authentication method

        Raises:
            ValueError: If authentication method is not supported

        """
        allowed = {"basic", "token", "oauth"}
        if v not in allowed:
            msg = f"Invalid auth_method: {v}. Must be one of {allowed}"
            raise ValueError(msg)
        return v


class WMSConnectionConfig(DomainValueObject):
    """WMS connection configuration value object."""

    base_url: str = Field(
        ...,
        description="Oracle WMS base URL",
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts",
    )
    verify_ssl: bool = Field(
        default=True,
        description="Verify SSL certificates",
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format.

        Args:
            v: Base URL to validate

        Returns:
            Validated and normalized base URL

        Raises:
            ValueError: If URL format is invalid

        """
        if not v.startswith(("http://", "https://")):
            msg = f"Invalid base_url: {v}. Must start with http:// or https://"
            raise ValueError(msg)
        return v.rstrip("/")


class WMSDiscoveryConfig(DomainValueObject):
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


class WMSExtractionConfig(DomainValueObject):
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


class TapOracleWMSConfig(DomainBaseModel):
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
    def validate_log_level(cls, v: str) -> str:
        """Validate logging level.

        Args:
            v: Log level to validate

        Returns:
            Validated and normalized log level

        Raises:
            ValueError: If log level is not supported

        """
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            msg = f"Invalid log_level: {v}. Must be one of {allowed}"
            raise ValueError(msg)
        return v.upper()

    def to_singer_config(self) -> dict[str, Any]:
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
    def from_singer_config(cls, config: dict[str, Any]) -> TapOracleWMSConfig:
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

"""Configuration management for FLEXT Tap Oracle WMS.

Type-safe configuration using FLEXT patterns with Pydantic validation.
Consolidates configuration management and constants following PEP8 patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Final, Self

from flext_core import (
    FlextConstants,
    FlextResult,
    FlextSettings,
    t,
)
from flext_oracle_wms import (
    FlextOracleWmsConstants as _WmsConstants,
)
from pydantic import AnyUrl, Field, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict


class FlextTapOracleWmsConstants(FlextConstants):
    """Constants for Oracle WMS tap configuration - consuming from flext-oracle-wms API."""

    # API defaults from flext-oracle-wms (using available constants)
    DEFAULT_API_VERSION: Final[str] = str(_WmsConstants.API_CONFIG["version_default"])

    # Validation limits - using FlextConstants as SOURCE OF TRUTH
    MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT: Final[int] = 5
    # DEFAULT_PAGE_SIZE: Final[int] = _WmsConstants.DEFAULT_PAGE_SIZE - Removed to avoid override conflict
    # DEFAULT_TIMEOUT: Final[int] = _WmsConstants.Api.DEFAULT_TIMEOUT - Removed
    DEFAULT_MAX_RETRIES: Final[int] = 3
    DEFAULT_RETRY_DELAY: Final[float] = 1.0  # Standard retry delay

    # Pagination limits (hardcoded since not available in nested structure)
    # MIN_PAGE_SIZE: Final[int] = 1 - Removed
    # MAX_PAGE_SIZE: Final[int] = 1000 - Removed
    MIN_TIMEOUT: Final[int] = 1  # Singer-specific minimum
    MAX_TIMEOUT: Final[int] = 300  # Singer-specific maximum

    # Discovery settings (hardcoded since not available)

    DEFAULT_DISCOVERY_SAMPLE_SIZE: Final[int] = 100
    MAX_DISCOVERY_SAMPLE_SIZE: Final[int] = (
        FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE
    )  # Singer-specific maximum


class FlextTapOracleWmsSettings(FlextSettings):
    """Configuration for Oracle WMS tap.

    Type-safe configuration with validation for Oracle WMS data extraction.
    Follows FLEXT patterns using FlextSettings for complete validation.
    """

    # Connection settings
    base_url: AnyUrl = Field(
        ...,
        description="Oracle WMS base URL",
        examples=["https://wms.example.com/api"],
    )
    username: str = Field(
        ...,
        description="Oracle WMS username",
        min_length=1,
    )
    password: SecretStr = Field(
        ...,
        description="Oracle WMS password",
    )

    # API settings
    api_version: str = Field(
        default="v1",
        description="Oracle WMS API version",
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
        ge=FlextTapOracleWmsConstants.MIN_TIMEOUT,
        le=FlextTapOracleWmsConstants.MAX_TIMEOUT,
    )

    max_retries: int = Field(
        default=FlextTapOracleWmsConstants.DEFAULT_MAX_RETRIES,
        description="Maximum number of retries for failed requests",
        ge=0,
        le=10,
    )
    retry_delay_seconds: float = Field(
        default=FlextTapOracleWmsConstants.DEFAULT_RETRY_DELAY,
        description="Delay between retries in seconds",
        ge=0.1,
        le=60.0,
    )

    # Pagination settings
    page_size: int = Field(
        default=FlextTapOracleWmsConstants.DEFAULT_PAGE_SIZE,
        description="Number of records per page",
        ge=FlextTapOracleWmsConstants.MIN_PAGE_SIZE,
        le=FlextTapOracleWmsConstants.MAX_PAGE_SIZE,
    )

    # SSL settings
    verify_ssl: bool = Field(
        default=True,
        description="Verify SSL certificates",
    )
    ssl_cert_path: str | None = Field(
        default=None,
        description="Path to SSL certificate file",
    )

    # Stream selection
    include_entities: list[str] | None = Field(
        default=None,
        description="List of entities to include (default: all)",
    )
    exclude_entities: list[str] | None = Field(
        default=None,
        description="List of entities to exclude",
    )

    # Discovery settings
    discovery_sample_size: int = Field(
        default=FlextTapOracleWmsConstants.DEFAULT_DISCOVERY_SAMPLE_SIZE,
        description="Number of records to sample for schema discovery",
        ge=1,
        le=FlextTapOracleWmsConstants.MAX_DISCOVERY_SAMPLE_SIZE,
    )
    enable_schema_flattening: bool = Field(
        default=True,
        description="Enable flattening of nested structures",
    )
    max_flattening_depth: int = Field(
        default=FlextConstants.Reliability.MAX_RETRY_ATTEMPTS,  # 3
        description="Maximum depth for schema flattening",
        ge=0,
        le=10,
    )

    # Rate limiting
    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable rate limiting",
    )
    max_requests_per_minute: int = Field(
        default=60,
        description="Maximum requests per minute",
        ge=1,
        le=1000,
    )

    # Advanced settings
    user_agent: str | None = Field(
        default=None,
        description="Custom User-Agent header",
    )
    additional_headers: Mapping[str, str] | None = Field(
        default=None,
        description="Additional HTTP headers",
    )

    # Column filtering
    column_mappings: Mapping[str, Mapping[str, str]] | None = Field(
        default=None,
        description="Column name mappings per stream",
    )
    ignored_columns: list[str] | None = Field(
        default=None,
        description="Columns to ignore globally",
    )

    # Replication settings
    start_date: str | None = Field(
        default=None,
        description="Start date for incremental replication (ISO format)",
    )
    end_date: str | None = Field(
        default=None,
        description="End date for data extraction (ISO format)",
    )

    # API settings
    enable_request_logging: bool = Field(
        default=False,
        description="Enable detailed request/response logging",
    )

    # Performance settings
    enable_parallel_extraction: bool = Field(
        default=False,
        description="Enable parallel stream extraction",
    )
    max_parallel_streams: int = Field(
        default=FlextConstants.Reliability.MAX_RETRY_ATTEMPTS,  # 3
        description="Maximum number of parallel streams",
        ge=1,
        le=10,
    )

    # Validation settings
    validate_config: bool = Field(
        default=True,
        description="Validate configuration on startup",
    )
    validate_schemas: bool = Field(
        default=True,
        description="Validate record schemas during extraction",
    )

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_TAP_ORACLE_WMS_",
        case_sensitive=False,
        extra="ignore",
        str_strip_whitespace=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        frozen=False,
    )

    @classmethod
    def get_or_create_shared_instance(
        cls,
        project_name: str,
        **overrides: t.GeneralValueType,
    ) -> Self:
        """Create or return a shared instance for this project."""
        _ = project_name
        init_kwargs: dict[str, Any] = overrides
        return cls(**init_kwargs)

    @classmethod
    def get_global_instance(cls) -> Self:
        """Return the global singleton settings instance."""
        return cls.get_or_create_shared_instance(project_name="flext-tap-oracle-wms")

    @classmethod
    def create_for_development(cls, **overrides: t.GeneralValueType) -> Self:
        """Create configuration for development environment."""
        dev_overrides = {
            "timeout": FlextConstants.Network.DEFAULT_TIMEOUT * 2,
            "max_retries": FlextConstants.Reliability.MAX_RETRY_ATTEMPTS + 2,
            "page_size": FlextTapOracleWmsConstants.DEFAULT_PAGE_SIZE // 2,
            "enable_request_logging": True,
            "enable_parallel_extraction": True,
            **overrides,
        }
        return cls.get_or_create_shared_instance(
            project_name="flext-tap-oracle-wms",
            **dev_overrides,
        )

    @classmethod
    def create_for_production(cls, **overrides: t.GeneralValueType) -> Self:
        """Create configuration for production environment."""
        prod_overrides = {
            "timeout": FlextConstants.Network.DEFAULT_TIMEOUT,
            "max_retries": FlextConstants.Reliability.MAX_RETRY_ATTEMPTS,
            "page_size": FlextTapOracleWmsConstants.DEFAULT_PAGE_SIZE,
            "enable_request_logging": False,
            "enable_parallel_extraction": False,
            **overrides,
        }
        return cls.get_or_create_shared_instance(
            project_name="flext-tap-oracle-wms",
            **prod_overrides,
        )

    @classmethod
    def create_for_testing(cls, **overrides: t.GeneralValueType) -> Self:
        """Create configuration for testing environment."""
        test_overrides = {
            "timeout": FlextConstants.Network.DEFAULT_TIMEOUT // 3,
            "max_retries": 1,
            "page_size": FlextTapOracleWmsConstants.MIN_PAGE_SIZE,
            "enable_request_logging": True,
            "enable_parallel_extraction": True,
            **overrides,
        }
        return cls.get_or_create_shared_instance(
            project_name="flext-tap-oracle-wms",
            **test_overrides,
        )

    @field_validator("include_entities", "exclude_entities")
    @classmethod
    def validate_entity_lists(
        cls,
        v: list[str] | None,
    ) -> list[str] | None:
        """Validate entity lists are unique."""
        if v is not None:
            unique_entities = list(dict.fromkeys(v))
            if len(unique_entities) != len(v):
                msg = "Entity list contains duplicates"
                raise ValueError(msg)
        return v

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, v: str | None) -> str | None:
        """Validate date fields using ISO-8601 compatible parsing."""
        if v is not None:
            normalized = v.replace("Z", "+00:00")
            try:
                datetime.fromisoformat(normalized)
            except ValueError as exc:
                msg = f"Invalid date format: {v}"
                raise ValueError(msg) from exc
        return v

    def validate_business_rules(self) -> FlextResult[bool]:
        """Validate Oracle WMS tap configuration business rules using FlextSettings pattern.

        Consolidates all validation logic into a single complete method.

        """
        # Run all validations
        validations = [
            self._validate_required_fields(),
            self._validate_url_format(),
            self._validate_page_size(),
            self._validate_timeout(),
            self._validate_entity_settings(),
            self._validate_date_range(),
            self._validate_performance_settings(),
        ]

        # Check if any validation failed
        for validation in validations:
            if not validation.is_success:
                return validation

        return FlextResult[bool].ok(value=True)

    def _validate_required_fields(self) -> FlextResult[bool]:
        """Validate required fields."""
        if not self.base_url or not self.username or not self.password:
            return FlextResult[bool].fail(
                "base_url, username, and password are required",
            )
        return FlextResult[bool].ok(value=True)

    def _validate_url_format(self) -> FlextResult[bool]:
        """Validate URL format."""
        if self.base_url.scheme not in {"http", "https"}:
            return FlextResult[bool].fail(
                "base_url must start with http:// or https://",
            )
        return FlextResult[bool].ok(value=True)

    def _validate_page_size(self) -> FlextResult[bool]:
        """Validate page size limits."""
        if not (
            FlextTapOracleWmsConstants.MIN_PAGE_SIZE
            <= self.page_size
            <= FlextTapOracleWmsConstants.MAX_PAGE_SIZE
        ):
            return FlextResult[bool].fail(
                f"page_size must be between {FlextTapOracleWmsConstants.MIN_PAGE_SIZE} and {FlextTapOracleWmsConstants.MAX_PAGE_SIZE}",
            )
        return FlextResult[bool].ok(value=True)

    def _validate_timeout(self) -> FlextResult[bool]:
        """Validate timeout."""
        if self.timeout <= 0:
            return FlextResult[bool].fail("timeout must be positive")
        return FlextResult[bool].ok(value=True)

    def _validate_entity_settings(self) -> FlextResult[bool]:
        """Validate entity settings."""
        if self.include_entities and self.exclude_entities:
            common = set(self.include_entities) & set(self.exclude_entities)
            if common:
                return FlextResult[bool].fail(
                    f"Entities cannot be both included and excluded: {common}",
                )
        return FlextResult[bool].ok(value=True)

    def _validate_date_range(self) -> FlextResult[bool]:
        if self.start_date and self.end_date:
            start_value = datetime.fromisoformat(self.start_date)
            end_value = datetime.fromisoformat(self.end_date)
            if start_value > end_value:
                return FlextResult[bool].fail("start_date must be <= end_date")
        return FlextResult[bool].ok(value=True)

    def _validate_performance_settings(self) -> FlextResult[bool]:
        """Validate performance settings."""
        if (
            self.enable_parallel_extraction
            and self.max_parallel_streams
            > FlextTapOracleWmsConstants.MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT
            and not self.enable_rate_limiting
        ):
            return FlextResult[bool].fail(
                f"Rate limiting must be enabled for more than {FlextTapOracleWmsConstants.MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT} parallel streams",
            )
        return FlextResult[bool].ok(value=True)

    def validate_domain_rules(self) -> FlextResult[bool]:
        """Validate domain rules using the canonical business-rules gate."""
        return self.validate_business_rules()

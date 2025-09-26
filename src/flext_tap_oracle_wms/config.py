"""Configuration management for FLEXT Tap Oracle WMS.

Type-safe configuration using FLEXT patterns with Pydantic validation.
Consolidates configuration management and constants following PEP8 patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from pydantic import Field, SecretStr, field_validator

from flext_core import FlextConfig, FlextConstants, FlextModels, FlextResult, FlextTypes
from flext_oracle_wms import (
    FlextOracleWmsSemanticConstants as _WmsConstants,
)


class FlextTapOracleWMSConstants(FlextConstants):
    """Constants for Oracle WMS tap configuration - consuming from flext-oracle-wms API."""

    # CONSUME API defaults from flext-oracle-wms
    DEFAULT_API_VERSION: Final[str] = _WmsConstants.OracleWmsApi.DEFAULT_VERSION

    # Validation limits - using FlextConstants as SOURCE OF TRUTH
    MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT: Final[int] = (
        FlextConstants.Container.MAX_WORKERS + 1
    )  # 5
    DEFAULT_PAGE_SIZE: Final[int] = _WmsConstants.Pagination.DEFAULT_PAGE_SIZE
    DEFAULT_TIMEOUT: Final[int] = int(_WmsConstants.OracleWmsApi.DEFAULT_TIMEOUT)
    DEFAULT_MAX_RETRIES: Final[int] = _WmsConstants.OracleWmsApi.DEFAULT_MAX_RETRIES
    DEFAULT_RETRY_DELAY: Final[float] = _WmsConstants.OracleWmsApi.DEFAULT_RETRY_DELAY

    # CONSUME limits from flext-oracle-wms
    MIN_PAGE_SIZE: Final[int] = _WmsConstants.Pagination.MIN_PAGE_SIZE
    MAX_PAGE_SIZE: Final[int] = _WmsConstants.Pagination.MAX_PAGE_SIZE
    MIN_TIMEOUT: Final[int] = 1  # Singer-specific minimum
    MAX_TIMEOUT: Final[int] = 300  # Singer-specific maximum

    # CONSUME discovery settings from flext-oracle-wms
    DEFAULT_DISCOVERY_SAMPLE_SIZE: Final[int] = (
        _WmsConstants.Processing.DEFAULT_SAMPLE_SIZE
    )
    MAX_DISCOVERY_SAMPLE_SIZE: Final[int] = 1000  # Singer-specific maximum


class FlextTapOracleWMSConfig(FlextConfig):
    """Configuration for Oracle WMS tap.

    Type-safe configuration with validation for Oracle WMS data extraction.
    Follows FLEXT patterns using FlextConfig for comprehensive validation.
    """

    # Connection settings
    base_url: str = Field(
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
        default=FlextTapOracleWMSConstants.DEFAULT_API_VERSION,
        description="Oracle WMS API version",
    )
    timeout: int = Field(
        default=FlextTapOracleWMSConstants.DEFAULT_TIMEOUT,
        description="Request timeout in seconds",
        ge=FlextTapOracleWMSConstants.MIN_TIMEOUT,
        le=FlextTapOracleWMSConstants.MAX_TIMEOUT,
    )
    max_retries: int = Field(
        default=FlextTapOracleWMSConstants.DEFAULT_MAX_RETRIES,
        description="Maximum number of retries for failed requests",
        ge=0,
        le=10,
    )
    retry_delay: float = Field(
        default=FlextTapOracleWMSConstants.DEFAULT_RETRY_DELAY,
        description="Delay between retries in seconds",
        ge=0.1,
        le=60.0,
    )

    # Pagination settings
    page_size: int = Field(
        default=FlextTapOracleWMSConstants.DEFAULT_PAGE_SIZE,
        description="Number of records per page",
        ge=FlextTapOracleWMSConstants.MIN_PAGE_SIZE,
        le=FlextTapOracleWMSConstants.MAX_PAGE_SIZE,
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
    include_entities: FlextTypes.Core.StringList | None = Field(
        default=None,
        description="List of entities to include (default: all)",
    )
    exclude_entities: FlextTypes.Core.StringList | None = Field(
        default=None,
        description="List of entities to exclude",
    )

    # Discovery settings
    discovery_sample_size: int = Field(
        default=FlextTapOracleWMSConstants.DEFAULT_DISCOVERY_SAMPLE_SIZE,
        description="Number of records to sample for schema discovery",
        ge=1,
        le=FlextTapOracleWMSConstants.MAX_DISCOVERY_SAMPLE_SIZE,
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
        default=FlextConstants.Utilities.SECONDS_PER_MINUTE,  # 60
        description="Maximum requests per minute",
        ge=1,
        le=1000,
    )

    # Advanced settings
    user_agent: str | None = Field(
        default=None,
        description="Custom User-Agent header",
    )
    additional_headers: FlextTypes.Core.Headers | None = Field(
        default=None,
        description="Additional HTTP headers",
    )

    # Column filtering
    column_mappings: dict[str, FlextTypes.Core.Headers] | None = Field(
        default=None,
        description="Column name mappings per stream",
    )
    ignored_columns: FlextTypes.Core.StringList | None = Field(
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

    # Logging and debugging
    log_level: str = Field(
        default=FlextConstants.Config.LogLevel.DEFAULT_LEVEL,  # SOURCE OF TRUTH
        description="Logging level",
        pattern="^("
        + "|".join(FlextConstants.Config.LogLevel.VALID_LEVELS)
        + ")$",  # SOURCE OF TRUTH
    )
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

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL using centralized FlextModels validation."""
        # Use centralized FlextModels validation instead of duplicate logic
        stripped_url = v.rstrip("/")  # Remove trailing slash
        validation_result: FlextResult[object] = FlextModels.create_validated_http_url(
            stripped_url
        )
        if validation_result.is_failure:
            error_msg = f"Invalid base URL: {validation_result.error}"
            raise ValueError(error_msg)
        return stripped_url

    @field_validator("include_entities", "exclude_entities")
    @classmethod
    def validate_entity_lists(
        cls,
        v: FlextTypes.Core.StringList | None,
    ) -> FlextTypes.Core.StringList | None:
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
        """Validate date format using centralized FlextModels validation."""
        if v is not None:
            # Use centralized FlextModels validation instead of duplicate logic
            validation_result: FlextResult[object] = (
                FlextModels.create_validated_iso_date(v)
            )
            if validation_result.is_failure:
                error_msg = f"Invalid date format: {validation_result.error}"
                raise ValueError(error_msg)
            return validation_result.unwrap()
        return v

    def validate_business_rules(self: object) -> FlextResult[None]:
        """Validate Oracle WMS tap configuration business rules using FlextConfig pattern.

        Consolidates all validation logic into a single comprehensive method.

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
            if not validation.success:
                return validation

        return FlextResult[None].ok(None)

    def _validate_required_fields(self: object) -> FlextResult[None]:
        """Validate required fields."""
        if not self.base_url or not self.username or not self.password:
            return FlextResult[None].fail(
                "base_url, username, and password are required",
            )
        return FlextResult[None].ok(None)

    def _validate_url_format(self: object) -> FlextResult[None]:
        """Validate URL format."""
        if not self.base_url.startswith(("http://", "https://")):
            return FlextResult[None].fail(
                "base_url must start with http:// or https://",
            )
        return FlextResult[None].ok(None)

    def _validate_page_size(self: object) -> FlextResult[None]:
        """Validate page size limits."""
        if not (
            FlextTapOracleWMSConstants.MIN_PAGE_SIZE
            <= self.page_size
            <= FlextTapOracleWMSConstants.MAX_PAGE_SIZE
        ):
            return FlextResult[None].fail(
                f"page_size must be between {FlextTapOracleWMSConstants.MIN_PAGE_SIZE} and {FlextTapOracleWMSConstants.MAX_PAGE_SIZE}",
            )
        return FlextResult[None].ok(None)

    def _validate_timeout(self: object) -> FlextResult[None]:
        """Validate timeout."""
        if self.timeout <= 0:
            return FlextResult[None].fail("timeout must be positive")
        return FlextResult[None].ok(None)

    def _validate_entity_settings(self: object) -> FlextResult[None]:
        """Validate entity settings."""
        if self.include_entities and self.exclude_entities:
            common = set(self.include_entities) & set(self.exclude_entities)
            if common:
                return FlextResult[None].fail(
                    f"Entities cannot be both included and excluded: {common}",
                )
        return FlextResult[None].ok(None)

    def _validate_date_range(self: object) -> FlextResult[None]:
        """Validate date range using centralized FlextModels validation."""
        if self.start_date and self.end_date:
            # Use centralized FlextModels date range validation instead of duplicate logic
            validation_result = FlextModels.create_validated_date_range(
                self.start_date,
                self.end_date,
            )
            if validation_result.is_failure:
                return FlextResult[None].fail(
                    validation_result.error or "Date range validation failed",
                )
        return FlextResult[None].ok(None)

    def _validate_performance_settings(self: object) -> FlextResult[None]:
        """Validate performance settings."""
        if (
            self.enable_parallel_extraction
            and self.max_parallel_streams
            > FlextTapOracleWMSConstants.MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT
            and not self.enable_rate_limiting
        ):
            return FlextResult[None].fail(
                f"Rate limiting must be enabled for more than {FlextTapOracleWMSConstants.MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT} parallel streams",
            )
        return FlextResult[None].ok(None)

    def validate_oracle_wms_config(self: object) -> FlextResult[FlextTypes.Core.Dict]:
        """Validate Oracle WMS specific configuration.

        Returns:
            FlextResult with validation status

        """
        try:
            # Check for conflicting settings
            if self.include_entities and self.exclude_entities:
                common = set(self.include_entities) & set(self.exclude_entities)
                if common:
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Entities cannot be both included and excluded: {common}",
                    )

            # Validate date range using centralized FlextModels validation
            if self.start_date and self.end_date:
                date_range_result = FlextModels.create_validated_date_range(
                    self.start_date,
                    self.end_date,
                )
                if date_range_result.is_failure:
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        date_range_result.error or "Date range validation failed",
                    )

            # Validate performance settings
            max_parallel_streams_without_rate_limit = 5
            if (
                self.enable_parallel_extraction
                and self.max_parallel_streams > max_parallel_streams_without_rate_limit
                and not self.enable_rate_limiting
            ):
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Rate limiting must be enabled for more than {max_parallel_streams_without_rate_limit} parallel streams",
                )

            validation_data = {
                "valid": "True",
                "base_url": self.base_url,
                "api_version": self.api_version,
                "streams_included": len(self.include_entities)
                if self.include_entities
                else "all",
                "streams_excluded": len(self.exclude_entities)
                if self.exclude_entities
                else 0,
            }

            return FlextResult[FlextTypes.Core.Dict].ok(validation_data)

        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Configuration validation failed: {e}",
            )

    def validate_domain_rules(self: object) -> FlextResult[None]:
        """Validate Oracle WMS tap-specific domain rules.

        Returns:
            FlextResult indicating validation success or failure

        """
        try:
            # Run all validation checks in sequence
            validation_methods = [
                self._validate_required_fields,
                self._validate_url_format,
                self._validate_date_range,
            ]

            for validation_method in validation_methods:
                result: FlextResult[object] = validation_method()
                if result.is_failure:
                    return result

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Domain rule validation failed: {e}")

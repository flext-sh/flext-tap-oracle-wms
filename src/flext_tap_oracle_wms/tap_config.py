"""Configuration management for FLEXT Tap Oracle WMS.

Type-safe configuration using FLEXT patterns with Pydantic validation.
Consolidates configuration management and constants following PEP8 patterns.
"""

from __future__ import annotations

from datetime import datetime
from typing import Final

from flext_core import FlextResult
from flext_meltano import FlextMeltanoConfig
from flext_oracle_wms.constants import (
    FlextOracleWmsSemanticConstants as _WmsConstants,
)
from pydantic import Field, SecretStr, field_validator


class FlextTapOracleWMSConstants:
    """Constants for Oracle WMS tap configuration - consuming from flext-oracle-wms API."""

    # CONSUME API defaults from flext-oracle-wms - NO DUPLICATION
    DEFAULT_API_VERSION: Final[str] = _WmsConstants.Api.DEFAULT_VERSION
    DEFAULT_PAGE_SIZE: Final[int] = _WmsConstants.Pagination.DEFAULT_PAGE_SIZE
    DEFAULT_TIMEOUT: Final[int] = int(_WmsConstants.Api.DEFAULT_TIMEOUT)
    DEFAULT_MAX_RETRIES: Final[int] = _WmsConstants.Api.DEFAULT_MAX_RETRIES
    DEFAULT_RETRY_DELAY: Final[float] = _WmsConstants.Api.DEFAULT_RETRY_DELAY

    # CONSUME limits from flext-oracle-wms - NO DUPLICATION
    MIN_PAGE_SIZE: Final[int] = _WmsConstants.Pagination.MIN_PAGE_SIZE
    MAX_PAGE_SIZE: Final[int] = _WmsConstants.Pagination.MAX_PAGE_SIZE
    MIN_TIMEOUT: Final[int] = 1  # Singer-specific minimum
    MAX_TIMEOUT: Final[int] = 300  # Singer-specific maximum

    # CONSUME discovery settings from flext-oracle-wms - NO DUPLICATION
    DEFAULT_DISCOVERY_SAMPLE_SIZE: Final[int] = (
        _WmsConstants.Processing.DEFAULT_SAMPLE_SIZE
    )
    MAX_DISCOVERY_SAMPLE_SIZE: Final[int] = 1000  # Singer-specific maximum


class FlextTapOracleWMSConfig(FlextMeltanoConfig):
    """Configuration for Oracle WMS tap.

    Type-safe configuration with validation for Oracle WMS data extraction.
    Follows FLEXT patterns using FlextMeltanoConfig for Singer/Meltano integration.
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
        default=3,
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
    additional_headers: dict[str, str] | None = Field(
        default=None,
        description="Additional HTTP headers",
    )

    # Column filtering
    column_mappings: dict[str, dict[str, str]] | None = Field(
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

    # Logging and debugging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
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
        default=3,
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
        """Validate base URL format."""
        v = v.rstrip("/")  # Remove trailing slash
        if not v.startswith(("http://", "https://")):
            msg = "Base URL must start with http:// or https://"
            raise ValueError(msg)
        return v

    @field_validator("include_entities", "exclude_entities")
    @classmethod
    def validate_entity_lists(cls, v: list[str] | None) -> list[str] | None:
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
        """Validate date format."""
        if v is not None:
            try:
                datetime.fromisoformat(v)
            except ValueError as e:
                msg = f"Invalid date format. Use ISO format: {e}"
                raise ValueError(msg) from e
        return v

    def validate_oracle_wms_config(self) -> FlextResult[dict[str, object]]:
        """Validate Oracle WMS specific configuration.

        Returns:
            FlextResult with validation status

        """
        try:
            # Check for conflicting settings
            if self.include_entities and self.exclude_entities:
                common = set(self.include_entities) & set(self.exclude_entities)
                if common:
                    return FlextResult.fail(
                        f"Entities cannot be both included and excluded: {common}",
                    )

            # Validate date range
            if self.start_date and self.end_date:
                start = datetime.fromisoformat(self.start_date)
                end = datetime.fromisoformat(self.end_date)
                if start > end:
                    return FlextResult.fail("Start date must be before end date")

            # Validate performance settings
            max_parallel_streams_without_rate_limit = 5
            if (
                self.enable_parallel_extraction
                and self.max_parallel_streams > max_parallel_streams_without_rate_limit
                and not self.enable_rate_limiting
            ):
                return FlextResult.fail(
                    f"Rate limiting must be enabled for more than {max_parallel_streams_without_rate_limit} parallel streams",
                )

            validation_result = {
                "valid": True,
                "base_url": self.base_url,
                "api_version": self.api_version,
                "streams_included": len(self.include_entities)
                if self.include_entities
                else "all",
                "streams_excluded": len(self.exclude_entities)
                if self.exclude_entities
                else 0,
            }

            return FlextResult.ok(validation_result)

        except Exception as e:
            return FlextResult.fail(f"Configuration validation failed: {e}")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate Oracle WMS tap-specific domain rules.

        Returns:
            FlextResult indicating validation success or failure

        """
        try:
            # Run all validation checks in sequence
            validation_methods = [
                self._validate_required_fields,
                self._validate_url_format,
                self._validate_page_size_limits,
                self._validate_date_range,
                self._validate_entity_selections,
            ]

            for validation_method in validation_methods:
                result = validation_method()
                if result.is_failure:
                    return result

            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Domain rule validation failed: {e}")

    def _validate_required_fields(self) -> FlextResult[None]:
        """Validate required configuration fields."""
        if not self.base_url:
            return FlextResult.fail("base_url is required")

        if not self.username:
            return FlextResult.fail("username is required")

        if not self.password:
            return FlextResult.fail("password is required")

        return FlextResult.ok(None)

    def _validate_url_format(self) -> FlextResult[None]:
        """Validate URL format requirements."""
        if not self.base_url.startswith(("http://", "https://")):
            return FlextResult.fail("base_url must start with http:// or https://")

        return FlextResult.ok(None)

    def _validate_page_size_limits(self) -> FlextResult[None]:
        """Validate page size limits."""
        if self.page_size > FlextTapOracleWMSConstants.MAX_PAGE_SIZE:
            return FlextResult.fail(
                f"page_size cannot exceed {FlextTapOracleWMSConstants.MAX_PAGE_SIZE}",
            )

        return FlextResult.ok(None)

    def _validate_date_range(self) -> FlextResult[None]:
        """Validate date range consistency."""
        if not (self.start_date and self.end_date):
            return FlextResult.ok(None)

        try:
            start = datetime.fromisoformat(self.start_date)
            end = datetime.fromisoformat(self.end_date)
            if start >= end:
                return FlextResult.fail("start_date must be before end_date")
        except ValueError as e:
            return FlextResult.fail(f"Invalid date format: {e}")

        return FlextResult.ok(None)

    def _validate_entity_selections(self) -> FlextResult[None]:
        """Validate entity inclusion/exclusion logic."""
        if not (self.include_entities and self.exclude_entities):
            return FlextResult.ok(None)

        # Check for overlap between included and excluded entities
        included_set = set(self.include_entities)
        excluded_set = set(self.exclude_entities)
        overlap = included_set & excluded_set

        if overlap:
            return FlextResult.fail(
                f"Entities cannot be both included and excluded: {list(overlap)}",
            )

        return FlextResult.ok(None)

    def get_stream_config(self, stream_name: str) -> dict[str, object]:
        """Get configuration for a specific stream.

        Args:
            stream_name: Name of the stream

        Returns:
            Stream-specific configuration

        """
        config: dict[str, object] = {
            "page_size": self.page_size,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "validate_records": self.validate_schemas,
        }

        # Add column mappings if available
        if self.column_mappings and stream_name in self.column_mappings:
            config["column_mappings"] = self.column_mappings[stream_name]

        # Add ignored columns
        if self.ignored_columns:
            config["ignored_columns"] = self.ignored_columns

        return config

    def validate_oracle_wms_business_rules(self) -> FlextResult[None]:
        """Validate business rules for Oracle WMS tap configuration.

        Returns:
            FlextResult indicating success or failure with validation errors.

        """
        # Validate basic URL format
        if not self.base_url.startswith(("http://", "https://")):
            return FlextResult.fail("base_url must start with http:// or https://")

        # Validate timeout settings
        if self.timeout <= 0:
            return FlextResult.fail("timeout must be positive")

        # Validate page size limits
        if not (
            self.page_size <= FlextTapOracleWMSConstants.MAX_PAGE_SIZE
            and self.page_size >= FlextTapOracleWMSConstants.MIN_PAGE_SIZE
        ):
            return FlextResult.fail(
                f"page_size must be between {FlextTapOracleWMSConstants.MIN_PAGE_SIZE} and {FlextTapOracleWMSConstants.MAX_PAGE_SIZE}",
            )

        # Validate auth credentials
        if not self.username or not self.password:
            return FlextResult.fail("username and password are required")

        return FlextResult.ok(None)

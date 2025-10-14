"""Configuration management for FLEXT Tap Oracle WMS.

Type-safe configuration using FLEXT patterns with Pydantic validation.
Consolidates configuration management and constants following PEP8 patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Final, Self

from flext_core import FlextCore
from flext_oracle_wms import (
    FlextOracleWmsConstants as _WmsConstants,
)
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict


class FlextMeltanoTapOracleWMSConstants(FlextCore.Constants):
    """Constants for Oracle WMS tap configuration - consuming from flext-oracle-wms API."""

    # API defaults from flext-oracle-wms (using available constants)
    DEFAULT_API_VERSION: Final[str] = _WmsConstants.API_VERSION_DEFAULT

    # Validation limits - using FlextCore.Constants as SOURCE OF TRUTH
    MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT: Final[int] = (
        FlextCore.Constants.Container.MAX_WORKERS + 1
    )  # 5
    DEFAULT_PAGE_SIZE: Final[int] = _WmsConstants.DEFAULT_PAGE_SIZE
    DEFAULT_TIMEOUT: Final[int] = _WmsConstants.Api.DEFAULT_TIMEOUT
    DEFAULT_MAX_RETRIES: Final[int] = _WmsConstants.API_MAX_RETRIES
    DEFAULT_RETRY_DELAY: Final[float] = 1.0  # Standard retry delay

    # Pagination limits (hardcoded since not available in nested structure)
    MIN_PAGE_SIZE: Final[int] = 1
    MAX_PAGE_SIZE: Final[int] = 1000
    MIN_TIMEOUT: Final[int] = 1  # Singer-specific minimum
    MAX_TIMEOUT: Final[int] = (
        FlextCore.Constants.Network.DEFAULT_TIMEOUT * 10
    )  # Singer-specific maximum

    # Discovery settings (hardcoded since not available)
    DEFAULT_DISCOVERY_SAMPLE_SIZE: Final[int] = 100
    MAX_DISCOVERY_SAMPLE_SIZE: Final[int] = (
        FlextCore.Constants.Performance.BatchProcessing.DEFAULT_SIZE
    )  # Singer-specific maximum


class FlextMeltanoTapOracleWMSConfig(FlextCore.Config):
    """Configuration for Oracle WMS tap.

    Type-safe configuration with validation for Oracle WMS data extraction.
    Follows FLEXT patterns using FlextCore.Config for comprehensive validation.
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

    # Backward compatibility properties for old attribute names
    @property
    def host(self) -> str:
        """Backward compatibility property for base_url."""
        return self.base_url

    @property
    def port(self) -> int:
        """Backward compatibility property for port."""
        return 443  # Default HTTPS port

    @property
    def service_name(self) -> str:
        """Backward compatibility property for service name."""
        return "oracle-wms"

    @property
    def protocol(self) -> str:
        """Backward compatibility property for connection protocol."""
        return "https"  # Default protocol for WMS connections

    @property
    def ssl_enabled(self) -> bool:
        """Backward compatibility property for SSL configuration."""
        return True  # Default SSL enabled for WMS connections

    @property
    def pool_min(self) -> int:
        """Backward compatibility property for minimum pool size."""
        return 1  # Default minimum pool size

    @property
    def pool_max(self) -> int:
        """Backward compatibility property for maximum pool size."""
        return 10  # Default maximum pool size

    # API settings
    api_version: str = Field(
        default=FlextMeltanoTapOracleWMSConstants.DEFAULT_API_VERSION,
        description="Oracle WMS API version",
    )
    timeout: int = Field(
        default=FlextMeltanoTapOracleWMSConstants.DEFAULT_TIMEOUT,
        description="Request timeout in seconds",
        ge=FlextMeltanoTapOracleWMSConstants.MIN_TIMEOUT,
        le=FlextMeltanoTapOracleWMSConstants.MAX_TIMEOUT,
    )
    max_retries: int = Field(
        default=FlextMeltanoTapOracleWMSConstants.DEFAULT_MAX_RETRIES,
        description="Maximum number of retries for failed requests",
        ge=0,
        le=10,
    )
    retry_delay: float = Field(
        default=FlextMeltanoTapOracleWMSConstants.DEFAULT_RETRY_DELAY,
        description="Delay between retries in seconds",
        ge=0.1,
        le=60.0,
    )

    # Pagination settings
    page_size: int = Field(
        default=FlextMeltanoTapOracleWMSConstants.DEFAULT_PAGE_SIZE,
        description="Number of records per page",
        ge=FlextMeltanoTapOracleWMSConstants.MIN_PAGE_SIZE,
        le=FlextMeltanoTapOracleWMSConstants.MAX_PAGE_SIZE,
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
    include_entities: FlextCore.Types.StringList | None = Field(
        default=None,
        description="List of entities to include (default: all)",
    )
    exclude_entities: FlextCore.Types.StringList | None = Field(
        default=None,
        description="List of entities to exclude",
    )

    # Discovery settings
    discovery_sample_size: int = Field(
        default=FlextMeltanoTapOracleWMSConstants.DEFAULT_DISCOVERY_SAMPLE_SIZE,
        description="Number of records to sample for schema discovery",
        ge=1,
        le=FlextMeltanoTapOracleWMSConstants.MAX_DISCOVERY_SAMPLE_SIZE,
    )
    enable_schema_flattening: bool = Field(
        default=True,
        description="Enable flattening of nested structures",
    )
    max_flattening_depth: int = Field(
        default=FlextCore.Constants.Reliability.MAX_RETRY_ATTEMPTS,  # 3
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
        default=FlextCore.Constants.Utilities.SECONDS_PER_MINUTE,  # 60
        description="Maximum requests per minute",
        ge=1,
        le=1000,
    )

    # Advanced settings
    user_agent: str | None = Field(
        default=None,
        description="Custom User-Agent header",
    )
    additional_headers: FlextCore.Types.StringDict | None = Field(
        default=None,
        description="Additional HTTP headers",
    )

    # Column filtering
    column_mappings: dict[str, FlextCore.Types.StringDict] | None = Field(
        default=None,
        description="Column name mappings per stream",
    )
    ignored_columns: FlextCore.Types.StringList | None = Field(
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
        default=FlextCore.Constants.Reliability.MAX_RETRY_ATTEMPTS,  # 3
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
    def get_global_instance(cls) -> Self:
        """Get the global singleton instance using enhanced FlextCore.Config pattern."""
        return cls.get_or_create_shared_instance(project_name="flext-tap-oracle-wms")

    @classmethod
    def create_for_development(cls, **overrides: object) -> Self:
        """Create configuration for development environment."""
        dev_overrides: FlextCore.Types.Dict = {
            "timeout": FlextCore.Constants.Network.DEFAULT_TIMEOUT * 2,
            "max_retries": FlextCore.Constants.Reliability.MAX_RETRY_ATTEMPTS + 2,
            "page_size": FlextMeltanoTapOracleWMSConstants.DEFAULT_PAGE_SIZE // 2,
            "enable_request_logging": True,
            "enable_parallel_extraction": True,
            **overrides,
        }
        return cls.get_or_create_shared_instance(
            project_name="flext-tap-oracle-wms", **dev_overrides
        )

    @classmethod
    def create_for_production(cls, **overrides: object) -> Self:
        """Create configuration for production environment."""
        prod_overrides: FlextCore.Types.Dict = {
            "timeout": FlextCore.Constants.Network.DEFAULT_TIMEOUT,
            "max_retries": FlextCore.Constants.Reliability.MAX_RETRY_ATTEMPTS,
            "page_size": FlextMeltanoTapOracleWMSConstants.DEFAULT_PAGE_SIZE,
            "enable_request_logging": False,
            "enable_parallel_extraction": False,
            **overrides,
        }
        return cls.get_or_create_shared_instance(
            project_name="flext-tap-oracle-wms", **prod_overrides
        )

    @classmethod
    def create_for_testing(cls, **overrides: object) -> Self:
        """Create configuration for testing environment."""
        test_overrides: FlextCore.Types.Dict = {
            "timeout": FlextCore.Constants.Network.DEFAULT_TIMEOUT // 3,
            "max_retries": 1,
            "page_size": FlextMeltanoTapOracleWMSConstants.MIN_PAGE_SIZE,
            "enable_request_logging": True,
            "enable_parallel_extraction": True,
            **overrides,
        }
        return cls.get_or_create_shared_instance(
            project_name="flext-tap-oracle-wms", **test_overrides
        )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL using centralized FlextCore.Models validation."""
        # Use centralized FlextCore.Models validation instead of duplicate logic
        stripped_url = v.rstrip("/")  # Remove trailing slash
        validation_result: FlextCore.Result[object] = (
            FlextCore.Models.create_validated_http_url(stripped_url)
        )
        if validation_result.is_failure:
            error_msg = f"Invalid base URL: {validation_result.error}"
            raise ValueError(error_msg)
        return stripped_url

    @field_validator("include_entities", "exclude_entities")
    @classmethod
    def validate_entity_lists(
        cls,
        v: FlextCore.Types.StringList | None,
    ) -> FlextCore.Types.StringList | None:
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
        """Validate date format using centralized FlextCore.Models validation."""
        if v is not None:
            # Use centralized FlextCore.Models validation instead of duplicate logic
            validation_result: FlextCore.Result[object] = (
                FlextCore.Models.create_validated_iso_date(v)
            )
            if validation_result.is_failure:
                error_msg = f"Invalid date format: {validation_result.error}"
                raise ValueError(error_msg)
            return validation_result.unwrap()
        return v

    def validate_business_rules(self: object) -> FlextCore.Result[None]:
        """Validate Oracle WMS tap configuration business rules using FlextCore.Config pattern.

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

        return FlextCore.Result[None].ok(None)

    def _validate_required_fields(self: object) -> FlextCore.Result[None]:
        """Validate required fields."""
        if not self.base_url or not self.username or not self.password:
            return FlextCore.Result[None].fail(
                "base_url, username, and password are required",
            )
        return FlextCore.Result[None].ok(None)

    def _validate_url_format(self: object) -> FlextCore.Result[None]:
        """Validate URL format."""
        if not self.base_url.startswith(("http://", "https://")):
            return FlextCore.Result[None].fail(
                "base_url must start with http:// or https://",
            )
        return FlextCore.Result[None].ok(None)

    def _validate_page_size(self: object) -> FlextCore.Result[None]:
        """Validate page size limits."""
        if not (
            FlextMeltanoTapOracleWMSConstants.MIN_PAGE_SIZE
            <= self.page_size
            <= FlextMeltanoTapOracleWMSConstants.MAX_PAGE_SIZE
        ):
            return FlextCore.Result[None].fail(
                f"page_size must be between {FlextMeltanoTapOracleWMSConstants.MIN_PAGE_SIZE} and {FlextMeltanoTapOracleWMSConstants.MAX_PAGE_SIZE}",
            )
        return FlextCore.Result[None].ok(None)

    def _validate_timeout(self: object) -> FlextCore.Result[None]:
        """Validate timeout."""
        if self.timeout <= 0:
            return FlextCore.Result[None].fail("timeout must be positive")
        return FlextCore.Result[None].ok(None)

    def _validate_entity_settings(self: object) -> FlextCore.Result[None]:
        """Validate entity settings."""
        if self.include_entities and self.exclude_entities:
            common = set(self.include_entities) & set(self.exclude_entities)
            if common:
                return FlextCore.Result[None].fail(
                    f"Entities cannot be both included and excluded: {common}",
                )
        return FlextCore.Result[None].ok(None)

    def _validate_date_range(self: object) -> FlextCore.Result[None]:
        """Validate date range using centralized FlextCore.Models validation."""
        if self.start_date and self.end_date:
            # Use centralized FlextCore.Models date range validation instead of duplicate logic
            validation_result = FlextCore.Models.create_validated_date_range(
                self.start_date,
                self.end_date,
            )
            if validation_result.is_failure:
                return FlextCore.Result[None].fail(
                    validation_result.error or "Date range validation failed",
                )
        return FlextCore.Result[None].ok(None)

    def _validate_performance_settings(self: object) -> FlextCore.Result[None]:
        """Validate performance settings."""
        if (
            self.enable_parallel_extraction
            and self.max_parallel_streams
            > FlextMeltanoTapOracleWMSConstants.MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT
            and not self.enable_rate_limiting
        ):
            return FlextCore.Result[None].fail(
                f"Rate limiting must be enabled for more than {FlextMeltanoTapOracleWMSConstants.MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT} parallel streams",
            )
        return FlextCore.Result[None].ok(None)

    def validate_oracle_wms_config(
        self: object,
    ) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Validate Oracle WMS specific configuration.

        Returns:
            FlextCore.Result with validation status

        """
        try:
            # Check for conflicting settings
            if self.include_entities and self.exclude_entities:
                common = set(self.include_entities) & set(self.exclude_entities)
                if common:
                    return FlextCore.Result[FlextCore.Types.Dict].fail(
                        f"Entities cannot be both included and excluded: {common}",
                    )

            # Validate date range using centralized FlextCore.Models validation
            if self.start_date and self.end_date:
                date_range_result = FlextCore.Models.create_validated_date_range(
                    self.start_date,
                    self.end_date,
                )
                if date_range_result.is_failure:
                    return FlextCore.Result[FlextCore.Types.Dict].fail(
                        date_range_result.error or "Date range validation failed",
                    )

            # Validate performance settings
            max_parallel_streams_without_rate_limit = FlextMeltanoTapOracleWMSConstants.MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT
            if (
                self.enable_parallel_extraction
                and self.max_parallel_streams > max_parallel_streams_without_rate_limit
                and not self.enable_rate_limiting
            ):
                return FlextCore.Result[FlextCore.Types.Dict].fail(
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

            return FlextCore.Result[FlextCore.Types.Dict].ok(validation_data)

        except Exception as e:
            return FlextCore.Result[FlextCore.Types.Dict].fail(
                f"Configuration validation failed: {e}",
            )

    def validate_domain_rules(self: object) -> FlextCore.Result[None]:
        """Validate Oracle WMS tap-specific domain rules.

        Returns:
            FlextCore.Result indicating validation success or failure

        """
        try:
            # Run all validation checks in sequence
            validation_methods = [
                self._validate_required_fields,
                self._validate_url_format,
                self._validate_date_range,
            ]

            for validation_method in validation_methods:
                result: FlextCore.Result[object] = validation_method()
                if result.is_failure:
                    return result

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Domain rule validation failed: {e}")

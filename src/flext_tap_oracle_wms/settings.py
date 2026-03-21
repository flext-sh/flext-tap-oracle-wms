"""Configuration contracts for FLEXT Tap Oracle WMS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from typing import Annotated, Final

from flext_core import FlextConstants, r
from flext_oracle_wms import FlextOracleWmsConstants as _WmsConstants
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from pydantic.networks import AnyUrl


class FlextTapOracleWmsConstants(FlextConstants):
    """Constants for Oracle WMS tap configuration - consuming from flext-oracle-wms API."""

    DEFAULT_API_VERSION: Final[str] = _WmsConstants.WmsApiVersion.V1
    MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT: Final[int] = 5
    TAP_DEFAULT_MAX_RETRIES: Final[int] = 3
    TAP_DEFAULT_RETRY_DELAY: Final[float] = 1.0
    TAP_MIN_TIMEOUT: Final[int] = 1
    TAP_MAX_TIMEOUT: Final[int] = 300
    TAP_DEFAULT_TIMEOUT: Final[int] = 30
    TAP_DEFAULT_PAGE_SIZE: Final[int] = 10
    DEFAULT_DISCOVERY_SAMPLE_SIZE: Final[int] = 100
    MAX_DISCOVERY_SAMPLE_SIZE: Final[int] = FlextConstants.DEFAULT_SIZE
    DEFAULT_MAX_PARALLEL_STREAMS: Final[int] = 5
    DEFAULT_FLATTENING_DEPTH: Final[int] = 10
    ISO_DATE_PATTERN: Final[str] = (
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
    )


class FlextTapOracleWmsSettings(BaseModel):
    """Validated settings consumed by the Oracle WMS tap runtime."""

    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    base_url: Annotated[
        AnyUrl,
        Field(description="Base Oracle WMS API URL."),
    ]
    username: Annotated[
        str,
        Field(min_length=1, description="Oracle WMS username."),
    ]
    password: Annotated[
        SecretStr,
        Field(description="Oracle WMS password."),
    ]
    api_version: Annotated[
        str,
        Field(
            default=FlextTapOracleWmsConstants.DEFAULT_API_VERSION,
            min_length=1,
            description="Oracle WMS API version.",
        ),
    ]
    timeout: Annotated[
        int,
        Field(
            default=FlextTapOracleWmsConstants.TAP_DEFAULT_TIMEOUT,
            ge=FlextTapOracleWmsConstants.TAP_MIN_TIMEOUT,
            le=FlextTapOracleWmsConstants.TAP_MAX_TIMEOUT,
            description="Request timeout in seconds.",
        ),
    ]
    max_retries: Annotated[
        int,
        Field(
            default=FlextTapOracleWmsConstants.TAP_DEFAULT_MAX_RETRIES,
            ge=0,
            description="Maximum request retries.",
        ),
    ]
    retry_delay: Annotated[
        float,
        Field(
            default=FlextTapOracleWmsConstants.TAP_DEFAULT_RETRY_DELAY,
            ge=0.0,
            description="Retry delay in seconds.",
        ),
    ]
    verify_ssl: Annotated[
        bool,
        Field(default=True, description="Enable SSL verification."),
    ]
    ssl_cert_path: Annotated[
        str | None,
        Field(default=None, description="Path to SSL certificate."),
    ]
    page_size: Annotated[
        int,
        Field(
            default=FlextTapOracleWmsConstants.TAP_DEFAULT_PAGE_SIZE,
            ge=1,
            description="Page size used for extraction requests.",
        ),
    ]
    discovery_sample_size: Annotated[
        int,
        Field(
            default=FlextTapOracleWmsConstants.DEFAULT_DISCOVERY_SAMPLE_SIZE,
            ge=1,
            description="Sample size for schema discovery.",
        ),
    ]
    effective_log_level: Annotated[
        str,
        Field(
            default="INFO",
            min_length=1,
            description="Optional effective log level inherited from runtime.",
        ),
    ]
    include_entities: Annotated[
        list[str],
        Field(default_factory=list, description="Entities to include."),
    ]
    exclude_entities: Annotated[
        list[str],
        Field(default_factory=list, description="Entities to exclude."),
    ]
    start_date: Annotated[
        str | None,
        Field(default=None, description="Start date for incremental extraction."),
    ]
    end_date: Annotated[
        str | None,
        Field(default=None, description="End date for incremental extraction."),
    ]
    column_mappings: Annotated[
        dict[str, dict[str, str]],
        Field(default_factory=dict, description="Column rename mappings per stream."),
    ]
    ignored_columns: Annotated[
        list[str],
        Field(default_factory=list, description="Columns to ignore during extraction."),
    ]
    enable_parallel_extraction: Annotated[
        bool,
        Field(default=False, description="Enable parallel stream extraction."),
    ]
    max_parallel_streams: Annotated[
        int,
        Field(
            default=FlextTapOracleWmsConstants.DEFAULT_MAX_PARALLEL_STREAMS,
            ge=1,
            description="Maximum parallel streams.",
        ),
    ]
    enable_rate_limiting: Annotated[
        bool,
        Field(default=True, description="Enable API rate limiting."),
    ]
    max_requests_per_minute: Annotated[
        int,
        Field(default=60, ge=1, description="Maximum API requests per minute."),
    ]
    enable_schema_flattening: Annotated[
        bool,
        Field(default=True, description="Enable schema flattening."),
    ]
    max_flattening_depth: Annotated[
        int,
        Field(
            default=FlextTapOracleWmsConstants.DEFAULT_FLATTENING_DEPTH,
            ge=1,
            description="Maximum schema flattening depth.",
        ),
    ]
    user_agent: Annotated[
        str | None,
        Field(default=None, description="Custom User-Agent header."),
    ]
    additional_headers: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Additional HTTP headers."),
    ]
    log_level: Annotated[
        str,
        Field(default="INFO", min_length=1, description="Log level."),
    ]
    enable_request_logging: Annotated[
        bool,
        Field(default=False, description="Enable HTTP request logging."),
    ]
    validate_config: Annotated[
        bool,
        Field(default=True, description="Enable configuration validation."),
    ]
    validate_schemas: Annotated[
        bool,
        Field(default=True, description="Enable schema validation."),
    ]

    @field_validator("include_entities", "exclude_entities")
    @classmethod
    def _check_no_duplicates(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            msg = "Entity list contains duplicates"
            raise ValueError(msg)
        return v

    @field_validator("start_date", "end_date")
    @classmethod
    def _check_iso_date(cls, v: str | None) -> str | None:
        if v is not None and not re.match(
            FlextTapOracleWmsConstants.ISO_DATE_PATTERN, v
        ):
            msg = f"Invalid date format: {v}. Expected ISO 8601 format."
            raise ValueError(msg)
        return v

    @classmethod
    def reset_for_testing(cls) -> None:
        """Reset any cached state for test isolation."""

    def validate_domain_rules(self) -> r[bool]:
        """Validate domain-specific rules."""
        return self.validate_business_rules()

    def validate_business_rules(self) -> r[bool]:
        """Validate Oracle WMS business rules."""
        overlap = set(self.include_entities) & set(self.exclude_entities)
        if overlap:
            return r[bool].fail(
                f"Entities {overlap} cannot be both included and excluded",
            )
        if self.start_date and self.end_date and self.start_date > self.end_date:
            return r[bool].fail("start_date must be <= end_date")
        return r[bool].ok(True)


__all__ = ["FlextTapOracleWmsConstants", "FlextTapOracleWmsSettings"]

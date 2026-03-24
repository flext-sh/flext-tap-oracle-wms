"""Configuration contracts for FLEXT Tap Oracle WMS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Annotated, ClassVar

from flext_core import r
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from pydantic.networks import AnyUrl

from flext_tap_oracle_wms import c, t


class FlextTapOracleWmsSettings(BaseModel):
    """Validated settings consumed by the Oracle WMS tap runtime."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="ignore",
        validate_assignment=True,
    )

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
            default=c.Settings.DEFAULT_API_VERSION,
            min_length=1,
            description="Oracle WMS API version.",
        ),
    ]
    timeout: Annotated[
        int,
        Field(
            default=c.Settings.TAP_DEFAULT_TIMEOUT,
            ge=c.Settings.TAP_MIN_TIMEOUT,
            le=c.Settings.TAP_MAX_TIMEOUT,
            description="Request timeout in seconds.",
        ),
    ]
    max_retries: Annotated[
        int,
        Field(
            default=c.Settings.TAP_DEFAULT_MAX_RETRIES,
            ge=0,
            description="Maximum request retries.",
        ),
    ]
    retry_delay: Annotated[
        float,
        Field(
            default=c.Settings.TAP_DEFAULT_RETRY_DELAY,
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
            default=c.Settings.TAP_DEFAULT_PAGE_SIZE,
            ge=1,
            description="Page size used for extraction requests.",
        ),
    ]
    discovery_sample_size: Annotated[
        int,
        Field(
            default=c.Settings.DEFAULT_DISCOVERY_SAMPLE_SIZE,
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
        t.StrSequence,
        Field(default_factory=list, description="Entities to include."),
    ]
    exclude_entities: Annotated[
        t.StrSequence,
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
        Mapping[str, t.StrMapping],
        Field(default_factory=dict, description="Column rename mappings per stream."),
    ]
    ignored_columns: Annotated[
        t.StrSequence,
        Field(default_factory=list, description="Columns to ignore during extraction."),
    ]
    enable_parallel_extraction: Annotated[
        bool,
        Field(default=False, description="Enable parallel stream extraction."),
    ]
    max_parallel_streams: Annotated[
        int,
        Field(
            default=c.Settings.DEFAULT_MAX_PARALLEL_STREAMS,
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
            default=c.Settings.DEFAULT_FLATTENING_DEPTH,
            ge=1,
            description="Maximum schema flattening depth.",
        ),
    ]
    user_agent: Annotated[
        str | None,
        Field(default=None, description="Custom User-Agent header."),
    ]
    additional_headers: Annotated[
        t.StrMapping,
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
    def _check_no_duplicates(cls, v: t.StrSequence) -> t.StrSequence:
        if len(v) != len(set(v)):
            msg = "Entity list contains duplicates"
            raise ValueError(msg)
        return v

    @field_validator("start_date", "end_date")
    @classmethod
    def _check_iso_date(cls, v: str | None) -> str | None:
        if v is not None and not re.match(c.Settings.ISO_DATE_PATTERN, v):
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


__all__ = ["FlextTapOracleWmsSettings"]

"""Configuration contracts for FLEXT Tap Oracle WMS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Annotated, ClassVar, override

from pydantic import SecretStr, field_validator
from pydantic.networks import AnyUrl
from pydantic_settings import SettingsConfigDict

from flext_core import FlextSettings
from flext_tap_oracle_wms import c, m, p, r, t


@FlextSettings.auto_register("tap-oracle-wms")
class FlextTapOracleWmsSettings(FlextSettings):
    """Validated settings consumed by the Oracle WMS tap runtime."""

    model_config: ClassVar[SettingsConfigDict] = m.SettingsConfigDict(
        env_prefix="FLEXT_TAP_ORACLE_WMS_", extra="ignore", validate_assignment=True
    )

    base_url: Annotated[
        str | AnyUrl,
        m.Field(description="Base Oracle WMS API URL."),
    ]
    username: Annotated[
        str,
        m.Field(min_length=1, description="Oracle WMS username."),
    ]
    password: Annotated[
        str | SecretStr,
        m.Field(description="Oracle WMS password."),
    ]
    api_version: Annotated[
        str,
        m.Field(
            min_length=1,
            description="Oracle WMS API version.",
        ),
    ] = c.TapOracleWms.Settings.DEFAULT_API_VERSION
    timeout: Annotated[
        int,
        m.Field(
            ge=c.TapOracleWms.Settings.TAP_MIN_TIMEOUT,
            le=c.TapOracleWms.Settings.TAP_MAX_TIMEOUT,
            description="Request timeout in seconds.",
        ),
    ] = c.TapOracleWms.Settings.TAP_DEFAULT_TIMEOUT
    max_retries: Annotated[
        int,
        m.Field(
            ge=0,
            description="Maximum request retries.",
        ),
    ] = c.TapOracleWms.Settings.TAP_DEFAULT_MAX_RETRIES
    retry_delay: Annotated[
        int,
        m.Field(
            ge=0,
            description="Retry delay in seconds.",
        ),
    ] = int(c.TapOracleWms.Settings.TAP_DEFAULT_RETRY_DELAY)
    verify_ssl: Annotated[
        bool,
        m.Field(description="Enable SSL verification."),
    ] = c.TapOracleWms.Settings.DEFAULT_VERIFY_SSL
    ssl_cert_path: Annotated[
        str | None,
        m.Field(description="Path to SSL certificate."),
    ] = None
    page_size: Annotated[
        int,
        m.Field(
            ge=1,
            description="Page size used for extraction requests.",
        ),
    ] = c.TapOracleWms.Settings.TAP_DEFAULT_PAGE_SIZE
    discovery_sample_size: Annotated[
        int,
        m.Field(
            ge=1,
            description="Sample size for schema discovery.",
        ),
    ] = c.TapOracleWms.Settings.DEFAULT_DISCOVERY_SAMPLE_SIZE
    include_entities: Annotated[
        t.StrSequence,
        m.Field(description="Entities to include."),
    ] = m.Field(default_factory=list)
    exclude_entities: Annotated[
        t.StrSequence,
        m.Field(description="Entities to exclude."),
    ] = m.Field(default_factory=list)
    start_date: Annotated[
        str | None,
        m.Field(description="Start date for incremental extraction."),
    ] = None
    end_date: Annotated[
        str | None,
        m.Field(description="End date for incremental extraction."),
    ] = None
    column_mappings: Annotated[
        Mapping[str, t.StrMapping],
        m.Field(description="Column rename mappings per stream."),
    ] = m.Field(default_factory=dict)
    ignored_columns: Annotated[
        t.StrSequence,
        m.Field(description="Columns to ignore during extraction."),
    ] = m.Field(default_factory=list)
    enable_parallel_extraction: Annotated[
        bool,
        m.Field(description="Enable parallel stream extraction."),
    ] = c.TapOracleWms.Settings.DEFAULT_ENABLE_PARALLEL_EXTRACTION
    max_parallel_streams: Annotated[
        int,
        m.Field(
            ge=1,
            description="Maximum parallel streams.",
        ),
    ] = c.TapOracleWms.Settings.DEFAULT_MAX_PARALLEL_STREAMS
    enable_rate_limiting: Annotated[
        bool,
        m.Field(description="Enable API rate limiting."),
    ] = c.TapOracleWms.Settings.DEFAULT_ENABLE_RATE_LIMITING
    max_requests_per_minute: Annotated[
        int,
        m.Field(ge=1, description="Maximum API requests per minute."),
    ] = c.TapOracleWms.Settings.DEFAULT_MAX_REQUESTS_PER_MINUTE
    enable_schema_flattening: Annotated[
        bool,
        m.Field(description="Enable schema flattening."),
    ] = c.TapOracleWms.Settings.DEFAULT_ENABLE_SCHEMA_FLATTENING
    max_flattening_depth: Annotated[
        int,
        m.Field(
            ge=1,
            description="Maximum schema flattening depth.",
        ),
    ] = c.TapOracleWms.Settings.DEFAULT_FLATTENING_DEPTH
    user_agent: Annotated[
        str | None,
        m.Field(description="Custom User-Agent header."),
    ] = None
    additional_headers: Annotated[
        t.StrMapping,
        m.Field(description="Additional HTTP headers."),
    ] = m.Field(default_factory=dict)
    log_level: Annotated[
        c.LogLevel,
        m.Field(description="Log level."),
    ] = c.LogLevel.INFO
    enable_request_logging: Annotated[
        bool,
        m.Field(description="Enable HTTP request logging."),
    ] = c.TapOracleWms.Settings.DEFAULT_ENABLE_REQUEST_LOGGING
    validate_config: Annotated[
        bool,
        m.Field(description="Enable configuration validation."),
    ] = c.TapOracleWms.Settings.DEFAULT_VALIDATE_CONFIG
    validate_schemas: Annotated[
        bool,
        m.Field(description="Enable schema validation."),
    ] = c.TapOracleWms.Settings.DEFAULT_VALIDATE_SCHEMAS

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
        if v is not None and not re.match(c.TapOracleWms.Settings.ISO_DATE_PATTERN, v):
            msg = f"Invalid date format: {v}. Expected ISO 8601 format."
            raise ValueError(msg)
        return v

    @classmethod
    @override
    def reset_for_testing(cls) -> None:
        """Reset any cached state for test isolation."""
        cls._reset_instance()

    def validate_domain_rules(self) -> p.Result[bool]:
        """Validate domain-specific rules."""
        return self.validate_business_rules()

    def validate_business_rules(self) -> p.Result[bool]:
        """Validate Oracle WMS business rules."""
        overlap = set(self.include_entities) & set(self.exclude_entities)
        if overlap:
            return r[bool].fail(
                f"Entities {overlap} cannot be both included and excluded",
            )
        if self.start_date and self.end_date and self.start_date > self.end_date:
            return r[bool].fail("start_date must be <= end_date")
        return r[bool].ok(True)


__all__: list[str] = ["FlextTapOracleWmsSettings"]

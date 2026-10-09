"""FLEXT Tap Oracle WMS settings — namespaced under ``settings.TapOracleWms``.

Universal fields via MRO; project fields in the ``TapOracleWms`` group with
simple scalar types (env-settable). Domain/business validation lives at the
model boundary, not in settings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from typing import Annotated

from flext_core import FlextSettings, m, t

_ISO_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$",
)


class FlextTapOracleWmsSettings(FlextSettings):
    """Oracle WMS Singer tap settings; fields under ``settings.TapOracleWms.*``."""

    model_config = m.SettingsConfigDict(
        env_prefix="FLEXT_TAP_ORACLE_WMS_",
        env_nested_delimiter="__",
        extra="ignore",
        validate_assignment=True,
    )

    class TapOracleWmsSettings(m.BaseModel):
        """Namespaced Oracle WMS tap settings (simple scalars only)."""

        base_url: Annotated[str, m.Field(description="Base Oracle WMS API URL")] = ""
        username: Annotated[str, m.Field(description="Oracle WMS username")] = ""
        password: Annotated[str, m.Field(description="Oracle WMS password")] = ""
        api_version: Annotated[
            str,
            m.Field(min_length=1, description="Oracle WMS API version"),
        ] = "V1"
        timeout: Annotated[
            int,
            m.Field(ge=1, le=300, description="Request timeout (s)"),
        ] = 30
        max_retries: Annotated[int, m.Field(ge=0, description="Max retries")] = 3
        retry_delay: Annotated[
            float,
            m.Field(ge=0, description="Retry delay (s)"),
        ] = 1.0
        verify_ssl: Annotated[bool, m.Field(description="Verify SSL")] = True
        ssl_cert_path: Annotated[
            str | None,
            m.Field(description="Path to SSL certificate"),
        ] = None
        page_size: Annotated[int, m.Field(ge=1, description="Page size")] = 10
        discovery_sample_size: Annotated[
            int,
            m.Field(ge=1, description="Schema discovery sample size"),
        ] = 100
        include_entities: Annotated[
            list[str],
            m.Field(description="Entities to include"),
        ] = m.Field(default_factory=list[str])
        exclude_entities: Annotated[
            list[str],
            m.Field(description="Entities to exclude"),
        ] = m.Field(default_factory=list[str])
        start_date: Annotated[
            str | None,
            m.Field(description="Incremental extraction start date"),
        ] = None
        end_date: Annotated[
            str | None,
            m.Field(description="Incremental extraction end date"),
        ] = None
        column_mappings: Annotated[
            str,
            m.Field(description="Column rename mappings per stream (JSON)"),
        ] = "{}"
        ignored_columns: Annotated[
            list[str],
            m.Field(description="Columns to ignore"),
        ] = m.Field(default_factory=list[str])
        enable_parallel_extraction: Annotated[
            bool,
            m.Field(description="Enable parallel stream extraction"),
        ] = False
        max_parallel_streams: Annotated[
            int,
            m.Field(ge=1, description="Maximum parallel streams"),
        ] = 5
        enable_rate_limiting: Annotated[
            bool,
            m.Field(description="Enable API rate limiting"),
        ] = True
        max_requests_per_minute: Annotated[
            int,
            m.Field(ge=1, description="Maximum API requests per minute"),
        ] = 60
        enable_schema_flattening: Annotated[
            bool,
            m.Field(description="Enable schema flattening"),
        ] = True
        max_flattening_depth: Annotated[
            int,
            m.Field(ge=1, description="Maximum schema flattening depth"),
        ] = 10
        user_agent: Annotated[
            str | None,
            m.Field(description="Custom User-Agent header"),
        ] = None
        additional_headers: Annotated[
            t.StrMapping,
            m.Field(description="Additional HTTP headers"),
        ] = m.Field(default_factory=dict[str, str])
        log_level: Annotated[str, m.Field(description="Log level")] = "INFO"
        enable_request_logging: Annotated[
            bool,
            m.Field(description="Enable HTTP request logging"),
        ] = False
        validate_config: Annotated[
            bool,
            m.Field(description="Enable configuration validation"),
        ] = True
        validate_schemas: Annotated[
            bool,
            m.Field(description="Enable schema validation"),
        ] = True

        @m.field_validator("include_entities", "exclude_entities")
        @classmethod
        def _check_no_duplicates(cls, v: list[str]) -> list[str]:
            if len(v) != len(set(v)):
                msg = "Entity list contains duplicates"
                raise ValueError(msg)
            return v

        @m.field_validator("start_date", "end_date")
        @classmethod
        def _check_iso_date(cls, v: str | None) -> str | None:
            if v is not None and not _ISO_DATE_RE.match(v):
                msg = f"Invalid date format: {v}. Expected ISO 8601 format."
                raise ValueError(msg)
            return v

    TapOracleWms: TapOracleWmsSettings = m.Field(
        default_factory=TapOracleWmsSettings,
        description="Namespaced Oracle WMS tap settings.",
    )


settings: FlextTapOracleWmsSettings = FlextTapOracleWmsSettings.fetch_global()
"""Pre-instantiated project settings singleton.

Exposed as ``from flext_tap_oracle_wms import settings``.
"""

__all__: list[str] = ["FlextTapOracleWmsSettings", "settings"]

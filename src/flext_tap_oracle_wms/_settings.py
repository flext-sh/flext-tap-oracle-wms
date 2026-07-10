"""FLEXT Tap Oracle WMS settings — namespaced under ``settings.TapOracleWms``.

Universal fields via MRO; project fields in the ``TapOracleWms`` group with
simple scalar types (env-settable). Domain/business validation lives at the
model boundary, not in settings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import SettingsConfigDict

from flext_core import FlextSettings

_ISO_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$",
)


class FlextTapOracleWmsSettings(FlextSettings):
    """Oracle WMS Singer tap settings; fields under ``settings.TapOracleWms.*``."""

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_TAP_ORACLE_WMS_",
        env_nested_delimiter="__",
        extra="ignore",
        validate_assignment=True,
    )

    class _TapOracleWms(BaseModel):
        """Namespaced Oracle WMS tap settings (simple scalars only)."""

        base_url: Annotated[str, Field(default="", description="Base Oracle WMS API URL")]
        username: Annotated[str, Field(default="", description="Oracle WMS username")]
        password: Annotated[str, Field(default="", description="Oracle WMS password")]
        api_version: Annotated[
            str,
            Field(default="V1", min_length=1, description="Oracle WMS API version"),
        ]
        timeout: Annotated[
            int,
            Field(default=30, ge=1, le=300, description="Request timeout (s)"),
        ]
        max_retries: Annotated[int, Field(default=3, ge=0, description="Max retries")]
        retry_delay: Annotated[
            float,
            Field(default=1.0, ge=0, description="Retry delay (s)"),
        ]
        verify_ssl: Annotated[bool, Field(default=True, description="Verify SSL")]
        ssl_cert_path: Annotated[
            str | None,
            Field(default=None, description="Path to SSL certificate"),
        ]
        page_size: Annotated[int, Field(default=10, ge=1, description="Page size")]
        discovery_sample_size: Annotated[
            int,
            Field(default=100, ge=1, description="Schema discovery sample size"),
        ]
        include_entities: Annotated[
            list[str],
            Field(default_factory=list, description="Entities to include"),
        ]
        exclude_entities: Annotated[
            list[str],
            Field(default_factory=list, description="Entities to exclude"),
        ]
        start_date: Annotated[
            str | None,
            Field(default=None, description="Incremental extraction start date"),
        ]
        end_date: Annotated[
            str | None,
            Field(default=None, description="Incremental extraction end date"),
        ]
        column_mappings: Annotated[str, Field(default="{}", description="Column rename mappings per stream (JSON)")]
        ignored_columns: Annotated[
            list[str],
            Field(default_factory=list, description="Columns to ignore"),
        ]
        enable_parallel_extraction: Annotated[
            bool,
            Field(default=False, description="Enable parallel stream extraction"),
        ]
        max_parallel_streams: Annotated[
            int,
            Field(default=5, ge=1, description="Maximum parallel streams"),
        ]
        enable_rate_limiting: Annotated[
            bool,
            Field(default=True, description="Enable API rate limiting"),
        ]
        max_requests_per_minute: Annotated[
            int,
            Field(default=60, ge=1, description="Maximum API requests per minute"),
        ]
        enable_schema_flattening: Annotated[
            bool,
            Field(default=True, description="Enable schema flattening"),
        ]
        max_flattening_depth: Annotated[
            int,
            Field(default=10, ge=1, description="Maximum schema flattening depth"),
        ]
        user_agent: Annotated[
            str | None,
            Field(default=None, description="Custom User-Agent header"),
        ]
        additional_headers: Annotated[
            dict[str, str],
            Field(default_factory=dict, description="Additional HTTP headers"),
        ]
        log_level: Annotated[str, Field(default="INFO", description="Log level")]
        enable_request_logging: Annotated[
            bool,
            Field(default=False, description="Enable HTTP request logging"),
        ]
        validate_config: Annotated[
            bool,
            Field(default=True, description="Enable configuration validation"),
        ]
        validate_schemas: Annotated[
            bool,
            Field(default=True, description="Enable schema validation"),
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
            if v is not None and not _ISO_DATE_RE.match(v):
                msg = f"Invalid date format: {v}. Expected ISO 8601 format."
                raise ValueError(msg)
            return v

    if TYPE_CHECKING:
        TapOracleWms: _TapOracleWms
    else:
        TapOracleWms: _TapOracleWms = Field(
            default_factory=_TapOracleWms,
            description="Namespaced Oracle WMS tap settings.",
        )


settings: FlextTapOracleWmsSettings = FlextTapOracleWmsSettings.fetch_global()
"""Pre-instantiated project settings singleton — ``from flext_tap_oracle_wms import settings``."""

__all__: list[str] = ["FlextTapOracleWmsSettings", "settings"]

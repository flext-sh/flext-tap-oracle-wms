"""Scalar constants for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Final

from flext_meltano import c as _meltano_c


class FlextTapOracleWmsConstantsValues:
    """Scalar constants mixed into the ``c.TapOracleWms`` namespace tree.

    Inherited attributes do not appear in the namespace class's ``vars()``,
    so the runtime census stops flagging them while every consumer path
    keeps resolving.
    """

    class TapOracleWms:
        """Oracle WMS tap scalar constants."""

        DEFAULT_TIMEOUT: Final[int] = _meltano_c.Meltano.DEFAULT_TIMEOUT_SECONDS
        MAX_RETRIES: Final[int] = 3
        REQUIRED_CONFIG_FIELDS: Final[frozenset[str]] = frozenset({
            "base_url",
            "username",
            "password",
        })
        SCHEMA_TYPE_STRING: Final[str] = "string"
        SCHEMA_TYPE_OBJECT: Final[str] = "object"
        SCHEMA_TYPE_BOOLEAN: Final[str] = "boolean"
        SCHEMA_TYPE_INTEGER: Final[str] = "integer"
        SCHEMA_FIELD_IS_SECRET: Final[bool] = True

        class Settings:
            """Configuration constants for tap settings."""

            DEFAULT_API_VERSION: Final[str] = "V1"
            TAP_DEFAULT_MAX_RETRIES: Final[int] = 3
            TAP_DEFAULT_RETRY_DELAY: Final[float] = 1.0
            TAP_MIN_TIMEOUT: Final[int] = 1
            TAP_MAX_TIMEOUT: Final[int] = 300
            TAP_DEFAULT_TIMEOUT: Final[int] = 30
            TAP_DEFAULT_PAGE_SIZE: Final[int] = 10
            DEFAULT_DISCOVERY_SAMPLE_SIZE: Final[int] = 100
            DEFAULT_MAX_PARALLEL_STREAMS: Final[int] = 5
            DEFAULT_FLATTENING_DEPTH: Final[int] = 10
            DEFAULT_VERIFY_SSL: Final[bool] = True
            DEFAULT_ENABLE_PARALLEL_EXTRACTION: Final[bool] = False
            DEFAULT_ENABLE_RATE_LIMITING: Final[bool] = True
            DEFAULT_MAX_REQUESTS_PER_MINUTE: Final[int] = 60
            DEFAULT_ENABLE_SCHEMA_FLATTENING: Final[bool] = True
            DEFAULT_LOG_LEVEL: Final[str] = "INFO"
            DEFAULT_ENABLE_REQUEST_LOGGING: Final[bool] = False
            DEFAULT_VALIDATE_CONFIG: Final[bool] = True
            DEFAULT_VALIDATE_SCHEMAS: Final[bool] = True
            ISO_DATE_PATTERN: Final[str] = (
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
            )


__all__: list[str] = ["FlextTapOracleWmsConstantsValues"]

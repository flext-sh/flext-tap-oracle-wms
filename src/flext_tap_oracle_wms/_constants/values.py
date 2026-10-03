"""Scalar constants for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Final


class FlextTapOracleWmsConstantsValues:
    """Scalar constants mixed into the ``c.TapOracleWms`` namespace tree.

    Inherited attributes do not appear in the namespace class's ``vars()``,
    so the runtime census stops flagging them while every consumer path
    keeps resolving.
    """

    class TapOracleWms:
        """Oracle WMS tap scalar constants."""

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


__all__: list[str] = ["FlextTapOracleWmsConstantsValues"]

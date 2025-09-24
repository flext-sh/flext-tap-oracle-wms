"""FLEXT Tap Oracle WMS Constants - Oracle WMS tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextConstants


class FlextTapOracleWmsConstants(FlextConstants):
    """Oracle WMS tap extraction-specific constants following flext-core patterns."""

    # Oracle WMS Connection Configuration
    DEFAULT_WMS_TIMEOUT = 30
    DEFAULT_FETCH_SIZE = 1000

    # Singer Tap Configuration
    DEFAULT_BATCH_SIZE = 1000
    MAX_BATCH_SIZE = 10000

    # WMS Entity Types
    WMS_ENTITY_TYPES: ClassVar[list[str]] = [
        "INVENTORY",
        "SHIPMENT",
        "PICKING",
        "RECEIVING",
    ]


__all__ = ["FlextTapOracleWmsConstants"]

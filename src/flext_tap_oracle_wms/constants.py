"""FLEXT Tap Oracle WMS Constants - Oracle WMS tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_oracle_wms.constants import FlextOracleWmsConstants

from flext_core import FlextConstants


class FlextTapOracleWmsConstants(FlextConstants):
    """Oracle WMS tap extraction-specific constants following flext-core patterns.

    Composes with FlextOracleWmsConstants to avoid duplication and ensure consistency.
    """

    # Oracle WMS Connection Configuration
    DEFAULT_WMS_TIMEOUT = FlextOracleWmsConstants.Connection.DEFAULT_TIMEOUT
    DEFAULT_FETCH_SIZE = FlextOracleWmsConstants.Processing.DEFAULT_BATCH_SIZE

    # Singer Tap Configuration - using FlextConstants composition
    DEFAULT_BATCH_SIZE = FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE
    MAX_BATCH_SIZE = FlextConstants.Performance.BatchProcessing.MAX_ITEMS

    # WMS Entity Types from Oracle WMS constants
    WMS_ENTITY_TYPES: ClassVar[list[str]] = [
        "INVENTORY",
        "SHIPMENT",
        "PICKING",
        "RECEIVING",
    ]

    class Connection:
        """Oracle WMS connection configuration."""

        DEFAULT_HOST = FlextOracleWmsConstants.Connection.DEFAULT_HOST
        DEFAULT_PORT = FlextOracleWmsConstants.Connection.DEFAULT_PORT
        DEFAULT_TIMEOUT = FlextOracleWmsConstants.Connection.DEFAULT_TIMEOUT
        MAX_RETRIES = FlextOracleWmsConstants.Connection.DEFAULT_MAX_RETRIES

    class Processing:
        """WMS tap processing configuration."""

        DEFAULT_PAGE_SIZE = FlextOracleWmsConstants.Processing.DEFAULT_BATCH_SIZE
        MAX_RECORDS_PER_BATCH = FlextOracleWmsConstants.Processing.MAX_BATCH_SIZE
        DEFAULT_API_TIMEOUT = FlextOracleWmsConstants.Connection.DEFAULT_TIMEOUT

    class Extraction:
        """WMS-specific extraction configuration."""

        DEFAULT_ENTITY_LIMIT = FlextOracleWmsConstants.Processing.DEFAULT_BATCH_SIZE
        DEFAULT_DISCOVERY_TIMEOUT = FlextOracleWmsConstants.Connection.DEFAULT_TIMEOUT
        MAX_ENTITY_BATCH_SIZE = FlextOracleWmsConstants.Processing.MAX_BATCH_SIZE


__all__ = ["FlextTapOracleWmsConstants"]

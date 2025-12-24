"""FLEXT Tap Oracle WMS Constants - Oracle WMS tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum
from typing import Final, Literal

from flext_oracle_wms.constants import FlextOracleWmsConstants

from flext import FlextConstants


class FlextTapOracleWmsConstants(FlextConstants):
    """Oracle WMS tap extraction-specific constants following flext-core patterns.

    Composes with FlextOracleWmsConstants to avoid duplication and ensure consistency.
    """

    # Oracle WMS Connection Configuration
    DEFAULT_WMS_TIMEOUT: Final[int] = FlextOracleWmsConstants.Connection.DEFAULT_TIMEOUT
    DEFAULT_FETCH_SIZE: Final[int] = (
        FlextOracleWmsConstants.WmsProcessing.DEFAULT_BATCH_SIZE
    )

    # Singer Tap Configuration - using FlextConstants composition
    # Note: DEFAULT_BATCH_SIZE inherited from FlextConstants (Final, cannot override)
    MAX_BATCH_SIZE: Final[int] = FlextConstants.Performance.BatchProcessing.MAX_ITEMS

    # WMS Entity Types - Oracle WMS tap-specific
    class WmsEntityType(StrEnum):
        """Oracle WMS entity types using StrEnum for type safety.

        DRY Pattern:
            StrEnum is the single source of truth. Use WmsEntityType.INVENTORY.value
            or WmsEntityType.INVENTORY directly - no base strings needed.
        """

        INVENTORY = "INVENTORY"
        SHIPMENT = "SHIPMENT"
        PICKING = "PICKING"
        RECEIVING = "RECEIVING"

    class Connection:
        """Oracle WMS connection configuration."""

        DEFAULT_TIMEOUT: Final[int] = FlextOracleWmsConstants.Connection.DEFAULT_TIMEOUT
        MAX_RETRIES: Final[int] = FlextOracleWmsConstants.Connection.DEFAULT_MAX_RETRIES

    class TapWmsProcessing:
        """WMS tap processing configuration.

        Note: Does not override parent Processing class to avoid inheritance conflicts.
        """

        DEFAULT_PAGE_SIZE: Final[int] = (
            FlextOracleWmsConstants.WmsProcessing.DEFAULT_BATCH_SIZE
        )
        MAX_RECORDS_PER_BATCH: Final[int] = (
            FlextOracleWmsConstants.WmsProcessing.MAX_BATCH_SIZE
        )
        DEFAULT_API_TIMEOUT: Final[int] = (
            FlextOracleWmsConstants.Connection.DEFAULT_TIMEOUT
        )
        ORACLE_WMS_PAGE_SIZE_LIMIT: Final[int] = 1250
        USERNAME_TRUNCATION_LENGTH: Final[int] = 3
        HIGH_ALLOCATION_THRESHOLD: Final[float] = 0.8
        MEDIUM_ALLOCATION_THRESHOLD: Final[float] = 0.5

    class Extraction:
        """WMS-specific extraction configuration."""

        DEFAULT_ENTITY_LIMIT: Final[int] = (
            FlextOracleWmsConstants.WmsProcessing.DEFAULT_BATCH_SIZE
        )
        DEFAULT_DISCOVERY_TIMEOUT: Final[int] = (
            FlextOracleWmsConstants.Connection.DEFAULT_TIMEOUT
        )
        MAX_ENTITY_BATCH_SIZE: Final[int] = (
            FlextOracleWmsConstants.WmsProcessing.MAX_BATCH_SIZE
        )

    # Type-safe literals - PEP 695 syntax for type checking
    # All Literal types reference StrEnum members where available - NO string duplication!
    type WmsEntityTypeLiteral = Literal[
        WmsEntityType.INVENTORY,
        WmsEntityType.SHIPMENT,
        WmsEntityType.PICKING,
        WmsEntityType.RECEIVING,
    ]
    """Oracle WMS entity type literal - references WmsEntityType StrEnum members."""


c = FlextTapOracleWmsConstants

__all__ = ["FlextTapOracleWmsConstants", "c"]

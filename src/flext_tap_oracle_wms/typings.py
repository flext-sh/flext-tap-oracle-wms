"""FLEXT Tap Oracle WMS Types - Domain-specific Singer Oracle WMS tap type definitions.

This module provides Singer Oracle WMS tap-specific type definitions extending FlextTypes.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends FlextTypes properly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

from flext_core import FlextTypes

# =============================================================================
# TAP ORACLE WMS-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for Singer Oracle WMS operations
# =============================================================================


# Singer Oracle WMS tap domain TypeVars
class FlextTapOracleWmsTypes(FlextTypes):
    """Singer Oracle WMS tap-specific type definitions extending FlextTypes.

    Domain-specific type system for Singer Oracle WMS tap operations.
    Contains ONLY complex Oracle WMS tap-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # SINGER TAP TYPES - Complex Singer protocol types
    # =========================================================================

    class SingerTap:
        """Singer tap protocol complex types."""

        type TapConfiguration = dict[
            str, str | int | bool | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type StreamConfiguration = dict[
            str, str | bool | dict[str, FlextTypes.Core.JsonValue]
        ]
        type CatalogDefinition = dict[
            str, str | list[dict[str, FlextTypes.Core.JsonValue]]
        ]
        type SchemaDefinition = dict[
            str, str | dict[str, FlextTypes.Core.JsonValue] | bool
        ]
        type MessageOutput = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type StateManagement = dict[
            str, str | int | dict[str, FlextTypes.Core.JsonValue]
        ]

    # =========================================================================
    # ORACLE WMS WAREHOUSE TYPES - Complex warehouse management types
    # =========================================================================

    class WmsWarehouse:
        """Oracle WMS warehouse management complex types."""

        type WarehouseConfiguration = dict[
            str, str | int | bool | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type FacilityDefinition = dict[
            str, str | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        type LocationManagement = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type ZoneConfiguration = dict[str, str | dict[str, object]]
        type WarehouseMetadata = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type LayoutDefinition = dict[str, str | bool | dict[str, object]]

    # =========================================================================
    # WMS INVENTORY TYPES - Complex inventory management types
    # =========================================================================

    class WmsInventory:
        """Oracle WMS inventory management complex types."""

        type InventoryConfiguration = dict[
            str, str | int | bool | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type ItemMasterData = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type StockLevelTracking = dict[
            str, int | float | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type AllocationManagement = dict[str, int | str | dict[str, object]]
        type InventoryMetrics = dict[
            str, int | float | dict[str, FlextTypes.Core.JsonValue]
        ]
        type CycleCountData = dict[str, str | int | dict[str, object]]

    # =========================================================================
    # WMS ORDER MANAGEMENT TYPES - Complex order processing types
    # =========================================================================

    class WmsOrderManagement:
        """Oracle WMS order management complex types."""

        type OrderConfiguration = dict[
            str, str | int | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type OrderProcessing = dict[
            str, str | bool | dict[str, FlextTypes.Core.JsonValue]
        ]
        type FulfillmentWorkflow = dict[str, str | int | dict[str, object]]
        type PickingInstructions = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type ShippingConfiguration = dict[
            str, bool | str | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type OrderTracking = dict[str, str | int | dict[str, object]]

    # =========================================================================
    # WMS LABOR MANAGEMENT TYPES - Complex workforce management types
    # =========================================================================

    class WmsLaborManagement:
        """Oracle WMS labor management complex types."""

        type LaborConfiguration = dict[
            str, str | bool | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type WorkforceManagement = dict[
            str, int | float | dict[str, FlextTypes.Core.JsonValue]
        ]
        type TaskAssignment = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type ProductivityMetrics = dict[str, float | int | dict[str, object]]
        type PerformanceTracking = dict[
            str, int | float | dict[str, FlextTypes.Core.JsonValue]
        ]
        type WorkforceScheduling = dict[str, str | int | dict[str, object]]

    # =========================================================================
    # WMS TRANSPORTATION TYPES - Complex transportation management types
    # =========================================================================

    class WmsTransportation:
        """Oracle WMS transportation management complex types."""

        type TransportConfiguration = dict[
            str, str | int | bool | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type CarrierManagement = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type ShipmentTracking = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type DeliveryScheduling = dict[str, str | bool | dict[str, object]]
        type TransportMetrics = dict[
            str, int | float | dict[str, FlextTypes.Core.JsonValue]
        ]
        type RouteOptimization = dict[str, str | list[str] | dict[str, object]]

    # =========================================================================
    # DATA EXTRACTION TYPES - Complex data extraction types
    # =========================================================================

    class DataExtraction:
        """Data extraction complex types."""

        type ExtractionConfiguration = dict[
            str, str | bool | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type ExtractionFilter = dict[str, str | list[str] | dict[str, object]]
        type ExtractionMapping = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type ExtractionResult = dict[str, bool | list[dict[str, object]]]
        type ExtractionMetrics = dict[
            str, int | float | dict[str, FlextTypes.Core.JsonValue]
        ]
        type ExtractionState = dict[
            str, str | int | dict[str, FlextTypes.Core.JsonValue]
        ]

    # =========================================================================
    # STREAM PROCESSING TYPES - Complex stream handling types
    # =========================================================================

    class StreamProcessing:
        """Stream processing complex types."""

        type StreamConfiguration = dict[
            str, str | bool | int | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type StreamMetadata = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type StreamRecord = dict[str, FlextTypes.Core.JsonValue | dict[str, object]]
        type StreamState = dict[str, str | int | dict[str, FlextTypes.Core.JsonValue]]
        type StreamBookmark = dict[str, str | int | dict[str, object]]
        type StreamSchema = dict[str, str | dict[str, FlextTypes.Core.JsonValue] | bool]

    # =========================================================================
    # ERROR HANDLING TYPES - Complex error management types
    # =========================================================================

    class ErrorHandling:
        """Error handling complex types."""

        type ErrorConfiguration = dict[
            str, bool | str | int | dict[str, FlextTypes.Core.ConfigValue]
        ]
        type ErrorRecovery = dict[str, str | bool | dict[str, object]]
        type ErrorReporting = dict[
            str, str | int | dict[str, FlextTypes.Core.JsonValue]
        ]
        type ErrorClassification = dict[str, str | int | dict[str, object]]
        type ErrorMetrics = dict[
            str, int | float | dict[str, FlextTypes.Core.JsonValue]
        ]
        type ErrorTracking = list[
            dict[str, str | int | dict[str, FlextTypes.Core.JsonValue]]
        ]

    # =========================================================================
    # SINGER TAP ORACLE WMS PROJECT TYPES - Domain-specific project types extending FlextTypes
    # =========================================================================

    class Project(FlextTypes.Project):
        """Singer Tap Oracle WMS-specific project types extending FlextTypes.Project.

        Adds Singer tap Oracle WMS-specific project types while inheriting
        generic types from FlextTypes. Follows domain separation principle:
        Singer tap Oracle WMS domain owns WMS extraction and Singer protocol-specific types.
        """

        # Singer tap Oracle WMS-specific project types extending the generic ones
        type ProjectType = Literal[
            # Generic types inherited from FlextTypes.Project
            "library",
            "application",
            "service",
            # Singer tap Oracle WMS-specific types
            "singer-tap",
            "wms-extractor",
            "warehouse-extractor",
            "singer-tap-oracle-wms",
            "tap-oracle-wms",
            "wms-connector",
            "warehouse-connector",
            "singer-protocol",
            "wms-integration",
            "oracle-wms",
            "warehouse-management",
            "singer-stream",
            "etl-tap",
            "data-pipeline",
            "wms-tap",
            "singer-integration",
        ]

        # Singer tap Oracle WMS-specific project configurations
        type SingerTapOracleWmsProjectConfig = dict[
            str, FlextTypes.Core.ConfigValue | object
        ]
        type WmsExtractorConfig = dict[str, str | int | bool | list[str]]
        type SingerProtocolConfig = dict[str, bool | str | dict[str, object]]
        type TapOracleWmsPipelineConfig = dict[
            str, FlextTypes.Core.ConfigValue | object
        ]


# =============================================================================
# PUBLIC API EXPORTS - Singer Oracle WMS tap TypeVars and types
# =============================================================================

__all__: list[str] = [
    "FlextTapOracleWmsTypes",
]

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

from flext import FlextTypes

# =============================================================================
# TAP ORACLE WMS-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for Singer Oracle WMS operations
# =============================================================================


# Singer Oracle WMS tap domain TypeVars
class FlextMeltanoTapOracleWmsTypes(FlextTypes):
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

        type TapConfiguration = dict[str, str | int | bool | dict[str, object]]
        type StreamConfiguration = dict[
            str, str | bool | dict[str, FlextTypes.JsonValue],
        ]
        type CatalogDefinition = dict[str, str | list[dict[str, FlextTypes.JsonValue]]]
        type SchemaDefinition = dict[str, str | dict[str, FlextTypes.JsonValue] | bool]
        type MessageOutput = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type StateManagement = dict[str, str | int | dict[str, FlextTypes.JsonValue]]

    # =========================================================================
    # ORACLE WMS WAREHOUSE TYPES - Complex warehouse management types
    # =========================================================================

    class WmsWarehouse:
        """Oracle WMS warehouse management complex types."""

        type WarehouseConfiguration = dict[str, str | int | bool | dict[str, object]]
        type FacilityDefinition = dict[
            str, str | list[str] | dict[str, FlextTypes.JsonValue],
        ]
        type LocationManagement = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type ZoneConfiguration = dict[str, str | dict[str, object]]
        type WarehouseMetadata = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type LayoutDefinition = dict[str, str | bool | dict[str, object]]

    # =========================================================================
    # WMS INVENTORY TYPES - Complex inventory management types
    # =========================================================================

    class WmsInventory:
        """Oracle WMS inventory management complex types."""

        type InventoryConfiguration = dict[str, str | int | bool | dict[str, object]]
        type ItemMasterData = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type StockLevelTracking = dict[str, int | float | dict[str, object]]
        type AllocationManagement = dict[str, int | str | dict[str, object]]
        type InventoryMetrics = dict[str, int | float | dict[str, FlextTypes.JsonValue]]
        type CycleCountData = dict[str, str | int | dict[str, object]]

    # =========================================================================
    # WMS ORDER MANAGEMENT TYPES - Complex order processing types
    # =========================================================================

    class WmsOrderManagement:
        """Oracle WMS order management complex types."""

        type OrderConfiguration = dict[str, str | int | dict[str, object]]
        type OrderProcessing = dict[str, str | bool | dict[str, FlextTypes.JsonValue]]
        type FulfillmentWorkflow = dict[str, str | int | dict[str, object]]
        type PickingInstructions = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type ShippingConfiguration = dict[str, bool | str | dict[str, object]]
        type OrderTracking = dict[str, str | int | dict[str, object]]

    # =========================================================================
    # WMS LABOR MANAGEMENT TYPES - Complex workforce management types
    # =========================================================================

    class WmsLaborManagement:
        """Oracle WMS labor management complex types."""

        type LaborConfiguration = dict[str, str | bool | dict[str, object]]
        type WorkforceManagement = dict[
            str, int | float | dict[str, FlextTypes.JsonValue],
        ]
        type TaskAssignment = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type ProductivityMetrics = dict[str, float | int | dict[str, object]]
        type PerformanceTracking = dict[
            str, int | float | dict[str, FlextTypes.JsonValue],
        ]
        type WorkforceScheduling = dict[str, str | int | dict[str, object]]

    # =========================================================================
    # WMS TRANSPORTATION TYPES - Complex transportation management types
    # =========================================================================

    class WmsTransportation:
        """Oracle WMS transportation management complex types."""

        type TransportConfiguration = dict[str, str | int | bool | dict[str, object]]
        type CarrierManagement = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type ShipmentTracking = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type DeliveryScheduling = dict[str, str | bool | dict[str, object]]
        type TransportMetrics = dict[str, int | float | dict[str, FlextTypes.JsonValue]]
        type RouteOptimization = dict[str, str | list[str] | dict[str, object]]

    # =========================================================================
    # DATA EXTRACTION TYPES - Complex data extraction types
    # =========================================================================

    class DataExtraction:
        """Data extraction complex types."""

        type ExtractionConfiguration = dict[str, str | bool | dict[str, object]]
        type ExtractionFilter = dict[str, str | list[str] | dict[str, object]]
        type ExtractionMapping = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type ExtractionResult = dict[str, bool | list[dict[str, object]]]
        type ExtractionMetrics = dict[
            str, int | float | dict[str, FlextTypes.JsonValue],
        ]
        type ExtractionState = dict[str, str | int | dict[str, FlextTypes.JsonValue]]

    # =========================================================================
    # STREAM PROCESSING TYPES - Complex stream handling types
    # =========================================================================

    class StreamProcessing:
        """Stream processing complex types."""

        type StreamConfiguration = dict[str, str | bool | int | dict[str, object]]
        type StreamMetadata = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type StreamRecord = dict[str, FlextTypes.JsonValue | dict[str, object]]
        type StreamState = dict[str, str | int | dict[str, FlextTypes.JsonValue]]
        type StreamBookmark = dict[str, str | int | dict[str, object]]
        type StreamSchema = dict[str, str | dict[str, FlextTypes.JsonValue] | bool]

    # =========================================================================
    # ERROR HANDLING TYPES - Complex error management types
    # =========================================================================

    class ErrorHandling:
        """Error handling complex types."""

        type ErrorConfiguration = dict[str, bool | str | int | dict[str, object]]
        type ErrorRecovery = dict[str, str | bool | dict[str, object]]
        type ErrorReporting = dict[str, str | int | dict[str, FlextTypes.JsonValue]]
        type ErrorClassification = dict[str, str | int | dict[str, object]]
        type ErrorMetrics = dict[str, int | float | dict[str, FlextTypes.JsonValue]]
        type ErrorTracking = list[
            dict[str, str | int | dict[str, FlextTypes.JsonValue]]
        ]

    # =========================================================================
    # SINGER TAP ORACLE WMS PROJECT TYPES - Domain-specific project types extending FlextTypes
    # =========================================================================

    class Project:
        """Singer Tap Oracle WMS-specific project types.

        Adds Singer tap Oracle WMS-specific project types.
        Follows domain separation principle:
        Singer tap Oracle WMS domain owns WMS extraction and Singer protocol-specific types.
        """

        # Singer tap Oracle WMS-specific project types extending the generic ones
        type ProjectType = Literal[
            # Generic types inherited from FlextTypes
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
        type SingerTapOracleWmsProjectConfig = dict[str, object]
        type WmsExtractorConfig = dict[str, str | int | bool | list[str]]
        type SingerProtocolConfig = dict[str, bool | str | dict[str, object]]
        type TapOracleWmsPipelineConfig = dict[str, object]


# =============================================================================
# PUBLIC API EXPORTS - Singer Oracle WMS tap TypeVars and types
# =============================================================================

t = FlextMeltanoTapOracleWmsTypes

__all__: list[str] = [
    "FlextMeltanoTapOracleWmsTypes",
]

"""Singer Oracle WMS tap protocols for FLEXT ecosystem."""

from typing import Protocol, runtime_checkable

from flext_core import FlextCore


class FlextMeltanoTapOracleWmsProtocols:
    """Singer Tap Oracle WMS protocols with explicit re-exports from FlextCore.Protocols foundation.

    Domain Extension Pattern (Phase 3):
    - Explicit re-export of foundation protocols (not inheritance)
    - Domain-specific protocols organized in TapOracleWms namespace
    - 100% backward compatibility through aliases
    """

    # ============================================================================
    # RE-EXPORT FOUNDATION PROTOCOLS (EXPLICIT PATTERN)
    # ============================================================================

    Foundation = FlextCore.Protocols.Foundation
    Domain = FlextCore.Protocols.Domain
    Application = FlextCore.Protocols.Application
    Infrastructure = FlextCore.Protocols.Infrastructure
    Extensions = FlextCore.Protocols.Extensions
    Commands = FlextCore.Protocols.Commands

    # ============================================================================
    # SINGER TAP ORACLE WMS-SPECIFIC PROTOCOLS (DOMAIN NAMESPACE)
    # ============================================================================

    class TapOracleWms:
        """Singer Tap Oracle WMS domain protocols for Oracle Warehouse Management System extraction."""

        @runtime_checkable
        class WmsConnectionProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Oracle WMS connection operations."""

            def establish_wms_connection(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[object]: ...

        @runtime_checkable
        class InventoryDiscoveryProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for WMS inventory discovery."""

            def discover_inventory(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[list[FlextCore.Types.Dict]]: ...

        @runtime_checkable
        class OrderProcessingProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for WMS order processing."""

            def process_orders(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[list[FlextCore.Types.Dict]]: ...

        @runtime_checkable
        class WarehouseOperationsProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for WMS warehouse operations."""

            def get_warehouse_operations(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[list[FlextCore.Types.Dict]]: ...

        @runtime_checkable
        class StreamGenerationProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Singer stream generation."""

            def generate_catalog(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[FlextCore.Types.Dict]: ...

        @runtime_checkable
        class PerformanceProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for WMS extraction performance."""

            def optimize_query(self, query: str) -> FlextCore.Result[str]: ...

        @runtime_checkable
        class ValidationProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for WMS data validation."""

            def validate_config(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[bool]: ...

        @runtime_checkable
        class MonitoringProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for WMS extraction monitoring."""

            def track_progress(
                self, entity: str, records: int
            ) -> FlextCore.Result[None]: ...

    # ============================================================================
    # BACKWARD COMPATIBILITY ALIASES (100% COMPATIBILITY)
    # ============================================================================

    WmsConnectionProtocol = TapOracleWms.WmsConnectionProtocol
    InventoryDiscoveryProtocol = TapOracleWms.InventoryDiscoveryProtocol
    OrderProcessingProtocol = TapOracleWms.OrderProcessingProtocol
    WarehouseOperationsProtocol = TapOracleWms.WarehouseOperationsProtocol
    StreamGenerationProtocol = TapOracleWms.StreamGenerationProtocol
    PerformanceProtocol = TapOracleWms.PerformanceProtocol
    ValidationProtocol = TapOracleWms.ValidationProtocol
    MonitoringProtocol = TapOracleWms.MonitoringProtocol

    TapOracleWmsConnectionProtocol = TapOracleWms.WmsConnectionProtocol
    TapOracleWmsInventoryDiscoveryProtocol = TapOracleWms.InventoryDiscoveryProtocol
    TapOracleWmsOrderProcessingProtocol = TapOracleWms.OrderProcessingProtocol
    TapOracleWmsWarehouseOperationsProtocol = TapOracleWms.WarehouseOperationsProtocol
    TapOracleWmsStreamGenerationProtocol = TapOracleWms.StreamGenerationProtocol
    TapOracleWmsPerformanceProtocol = TapOracleWms.PerformanceProtocol
    TapOracleWmsValidationProtocol = TapOracleWms.ValidationProtocol
    TapOracleWmsMonitoringProtocol = TapOracleWms.MonitoringProtocol


__all__ = [
    "FlextMeltanoTapOracleWmsProtocols",
]

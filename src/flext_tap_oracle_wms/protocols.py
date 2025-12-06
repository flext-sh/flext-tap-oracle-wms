"""Singer Oracle WMS tap protocols for FLEXT ecosystem."""

from typing import Protocol, runtime_checkable

from flext_core import FlextResult, p


class FlextMeltanoTapOracleWmsProtocols:
    """Singer Tap Oracle WMS protocols with explicit re-exports from p foundation.

    Domain Extension Pattern (Phase 3):
    - Explicit re-export of foundation protocols (not inheritance)
    - Domain-specific protocols organized in TapOracleWms namespace
    - 100% backward compatibility through aliases
    """

    # ============================================================================
    # RE-EXPORT FOUNDATION PROTOCOLS (EXPLICIT PATTERN)
    # ============================================================================

    # ============================================================================
    # SINGER TAP ORACLE WMS-SPECIFIC PROTOCOLS (DOMAIN NAMESPACE)
    # ============================================================================

    class TapOracleWms:
        """Singer Tap Oracle WMS domain protocols for Oracle Warehouse Management System extraction."""

        @runtime_checkable
        class WmsConnectionProtocol(p.Service, Protocol):
            """Protocol for Oracle WMS connection operations."""

            def establish_wms_connection(
                self,
                config: dict[str, object],
            ) -> FlextResult[object]: ...

        @runtime_checkable
        class InventoryDiscoveryProtocol(p.Service, Protocol):
            """Protocol for WMS inventory discovery."""

            def discover_inventory(
                self,
                config: dict[str, object],
            ) -> FlextResult[list[dict[str, object]]]: ...

        @runtime_checkable
        class OrderProcessingProtocol(p.Service, Protocol):
            """Protocol for WMS order processing."""

            def process_orders(
                self,
                config: dict[str, object],
            ) -> FlextResult[list[dict[str, object]]]: ...

        @runtime_checkable
        class WarehouseOperationsProtocol(p.Service, Protocol):
            """Protocol for WMS warehouse operations."""

            def get_warehouse_operations(
                self,
                config: dict[str, object],
            ) -> FlextResult[list[dict[str, object]]]: ...

        @runtime_checkable
        class StreamGenerationProtocol(p.Service, Protocol):
            """Protocol for Singer stream generation."""

            def generate_catalog(
                self,
                config: dict[str, object],
            ) -> FlextResult[dict[str, object]]: ...

        @runtime_checkable
        class PerformanceProtocol(p.Service, Protocol):
            """Protocol for WMS extraction performance."""

            def optimize_query(self, query: str) -> FlextResult[str]: ...

        @runtime_checkable
        class ValidationProtocol(p.Service, Protocol):
            """Protocol for WMS data validation."""

            def validate_config(
                self,
                config: dict[str, object],
            ) -> FlextResult[bool]: ...

        @runtime_checkable
        class MonitoringProtocol(p.Service, Protocol):
            """Protocol for WMS extraction monitoring."""

            def track_progress(
                self,
                entity: str,
                records: int,
            ) -> FlextResult[None]: ...

    # ============================================================================
    # BACKWARD COMPATIBILITY ALIASES (100% COMPATIBILITY)
    # ============================================================================

    @runtime_checkable
    class WmsConnectionProtocol(TapOracleWms.WmsConnectionProtocol):
        """WmsConnectionProtocol - real inheritance."""

    @runtime_checkable
    class InventoryDiscoveryProtocol(TapOracleWms.InventoryDiscoveryProtocol):
        """InventoryDiscoveryProtocol - real inheritance."""

    @runtime_checkable
    class OrderProcessingProtocol(TapOracleWms.OrderProcessingProtocol):
        """OrderProcessingProtocol - real inheritance."""

    @runtime_checkable
    class WarehouseOperationsProtocol(TapOracleWms.WarehouseOperationsProtocol):
        """WarehouseOperationsProtocol - real inheritance."""

    @runtime_checkable
    class StreamGenerationProtocol(TapOracleWms.StreamGenerationProtocol):
        """StreamGenerationProtocol - real inheritance."""

    @runtime_checkable
    class PerformanceProtocol(TapOracleWms.PerformanceProtocol):
        """PerformanceProtocol - real inheritance."""

    @runtime_checkable
    class ValidationProtocol(TapOracleWms.ValidationProtocol):
        """ValidationProtocol - real inheritance."""

    @runtime_checkable
    class MonitoringProtocol(TapOracleWms.MonitoringProtocol):
        """MonitoringProtocol - real inheritance."""

    @runtime_checkable
    class TapOracleWmsConnectionProtocol(TapOracleWms.WmsConnectionProtocol):
        """TapOracleWmsConnectionProtocol - real inheritance."""

    @runtime_checkable
    class TapOracleWmsInventoryDiscoveryProtocol(
        TapOracleWms.InventoryDiscoveryProtocol,
    ):
        """TapOracleWmsInventoryDiscoveryProtocol - real inheritance."""

    @runtime_checkable
    class TapOracleWmsOrderProcessingProtocol(TapOracleWms.OrderProcessingProtocol):
        """TapOracleWmsOrderProcessingProtocol - real inheritance."""

    @runtime_checkable
    class TapOracleWmsWarehouseOperationsProtocol(
        TapOracleWms.WarehouseOperationsProtocol,
    ):
        """TapOracleWmsWarehouseOperationsProtocol - real inheritance."""

    @runtime_checkable
    class TapOracleWmsStreamGenerationProtocol(TapOracleWms.StreamGenerationProtocol):
        """TapOracleWmsStreamGenerationProtocol - real inheritance."""

    @runtime_checkable
    class TapOracleWmsPerformanceProtocol(TapOracleWms.PerformanceProtocol):
        """TapOracleWmsPerformanceProtocol - real inheritance."""

    @runtime_checkable
    class TapOracleWmsValidationProtocol(TapOracleWms.ValidationProtocol):
        """TapOracleWmsValidationProtocol - real inheritance."""

    @runtime_checkable
    class TapOracleWmsMonitoringProtocol(TapOracleWms.MonitoringProtocol):
        """TapOracleWmsMonitoringProtocol - real inheritance."""


__all__ = [
    "FlextMeltanoTapOracleWmsProtocols",
]

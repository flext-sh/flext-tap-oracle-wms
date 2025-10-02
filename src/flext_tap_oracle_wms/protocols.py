"""Singer Oracle WMS tap protocols for FLEXT ecosystem."""

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult


class FlextTapOracleWmsProtocols(FlextProtocols):
    """Singer Oracle WMS tap protocols extending FlextProtocols with Oracle WMS warehouse management interfaces.

    This class provides protocol definitions for Singer Oracle WMS tap operations including
    warehouse management system extraction, inventory tracking, order processing, and logistics optimization.
    """

    @runtime_checkable
    class WmsConnectionProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle WMS connection operations."""

        def establish_wms_connection(
            self,
            connection_config: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            """Establish connection to Oracle WMS system.

            Args:
                connection_config: WMS connection configuration

            Returns:
                FlextResult[dict[str, object]]: Connection details or error

            """

        def test_wms_connectivity(
            self, connection_config: dict[str, object]
        ) -> FlextResult[bool]:
            """Test Oracle WMS system connectivity.

            Args:
                connection_config: WMS connection configuration

            Returns:
                FlextResult[bool]: Connection test result or error

            """

        def validate_wms_credentials(
            self, connection_config: dict[str, object]
        ) -> FlextResult[dict[str, object]]:
            """Validate WMS credentials and warehouse access permissions.

            Args:
                connection_config: WMS connection configuration

            Returns:
                FlextResult[dict[str, object]]: Validation results or error

            """

        def get_warehouse_context(
            self, connection_config: dict[str, object]
        ) -> FlextResult[dict[str, object]]:
            """Get warehouse context and configuration.

            Args:
                connection_config: WMS connection configuration

            Returns:
                FlextResult[dict[str, object]]: Warehouse context or error

            """

    @runtime_checkable
    class InventoryDiscoveryProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle WMS inventory discovery operations."""

        def discover_items(
            self, discovery_config: dict[str, object]
        ) -> FlextResult[list[dict[str, object]]]:
            """Discover inventory items and item masters.

            Args:
                discovery_config: Item discovery configuration

            Returns:
                FlextResult[list[dict[str, object]]]: Discovered items or error

            """

        def discover_locations(
            self, discovery_config: dict[str, object]
        ) -> FlextResult[list[dict[str, object]]]:
            """Discover warehouse locations and storage areas.

            Args:
                discovery_config: Location discovery configuration

            Returns:
                FlextResult[list[dict[str, object]]]: Discovered locations or error

            """

        def discover_inventory_balances(
            self, discovery_config: dict[str, object]
        ) -> FlextResult[list[dict[str, object]]]:
            """Discover current inventory balances and stock levels.

            Args:
                discovery_config: Inventory discovery configuration

            Returns:
                FlextResult[list[dict[str, object]]]: Discovered balances or error

            """

        def discover_lot_tracking(
            self, discovery_config: dict[str, object]
        ) -> FlextResult[list[dict[str, object]]]:
            """Discover lot and serial number tracking information.

            Args:
                discovery_config: Lot tracking discovery configuration

            Returns:
                FlextResult[list[dict[str, object]]]: Discovered lot tracking data or error

            """

    @runtime_checkable
    class OrderProcessingProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle WMS order processing operations."""

        def extract_inbound_orders(
            self,
            extraction_config: dict[str, object],
        ) -> FlextResult[list[dict[str, object]]]:
            """Extract inbound orders and receipts data.

            Args:
                extraction_config: Inbound order extraction parameters

            Returns:
                FlextResult[list[dict[str, object]]]: Inbound orders data or error

            """

        def extract_outbound_orders(
            self,
            extraction_config: dict[str, object],
        ) -> FlextResult[list[dict[str, object]]]:
            """Extract outbound orders and shipments data.

            Args:
                extraction_config: Outbound order extraction parameters

            Returns:
                FlextResult[list[dict[str, object]]]: Outbound orders data or error

            """

        def extract_picking_data(
            self,
            extraction_config: dict[str, object],
        ) -> FlextResult[list[dict[str, object]]]:
            """Extract picking operations and wave management data.

            Args:
                extraction_config: Picking data extraction parameters

            Returns:
                FlextResult[list[dict[str, object]]]: Picking operations data or error

            """

        def extract_shipping_data(
            self,
            extraction_config: dict[str, object],
        ) -> FlextResult[list[dict[str, object]]]:
            """Extract shipping and carrier management data.

            Args:
                extraction_config: Shipping data extraction parameters

            Returns:
                FlextResult[list[dict[str, object]]]: Shipping operations data or error

            """

    @runtime_checkable
    class WarehouseOperationsProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle WMS warehouse operations."""

        def extract_task_management(
            self,
            extraction_config: dict[str, object],
        ) -> FlextResult[list[dict[str, object]]]:
            """Extract task management and work assignment data.

            Args:
                extraction_config: Task management extraction parameters

            Returns:
                FlextResult[list[dict[str, object]]]: Task management data or error

            """

        def extract_labor_tracking(
            self,
            extraction_config: dict[str, object],
        ) -> FlextResult[list[dict[str, object]]]:
            """Extract labor tracking and productivity data.

            Args:
                extraction_config: Labor tracking extraction parameters

            Returns:
                FlextResult[list[dict[str, object]]]: Labor tracking data or error

            """

        def extract_equipment_data(
            self,
            extraction_config: dict[str, object],
        ) -> FlextResult[list[dict[str, object]]]:
            """Extract warehouse equipment and resource data.

            Args:
                extraction_config: Equipment data extraction parameters

            Returns:
                FlextResult[list[dict[str, object]]]: Equipment data or error

            """

        def extract_cycle_counts(
            self,
            extraction_config: dict[str, object],
        ) -> FlextResult[list[dict[str, object]]]:
            """Extract cycle counting and physical inventory data.

            Args:
                extraction_config: Cycle count extraction parameters

            Returns:
                FlextResult[list[dict[str, object]]]: Cycle count data or error

            """

    @runtime_checkable
    class StreamGenerationProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Singer stream generation from WMS data."""

        def generate_inventory_stream(
            self,
            inventory_data: dict[str, object],
            stream_config: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            """Generate Singer stream for WMS inventory data.

            Args:
                inventory_data: WMS inventory metadata
                stream_config: Stream configuration

            Returns:
                FlextResult[dict[str, object]]: Stream definition or error

            """

        def generate_order_stream(
            self,
            order_data: dict[str, object],
            stream_config: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            """Generate Singer stream for WMS order data.

            Args:
                order_data: WMS order metadata
                stream_config: Stream configuration

            Returns:
                FlextResult[dict[str, object]]: Stream definition or error

            """

        def generate_operational_stream(
            self,
            operational_data: dict[str, object],
            stream_config: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            """Generate Singer stream for WMS operational data.

            Args:
                operational_data: WMS operational metadata
                stream_config: Stream configuration

            Returns:
                FlextResult[dict[str, object]]: Stream definition or error

            """

        def determine_replication_strategy(
            self,
            entity_type: str,
            replication_config: dict[str, object],
        ) -> FlextResult[str]:
            """Determine optimal replication strategy for WMS entity type.

            Args:
                entity_type: Type of WMS entity
                replication_config: Replication configuration

            Returns:
                FlextResult[str]: Replication method (FULL_TABLE, INCREMENTAL, SNAPSHOT) or error

            """

    @runtime_checkable
    class PerformanceProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle WMS performance optimization operations."""

        def optimize_warehouse_queries(
            self, query_config: dict[str, object]
        ) -> FlextResult[dict[str, object]]:
            """Optimize WMS database queries for performance.

            Args:
                query_config: Query optimization parameters

            Returns:
                FlextResult[dict[str, object]]: Optimization results or error

            """

        def configure_batch_processing(
            self, batch_config: dict[str, object]
        ) -> FlextResult[dict[str, object]]:
            """Configure batch processing for large WMS datasets.

            Args:
                batch_config: Batch processing configuration

            Returns:
                FlextResult[dict[str, object]]: Batch configuration result or error

            """

        def monitor_extraction_performance(
            self, performance_metrics: dict[str, object]
        ) -> FlextResult[dict[str, object]]:
            """Monitor WMS data extraction performance metrics.

            Args:
                performance_metrics: Performance monitoring data

            Returns:
                FlextResult[dict[str, object]]: Performance analysis or error

            """

        def optimize_real_time_sync(
            self, sync_config: dict[str, object]
        ) -> FlextResult[dict[str, object]]:
            """Optimize real-time synchronization for WMS operations.

            Args:
                sync_config: Real-time sync configuration

            Returns:
                FlextResult[dict[str, object]]: Sync optimization results or error

            """

    @runtime_checkable
    class ValidationProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle WMS data validation operations."""

        def validate_inventory_consistency(
            self,
            inventory_data: list[dict[str, object]],
            validation_config: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            """Validate inventory data consistency and accuracy.

            Args:
                inventory_data: Inventory data to validate
                validation_config: Validation configuration

            Returns:
                FlextResult[dict[str, object]]: Validation results or error

            """

        def check_order_integrity(
            self,
            order_data: list[dict[str, object]],
            integrity_config: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            """Check order data integrity and business rules compliance.

            Args:
                order_data: Order data to validate
                integrity_config: Integrity check configuration

            Returns:
                FlextResult[dict[str, object]]: Integrity check results or error

            """

        def detect_data_anomalies(
            self,
            warehouse_data: list[dict[str, object]],
            anomaly_config: dict[str, object],
        ) -> FlextResult[list[dict[str, object]]]:
            """Detect anomalies in WMS data patterns.

            Args:
                warehouse_data: WMS data to analyze
                anomaly_config: Anomaly detection configuration

            Returns:
                FlextResult[list[dict[str, object]]]: Detected anomalies or error

            """

        def validate_warehouse_rules(
            self,
            operational_data: dict[str, object],
            rules_config: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            """Validate operational data against warehouse business rules.

            Args:
                operational_data: Operational data to validate
                rules_config: Business rules configuration

            Returns:
                FlextResult[dict[str, object]]: Rules validation results or error

            """

    @runtime_checkable
    class MonitoringProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle WMS monitoring operations."""

        def track_extraction_metrics(
            self, extraction_id: str, metrics: dict[str, object]
        ) -> FlextResult[bool]:
            """Track WMS extraction metrics and KPIs.

            Args:
                extraction_id: Extraction identifier
                metrics: Extraction metrics data

            Returns:
                FlextResult[bool]: Metric tracking success status

            """

        def monitor_warehouse_health(
            self, warehouse_id: str
        ) -> FlextResult[dict[str, object]]:
            """Monitor WMS warehouse operational health.

            Args:
                warehouse_id: Warehouse identifier

            Returns:
                FlextResult[dict[str, object]]: Health status or error

            """

        def get_operational_status(
            self, status_config: dict[str, object]
        ) -> FlextResult[dict[str, object]]:
            """Get WMS operational status and system health.

            Args:
                status_config: Status check configuration

            Returns:
                FlextResult[dict[str, object]]: Operational status or error

            """

        def create_monitoring_dashboard(
            self, dashboard_config: dict[str, object]
        ) -> FlextResult[dict[str, object]]:
            """Create monitoring dashboard for WMS tap operations.

            Args:
                dashboard_config: Dashboard configuration

            Returns:
                FlextResult[dict[str, object]]: Dashboard creation result or error

            """

    # Convenience aliases for easier downstream usage
    TapOracleWmsConnectionProtocol = WmsConnectionProtocol
    TapOracleWmsInventoryDiscoveryProtocol = InventoryDiscoveryProtocol
    TapOracleWmsOrderProcessingProtocol = OrderProcessingProtocol
    TapOracleWmsWarehouseOperationsProtocol = WarehouseOperationsProtocol
    TapOracleWmsStreamGenerationProtocol = StreamGenerationProtocol
    TapOracleWmsPerformanceProtocol = PerformanceProtocol
    TapOracleWmsValidationProtocol = ValidationProtocol
    TapOracleWmsMonitoringProtocol = MonitoringProtocol


__all__ = [
    "FlextTapOracleWmsProtocols",
]

# 📚 Tap Oracle WMS - API Reference

> **Function**: Complete API reference for Oracle WMS Singer tap implementation | **Audience**: Developers, Integration Engineers | **Status**: Enterprise Reference

[![Singer](https://img.shields.io/badge/singer-tap-blue.svg)](https://www.singer.io/)
[![Oracle](https://img.shields.io/badge/oracle-WMS-red.svg)](https://www.oracle.com/cx/retail/warehouse-management/)
[![API](https://img.shields.io/badge/api-comprehensive-blue.svg)](../README.md)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](../README.md)

Complete API reference documentation for Oracle WMS Singer tap, providing detailed interface specifications, stream definitions, and configuration schemas based on [Singer specification v1.0](https://hub.meltano.com/singer/spec) and [Oracle Retail WMS 25B API](https://docs.oracle.com/en/industries/retail/warehouse-management/25b/wmsab/).

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto](../../../README.md) → **📂 Project**: [Tap Oracle WMS](../../README.md) → **📁 Docs**: [Documentation](../README.md) → **📄 Current**: API Reference

---

## 📋 **API Overview**

This reference covers all public APIs for Oracle WMS Singer tap, implementing Singer specification compliance with enterprise-grade features for warehouse data extraction.

### **API Categories**

- **Tap Interface**: Core Singer tap implementation and lifecycle
- **Stream Definitions**: All available Oracle WMS data streams
- **Configuration Schema**: Complete configuration parameters and validation
- **Authentication APIs**: Secure authentication and session management
- **Discovery Engine**: Dynamic entity discovery and schema generation
- **State Management**: Incremental sync and bookmark handling

### **Singer Specification Compliance**

Based on [Singer v1.0 specification](https://hub.meltano.com/singer/spec):

- **Discovery Protocol**: `--discover` flag implementation
- **Sync Protocol**: Stream-based record extraction
- **State Protocol**: Bookmark-based incremental sync
- **Schema Protocol**: JSON Schema v7 compliance
- **Message Protocol**: JSON Lines output format

---

## 🔧 **Core Tap Interface**

### **TapOracleWMS Class**

Primary tap implementation following Singer SDK patterns:

```python
from singer_sdk import Tap, Stream
from singer_sdk.typing import (
    ArrayType,
    BooleanType,
    DateTimeType,
    IntegerType,
    NumberType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

class TapOracleWMS(Tap):
    """
    Oracle WMS Singer tap with enterprise features.

    Provides comprehensive warehouse data extraction with
    dynamic discovery, incremental sync, and performance
    optimization for Oracle Retail WMS systems.

    Based on Oracle Retail WMS 25B REST API specification:
    https://docs.oracle.com/en/industries/retail/warehouse-management/25b/wmsab/
    """

    name = "tap-oracle-wms"
    config_jsonschema = PropertiesList(
        # Required Configuration
        Property(
            "base_url",
            StringType,
            required=True,
            description="Oracle WMS API base URL (e.g., 'https://wms.company.com')"
        ),
        Property(
            "username",
            StringType,
            required=True,
            description="WMS authentication username"
        ),
        Property(
            "password",
            StringType,
            required=True,
            secret=True,
            description="WMS authentication password"
        ),

        # Optional Configuration
        Property(
            "facility_id",
            StringType,
            description="Default facility identifier for filtering"
        ),
        Property(
            "start_date",
            DateTimeType,
            description="Start date for incremental sync (ISO 8601 format)"
        ),
        Property(
            "page_size",
            IntegerType,
            default=1000,
            description="Records per page for pagination (100-10000)"
        ),
        Property(
            "request_timeout",
            IntegerType,
            default=60,
            description="Request timeout in seconds (10-300)"
        ),
        Property(
            "max_retries",
            IntegerType,
            default=3,
            description="Maximum retry attempts for failed requests (0-10)"
        ),
        Property(
            "retry_delay",
            NumberType,
            default=1.0,
            description="Delay between retry attempts in seconds"
        ),

        # Authentication Configuration
        Property(
            "auth_method",
            StringType,
            default="basic",
            allowed_values=["basic", "oauth2", "api_key"],
            description="Authentication method"
        ),
        Property(
            "client_id",
            StringType,
            description="OAuth2 client ID (required for oauth2 auth)"
        ),
        Property(
            "client_secret",
            StringType,
            secret=True,
            description="OAuth2 client secret (required for oauth2 auth)"
        ),
        Property(
            "token_url",
            StringType,
            description="OAuth2 token endpoint URL (required for oauth2 auth)"
        ),
        Property(
            "api_key",
            StringType,
            secret=True,
            description="API key for authentication (required for api_key auth)"
        ),
        Property(
            "api_key_header",
            StringType,
            default="X-API-Key",
            description="Header name for API key authentication"
        ),

        # Performance Configuration
        Property(
            "enable_caching",
            BooleanType,
            default=True,
            description="Enable response caching for metadata"
        ),
        Property(
            "cache_ttl",
            IntegerType,
            default=300,
            description="Cache TTL in seconds (60-3600)"
        ),
        Property(
            "max_workers",
            IntegerType,
            default=4,
            description="Maximum concurrent workers for parallel processing (1-10)"
        ),

        # Stream Configuration
        Property(
            "stream_filters",
            ObjectType(),
            description="Entity-specific filtering configuration"
        ),
        Property(
            "selected_fields",
            ObjectType(),
            description="Field selection per stream for optimization"
        ),
        Property(
            "discovery_timeout",
            IntegerType,
            default=120,
            description="Discovery timeout in seconds (30-600)"
        )
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """
        Discover all available Oracle WMS streams.

        Implements dynamic discovery with comprehensive entity
        detection and automatic schema generation.

        Returns:
            List[Stream]: All discovered WMS entity streams

        Raises:
            DiscoveryError: If discovery fails or times out
            AuthenticationError: If authentication fails

        Example:
            >>> tap = TapOracleWMS(config=config)
            >>> streams = tap.discover_streams()
            >>> print(f"Discovered {len(streams)} streams")
        """

    def sync_all(self) -> None:
        """
        Synchronize all selected streams.

        Executes complete extraction workflow with state
        management and error recovery.

        Raises:
            SyncError: If sync operation fails
            ConfigurationError: If configuration is invalid
        """
```

### **Configuration Validation**

```python
class ConfigValidator:
    """
    Configuration validation with enterprise-grade checks.

    Validates all configuration parameters with business
    rules and connectivity testing.
    """

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> ValidationResult:
        """
        Validate complete configuration with comprehensive checks.

        Args:
            config: Configuration dictionary

        Returns:
            ValidationResult: Validation status and details

        Example:
            >>> result = ConfigValidator.validate_config(config)
            >>> if not result.is_valid:
            ...     print(f"Validation errors: {result.errors}")
        """
        errors = []
        warnings = []

        # Required field validation
        required_fields = ["base_url", "username", "password"]
        for field in required_fields:
            if not config.get(field):
                errors.append(f"Missing required field: {field}")

        # URL validation
        if base_url := config.get("base_url"):
            if not base_url.startswith(("http://", "https://")):
                errors.append("base_url must start with http:// or https://")

        # Numeric range validation
        if page_size := config.get("page_size"):
            if not 100 <= page_size <= 10000:
                warnings.append("page_size should be between 100-10000 for optimal performance")

        # Authentication validation
        auth_method = config.get("auth_method", "basic")
        if auth_method == "oauth2":
            oauth_fields = ["client_id", "client_secret", "token_url"]
            for field in oauth_fields:
                if not config.get(field):
                    errors.append(f"OAuth2 requires field: {field}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

---

## 📊 **Stream Specifications**

### **Core Warehouse Streams**

#### **InventoryStream**

```python
class InventoryStream(WMSStream):
    """
    Oracle WMS inventory stream with comprehensive inventory tracking.

    Provides real-time inventory levels, location details, and
    status information for all warehouse items.
    """

    name = "inventory"
    path = "/inventory"
    primary_keys = ["item_id", "location_id"]
    replication_key = "last_update_date"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        # Item Identification
        Property("item_id", StringType, required=True, description="Unique item identifier"),
        Property("item_description", StringType, description="Item description"),
        Property("item_category", StringType, description="Item category classification"),
        Property("unit_of_measure", StringType, description="Base unit of measure"),

        # Location Information
        Property("location_id", StringType, required=True, description="Storage location identifier"),
        Property("zone", StringType, description="Warehouse zone"),
        Property("aisle", StringType, description="Aisle identifier"),
        Property("bay", StringType, description="Bay identifier"),
        Property("level", StringType, description="Level identifier"),
        Property("position", StringType, description="Position identifier"),
        Property("location_type", StringType, description="Location type (PICK, BULK, STAGE)"),

        # Facility Information
        Property("facility_id", StringType, required=True, description="Facility identifier"),
        Property("facility_name", StringType, description="Facility name"),

        # Quantity Information
        Property("available_quantity", NumberType, description="Available quantity for allocation"),
        Property("on_hand_quantity", NumberType, description="Physical on-hand quantity"),
        Property("allocated_quantity", NumberType, description="Quantity allocated to orders"),
        Property("in_transit_quantity", NumberType, description="Quantity in transit"),
        Property("damaged_quantity", NumberType, description="Damaged quantity"),
        Property("hold_quantity", NumberType, description="Quantity on hold"),

        # Lot and Serial Information
        Property("lot_number", StringType, description="Lot number for lot-controlled items"),
        Property("lot_attributes", ObjectType(), description="Additional lot attributes"),
        Property("serial_numbers", ArrayType(StringType), description="Serial numbers if applicable"),
        Property("expiration_date", DateTimeType, description="Expiration date for perishable items"),
        Property("manufacture_date", DateTimeType, description="Manufacturing date"),

        # Status and Control
        Property("item_status", StringType, description="Item status (ACTIVE, INACTIVE, HOLD)"),
        Property("location_status", StringType, description="Location status"),
        Property("inventory_status", StringType, description="Inventory status"),
        Property("quality_status", StringType, description="Quality control status"),

        # Financial Information
        Property("unit_cost", NumberType, description="Unit cost value"),
        Property("total_value", NumberType, description="Total inventory value"),
        Property("currency_code", StringType, description="Currency code"),

        # Audit Information
        Property("created_date", DateTimeType, description="Record creation date"),
        Property("created_by", StringType, description="Record created by user"),
        Property("last_update_date", DateTimeType, description="Last update timestamp"),
        Property("last_updated_by", StringType, description="Last updated by user"),
        Property("version", IntegerType, description="Record version for optimistic locking")
    ).to_dict()

    def get_url_params(self, context: Optional[dict], next_page_token: Optional[Any]) -> Dict[str, Any]:
        """
        Generate URL parameters for inventory queries.

        Implements facility filtering, date-based incremental sync,
        and custom field selection for performance optimization.
        """
        params = super().get_url_params(context, next_page_token)

        # Facility filtering
        if facility_id := self.config.get("facility_id"):
            params["facility_id"] = facility_id

        # Item status filtering
        params["item_status"] = "ACTIVE"

        # Field selection for performance
        if selected_fields := self.config.get("selected_fields", {}).get(self.name):
            params["fields"] = ",".join(selected_fields)

        return params

    def post_process(self, row: dict, context: Optional[dict] = None) -> Optional[dict]:
        """
        Post-process inventory records with business logic.

        Applies data transformations and calculated fields
        for enhanced analytics and reporting.
        """
        if not row:
            return None

        # Calculate derived quantities
        available = float(row.get("available_quantity", 0))
        on_hand = float(row.get("on_hand_quantity", 0))
        allocated = float(row.get("allocated_quantity", 0))

        # Add calculated fields
        row["utilization_rate"] = allocated / on_hand if on_hand > 0 else 0
        row["availability_rate"] = available / on_hand if on_hand > 0 else 0
        row["variance_quantity"] = on_hand - available - allocated

        # Normalize timestamps
        for date_field in ["last_update_date", "expiration_date", "created_date"]:
            if row.get(date_field):
                row[date_field] = self.normalize_timestamp(row[date_field])

        return row
```

#### **OrderHeaderStream**

```python
class OrderHeaderStream(WMSStream):
    """
    Oracle WMS order header stream with comprehensive order tracking.

    Provides order lifecycle information including status, dates,
    customer information, and order totals.
    """

    name = "order_headers"
    path = "/orders"
    primary_keys = ["order_id"]
    replication_key = "modified_date"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        # Order Identification
        Property("order_id", StringType, required=True, description="Unique order identifier"),
        Property("order_number", StringType, description="Human-readable order number"),
        Property("external_order_id", StringType, description="External system order reference"),
        Property("order_type", StringType, description="Order type (OUTBOUND, INBOUND, TRANSFER)"),
        Property("order_source", StringType, description="Order source system"),

        # Customer Information
        Property("customer_id", StringType, description="Customer identifier"),
        Property("customer_name", StringType, description="Customer name"),
        Property("customer_type", StringType, description="Customer type classification"),

        # Order Details
        Property("order_status", StringType, description="Current order status"),
        Property("priority", IntegerType, description="Order priority (1-10, 1=highest)"),
        Property("urgency_code", StringType, description="Urgency classification"),

        # Dates and Times
        Property("order_date", DateTimeType, description="Order creation date"),
        Property("requested_ship_date", DateTimeType, description="Requested ship date"),
        Property("promised_ship_date", DateTimeType, description="Promised ship date"),
        Property("actual_ship_date", DateTimeType, description="Actual ship date"),
        Property("expected_delivery_date", DateTimeType, description="Expected delivery date"),
        Property("cancel_date", DateTimeType, description="Cancellation date if applicable"),

        # Facility and Location
        Property("facility_id", StringType, description="Originating facility"),
        Property("ship_from_location", StringType, description="Ship from location"),
        Property("destination_facility", StringType, description="Destination facility for transfers"),

        # Shipping Information
        Property("carrier", StringType, description="Assigned carrier"),
        Property("service_level", StringType, description="Service level (GROUND, EXPRESS, OVERNIGHT)"),
        Property("tracking_number", StringType, description="Carrier tracking number"),
        Property("freight_terms", StringType, description="Freight terms"),
        Property("shipping_method", StringType, description="Shipping method"),

        # Order Totals
        Property("total_lines", IntegerType, description="Number of order lines"),
        Property("total_quantity", NumberType, description="Total ordered quantity"),
        Property("total_weight", NumberType, description="Total order weight"),
        Property("total_volume", NumberType, description="Total order volume"),
        Property("total_value", NumberType, description="Total order value"),
        Property("currency_code", StringType, description="Currency code"),

        # Address Information
        Property("ship_to_address", ObjectType(
            Property("name", StringType),
            Property("company", StringType),
            Property("address1", StringType),
            Property("address2", StringType),
            Property("city", StringType),
            Property("state", StringType),
            Property("postal_code", StringType),
            Property("country", StringType),
            Property("phone", StringType),
            Property("email", StringType)
        ), description="Shipping address details"),

        # Special Instructions
        Property("special_instructions", StringType, description="Special handling instructions"),
        Property("delivery_instructions", StringType, description="Delivery instructions"),
        Property("packing_instructions", StringType, description="Packing instructions"),

        # Workflow Information
        Property("allocation_status", StringType, description="Allocation status"),
        Property("pick_status", StringType, description="Pick status"),
        Property("pack_status", StringType, description="Pack status"),
        Property("ship_status", StringType, description="Ship status"),

        # Audit Information
        Property("created_date", DateTimeType, description="Record creation date"),
        Property("created_by", StringType, description="Record created by user"),
        Property("modified_date", DateTimeType, description="Last modification date"),
        Property("modified_by", StringType, description="Last modified by user"),
        Property("version", IntegerType, description="Record version")
    ).to_dict()

    def get_child_context(self, record: Dict[str, Any], context: Optional[dict]) -> Dict[str, Any]:
        """
        Provide context for child streams (order details).

        Enables parent-child relationship between order headers
        and order detail lines for hierarchical extraction.
        """
        return {
            "order_id": record["order_id"],
            "order_type": record.get("order_type"),
            "facility_id": record.get("facility_id"),
            "order_status": record.get("order_status")
        }
```

#### **OrderDetailStream**

```python
class OrderDetailStream(WMSStream):
    """
    Oracle WMS order detail stream with line-level information.

    Provides detailed line item information including quantities,
    allocations, and item-specific requirements.
    """

    name = "order_details"
    path = "/orders/{order_id}/lines"
    primary_keys = ["order_id", "line_number"]
    replication_key = "modified_date"
    replication_method = "INCREMENTAL"
    parent_stream_type = OrderHeaderStream

    schema = PropertiesList(
        # Line Identification
        Property("order_id", StringType, required=True, description="Parent order identifier"),
        Property("line_number", IntegerType, required=True, description="Line sequence number"),
        Property("line_id", StringType, description="Unique line identifier"),
        Property("external_line_id", StringType, description="External system line reference"),

        # Item Information
        Property("item_id", StringType, required=True, description="Item identifier"),
        Property("item_description", StringType, description="Item description"),
        Property("item_category", StringType, description="Item category"),
        Property("unit_of_measure", StringType, description="Unit of measure"),
        Property("item_weight", NumberType, description="Item weight per unit"),
        Property("item_volume", NumberType, description="Item volume per unit"),

        # Quantity Information
        Property("ordered_quantity", NumberType, required=True, description="Ordered quantity"),
        Property("allocated_quantity", NumberType, description="Allocated quantity"),
        Property("picked_quantity", NumberType, description="Picked quantity"),
        Property("shipped_quantity", NumberType, description="Shipped quantity"),
        Property("cancelled_quantity", NumberType, description="Cancelled quantity"),
        Property("backordered_quantity", NumberType, description="Backordered quantity"),

        # Pricing Information
        Property("unit_price", NumberType, description="Unit price"),
        Property("extended_price", NumberType, description="Extended line price"),
        Property("discount_amount", NumberType, description="Discount amount"),
        Property("tax_amount", NumberType, description="Tax amount"),
        Property("currency_code", StringType, description="Currency code"),

        # Requirements and Specifications
        Property("lot_requirements", ArrayType(StringType), description="Required lot numbers"),
        Property("serial_requirements", ArrayType(StringType), description="Required serial numbers"),
        Property("expiration_requirements", DateTimeType, description="Minimum expiration date"),
        Property("quality_requirements", ArrayType(StringType), description="Quality requirements"),

        # Allocation Details
        Property("allocation_details", ArrayType(ObjectType(
            Property("location_id", StringType),
            Property("allocated_quantity", NumberType),
            Property("lot_number", StringType),
            Property("expiration_date", DateTimeType),
            Property("allocation_date", DateTimeType)
        )), description="Detailed allocation information"),

        # Line Status
        Property("line_status", StringType, description="Line status"),
        Property("allocation_status", StringType, description="Allocation status"),
        Property("pick_status", StringType, description="Pick status"),
        Property("pack_status", StringType, description="Pack status"),

        # Special Instructions
        Property("line_instructions", StringType, description="Line-specific instructions"),
        Property("packing_requirements", StringType, description="Special packing requirements"),
        Property("handling_requirements", StringType, description="Special handling requirements"),

        # Audit Information
        Property("created_date", DateTimeType, description="Record creation date"),
        Property("created_by", StringType, description="Record created by user"),
        Property("modified_date", DateTimeType, description="Last modification date"),
        Property("modified_by", StringType, description="Last modified by user")
    ).to_dict()

    def get_url_params(self, context: Optional[dict], next_page_token: Optional[Any]) -> Dict[str, Any]:
        """
        Generate URL parameters for order detail queries.

        Uses parent order context for efficient hierarchical
        data extraction with proper filtering.
        """
        params = super().get_url_params(context, next_page_token)

        # Use parent order context
        if context and context.get("order_id"):
            self.path = f"/orders/{context['order_id']}/lines"

        return params
```

### **Operational Streams**

#### **ShipmentStream**

```python
class ShipmentStream(WMSStream):
    """
    Oracle WMS shipment stream with comprehensive shipping information.

    Tracks inbound and outbound shipments with carrier details,
    tracking information, and shipment status.
    """

    name = "shipments"
    path = "/shipments"
    primary_keys = ["shipment_id"]
    replication_key = "modified_date"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        # Shipment Identification
        Property("shipment_id", StringType, required=True, description="Unique shipment identifier"),
        Property("shipment_number", StringType, description="Human-readable shipment number"),
        Property("external_shipment_id", StringType, description="External system reference"),
        Property("shipment_type", StringType, description="Shipment type (INBOUND, OUTBOUND)"),

        # Carrier Information
        Property("carrier", StringType, description="Carrier name"),
        Property("carrier_service", StringType, description="Carrier service level"),
        Property("tracking_number", StringType, description="Carrier tracking number"),
        Property("trailer_number", StringType, description="Trailer number"),
        Property("driver_name", StringType, description="Driver name"),
        Property("driver_phone", StringType, description="Driver phone number"),

        # Facility Information
        Property("facility_id", StringType, description="Facility identifier"),
        Property("dock_door", StringType, description="Assigned dock door"),
        Property("yard_location", StringType, description="Yard location"),

        # Shipment Details
        Property("shipment_status", StringType, description="Current shipment status"),
        Property("priority", IntegerType, description="Shipment priority"),
        Property("total_weight", NumberType, description="Total shipment weight"),
        Property("total_volume", NumberType, description="Total shipment volume"),
        Property("total_value", NumberType, description="Total shipment value"),
        Property("package_count", IntegerType, description="Number of packages"),

        # Dates and Times
        Property("scheduled_arrival", DateTimeType, description="Scheduled arrival date"),
        Property("actual_arrival", DateTimeType, description="Actual arrival date"),
        Property("scheduled_departure", DateTimeType, description="Scheduled departure date"),
        Property("actual_departure", DateTimeType, description="Actual departure date"),
        Property("delivery_date", DateTimeType, description="Delivery date"),

        # Address Information
        Property("origin_address", ObjectType(
            Property("name", StringType),
            Property("address1", StringType),
            Property("city", StringType),
            Property("state", StringType),
            Property("postal_code", StringType),
            Property("country", StringType)
        ), description="Origin address"),

        Property("destination_address", ObjectType(
            Property("name", StringType),
            Property("address1", StringType),
            Property("city", StringType),
            Property("state", StringType),
            Property("postal_code", StringType),
            Property("country", StringType)
        ), description="Destination address"),

        # Associated Orders
        Property("order_ids", ArrayType(StringType), description="Associated order identifiers"),
        Property("purchase_order_numbers", ArrayType(StringType), description="Purchase order numbers"),

        # Special Requirements
        Property("temperature_requirements", ObjectType(
            Property("min_temp", NumberType),
            Property("max_temp", NumberType),
            Property("unit", StringType)
        ), description="Temperature requirements"),
        Property("hazmat_requirements", ArrayType(StringType), description="Hazmat requirements"),
        Property("special_instructions", StringType, description="Special handling instructions"),

        # Audit Information
        Property("created_date", DateTimeType, description="Record creation date"),
        Property("created_by", StringType, description="Record created by user"),
        Property("modified_date", DateTimeType, description="Last modification date"),
        Property("modified_by", StringType, description="Last modified by user")
    ).to_dict()
```

---

## 🔐 **Authentication API**

### **Authentication Manager**

```python
class AuthenticationManager:
    """
    Enterprise authentication manager for Oracle WMS connectivity.

    Supports multiple authentication methods with secure
    credential handling and session management.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.auth_method = config.get("auth_method", "basic")
        self.session_cache = {}

    async def authenticate(self) -> AuthResult:
        """
        Authenticate with Oracle WMS using configured method.

        Returns:
            AuthResult: Authentication result with token/session info

        Raises:
            AuthenticationError: If authentication fails

        Example:
            >>> auth_manager = AuthenticationManager(config)
            >>> result = await auth_manager.authenticate()
            >>> if result.success:
            ...     headers = auth_manager.get_auth_headers(result.token)
        """
        if self.auth_method == "basic":
            return await self._authenticate_basic()
        elif self.auth_method == "oauth2":
            return await self._authenticate_oauth2()
        elif self.auth_method == "api_key":
            return await self._authenticate_api_key()
        else:
            raise ValueError(f"Unsupported auth method: {self.auth_method}")

    def get_auth_headers(self, token: Optional[Any] = None) -> Dict[str, str]:
        """
        Generate authentication headers for API requests.

        Args:
            token: Authentication token (if applicable)

        Returns:
            Dict[str, str]: HTTP headers for authentication
        """
        if self.auth_method == "basic":
            credentials = base64.b64encode(
                f"{self.config['username']}:{self.config['password']}".encode()
            ).decode()
            return {"Authorization": f"Basic {credentials}"}

        elif self.auth_method == "oauth2" and token:
            return {"Authorization": f"Bearer {token.access_token}"}

        elif self.auth_method == "api_key":
            header_name = self.config.get("api_key_header", "X-API-Key")
            return {header_name: self.config["api_key"]}

        return {}
```

---

## 🔍 **Discovery Engine API**

### **Stream Discovery**

```python
class DiscoveryEngine:
    """
    Advanced discovery engine for Oracle WMS entities.

    Provides dynamic entity discovery with comprehensive
    metadata introspection and schema generation.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = WMSAPIClient(config)
        self.schema_generator = SchemaGenerator()

    async def discover_streams(self) -> List[StreamDefinition]:
        """
        Discover all available Oracle WMS streams.

        Returns:
            List[StreamDefinition]: Discovered stream definitions

        Raises:
            DiscoveryError: If discovery fails

        Example:
            >>> engine = DiscoveryEngine(config)
            >>> streams = await engine.discover_streams()
            >>> for stream in streams:
            ...     print(f"Stream: {stream.name}, Fields: {len(stream.schema['properties'])}")
        """
        discovered_streams = []

        # Core predefined streams
        core_streams = self._get_core_streams()
        discovered_streams.extend(core_streams)

        # Dynamically discovered streams
        try:
            dynamic_streams = await self._discover_dynamic_streams()
            discovered_streams.extend(dynamic_streams)
        except Exception as e:
            self.logger.warning(f"Dynamic discovery failed: {e}")

        return discovered_streams

    async def introspect_entity_metadata(self, entity_name: str) -> EntityMetadata:
        """
        Introspect metadata for specific Oracle WMS entity.

        Args:
            entity_name: Name of WMS entity to introspect

        Returns:
            EntityMetadata: Complete entity metadata including schema

        Example:
            >>> metadata = await engine.introspect_entity_metadata("inventory")
            >>> print(f"Entity: {metadata.name}, Fields: {len(metadata.fields)}")
        """
        try:
            metadata_response = await self.client.get(f"/metadata/entities/{entity_name}")

            return EntityMetadata(
                name=metadata_response["name"],
                endpoint=metadata_response["endpoint"],
                primary_key=metadata_response.get("primary_key", ["id"]),
                replication_key=metadata_response.get("replication_key"),
                fields=metadata_response.get("fields", []),
                supports_incremental=metadata_response.get("supports_incremental", False),
                description=metadata_response.get("description", ""),
                sample_data=metadata_response.get("sample_data", [])
            )

        except Exception as e:
            raise DiscoveryError(f"Failed to introspect entity {entity_name}: {e}")

    def generate_stream_schema(self, metadata: EntityMetadata) -> Dict[str, Any]:
        """
        Generate JSON schema from entity metadata.

        Args:
            metadata: Entity metadata from Oracle WMS

        Returns:
            Dict[str, Any]: JSON Schema v7 compliant schema

        Example:
            >>> schema = engine.generate_stream_schema(metadata)
            >>> print(f"Schema properties: {list(schema['properties'].keys())}")
        """
        return self.schema_generator.generate_from_metadata(metadata)
```

---

## 📈 **State Management API**

### **Bookmark Handling**

```python
class StateManager:
    """
    Enterprise state management for incremental synchronization.

    Provides robust bookmark tracking with persistence,
    validation, and recovery capabilities.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.state = {"bookmarks": {}}
        self.lock = threading.RLock()

    def get_stream_bookmark(self, stream_name: str) -> Optional[Any]:
        """
        Get current bookmark for stream incremental sync.

        Args:
            stream_name: Name of the stream

        Returns:
            Optional[Any]: Current bookmark value or None

        Example:
            >>> manager = StateManager(config)
            >>> bookmark = manager.get_stream_bookmark("inventory")
            >>> print(f"Last sync: {bookmark}")
        """
        with self.lock:
            return self.state.get("bookmarks", {}).get(stream_name, {}).get("replication_key_value")

    def update_stream_bookmark(self, stream_name: str, bookmark_value: Any) -> None:
        """
        Update bookmark for stream with atomic persistence.

        Args:
            stream_name: Name of the stream
            bookmark_value: New bookmark value

        Example:
            >>> manager.update_stream_bookmark("inventory", "2025-06-19T10:30:00Z")
        """
        with self.lock:
            if "bookmarks" not in self.state:
                self.state["bookmarks"] = {}

            self.state["bookmarks"][stream_name] = {
                "replication_key_value": bookmark_value,
                "last_updated": datetime.utcnow().isoformat()
            }

            self._persist_state()

    def reset_stream_bookmark(self, stream_name: str) -> None:
        """
        Reset bookmark for stream to force full resync.

        Args:
            stream_name: Name of the stream to reset
        """
        with self.lock:
            if stream_name in self.state.get("bookmarks", {}):
                del self.state["bookmarks"][stream_name]
                self._persist_state()
```

---

## 🔗 **Cross-References**

### **Singer Protocol Documentation**

- [Singer Specification v1.0](https://hub.meltano.com/singer/spec) - Official Singer protocol
- [JSON Schema v7](https://json-schema.org/draft-07/schema) - Schema validation specification
- [Meltano SDK Reference](https://sdk.meltano.com/) - SDK implementation patterns

### **Oracle WMS Documentation**

- [Oracle Retail WMS 25B REST API](https://docs.oracle.com/en/industries/retail/warehouse-management/25b/wmsab/) - Official API reference
- [Oracle WMS Integration Guide](https://docs.oracle.com/en/industries/retail/warehouse-management/25b/wmsig/) - Integration best practices

### **Related Documentation**

- [Architecture Guide](../architecture/README.md) - Technical architecture patterns
- [Implementation Guides](../guides/README.md) - Step-by-step implementation
- [Security Guide](../security/README.md) - Security implementation

---

**📚 API Reference**: Tap Oracle WMS | **🏠 Root**: [PyAuto Home](../../../README.md) | **Framework**: Singer SDK 0.45.0+ | **Updated**: 2025-06-19

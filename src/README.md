# 📦 TAP Oracle WMS - Source Implementation

> **Module**: Oracle Warehouse Management System Singer tap source implementation with advanced stream management | **Audience**: Data Engineers, Singer SDK Developers, WMS Integration Specialists | **Status**: Production Ready

## 📋 **Overview**

Complete source implementation of the TAP Oracle WMS (Warehouse Management System) Singer tap, providing comprehensive data extraction from Oracle Fusion Cloud WMS with dynamic entity discovery, incremental sync capabilities, and advanced stream management for enterprise warehouse operations.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [TAP Oracle WMS](../README.md) → **📂 Current**: Source Implementation

---

## 🎯 **Module Purpose**

This source module implements a production-ready Singer tap for Oracle Warehouse Management System, following Singer SDK specifications with comprehensive entity discovery, incremental synchronization, advanced authentication, and real-time monitoring capabilities for enterprise warehouse data integration.

### **Key Capabilities**

- **Dynamic Entity Discovery** - Automatic WMS entity detection and schema generation
- **Incremental Synchronization** - Efficient incremental data extraction with bookmarking
- **Advanced Stream Management** - Multiple stream implementations for different use cases
- **Comprehensive Authentication** - OAuth2, Basic Auth, and JWT token support
- **Real-time Monitoring** - Performance metrics and operation monitoring
- **Enterprise Configuration** - Flexible configuration with environment support

---

## 📁 **Module Structure**

```
src/tap_oracle_wms/
├── __init__.py              # Public API exports and Singer tap registration
├── __main__.py              # CLI entry point for tap execution
├── auth.py                  # Authentication management with OAuth2/JWT support
├── cli.py                   # Command-line interface for tap operations
├── config.py                # Configuration management with Pydantic validation
├── discovery.py             # Dynamic entity discovery and schema generation
├── monitoring.py            # Performance monitoring and metrics collection
├── streams.py               # Dynamic stream implementations
├── streams_advanced.py      # Advanced stream patterns with complex logic
├── streams_real.py          # Real-world stream implementations
└── tap.py                   # Main Singer tap implementation
```

---

## 🔧 **Core Components**

### **1. Main Tap Implementation (tap.py)**

Singer SDK-compliant tap implementation:

```python
class TapOracleWMS(Tap):
    """Oracle WMS Singer tap for data extraction.

    Implements Singer SDK specification for Oracle Warehouse Management System
    data extraction with comprehensive stream management and incremental sync.
    """

    name = "tap-oracle-wms"
    config_jsonschema = th.PropertiesList(
        th.Property("wms_base_url", th.StringType, required=True),
        th.Property("username", th.StringType, required=True),
        th.Property("password", th.StringType, required=True, secret=True),
        th.Property("facility_id", th.StringType, required=True),
        th.Property("auth_type", th.StringType, default="basic"),
        th.Property("batch_size", th.IntegerType, default=1000),
        th.Property("enable_incremental", th.BooleanType, default=True),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Discover available WMS streams dynamically."""
        discovery_service = WMSDiscoveryService(self.config)
        return discovery_service.discover_all_streams()

    def get_stream_maps(self) -> Dict[str, StreamMap]:
        """Get stream maps for data transformation."""
        return {
            "facilities": FacilityStreamMap(),
            "items": ItemStreamMap(),
            "orders": OrderStreamMap(),
            "shipments": ShipmentStreamMap(),
            "receipts": ReceiptStreamMap(),
            "allocations": AllocationStreamMap(),
            "inventory": InventoryStreamMap(),
        }
```

### **2. Authentication Management (auth.py)**

Comprehensive WMS authentication handling:

```python
class WMSAuthManager:
    """Authentication manager for Oracle WMS REST API.

    Supports multiple authentication methods including Basic Auth,
    OAuth2, and JWT tokens with automatic token refresh.
    """

    def __init__(self, config: WMSConfig):
        self.config = config
        self._session = requests.Session()
        self._token_cache = {}

    async def authenticate(self) -> Dict[str, str]:
        """Authenticate with WMS and return headers."""
        auth_type = self.config.auth_type.lower()

        if auth_type == "basic":
            return self._basic_auth()
        elif auth_type == "oauth2":
            return await self._oauth2_auth()
        elif auth_type == "jwt":
            return await self._jwt_auth()
        else:
            raise AuthenticationError(f"Unsupported auth type: {auth_type}")

    def _basic_auth(self) -> Dict[str, str]:
        """Basic authentication headers."""
        credentials = base64.b64encode(
            f"{self.config.username}:{self.config.password}".encode()
        ).decode()
        return {"Authorization": f"Basic {credentials}"}

    async def _oauth2_auth(self) -> Dict[str, str]:
        """OAuth2 authentication with token management."""
        if self._is_token_valid():
            return {"Authorization": f"Bearer {self._token_cache['access_token']}"}

        token_response = await self._request_oauth2_token()
        self._token_cache = token_response
        return {"Authorization": f"Bearer {token_response['access_token']}"}

    async def _jwt_auth(self) -> Dict[str, str]:
        """JWT authentication with signature validation."""
        jwt_token = await self._generate_jwt_token()
        return {"Authorization": f"Bearer {jwt_token}"}
```

### **3. Dynamic Discovery (discovery.py)**

WMS entity discovery and schema generation:

```python
class WMSDiscoveryService:
    """Discovery service for WMS entities and schemas.

    Dynamically discovers available WMS entities, generates schemas,
    and creates stream definitions for data extraction.
    """

    def __init__(self, config: WMSConfig):
        self.config = config
        self.auth_manager = WMSAuthManager(config)
        self.http_client = WMSHttpClient(config, self.auth_manager)

    async def discover_all_streams(self) -> List[Stream]:
        """Discover all available WMS streams."""
        discovered_entities = await self._discover_entities()
        streams = []

        for entity in discovered_entities:
            schema = await self._generate_schema(entity)
            stream_class = self._create_stream_class(entity, schema)
            streams.append(stream_class(tap=self.tap))

        return streams

    async def _discover_entities(self) -> List[WMSEntity]:
        """Discover WMS entities through API exploration."""
        # Query WMS metadata endpoints
        metadata_response = await self.http_client.get("/metadata/entities")

        entities = []
        for entity_data in metadata_response.get("entities", []):
            entity = WMSEntity(
                name=entity_data["name"],
                endpoint=entity_data["endpoint"],
                primary_key=entity_data.get("primaryKey", "id"),
                supports_incremental=entity_data.get("supportsIncremental", False),
                incremental_key=entity_data.get("incrementalKey", "lastModified")
            )
            entities.append(entity)

        return entities

    async def _generate_schema(self, entity: WMSEntity) -> Dict:
        """Generate JSON schema for WMS entity."""
        # Sample data to infer schema
        sample_response = await self.http_client.get(
            f"{entity.endpoint}?limit=5"
        )

        schema_generator = SchemaGenerator()
        return schema_generator.infer_schema(
            sample_response.get("items", []),
            entity.name
        )
```

### **4. Stream Implementations**

#### **Dynamic Streams (streams.py)**

```python
class DynamicWMSStream(RESTStream):
    """Dynamic WMS stream for discovered entities."""

    def __init__(self, tap: Tap, entity: WMSEntity, schema: Dict):
        self.entity = entity
        self._schema = schema
        super().__init__(tap)

    @property
    def name(self) -> str:
        """Stream name from entity."""
        return self.entity.name

    @property
    def schema(self) -> Dict:
        """Stream schema."""
        return self._schema

    @property
    def path(self) -> str:
        """API endpoint path."""
        return self.entity.endpoint

    def get_url_params(
        self,
        context: Optional[Dict],
        next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Get URL parameters for API request."""
        params = {
            "facilityId": self.config.get("facility_id"),
            "limit": self.config.get("batch_size", 1000)
        }

        if next_page_token:
            params["offset"] = next_page_token

        # Add incremental parameters
        if self.entity.supports_incremental and self.get_starting_timestamp(context):
            params[self.entity.incremental_key] = self.get_starting_timestamp(context)

        return params
```

#### **Advanced Streams (streams_advanced.py)**

```python
class AdvancedInventoryStream(DynamicWMSStream):
    """Advanced inventory stream with complex aggregation logic."""

    replication_key = "lastModified"

    def post_process(self, row: Dict, context: Dict = None) -> Optional[Dict]:
        """Post-process inventory data with calculations."""
        # Calculate available quantity
        row["availableQuantity"] = (
            row.get("onHandQuantity", 0) -
            row.get("allocatedQuantity", 0) -
            row.get("reservedQuantity", 0)
        )

        # Add location hierarchy
        if row.get("locationId"):
            location_info = self._get_location_hierarchy(row["locationId"])
            row["locationHierarchy"] = location_info

        # Calculate inventory value
        if row.get("unitCost") and row.get("onHandQuantity"):
            row["inventoryValue"] = row["unitCost"] * row["onHandQuantity"]

        return row

    def _get_location_hierarchy(self, location_id: str) -> Dict:
        """Get location hierarchy information."""
        # Implementation for location hierarchy lookup
        pass
```

#### **Real-world Streams (streams_real.py)**

```python
class OrderStream(DynamicWMSStream):
    """Real-world order stream with business logic."""

    name = "orders"
    path = "/orders"
    primary_keys = ["orderId"]
    replication_key = "lastModified"

    def get_child_context(self, record: Dict, context: Optional[Dict]) -> Dict:
        """Get context for child streams (order lines)."""
        return {
            "order_id": record["orderId"],
            "facility_id": record["facilityId"]
        }

class OrderLineStream(DynamicWMSStream):
    """Order line stream with parent relationship."""

    name = "order_lines"
    path = "/orders/{order_id}/lines"
    primary_keys = ["orderLineId"]
    parent_stream_type = OrderStream

    def get_url_params(
        self,
        context: Optional[Dict],
        next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Get URL parameters including parent context."""
        params = super().get_url_params(context, next_page_token)

        if context and context.get("order_id"):
            params["orderId"] = context["order_id"]

        return params
```

### **5. Configuration Management (config.py)**

Comprehensive WMS configuration:

```python
class WMSConfig(BaseSettings):
    """Oracle WMS configuration with comprehensive validation."""

    # WMS Connection settings
    wms_base_url: HttpUrl = Field(..., description="WMS base URL")
    username: str = Field(..., description="WMS username")
    password: SecretStr = Field(..., description="WMS password")
    facility_id: str = Field(..., description="WMS facility ID")

    # Authentication settings
    auth_type: AuthType = Field(default=AuthType.BASIC, description="Authentication type")
    oauth_client_id: Optional[str] = Field(default=None)
    oauth_client_secret: Optional[SecretStr] = Field(default=None)
    oauth_scope: Optional[str] = Field(default=None)
    jwt_secret: Optional[SecretStr] = Field(default=None)

    # Performance settings
    batch_size: int = Field(default=1000, ge=1, le=10000)
    max_concurrent_requests: int = Field(default=5, ge=1, le=20)
    request_timeout: int = Field(default=60, ge=1, le=300)

    # Stream settings
    enable_incremental: bool = Field(default=True)
    incremental_lookback_days: int = Field(default=1, ge=0, le=30)
    stream_filter: Optional[List[str]] = Field(default=None)

    # Monitoring settings
    enable_metrics: bool = Field(default=True)
    metrics_interval: int = Field(default=60, ge=10)

    class Config:
        env_prefix = "TAP_ORACLE_WMS_"
        env_file = ".env"
```

### **6. Monitoring System (monitoring.py)**

Performance monitoring and metrics:

```python
class WMSMonitor:
    """Monitor WMS tap performance and operations."""

    def __init__(self, config: WMSConfig):
        self.config = config
        self.metrics = {
            "records_extracted": 0,
            "api_calls_made": 0,
            "errors_encountered": 0,
            "streams_processed": 0,
            "start_time": None,
            "last_sync_time": None
        }

    def record_extraction(self, stream_name: str, record_count: int) -> None:
        """Record successful data extraction."""
        self.metrics["records_extracted"] += record_count
        self.metrics["last_sync_time"] = datetime.utcnow()

    def record_api_call(self, endpoint: str, duration: float) -> None:
        """Record API call metrics."""
        self.metrics["api_calls_made"] += 1

    def record_error(self, error: Exception, context: Dict) -> None:
        """Record error with context."""
        self.metrics["errors_encountered"] += 1

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if self.metrics["start_time"]:
            duration = datetime.utcnow() - self.metrics["start_time"]
            records_per_second = (
                self.metrics["records_extracted"] / duration.total_seconds()
                if duration.total_seconds() > 0 else 0
            )
        else:
            records_per_second = 0

        return {
            "total_records": self.metrics["records_extracted"],
            "total_api_calls": self.metrics["api_calls_made"],
            "total_errors": self.metrics["errors_encountered"],
            "streams_processed": self.metrics["streams_processed"],
            "records_per_second": round(records_per_second, 2),
            "error_rate": (
                self.metrics["errors_encountered"] /
                max(self.metrics["api_calls_made"], 1)
            )
        }
```

### **7. CLI Interface (cli.py)**

Command-line interface for tap operations:

```python
class WMSCLIRunner:
    """CLI runner for WMS tap operations."""

    def __init__(self, config: WMSConfig):
        self.config = config
        self.tap = TapOracleWMS(config=config.dict())

    def discover(self) -> Dict[str, Any]:
        """Run discovery and output catalog."""
        catalog = self.tap.catalog
        return catalog.to_dict()

    def test_connection(self) -> Tuple[bool, str]:
        """Test WMS connection."""
        try:
            auth_manager = WMSAuthManager(self.config)
            headers = auth_manager.authenticate()

            http_client = WMSHttpClient(self.config, auth_manager)
            response = http_client.get("/health")

            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {e}"

    def run_sync(
        self,
        catalog_path: Optional[str] = None,
        state_path: Optional[str] = None
    ) -> None:
        """Run tap synchronization."""
        if catalog_path:
            with open(catalog_path) as f:
                catalog_data = json.load(f)
                self.tap.catalog = Catalog.from_dict(catalog_data)

        if state_path:
            with open(state_path) as f:
                state_data = json.load(f)
                self.tap.load_state(state_data)

        self.tap.sync_all()
```

---

## 🔄 **Operation Workflows**

### **Complete Sync Workflow**

```python
async def execute_full_sync_workflow(
    tap: TapOracleWMS,
    catalog: Catalog,
    state: Optional[Dict] = None
) -> SyncResult:
    """Execute complete WMS data synchronization."""

    monitor = WMSMonitor(tap.config)
    monitor.start_sync()

    try:
        # 1. Initialize tap with catalog and state
        tap.catalog = catalog
        if state:
            tap.load_state(state)

        # 2. Validate configuration and connectivity
        await tap.test_connection()

        # 3. Process each selected stream
        selected_streams = [
            stream for stream in catalog.streams
            if stream.metadata.selected
        ]

        sync_results = {}
        for catalog_stream in selected_streams:
            stream = tap.get_stream(catalog_stream.tap_stream_id)

            # Execute stream sync
            stream_result = await sync_stream_with_monitoring(
                stream, monitor, catalog_stream
            )
            sync_results[catalog_stream.tap_stream_id] = stream_result

        # 4. Generate final sync report
        return SyncResult(
            streams_synced=len(sync_results),
            total_records=sum(r.records_synced for r in sync_results.values()),
            sync_duration=monitor.get_duration(),
            final_state=tap.get_state(),
            performance_metrics=monitor.get_performance_summary()
        )

    except Exception as e:
        monitor.record_error(e, {"operation": "full_sync"})
        raise
    finally:
        monitor.end_sync()
```

---

## 🧪 **Testing Utilities**

### **Test Patterns**

```python
@pytest.mark.asyncio
async def test_stream_discovery():
    """Test WMS stream discovery functionality."""
    config = WMSConfig(
        wms_base_url="https://test-wms.oracle.com",
        username="test_user",
        password="test_password",
        facility_id="TEST_FACILITY"
    )

    discovery_service = WMSDiscoveryService(config)

    # Mock API responses
    with aioresponses() as mock:
        mock.get(
            "https://test-wms.oracle.com/metadata/entities",
            payload={"entities": [
                {
                    "name": "items",
                    "endpoint": "/items",
                    "primaryKey": "itemId",
                    "supportsIncremental": True,
                    "incrementalKey": "lastModified"
                }
            ]}
        )

        streams = await discovery_service.discover_all_streams()
        assert len(streams) == 1
        assert streams[0].name == "items"
```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete TAP Oracle WMS documentation
- [Examples](../examples/README.md) - Usage examples and configurations
- [Tests](../tests/README.md) - Testing strategies and utilities

### **Singer SDK References**

- [Singer SDK Documentation](https://sdk.meltano.com/en/latest/) - Singer SDK specification
- [Stream Patterns](https://sdk.meltano.com/en/latest/stream_maps.html) - Stream implementation patterns
- [Authentication Patterns](https://sdk.meltano.com/en/latest/guides/authentication.html) - Auth implementation

### **Oracle WMS References**

- [Oracle WMS REST API](https://docs.oracle.com/en/cloud/saas/applications/24a/fawms/api-warehouse-management/) - Official API reference
- [Oracle Cloud Authentication](https://docs.oracle.com/en/cloud/get-started/subscriptions-cloud/csgsg/authentication.html) - Authentication methods

---

**📂 Module**: Source Implementation | **🏠 Component**: [TAP Oracle WMS](../README.md) | **Framework**: Singer SDK 0.35.0+ | **Updated**: 2025-06-19

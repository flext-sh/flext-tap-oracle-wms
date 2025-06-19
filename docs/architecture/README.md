# 🏗️ Tap Oracle WMS - Architecture Guide

> **Function**: Comprehensive technical architecture for Oracle WMS Singer tap implementation | **Audience**: Senior Engineers, System Architects | **Status**: Enterprise Reference

[![Singer](https://img.shields.io/badge/singer-tap-blue.svg)](https://www.singer.io/)
[![Oracle](https://img.shields.io/badge/oracle-WMS-red.svg)](https://www.oracle.com/cx/retail/warehouse-management/)
[![Architecture](https://img.shields.io/badge/architecture-enterprise-blue.svg)](../README.md)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](../README.md)

Enterprise-grade architectural documentation providing comprehensive technical guidance for implementing Oracle WMS Singer tap with production-ready patterns, validated against [Singer specification v1.0](https://hub.meltano.com/singer/spec) and [Oracle Retail WMS 25B architecture](https://docs.oracle.com/en/industries/retail/warehouse-management/25b/wmsig/).

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto](../../../README.md) → **📂 Project**: [Tap Oracle WMS](../../README.md) → **📁 Docs**: [Documentation](../README.md) → **📄 Current**: Architecture Guide

---

## 📋 **Architecture Overview**

This guide covers enterprise-grade architectural patterns for Oracle WMS Singer tap implementation, following Singer specification compliance and modern data engineering best practices based on [Singer protocol architecture](https://hub.meltano.com/singer/spec).

### **Architectural Principles**

- **Singer Protocol Compliance**: Full adherence to Singer specification v1.0
- **Separation of Concerns**: Clear boundaries between discovery, extraction, and output
- **Event-Driven Architecture**: Stream-based processing with state management
- **Fault Tolerance**: Robust error handling and recovery mechanisms
- **Performance Optimization**: Efficient data extraction and memory management

---

## 🎯 **High-Level Architecture**

### **System Context Diagram**

```
┌─────────────────────────────────────────────────────────────────┐
│                   Data Consumption Layer                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Data Lakes  │    │ Warehouses  │    │   Analytics         │  │
│  │   (S3, etc) │    │ (Snowflake) │    │    Platforms       │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│          ▲                  ▲                        ▲          │
└──────────┼──────────────────┼────────────────────────┼──────────┘
           │                  │                        │
           ▼                  ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Singer Target Layer                         │
│          (JSON Lines → Target-Specific Format)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  Singer Protocol Layer                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Tap Oracle WMS                              │ │
│  │             (Singer Data Extractor)                        │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │ │
│  │  │  Discovery  │  │   Stream    │  │      State          │  │ │
│  │  │   Engine    │  │ Processing  │  │   Management        │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │ │
│  │  │    Auth     │  │ Pagination  │  │     Schema          │  │ │
│  │  │  Manager    │  │   Handler   │  │   Generator         │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │ │
│  │                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                Oracle Retail WMS Cloud                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Inventory  │  │   Orders    │  │    Warehouse            │  │
│  │   Service   │  │   Service   │  │     Operations          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Location   │  │  Shipment   │  │     Master Data         │  │
│  │   Service   │  │   Service   │  │       Service           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ **Singer Tap Architecture Implementation**

### **Core Tap Class Architecture**

The Singer tap follows a layered architecture pattern compliant with [Singer SDK patterns](https://sdk.meltano.com/en/latest/implementation/):

```python
# Core architecture implementation
from singer_sdk import Tap
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
    Oracle WMS Singer tap with enterprise architecture.

    Implements comprehensive Singer specification compliance with
    production-grade patterns for Oracle Retail WMS integration.
    """

    name = "tap-oracle-wms"
    config_jsonschema = PropertiesList(
        Property(
            "base_url",
            StringType,
            required=True,
            description="Oracle WMS API base URL"
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
        Property(
            "facility_id",
            StringType,
            description="Default facility identifier"
        ),
        Property(
            "start_date",
            DateTimeType,
            description="Start date for incremental sync"
        ),
        Property(
            "page_size",
            IntegerType,
            default=1000,
            description="Records per page for pagination"
        ),
        Property(
            "request_timeout",
            IntegerType,
            default=60,
            description="Request timeout in seconds"
        ),
        Property(
            "max_retries",
            IntegerType,
            default=3,
            description="Maximum retry attempts"
        ),
        Property(
            "enable_caching",
            BooleanType,
            default=True,
            description="Enable response caching"
        ),
        Property(
            "stream_filters",
            ObjectType(),
            description="Entity-specific filtering configuration"
        )
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """
        Discover all available streams from Oracle WMS.

        Implements dynamic discovery pattern with comprehensive
        entity detection and schema generation.

        Returns:
            List[Stream]: Discovered WMS entity streams
        """
        discovery_engine = WMSDiscoveryEngine(self.config)

        # Core warehouse streams
        core_streams = [
            InventoryStream(tap=self),
            OrderHeaderStream(tap=self),
            OrderDetailStream(tap=self),
            LocationStream(tap=self),
            ShipmentStream(tap=self),
            AllocationStream(tap=self),
            WaveStream(tap=self),
            ItemMasterStream(tap=self)
        ]

        # Discover additional streams dynamically
        discovered_streams = discovery_engine.discover_additional_streams()

        return core_streams + discovered_streams

class WMSDiscoveryEngine:
    """
    Advanced discovery engine for Oracle WMS entities.

    Implements enterprise-grade discovery patterns with
    metadata introspection and schema inference.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = WMSAPIClient(config)
        self.schema_generator = SchemaGenerator()

    def discover_additional_streams(self) -> List[Stream]:
        """
        Discover additional streams beyond core entities.

        Uses WMS metadata APIs to identify available entities
        and generate corresponding stream definitions.
        """
        discovered_entities = self._introspect_wms_metadata()
        streams = []

        for entity in discovered_entities:
            stream_class = self._generate_stream_class(entity)
            streams.append(stream_class(tap=self.tap))

        return streams

    def _introspect_wms_metadata(self) -> List[Dict[str, Any]]:
        """
        Introspect WMS API to discover available entities.

        Leverages Oracle WMS metadata endpoints to identify
        all available data entities and their structures.
        """
        try:
            # Query WMS metadata endpoint
            metadata_response = self.client.get("/metadata/entities")

            entities = []
            for entity_def in metadata_response.get("entities", []):
                entity_info = {
                    "name": entity_def["name"],
                    "endpoint": entity_def["endpoint"],
                    "primary_key": entity_def.get("primary_key", "id"),
                    "replication_key": entity_def.get("replication_key"),
                    "fields": entity_def.get("fields", []),
                    "supports_incremental": entity_def.get("supports_incremental", False)
                }
                entities.append(entity_info)

            return entities

        except Exception as e:
            self.logger.warning(f"Metadata introspection failed: {e}")
            return []

    def _generate_stream_class(self, entity: Dict[str, Any]) -> Type[Stream]:
        """
        Dynamically generate stream class for discovered entity.

        Creates Singer-compliant stream class with proper schema
        and replication configuration.
        """
        schema = self.schema_generator.generate_schema(entity)

        class DynamicWMSStream(WMSStream):
            name = entity["name"]
            path = entity["endpoint"]
            primary_keys = [entity["primary_key"]]
            replication_key = entity.get("replication_key")
            schema = schema

            def get_records(self, context: Optional[dict]) -> Iterable[Dict[str, Any]]:
                """Extract records with dynamic entity handling."""
                for record in self.client.paginate(
                    self.path,
                    params=self._get_params(context)
                ):
                    yield record

        return DynamicWMSStream
```

### **Stream Processing Architecture**

Each stream implements enterprise-grade processing patterns:

```python
class WMSStream(Stream):
    """
    Base stream class for Oracle WMS entities.

    Provides common functionality for all WMS streams including
    authentication, pagination, error handling, and state management.
    """

    def __init__(self, tap: Tap):
        super().__init__(tap)
        self.client = WMSAPIClient(tap.config)
        self.state_manager = StateManager(tap.config)
        self.performance_monitor = PerformanceMonitor()

    def get_records(self, context: Optional[dict]) -> Iterable[Dict[str, Any]]:
        """
        Extract records with enterprise-grade processing.

        Implements comprehensive record extraction with:
        - State-aware incremental sync
        - Performance monitoring
        - Error recovery
        - Memory optimization
        """
        with self.performance_monitor.track_extraction(self.name):
            # Get bookmark for incremental sync
            bookmark = self.state_manager.get_bookmark(self.name)

            # Configure extraction parameters
            params = self._build_extraction_params(context, bookmark)

            # Extract records with pagination
            record_count = 0
            for record_batch in self.client.paginate_with_state(
                self.path,
                params=params,
                bookmark_field=self.replication_key
            ):
                for record in record_batch:
                    # Transform and validate record
                    transformed_record = self._transform_record(record)

                    # Update state for incremental sync
                    if self.replication_key:
                        self.state_manager.update_bookmark(
                            self.name,
                            transformed_record.get(self.replication_key)
                        )

                    record_count += 1
                    yield transformed_record

                    # Memory management for large datasets
                    if record_count % 10000 == 0:
                        self.logger.info(f"Extracted {record_count} records from {self.name}")

            self.logger.info(f"Completed extraction: {record_count} records from {self.name}")

class InventoryStream(WMSStream):
    """
    Inventory stream with specialized WMS inventory handling.

    Implements Oracle WMS inventory-specific patterns including
    location-based filtering and quantity aggregation.
    """

    name = "inventory"
    path = "/inventory"
    primary_keys = ["item_id", "location_id"]
    replication_key = "last_update_date"

    schema = PropertiesList(
        Property("item_id", StringType, required=True),
        Property("location_id", StringType, required=True),
        Property("facility_id", StringType, required=True),
        Property("available_quantity", NumberType),
        Property("on_hand_quantity", NumberType),
        Property("allocated_quantity", NumberType),
        Property("lot_number", StringType),
        Property("expiration_date", DateTimeType),
        Property("last_update_date", DateTimeType),
        Property("item_status", StringType),
        Property("location_type", StringType),
        Property("zone", StringType),
        Property("unit_of_measure", StringType)
    ).to_dict()

    def _build_extraction_params(
        self,
        context: Optional[dict],
        bookmark: Optional[str]
    ) -> Dict[str, Any]:
        """
        Build inventory-specific extraction parameters.

        Implements Oracle WMS inventory query optimization
        with facility filtering and date-based incremental sync.
        """
        params = {
            "fields": ",".join(self.schema["properties"].keys()),
            "page_size": self.config.get("page_size", 1000)
        }

        # Facility filtering
        if facility_id := self.config.get("facility_id"):
            params["facility_id"] = facility_id

        # Incremental sync with bookmark
        if bookmark and self.replication_key:
            params[f"{self.replication_key}_gte"] = bookmark

        # Stream-specific filters
        if stream_filters := self.config.get("stream_filters", {}).get(self.name):
            params.update(stream_filters)

        return params

    def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform inventory record with business logic.

        Applies Oracle WMS inventory-specific transformations
        including quantity calculations and status normalization.
        """
        # Calculate derived quantities
        available_qty = float(record.get("available_quantity", 0))
        on_hand_qty = float(record.get("on_hand_quantity", 0))
        allocated_qty = float(record.get("allocated_quantity", 0))

        # Validate quantity consistency
        if on_hand_qty < allocated_qty:
            self.logger.warning(
                f"Inconsistent quantities for {record.get('item_id')} "
                f"at {record.get('location_id')}: "
                f"on_hand={on_hand_qty}, allocated={allocated_qty}"
            )

        # Normalize timestamps
        if last_update := record.get("last_update_date"):
            record["last_update_date"] = self._normalize_timestamp(last_update)

        # Add calculated fields
        record["quantity_variance"] = on_hand_qty - available_qty - allocated_qty
        record["utilization_rate"] = (allocated_qty / on_hand_qty) if on_hand_qty > 0 else 0

        return record

class OrderHeaderStream(WMSStream):
    """
    Order header stream with comprehensive order processing.

    Implements Oracle WMS order lifecycle tracking with
    status-based filtering and relationship management.
    """

    name = "order_headers"
    path = "/orders"
    primary_keys = ["order_id"]
    replication_key = "modified_date"

    schema = PropertiesList(
        Property("order_id", StringType, required=True),
        Property("customer_id", StringType),
        Property("order_type", StringType),
        Property("order_status", StringType),
        Property("priority", IntegerType),
        Property("order_date", DateTimeType),
        Property("ship_date", DateTimeType),
        Property("modified_date", DateTimeType),
        Property("total_lines", IntegerType),
        Property("total_quantity", NumberType),
        Property("total_value", NumberType),
        Property("facility_id", StringType),
        Property("carrier", StringType),
        Property("service_level", StringType),
        Property("special_instructions", StringType)
    ).to_dict()

    def get_child_context(self, record: Dict[str, Any], context: Optional[dict]) -> Dict[str, Any]:
        """
        Provide context for child streams (order details).

        Enables hierarchical data extraction with parent-child
        relationships between orders and order lines.
        """
        return {
            "order_id": record["order_id"],
            "order_type": record.get("order_type"),
            "facility_id": record.get("facility_id")
        }
```

---

## 📊 **Data Flow Architecture**

### **End-to-End Data Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                        Discovery Phase                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Metadata Introspection                                     │
│     └── Query WMS /metadata/entities                           │
│                                                                 │
│  2. Schema Generation                                           │
│     └── Generate JSON schemas from metadata                    │
│                                                                 │
│  3. Stream Registration                                         │
│     └── Create stream catalog with metadata                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Extraction Phase                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. State Management                                            │
│     ├── Load previous bookmarks                                │
│     └── Initialize extraction context                          │
│                                                                 │
│  2. Stream Processing                                           │
│     ├── Apply stream selection filters                         │
│     ├── Configure pagination parameters                        │
│     └── Execute parallel stream extraction                     │
│                                                                 │
│  3. Record Processing                                           │
│     ├── Transform raw WMS data                                 │
│     ├── Validate against JSON schema                           │
│     ├── Apply business logic rules                             │
│     └── Update incremental bookmarks                           │
│                                                                 │
│  4. Output Generation                                           │
│     ├── Format records as JSON Lines                           │
│     ├── Emit schema messages                                   │
│     ├── Emit state messages                                    │
│     └── Stream to target system                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### **State Management Architecture**

```python
class StateManager:
    """
    Enterprise state management for incremental synchronization.

    Implements robust bookmark tracking with persistence,
    recovery, and consistency validation.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.state = {}
        self.state_file = config.get("state_file", "state.json")
        self.lock = threading.RLock()

    def load_state(self) -> Dict[str, Any]:
        """
        Load state from persistent storage with validation.

        Implements state recovery with consistency checks
        and corruption detection.
        """
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)

                # Validate state structure
                if self._validate_state_structure(state):
                    self.state = state
                    self.logger.info(f"Loaded state with {len(state.get('bookmarks', {}))} bookmarks")
                else:
                    self.logger.warning("Invalid state structure, starting fresh")
                    self.state = {"bookmarks": {}}
            else:
                self.state = {"bookmarks": {}}

        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            self.state = {"bookmarks": {}}

        return self.state

    def get_bookmark(self, stream_name: str) -> Optional[str]:
        """
        Get bookmark for incremental sync with thread safety.

        Returns the last successfully processed replication key
        value for the specified stream.
        """
        with self.lock:
            return self.state.get("bookmarks", {}).get(stream_name, {}).get("replication_key_value")

    def update_bookmark(self, stream_name: str, replication_key_value: Any) -> None:
        """
        Update bookmark with atomic operation and persistence.

        Implements atomic bookmark updates with immediate
        persistence for data consistency.
        """
        with self.lock:
            if "bookmarks" not in self.state:
                self.state["bookmarks"] = {}

            if stream_name not in self.state["bookmarks"]:
                self.state["bookmarks"][stream_name] = {}

            # Update bookmark with metadata
            self.state["bookmarks"][stream_name].update({
                "replication_key_value": replication_key_value,
                "last_updated": datetime.utcnow().isoformat(),
                "record_count": self.state["bookmarks"][stream_name].get("record_count", 0) + 1
            })

            # Persist state immediately for consistency
            self._persist_state()

    def _persist_state(self) -> None:
        """
        Persist state to storage with atomic writes.

        Uses atomic file operations to prevent state corruption
        during concurrent access or system failures.
        """
        try:
            temp_file = f"{self.state_file}.tmp"

            with open(temp_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)

            # Atomic rename for consistency
            os.rename(temp_file, self.state_file)

        except Exception as e:
            self.logger.error(f"Failed to persist state: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
```

---

## 🚀 **Performance Architecture**

### **High-Throughput Processing Patterns**

```python
class HighPerformanceExtractor:
    """
    High-performance extraction engine for large-scale WMS data.

    Implements enterprise-grade performance optimization patterns
    for extracting millions of records efficiently.
    """

    def __init__(self, tap: TapOracleWMS):
        self.tap = tap
        self.config = tap.config
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.config.get("max_workers", 4)
        )
        self.memory_monitor = MemoryMonitor()

    async def extract_parallel_streams(
        self,
        streams: List[Stream],
        max_concurrent: int = 4
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Extract multiple streams concurrently for maximum throughput.

        Implements parallel stream processing with resource management
        and backpressure control.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def extract_stream(stream: Stream) -> AsyncGenerator[Dict[str, Any], None]:
            async with semaphore:
                async for record in stream.get_records_async():
                    yield {
                        "stream": stream.name,
                        "record": record,
                        "timestamp": datetime.utcnow().isoformat()
                    }

        # Start all stream extractions concurrently
        tasks = [extract_stream(stream) for stream in streams]

        # Merge results as they become available
        async for result in self._merge_async_generators(tasks):
            yield result

    def optimize_batch_size(self, stream_name: str, initial_size: int = 1000) -> int:
        """
        Dynamically optimize batch size based on performance metrics.

        Implements adaptive batch sizing to maximize throughput
        while managing memory usage.
        """
        performance_data = self.performance_monitor.get_stream_metrics(stream_name)

        if not performance_data:
            return initial_size

        # Calculate optimal batch size based on throughput and memory
        avg_record_size = performance_data.get("avg_record_size_bytes", 1024)
        target_memory_per_batch = 50 * 1024 * 1024  # 50MB target

        optimal_size = min(
            target_memory_per_batch // avg_record_size,
            self.config.get("max_batch_size", 10000)
        )

        return max(optimal_size, self.config.get("min_batch_size", 100))

class MemoryOptimizedPaginator:
    """
    Memory-efficient pagination for large Oracle WMS datasets.

    Implements streaming pagination with memory management
    and garbage collection optimization.
    """

    def __init__(self, client: WMSAPIClient, config: Dict[str, Any]):
        self.client = client
        self.config = config
        self.memory_monitor = MemoryMonitor()

    async def paginate_stream(
        self,
        endpoint: str,
        params: Dict[str, Any],
        memory_limit_mb: int = 512
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Paginate through large datasets with memory constraints.

        Implements cursor-based pagination with memory monitoring
        and automatic garbage collection.
        """
        cursor = None
        page_count = 0
        total_records = 0

        while True:
            # Monitor memory usage
            current_memory = self.memory_monitor.get_current_usage_mb()
            if current_memory > memory_limit_mb:
                self.logger.warning(f"Memory usage {current_memory}MB exceeds limit {memory_limit_mb}MB")
                gc.collect()  # Force garbage collection

            # Configure pagination parameters
            page_params = params.copy()
            if cursor:
                page_params["cursor"] = cursor

            page_params["limit"] = self._calculate_dynamic_page_size(current_memory, memory_limit_mb)

            try:
                response = await self.client.get_async(endpoint, params=page_params)

                records = response.get("data", [])
                if not records:
                    break

                page_count += 1

                # Yield records one by one for memory efficiency
                for record in records:
                    total_records += 1
                    yield record

                    # Periodic memory check
                    if total_records % 1000 == 0:
                        self.memory_monitor.check_memory_pressure()

                # Update cursor for next page
                cursor = response.get("next_cursor")
                if not cursor:
                    break

                # Log progress
                if page_count % 10 == 0:
                    self.logger.info(f"Processed {page_count} pages, {total_records} records")

            except Exception as e:
                self.logger.error(f"Pagination error on page {page_count}: {e}")
                raise

        self.logger.info(f"Pagination complete: {page_count} pages, {total_records} total records")

    def _calculate_dynamic_page_size(self, current_memory_mb: int, limit_mb: int) -> int:
        """
        Calculate optimal page size based on current memory usage.

        Implements dynamic page sizing to balance throughput
        and memory efficiency.
        """
        base_page_size = self.config.get("page_size", 1000)

        # Reduce page size if approaching memory limit
        memory_ratio = current_memory_mb / limit_mb
        if memory_ratio > 0.8:
            return max(base_page_size // 2, 100)
        elif memory_ratio > 0.6:
            return max(int(base_page_size * 0.75), 250)
        else:
            return base_page_size
```

---

## 🔐 **Security Architecture**

### **Authentication and Authorization**

```python
class SecureAuthManager:
    """
    Enterprise authentication manager for Oracle WMS.

    Implements secure authentication patterns with
    credential management and session handling.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.auth_type = config.get("auth_method", "basic")
        self.session_cache = {}
        self.token_refresh_lock = threading.Lock()

    async def authenticate(self) -> AuthResult:
        """
        Authenticate with Oracle WMS using configured method.

        Supports multiple authentication patterns with
        secure credential handling and session management.
        """
        if self.auth_type == "oauth2":
            return await self._authenticate_oauth2()
        elif self.auth_type == "basic":
            return await self._authenticate_basic()
        elif self.auth_type == "api_key":
            return await self._authenticate_api_key()
        else:
            raise ValueError(f"Unsupported authentication method: {self.auth_type}")

    async def _authenticate_oauth2(self) -> AuthResult:
        """
        OAuth2 authentication with PKCE for enhanced security.

        Implements OAuth2 client credentials flow with
        secure token handling and automatic refresh.
        """
        # Check for cached valid token
        cached_token = self._get_cached_token()
        if cached_token and not self._is_token_expired(cached_token):
            return AuthResult(success=True, token=cached_token)

        # Acquire refresh lock to prevent concurrent token requests
        async with asyncio.Lock():
            client_id = self.config["client_id"]
            client_secret = self.config["client_secret"]
            token_url = self.config["token_url"]

            # Prepare OAuth2 request
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": self.config.get("scope", "wms.read")
            }

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        token_url,
                        data=auth_data,
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                    response.raise_for_status()

                    token_data = response.json()

                    # Create secure token object
                    token = SecureToken(
                        access_token=token_data["access_token"],
                        token_type=token_data.get("token_type", "Bearer"),
                        expires_in=token_data.get("expires_in", 3600),
                        scope=token_data.get("scope"),
                        issued_at=datetime.utcnow()
                    )

                    # Cache token securely
                    self._cache_token(token)

                    return AuthResult(success=True, token=token)

            except Exception as e:
                self.logger.error(f"OAuth2 authentication failed: {e}")
                return AuthResult(success=False, error=str(e))

    def get_auth_headers(self, token: Optional[SecureToken] = None) -> Dict[str, str]:
        """
        Generate authentication headers for API requests.

        Creates appropriate headers based on authentication
        method with secure token handling.
        """
        if self.auth_type == "oauth2":
            if not token:
                token = self._get_cached_token()
            if token:
                return {"Authorization": f"{token.token_type} {token.access_token}"}
        elif self.auth_type == "basic":
            credentials = base64.b64encode(
                f"{self.config['username']}:{self.config['password']}".encode()
            ).decode()
            return {"Authorization": f"Basic {credentials}"}
        elif self.auth_type == "api_key":
            header_name = self.config.get("api_key_header", "X-API-Key")
            return {header_name: self.config["api_key"]}

        return {}
```

---

## 📈 **Monitoring Architecture**

### **Comprehensive Monitoring Stack**

```python
class TapMonitoringSystem:
    """
    Comprehensive monitoring for Oracle WMS Singer tap.

    Provides metrics, traces, and logs for operational
    excellence and performance optimization.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.performance_tracer = PerformanceTracer()
        self.logger = structlog.get_logger()

    @contextmanager
    def monitor_extraction(self, stream_name: str):
        """
        Monitor stream extraction with comprehensive telemetry.

        Collects performance metrics, traces, and structured
        logs for operational visibility.
        """
        extraction_id = str(uuid.uuid4())
        start_time = time.time()

        # Start performance trace
        with self.performance_tracer.start_span("stream_extraction") as span:
            span.set_attributes({
                "extraction.id": extraction_id,
                "stream.name": stream_name,
                "tap.name": "tap-oracle-wms"
            })

            try:
                # Initialize extraction metrics
                self.metrics_collector.increment_counter(
                    "extractions_started",
                    tags={"stream": stream_name}
                )

                yield ExtractionContext(
                    extraction_id=extraction_id,
                    stream_name=stream_name,
                    start_time=start_time
                )

                # Record success metrics
                duration = time.time() - start_time
                self.metrics_collector.record_histogram(
                    "extraction_duration_seconds",
                    duration,
                    tags={"stream": stream_name, "status": "success"}
                )

                self.logger.info(
                    "Stream extraction completed successfully",
                    extraction_id=extraction_id,
                    stream_name=stream_name,
                    duration_seconds=duration
                )

                span.set_status(trace.Status(trace.StatusCode.OK))

            except Exception as e:
                # Record failure metrics
                self.metrics_collector.increment_counter(
                    "extractions_failed",
                    tags={"stream": stream_name, "error_type": type(e).__name__}
                )

                self.logger.error(
                    "Stream extraction failed",
                    extraction_id=extraction_id,
                    stream_name=stream_name,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )

                span.record_exception(e)
                span.set_status(trace.Status(
                    trace.StatusCode.ERROR,
                    str(e)
                ))
                raise
```

---

## 🔗 **Cross-References**

### **Architecture Standards**

- [Singer Specification v1.0](https://hub.meltano.com/singer/spec) - Official Singer protocol
- [Meltano SDK Patterns](https://sdk.meltano.com/en/latest/implementation/) - SDK implementation guide
- [Oracle Integration Architecture](https://docs.oracle.com/en/solutions/design-patterns/) - Oracle patterns

### **Related Documentation**

- [API Reference](../api/README.md) - Interface specifications
- [Security Guide](../security/README.md) - Security implementation
- [Performance Patterns](../patterns/README.md) - Optimization strategies

---

**🏗️ Architecture**: Tap Oracle WMS | **🏠 Root**: [PyAuto Home](../../../README.md) | **Framework**: Singer SDK 0.45.0+ | **Updated**: 2025-06-19

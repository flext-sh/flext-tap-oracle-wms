# Oracle WMS Tap API Reference

## Table of Contents

- [TapOracleWMS](#taporaclewms)
- [OracleWMSStream](#oraclewmsstream)
- [EntityDiscovery](#entitydiscovery)
- [SchemaGenerator](#schemagenerator)
- [WMSAuthenticator](#wmsauthenticator)
- [CacheManager](#cachemanager)
- [Configuration Options](#configuration-options)
- [WMS Entity Reference](#wms-entity-reference)

## TapOracleWMS

Main Singer tap class for Oracle WMS.

### Class Definition

```python
class TapOracleWMS(Tap):
    """Singer tap for Oracle WMS Cloud REST APIs."""
```

### Properties

#### name

```python
name: str = "tap-oracle-wms"
```

The canonical name of the tap.

#### config_jsonschema

```python
config_jsonschema: dict
```

JSON schema for configuration validation.

#### default_stream_class

```python
default_stream_class = OracleWMSStream
```

Default stream class for WMS entities.

### Methods

#### discover_streams

```python
def discover_streams(self) -> list[Stream]
```

Discover available WMS entities and create streams.

**Returns:** List of discovered stream instances

**Example:**

```python
tap = TapOracleWMS(config)
streams = tap.discover_streams()
# Returns stream instances for each discovered WMS entity
```

#### get_singer_catalog

```python
def get_singer_catalog(self) -> Catalog
```

Generate Singer catalog from discovered streams.

**Returns:** Singer catalog with stream metadata

## OracleWMSStream

Base stream class for WMS entities.

### Class Definition

```python
class OracleWMSStream(RESTStream):
    """Base stream for Oracle WMS entities with HATEOAS pagination."""
```

### Properties

#### url_base

```python
@property
def url_base(self) -> str
```

Base URL for WMS API.

#### path

```python
@property
def path(self) -> str
```

API endpoint path for the entity.

#### primary_keys

```python
@property
def primary_keys(self) -> list[str]
```

Primary key fields for the entity.

#### replication_key

```python
@property
def replication_key(self) -> str | None
```

Field used for incremental replication.

#### schema

```python
@property
def schema(self) -> dict
```

JSON Schema for the stream.

### Methods

#### get_url_params

```python
def get_url_params(
    self,
    context: dict | None,
    next_page_token: Any | None
) -> dict[str, Any]
```

Build URL parameters for API request.

**Parameters:**

- `context`: Stream partition context
- `next_page_token`: Token for pagination

**Returns:** Dictionary of URL parameters

**Example:**

```python
params = stream.get_url_params(None, None)
# Returns: {"limit": 1000, "orderBy": "mod_ts"}
```

#### parse_response

```python
def parse_response(self, response: requests.Response) -> Iterable[dict]
```

Parse records from API response.

**Parameters:**

- `response`: HTTP response from WMS API

**Returns:** Iterator of parsed records

#### get_next_page_token

```python
def get_next_page_token(
    self,
    response: requests.Response,
    previous_token: Any | None
) -> Any | None
```

Extract next page token from HATEOAS links.

**Parameters:**

- `response`: Current page response
- `previous_token`: Previous page token

**Returns:** Next page token or None

#### post_process

```python
def post_process(
    self,
    row: dict,
    context: dict | None = None
) -> dict | None
```

Transform WMS record before emission.

**Parameters:**

- `row`: Raw record from API
- `context`: Stream context

**Returns:** Transformed record or None to skip

## EntityDiscovery

Discovers and describes WMS entities.

### Class Definition

```python
class EntityDiscovery:
    """Facade for WMS entity discovery operations."""
```

### Methods

#### **init**

```python
def __init__(self, config: dict[str, Any]) -> None
```

Initialize entity discovery.

**Parameters:**

- `config`: Tap configuration

#### discover_entities

```python
async def discover_entities(self) -> dict[str, str]
```

Discover available entities from WMS API.

**Returns:** Dictionary mapping entity names to API URLs

**Example:**

```python
discovery = EntityDiscovery(config)
entities = await discovery.discover_entities()
# Returns: {"customer": "/api/v1/customers", "order": "/api/v1/orders"}
```

#### describe_entity

```python
async def describe_entity(self, entity_name: str) -> dict[str, Any] | None
```

Get metadata description for an entity.

**Parameters:**

- `entity_name`: Name of the entity

**Returns:** Entity metadata or None

#### get_entity_sample

```python
async def get_entity_sample(
    self,
    entity_name: str,
    limit: int = 5
) -> list[dict[str, Any]]
```

Get sample records for schema inference.

**Parameters:**

- `entity_name`: Name of the entity
- `limit`: Maximum sample records

**Returns:** List of sample records

#### filter_entities

```python
def filter_entities(self, entities: dict[str, str]) -> dict[str, str]
```

Filter entities based on configuration.

**Parameters:**

- `entities`: Discovered entities

**Returns:** Filtered entity dictionary

## SchemaGenerator

Generates JSON Schema from WMS metadata.

### Class Definition

```python
class SchemaGenerator:
    """Generates JSON Schema from WMS metadata and samples."""
```

### Methods

#### generate_from_metadata

```python
def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]
```

Generate schema from API metadata.

**Parameters:**

- `metadata`: WMS entity metadata

**Returns:** JSON Schema

**Example:**

```python
generator = SchemaGenerator(config)
schema = generator.generate_from_metadata(entity_metadata)
```

#### generate_from_sample

```python
def generate_from_sample(self, samples: list[dict[str, Any]]) -> dict[str, Any]
```

Generate schema from sample records.

**Parameters:**

- `samples`: Sample records

**Returns:** Inferred JSON Schema

#### generate_hybrid_schema

```python
def generate_hybrid_schema(
    self,
    metadata: dict[str, Any],
    samples: list[dict[str, Any]]
) -> dict[str, Any]
```

Generate schema using both metadata and samples.

**Parameters:**

- `metadata`: Entity metadata
- `samples`: Sample records

**Returns:** Combined JSON Schema

#### flatten_complex_objects

```python
def flatten_complex_objects(
    self,
    data: dict[str, Any],
    prefix: str = "",
    separator: str = "_"
) -> dict[str, Any]
```

Flatten nested objects for simpler schema.

**Parameters:**

- `data`: Nested data structure
- `prefix`: Field name prefix
- `separator`: Separator for flattened names

**Returns:** Flattened dictionary

## WMSAuthenticator

Handles OAuth2 authentication for WMS API.

### Class Definition

```python
class WMSAuthenticator(OAuthAuthenticator):
    """OAuth2 authenticator for Oracle WMS."""
```

### Methods

#### **init**

```python
def __init__(
    self,
    stream: RESTStream,
    auth_endpoint: str | None = None,
    oauth_scopes: str | None = None
) -> None
```

Initialize OAuth2 authenticator.

**Parameters:**

- `stream`: Parent stream instance
- `auth_endpoint`: OAuth2 token endpoint
- `oauth_scopes`: Required OAuth scopes

#### update_access_token

```python
def update_access_token(self) -> None
```

Refresh the OAuth2 access token.

#### auth_headers

```python
@property
def auth_headers(self) -> dict[str, Any]
```

Get authentication headers.

**Returns:** Headers with Bearer token

## CacheManager

Manages response caching for performance.

### Class Definition

```python
class CacheManager:
    """Manages caching for WMS API responses."""
```

### Methods

#### get

```python
def get(self, key: str) -> Any | None
```

Get cached value.

**Parameters:**

- `key`: Cache key

**Returns:** Cached value or None

#### set

```python
def set(self, key: str, value: Any, ttl: int | None = None) -> None
```

Set cache value.

**Parameters:**

- `key`: Cache key
- `value`: Value to cache
- `ttl`: Time to live in seconds

#### clear_cache

```python
def clear_cache(self, cache_type: str = "all") -> None
```

Clear cache entries.

**Parameters:**

- `cache_type`: Type of cache to clear

## Configuration Options

### Connection Settings

| Option          | Type   | Required | Default  | Description           |
| --------------- | ------ | -------- | -------- | --------------------- |
| `base_url`      | string | Yes      | -        | WMS API base URL      |
| `client_id`     | string | Yes      | -        | OAuth2 client ID      |
| `client_secret` | string | Yes      | -        | OAuth2 client secret  |
| `wms_version`   | string | No       | "23.3.3" | WMS API version       |
| `facility_code` | string | No       | -        | Default facility code |

### Performance Settings

| Option               | Type    | Default | Description               |
| -------------------- | ------- | ------- | ------------------------- |
| `page_size`          | integer | 100     | Records per API page      |
| `request_timeout`    | integer | 300     | Request timeout (seconds) |
| `max_parallel_pages` | integer | 5       | Concurrent page fetches   |
| `cache_enabled`      | boolean | true    | Enable response caching   |
| `cache_ttl`          | integer | 3600    | Cache TTL (seconds)       |

### Entity Selection

| Option              | Type    | Default | Description               |
| ------------------- | ------- | ------- | ------------------------- |
| `entities`          | array   | []      | Specific entities to sync |
| `exclude_entities`  | array   | []      | Entities to exclude       |
| `discover_entities` | boolean | true    | Auto-discover entities    |
| `entity_filter`     | string  | -       | Regex filter for entities |

### Schema Generation

| Option                      | Type    | Default | Description            |
| --------------------------- | ------- | ------- | ---------------------- |
| `flattening_enabled`        | boolean | true    | Flatten nested objects |
| `flattening_max_depth`      | integer | 3       | Max flattening depth   |
| `infer_schema_from_samples` | boolean | true    | Use samples for schema |
| `sample_size`               | integer | 5       | Records for inference  |

### Incremental Sync

| Option                    | Type    | Default | Description             |
| ------------------------- | ------- | ------- | ----------------------- |
| `start_date`              | string  | -       | Start date for sync     |
| `lookback_window`         | integer | 0       | Lookback seconds        |
| `state_partitioning_keys` | array   | []      | Partition state by keys |

## WMS Entity Reference

### Standard Entities

| Entity       | Primary Keys                | Replication Key | Description           |
| ------------ | --------------------------- | --------------- | --------------------- |
| `customer`   | [`customer_id`]             | `mod_ts`        | Customer master       |
| `order`      | [`order_id`]                | `mod_ts`        | Order headers         |
| `order_line` | [`order_id`, `line_number`] | `mod_ts`        | Order lines           |
| `shipment`   | [`shipment_id`]             | `mod_ts`        | Shipments             |
| `inventory`  | [`item_id`, `location_id`]  | `mod_ts`        | Inventory             |
| `item`       | [`item_id`]                 | `mod_ts`        | Item master           |
| `location`   | [`location_id`]             | `mod_ts`        | Warehouse locations   |
| `adjustment` | [`adjustment_id`]           | `created_ts`    | Inventory adjustments |
| `receipt`    | [`receipt_id`]              | `mod_ts`        | Receipts              |
| `allocation` | [`allocation_id`]           | `mod_ts`        | Allocations           |

### Entity Field Types

Common field patterns across entities:

| Field Pattern | JSON Type          | Description     |
| ------------- | ------------------ | --------------- |
| `*_id`        | string             | Identifiers     |
| `*_ts`        | string (date-time) | Timestamps      |
| `*_qty`       | number             | Quantities      |
| `*_flg`       | boolean            | Flags           |
| `*_code`      | string             | Codes           |
| `*_desc`      | string             | Descriptions    |
| `*_amount`    | number             | Monetary values |

## Examples

### Basic Tap Usage

```python
from tap_oracle_wms import TapOracleWMS

# Initialize tap
config = {
    "base_url": "https://wms.example.com",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "entities": ["customer", "order", "inventory"]
}

tap = TapOracleWMS(config)

# Discover and sync
tap.run_discovery()
tap.run_sync()
```

### Custom Stream Implementation

```python
class CustomOrderStream(OracleWMSStream):
    """Custom order stream with business logic."""

    name = "order"
    path = "/orders"
    primary_keys = ["order_id"]
    replication_key = "mod_ts"

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """Add custom processing."""
        row = super().post_process(row, context)

        if row:
            # Custom business logic
            row["order_total"] = sum(line["amount"] for line in row.get("lines", []))

        return row
```

### Entity Discovery

```python
import asyncio
from tap_oracle_wms.discovery import EntityDiscovery

async def discover():
    discovery = EntityDiscovery(config)

    # Discover all entities
    entities = await discovery.discover_entities()
    print(f"Found entities: {list(entities.keys())}")

    # Get entity metadata
    metadata = await discovery.describe_entity("order")
    print(f"Order fields: {metadata['fields']}")

    # Get sample data
    samples = await discovery.get_entity_sample("order", limit=10)
    print(f"Sample orders: {len(samples)}")

asyncio.run(discover())
```

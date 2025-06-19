# Oracle WMS Entity Discovery

## Overview

Oracle WMS provides a powerful entity discovery mechanism that allows applications to dynamically discover available entities, their schemas, and relationships. This enables tap-oracle-wms to adapt automatically to different WMS configurations without hardcoding entity definitions.

## Entity Discovery API

### Primary Discovery Endpoint

```http
GET /wms/lgfapi/v10/entity
```

This endpoint returns a complete dictionary of all available entities in the WMS instance.

**Response Structure:**

```json
{
  "allocation": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/allocation",
  "appointment": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/appointment",
  "barcode_type": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/barcode_type",
  "batch_nbr": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/batch_nbr",
  "break_type": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/break_type"
  // ... 300+ more entities
}
```

### Entity Metadata Endpoint

```http
GET /wms/lgfapi/v10/entity/{entity_name}/describe/
```

Returns detailed metadata about a specific entity including field definitions, types, and constraints.

**Response Structure:**

```json
{
  "parameters": [
    {
      "name": "id",
      "type": "integer",
      "required": "X",
      "max_length": null,
      "allow_blank": false,
      "default": null,
      "description": "Primary key identifier"
    },
    {
      "name": "code",
      "type": "string",
      "required": "Y",
      "max_length": 50,
      "allow_blank": false,
      "default": null,
      "description": "Unique code for the entity"
    },
    {
      "name": "status",
      "type": "string",
      "required": "N",
      "max_length": 20,
      "allow_blank": true,
      "default": "ACTIVE",
      "choices": ["ACTIVE", "INACTIVE", "PENDING"],
      "description": "Current status of the record"
    },
    {
      "name": "facility_id",
      "type": "integer",
      "required": "C",
      "related_entity": "facility",
      "description": "Reference to facility entity"
    }
  ]
}
```

## Field Metadata Structure

### Field Types

The `type` field indicates the data type:

| Type       | Description         | JSON Schema Type     |
| ---------- | ------------------- | -------------------- |
| `integer`  | Whole numbers       | `integer`            |
| `string`   | Text values         | `string`             |
| `number`   | Decimal numbers     | `number`             |
| `boolean`  | True/false values   | `boolean`            |
| `datetime` | ISO 8601 timestamps | `string` with format |
| `date`     | ISO 8601 dates      | `string` with format |
| `array`    | List of values      | `array`              |
| `object`   | Nested object       | `object`             |

### Required Field Indicators

The `required` field uses these codes:

| Code | Meaning                       | JSON Schema Required  |
| ---- | ----------------------------- | --------------------- |
| `X`  | Always required (primary key) | Yes                   |
| `Y`  | Required for create/update    | Yes                   |
| `N`  | Optional                      | No                    |
| `C`  | Conditionally required        | No (with description) |

### Field Constraints

Additional metadata provides constraints:

- **`max_length`**: Maximum character length for strings
- **`allow_blank`**: Whether empty strings are allowed
- **`default`**: Default value if not provided
- **`choices`**: Enumerated values allowed
- **`min_value`/`max_value`**: Numeric ranges
- **`related_entity`**: Foreign key reference

## Schema Discovery Methods

tap-oracle-wms uses multiple methods to discover schemas:

### 1. Describe Endpoint (Primary)

```python
async def discover_schema_from_describe(entity_name: str) -> dict:
    """Get schema from describe endpoint."""
    response = await client.get(f"/entity/{entity_name}/describe/")
    return parse_describe_response(response.json())
```

### 2. OPTIONS Method

```python
async def discover_schema_from_options(entity_name: str) -> dict:
    """Get schema from OPTIONS response."""
    response = await client.options(f"/entity/{entity_name}")
    if "X-Schema" in response.headers:
        return json.loads(response.headers["X-Schema"])
    return None
```

### 3. Sample Data Inference

```python
async def infer_schema_from_sample(entity_name: str) -> dict:
    """Infer schema from sample records."""
    response = await client.get(f"/entity/{entity_name}?page_size=5")
    data = response.json()
    if data.get("results"):
        return infer_types(data["results"])
    return None
```

## Dynamic Stream Generation

Based on discovered entities, tap-oracle-wms generates streams dynamically:

```python
class WMSEntityStream(RESTStream):
    """Dynamic stream for any WMS entity."""

    def __init__(self, tap, entity_name: str, schema: dict):
        self.entity_name = entity_name
        self._schema = schema
        super().__init__(tap)

    @property
    def name(self) -> str:
        return self.entity_name

    @property
    def path(self) -> str:
        return f"/entity/{self.entity_name}"

    @property
    def schema(self) -> dict:
        return self._schema
```

## Entity Categories

WMS entities are organized into functional categories:

### Core Master Data

- `company`: Companies/tenants
- `facility`: Warehouse facilities
- `item`: Products/SKUs
- `location`: Storage locations
- `user`: System users

### Inventory Management

- `inventory`: On-hand inventory
- `allocation`: Reserved inventory
- `batch_nbr`: Batch/lot tracking
- `serial_nbr`: Serial number tracking
- `lock_code`: Inventory locks

### Inbound Operations

- `receipt`: Receipt headers
- `receipt_dtl`: Receipt details
- `iblpn`: Inbound containers
- `iblpn_dtl`: Container contents
- `putaway`: Put-away tasks

### Outbound Operations

- `order_hdr`: Order headers
- `order_dtl`: Order details
- `oblpn`: Outbound containers
- `oblpn_dtl`: Container contents
- `shipment`: Shipment documents
- `wave`: Wave planning

### Warehouse Operations

- `task`: Warehouse tasks
- `task_dtl`: Task details
- `replenishment`: Replenishment tasks
- `cycle_count`: Inventory counts
- `rf_menu`: RF device menus

### Configuration

- `screen_config`: UI configurations
- `rule`: Business rules
- `reason_code`: Transaction reasons
- `parameter`: System parameters

## Entity Relationships

Entities have relationships defined through foreign keys:

```json
{
  "name": "order_dtl",
  "parameters": [
    {
      "name": "order_id",
      "type": "integer",
      "related_entity": "order_hdr",
      "relationship": "many-to-one"
    },
    {
      "name": "item_id",
      "type": "integer",
      "related_entity": "item",
      "relationship": "many-to-one"
    }
  ]
}
```

## Schema Caching

To optimize performance, discovered schemas are cached:

```python
class SchemaCache:
    def __init__(self, ttl_seconds: int = 3600):
        self._cache = {}
        self._timestamps = {}
        self.ttl = ttl_seconds

    def get(self, entity_name: str) -> Optional[dict]:
        if entity_name in self._cache:
            if time.time() - self._timestamps[entity_name] < self.ttl:
                return self._cache[entity_name]
        return None

    def set(self, entity_name: str, schema: dict):
        self._cache[entity_name] = schema
        self._timestamps[entity_name] = time.time()
```

## Handling Schema Changes

WMS schemas can change with updates. tap-oracle-wms handles this:

1. **Version Detection**: Check WMS version on startup
2. **Schema Refresh**: Periodically refresh cached schemas
3. **Graceful Degradation**: Handle new/removed fields
4. **Schema Evolution**: Track schema versions in state

## Best Practices

### 1. Cache Entity List

The entity list changes infrequently, so cache it:

```python
entity_list = await discover_entities()
cache.set("entity_list", entity_list, ttl=86400)  # 24 hours
```

### 2. Lazy Schema Loading

Load schemas only when needed:

```python
async def get_stream_schema(entity_name: str) -> dict:
    schema = cache.get(f"schema_{entity_name}")
    if not schema:
        schema = await discover_schema(entity_name)
        cache.set(f"schema_{entity_name}", schema)
    return schema
```

### 3. Handle Missing Entities

Some entities may not be available in all configurations:

```python
try:
    schema = await discover_schema(entity_name)
except HTTPStatusError as e:
    if e.response.status_code == 404:
        logger.warning(f"Entity {entity_name} not available")
        return None
    raise
```

### 4. Schema Validation

Validate discovered schemas before use:

```python
def validate_schema(schema: dict) -> bool:
    required_fields = ["type", "properties"]
    return all(field in schema for field in required_fields)
```

## Entity Filtering

Not all discovered entities may be relevant. Filter by:

### 1. Entity Name Patterns

```python
def is_relevant_entity(entity_name: str) -> bool:
    # Skip system/internal entities
    if entity_name.startswith("_"):
        return False
    # Skip deprecated entities
    if "_old" in entity_name:
        return False
    return True
```

### 2. Required Permissions

Some entities require specific permissions:

```python
async def check_entity_access(entity_name: str) -> bool:
    try:
        response = await client.get(f"/entity/{entity_name}?page_size=1")
        return response.status_code == 200
    except HTTPStatusError as e:
        if e.response.status_code == 403:
            return False
        raise
```

### 3. Data Volume

Consider data volume when selecting entities:

```python
async def estimate_entity_size(entity_name: str) -> int:
    response = await client.get(f"/entity/{entity_name}?page_size=1")
    data = response.json()
    return data.get("result_count", 0)
```

## Troubleshooting Discovery

### Common Issues

1. **Entity Not Found**

   - Check entity name spelling
   - Verify permissions
   - Confirm WMS version compatibility

2. **Schema Missing Fields**

   - Some fields only appear with data
   - Use sample data inference
   - Check field-level permissions

3. **Performance Issues**
   - Implement caching
   - Use concurrent discovery
   - Filter unnecessary entities

### Debug Mode

Enable detailed discovery logging:

```python
logger.setLevel(logging.DEBUG)
# Logs all discovery attempts and results
```

This comprehensive entity discovery system ensures tap-oracle-wms can adapt to any Oracle WMS configuration dynamically, without hardcoding entity definitions or schemas.

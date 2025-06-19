# Oracle WMS REST API Reference

## API Overview

The Oracle WMS REST API provides comprehensive access to warehouse management data and operations through a consistent, RESTful interface. This API follows Oracle's standard REST patterns and supports over 300 entities for complete warehouse management functionality.

### Base URL Structure

```
https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/
```

Components:

- `{instance}`: Your WMS instance identifier (e.g., `mycompany-wms`)
- `{tenant}`: Your tenant/company identifier (e.g., `ACME`)
- `/wms/lgfapi/v10/`: API path with version (Logistics Foundation API v10)

### API Versioning

Current stable version: **v10**

The API version is included in the URL path. Oracle maintains backward compatibility within major versions and provides 12+ months notice for deprecations.

**Version History:**

- v10: Current stable version (Oracle WMS 24A+)
- v9: Legacy version (Oracle WMS 23C and earlier)

## Authentication

### Required Headers

All API requests must include these headers:

```http
Authorization: Basic {base64_encoded_credentials}
X-WMS-Company: {company_code}
X-WMS-Facility: {facility_code}
Content-Type: application/json
Accept: application/json
User-Agent: tap-oracle-wms/1.0
```

### Authentication Methods

#### Basic Authentication

```http
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

Where the value is base64 encoding of `username:password`.

#### OAuth 2.0 (Recommended for Production)

```http
Authorization: Bearer {access_token}
```

OAuth 2.0 flow:

1. Register application in Oracle Identity Cloud Service
2. Obtain authorization code
3. Exchange for access token
4. Use access token for API calls
5. Refresh token when expired

### Security Context Headers

```http
X-WMS-Company: ACME_CORP
X-WMS-Facility: DC01
X-WMS-User-Context: integration_user
```

## Data Input Considerations

### JSON Decimal Values

**Important**: Decimal values in JSON should be wrapped in quotes to prevent precision loss:

```json
{
  "weight": "123.456789", // ✓ Correct - preserves precision
  "height": 123.456789 // ✗ May lose precision
}
```

### Date/Time Format

All timestamps must be in ISO 8601 format with timezone:

- Full format: `2025-06-15T14:30:00.000Z`
- Date only: `2025-06-15`
- With timezone: `2025-06-15T14:30:00-07:00`

### XML List Format

When using XML format, lists require special `<list-item>` tags:

```xml
<serial_nbr_list>
  <list-item>SN001</list-item>
  <list-item>SN002</list-item>
  <list-item>SN003</list-item>
</serial_nbr_list>
```

### Character Encoding

- Request body encoding: UTF-8 (default) or specify with `charset` parameter
- Response body encoding: Always UTF-8
- URL parameters: Must be URL-encoded

## Core API Endpoints

### Entity Discovery

#### List All Entities

```http
GET /entity
```

**Response**: Dictionary of all available entities with their endpoint URLs.

```json
{
  "allocation": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/allocation",
  "appointment": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/appointment",
  "asn": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/asn",
  "asn_detail": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/asn_detail",
  "batch_nbr": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/batch_nbr",
  "carrier": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/carrier",
  "company": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/company",
  "customer": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/customer",
  "cycle_count": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/cycle_count",
  "facility": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/facility",
  "iblpn": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/iblpn",
  "inventory": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/inventory",
  "inventory_adjustment": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/inventory_adjustment",
  "inventory_lock": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/inventory_lock",
  "inventory_snapshot": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/inventory_snapshot",
  "item": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/item",
  "item_barcode": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/item_barcode",
  "item_facility_mapping": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/item_facility_mapping",
  "item_supplier": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/item_supplier",
  "location": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/location",
  "location_type": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/location_type",
  "lpn": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/lpn",
  "oblpn": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/oblpn",
  "order_dtl": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/order_dtl",
  "order_hdr": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/order_hdr",
  "pick_slip": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/pick_slip",
  "pick_slip_detail": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/pick_slip_detail",
  "putaway_task": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/putaway_task",
  "receipt": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/receipt",
  "receipt_detail": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/receipt_detail",
  "shipment": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/shipment",
  "shipment_detail": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/shipment_detail",
  "supplier": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/supplier",
  "task": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/task",
  "task_type": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/task_type",
  "wave": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/wave",
  "wave_detail": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/wave_detail",
  "zone": "https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/entity/zone"
}
```

**Total Entities**: 300+ entities covering all aspects of warehouse management.

#### Describe Entity Schema

```http
GET /entity/{entity_name}/describe/
```

**Response**: Complete schema definition including field types, constraints, and relationships.

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
      "help_text": "Unique identifier for the record",
      "primary_key": true
    },
    {
      "name": "code",
      "type": "string",
      "required": "Y",
      "max_length": 50,
      "allow_blank": false,
      "default": null,
      "help_text": "Unique code identifier",
      "unique": true
    },
    {
      "name": "description",
      "type": "string",
      "required": "N",
      "max_length": 200,
      "allow_blank": true,
      "default": "",
      "help_text": "Descriptive text"
    },
    {
      "name": "status",
      "type": "string",
      "required": "Y",
      "max_length": 20,
      "allow_blank": false,
      "default": "ACTIVE",
      "choices": ["ACTIVE", "INACTIVE", "PENDING"],
      "help_text": "Record status"
    },
    {
      "name": "create_ts",
      "type": "datetime",
      "required": "X",
      "allow_blank": false,
      "default": "now",
      "help_text": "Record creation timestamp"
    },
    {
      "name": "update_ts",
      "type": "datetime",
      "required": "X",
      "allow_blank": false,
      "default": "now",
      "help_text": "Last update timestamp"
    }
  ],
  "relationships": [
    {
      "name": "facility",
      "type": "foreign_key",
      "related_entity": "facility",
      "related_field": "id"
    }
  ]
}
```

### Entity Operations

#### List Records

```http
GET /entity/{entity_name}
```

**Query Parameters:**

| Parameter             | Type    | Description                           | Default  | Max  |
| --------------------- | ------- | ------------------------------------- | -------- | ---- |
| `page`                | integer | Page number                           | 1        | -    |
| `page_size`           | integer | Records per page                      | 20       | 1250 |
| `page_mode`           | string  | `standard` or `sequenced`             | standard | -    |
| `ordering`            | string  | Sort fields (comma-separated)         | -        | -    |
| `fields`              | string  | Fields to return (comma-separated)    | all      | -    |
| `values_list`         | string  | Return as array with specified fields | -        | -    |
| `distinct`            | boolean | Return distinct values only           | false    | -    |
| `{field}`             | various | Filter by field value                 | -        | -    |
| `{field}__{operator}` | various | Advanced filtering                    | -        | -    |

**Examples:**

```http
# Basic pagination
GET /entity/item?page=1&page_size=100

# Filtering
GET /entity/item?status=ACTIVE&code__startswith=PROD

# Field selection
GET /entity/item?fields=id,code,description,status

# Sorting
GET /entity/item?ordering=-create_ts,code

# Cursor-based pagination (recommended for large datasets)
GET /entity/item?page_mode=sequenced&page_size=1000

# Complex filtering
GET /entity/inventory?on_hand_qty__gt=0&location_id__in=LOC001,LOC002&create_ts__gte=2024-01-01
```

#### Get Single Record

```http
GET /entity/{entity_name}/{id}
```

**Query Parameters:**

- `fields`: Specific fields to return
- `expand`: Include related entity data

**Example:**

```http
GET /entity/item/12345?fields=id,code,description&expand=item_barcode,item_supplier
```

#### Create Record

```http
POST /entity/{entity_name}
Content-Type: application/json

{
  "code": "ITEM001",
  "description": "Test Item",
  "status": "ACTIVE",
  "item_type": "FINISHED_GOOD",
  "unit_of_measure": "EA"
}
```

**Response:**

```json
{
  "id": 12345,
  "code": "ITEM001",
  "description": "Test Item",
  "status": "ACTIVE",
  "create_ts": "2024-01-15T10:30:00Z",
  "update_ts": "2024-01-15T10:30:00Z"
}
```

#### Update Record (Full)

```http
PUT /entity/{entity_name}/{id}
Content-Type: application/json

{
  "id": 12345,
  "code": "ITEM001",
  "description": "Updated Item Description",
  "status": "ACTIVE",
  "item_type": "FINISHED_GOOD",
  "unit_of_measure": "EA"
}
```

#### Update Record (Partial)

```http
PATCH /entity/{entity_name}/{id}
Content-Type: application/json

{
  "description": "Partially Updated Item Description",
  "status": "INACTIVE"
}
```

#### Delete Record

```http
DELETE /entity/{entity_name}/{id}
```

**Note**: Not all entities support deletion. Some entities use soft deletion (status change) instead.

## Response Formats

### Successful List Response (Standard Pagination)

```json
{
  "results": [
    {
      "id": 1,
      "code": "ITEM001",
      "description": "Product 1",
      "status": "ACTIVE",
      "create_ts": "2024-01-15T10:30:00Z"
    }
  ],
  "result_count": 1000,
  "page_count": 10,
  "page_nbr": 1,
  "hasMore": true,
  "next_page": "https://.../entity/item?page=2",
  "previous_page": null
}
```

### Successful List Response (Cursor Pagination)

```json
{
  "results": [
    {
      "id": 1001,
      "code": "ITEM1001",
      "description": "Product 1001",
      "status": "ACTIVE"
    }
  ],
  "next_page": "https://.../entity/item?cursor=cD0yMDAw&page_mode=sequenced",
  "previous_page": "https://.../entity/item?cursor=cD0w&page_mode=sequenced"
}
```

### Single Record Response

```json
{
  "id": 1,
  "code": "ITEM001",
  "description": "Product 1",
  "status": "ACTIVE",
  "item_type": "FINISHED_GOOD",
  "unit_of_measure": "EA",
  "create_ts": "2024-01-15T10:30:00Z",
  "update_ts": "2024-01-15T10:30:00Z",
  "created_by": "integration_user",
  "updated_by": "integration_user"
}
```

### Error Response

```json
{
  "reference": "25b414f0-7a1d-4f35-ac3c-0ec9886cf37a",
  "code": "VALIDATION_ERROR",
  "message": "Invalid input.",
  "details": {
    "status": "Invalid status value",
    "code": "Code already exists"
  }
}
```

**Error Response Components:**

- `reference`: Unique error reference ID for support
- `code`: Generic error classification
- `message`: Human-readable error message
- `details`: Optional field-specific errors or list of detailed error messages

## Advanced Query Capabilities

### Filtering Operators

| Operator        | Description                  | Example                          | Data Types    |
| --------------- | ---------------------------- | -------------------------------- | ------------- |
| (none)          | Exact match                  | `?status=ACTIVE`                 | All           |
| `__contains`    | Contains substring           | `?description__contains=widget`  | String        |
| `__icontains`   | Case-insensitive contains    | `?description__icontains=Widget` | String        |
| `__startswith`  | Starts with                  | `?code__startswith=PROD`         | String        |
| `__istartswith` | Case-insensitive starts with | `?code__istartswith=prod`        | String        |
| `__endswith`    | Ends with                    | `?code__endswith=001`            | String        |
| `__iendswith`   | Case-insensitive ends with   | `?code__iendswith=001`           | String        |
| `__exact`       | Exact match (explicit)       | `?code__exact=ITEM001`           | All           |
| `__iexact`      | Case-insensitive exact       | `?code__iexact=item001`          | String        |
| `__gte`         | Greater than or equal        | `?qty__gte=100`                  | Numeric, Date |
| `__gt`          | Greater than                 | `?qty__gt=100`                   | Numeric, Date |
| `__lte`         | Less than or equal           | `?qty__lte=100`                  | Numeric, Date |
| `__lt`          | Less than                    | `?qty__lt=100`                   | Numeric, Date |
| `__in`          | In list                      | `?status__in=ACTIVE,PENDING`     | All           |
| `__range`       | Between values               | `?qty__range=10,100`             | Numeric, Date |
| `__isnull`      | Is null/not null             | `?deleted_ts__isnull=true`       | All           |
| `__regex`       | Regular expression           | `?code__regex=^PROD.*001$`       | String        |
| `__iregex`      | Case-insensitive regex       | `?code__iregex=^prod.*001$`      | String        |
| `__year`        | Extract year                 | `?create_ts__year=2025`          | Date/DateTime |
| `__month`       | Extract month                | `?create_ts__month=6`            | Date/DateTime |
| `__day`         | Extract day                  | `?create_ts__day=15`             | Date/DateTime |
| `__week_day`    | Day of week (1=Sunday)       | `?create_ts__week_day=1`         | Date/DateTime |
| `__hour`        | Extract hour                 | `?create_ts__hour=14`            | DateTime      |
| `__minute`      | Extract minute               | `?create_ts__minute=30`          | DateTime      |

### Date/Time Filtering

```http
# Specific date
GET /entity/order_hdr?order_date=2024-01-15

# Date range
GET /entity/order_hdr?order_date__range=2024-01-01,2024-01-31

# Since timestamp
GET /entity/inventory?update_ts__gte=2024-01-15T10:30:00Z

# Relative dates (Oracle WMS 25A+)
GET /entity/order_hdr?order_date__gte=today-7
GET /entity/order_hdr?order_date__gte=now-1h
```

### Negation

Add `!` before the `=` sign for negation:

```http
# Not equal
GET /entity/item?status!=INACTIVE

# Does not contain
GET /entity/item?description__contains!=obsolete

# Not in list
GET /entity/item?status__in!=INACTIVE,DISCONTINUED
```

**Note**: The NOT operator ('!') is placed before the equals ('=') symbol and negates the statement.

### Complex Filtering

```http
# Multiple conditions (AND)
GET /entity/inventory?on_hand_qty__gt=0&status=AVAILABLE&location_id__startswith=A

# OR conditions using Q objects (Oracle WMS 25A+)
GET /entity/item?q=(status=ACTIVE OR status=PENDING) AND code__startswith=PROD
```

### Ordering

**Single field:**

```http
GET /entity/item?ordering=code
```

**Multiple fields:**

```http
GET /entity/item?ordering=-create_ts,code,description
```

**Ordering options:**

- Ascending: `field_name`
- Descending: `-field_name`
- Multiple: comma-separated

### Field Selection

**Return specific fields:**

```http
GET /entity/item?fields=id,code,description,status
```

**Exclude fields:**

```http
GET /entity/item?exclude_fields=create_ts,update_ts,created_by,updated_by
```

### Values List

**Return as array:**

```http
GET /entity/item?values_list=id,code
```

**Response:**

```json
[
  [1, "ITEM001"],
  [2, "ITEM002"]
]
```

**With aliases:**

```http
GET /entity/item?values_list=id:item_id,code:item_code
```

**Response:**

```json
[
  { "item_id": 1, "item_code": "ITEM001" },
  { "item_id": 2, "item_code": "ITEM002" }
]
```

### Distinct Values

```http
GET /entity/item?values_list=status&distinct=1
```

**Response:**

```json
["ACTIVE", "INACTIVE", "PENDING"]
```

### Related Entity Access

```http
# Access related entities
GET /entity/order_hdr/12345/order_dtl

# Access related collections using _set suffix
GET /entity/order_hdr?fields=id,order_nbr,order_dtl_set
```

## Major Entity References

### Master Data Entities

#### Item Entity (`/entity/item`)

**Primary Key**: `id`

**Key Fields**:

- `code`: Item SKU/Part Number (unique)
- `description`: Item description
- `status`: ACTIVE, INACTIVE, DISCONTINUED
- `item_type`: FINISHED_GOOD, RAW_MATERIAL, COMPONENT, etc.
- `unit_of_measure`: Base UOM (EA, LB, KG, etc.)
- `weight`: Item weight
- `length`, `width`, `height`: Dimensions
- `hazmat_flag`: Hazardous material indicator
- `lot_control_flag`: Lot tracking required
- `serial_control_flag`: Serial number tracking required

**Related Entities**:

- `item_barcode`: Barcode configurations
- `item_supplier`: Supplier relationships
- `item_facility_mapping`: Facility-specific settings
- `item_uom`: Unit of measure conversions

#### Location Entity (`/entity/location`)

**Primary Key**: `id`

**Key Fields**:

- `location_id`: Location identifier (unique within facility)
- `zone_id`: Zone assignment
- `location_type`: PICK, RESERVE, STAGE, DOCK, etc.
- `status`: ACTIVE, INACTIVE, BLOCKED
- `capacity_qty`: Maximum quantity capacity
- `capacity_volume`: Maximum volume capacity
- `capacity_weight`: Maximum weight capacity
- `pick_sequence`: Picking sequence number
- `x_coordinate`, `y_coordinate`, `z_coordinate`: Physical coordinates

#### Facility Entity (`/entity/facility`)

**Primary Key**: `id`

**Key Fields**:

- `facility_id`: Facility identifier
- `facility_name`: Facility name
- `status`: ACTIVE, INACTIVE
- `address_line1`, `address_line2`: Physical address
- `city`, `state`, `postal_code`, `country`: Location details
- `time_zone`: Facility time zone

### Transactional Entities

#### Inventory Entity (`/entity/inventory`)

**Primary Key**: `id`

**Key Fields**:

- `item_id`: Reference to item
- `location_id`: Storage location
- `on_hand_qty`: Available quantity
- `allocated_qty`: Reserved/allocated quantity
- `available_qty`: Available for allocation (on_hand - allocated)
- `batch_nbr`: Batch/lot number
- `serial_nbr`: Serial number
- `lpn_id`: License plate number (container)
- `status`: AVAILABLE, HOLD, DAMAGED, etc.
- `expiry_date`: Expiration date for perishable items
- `receive_date`: Date received into inventory

#### Order Header Entity (`/entity/order_hdr`)

**Primary Key**: `id`

**Key Fields**:

- `order_nbr`: Order number (unique)
- `status`: CREATED, ALLOCATED, PICKED, SHIPPED, COMPLETED, CANCELLED
- `order_type`: SALES, TRANSFER, RETURN, SAMPLE, etc.
- `priority`: Order priority (1-10)
- `customer_id`: Customer reference
- `ship_to_name`: Shipping name
- `ship_to_address1`, `ship_to_address2`: Shipping address
- `ship_to_city`, `ship_to_state`, `ship_to_postal_code`: Shipping location
- `order_date`: Order creation date
- `requested_date`: Requested ship date
- `promised_date`: Promised delivery date

#### Order Detail Entity (`/entity/order_dtl`)

**Primary Key**: `id`

**Key Fields**:

- `order_id`: Reference to order header
- `line_nbr`: Line number within order
- `item_id`: Ordered item
- `ordered_qty`: Quantity ordered
- `allocated_qty`: Quantity allocated
- `picked_qty`: Quantity picked
- `shipped_qty`: Quantity shipped
- `status`: CREATED, ALLOCATED, PICKED, SHIPPED, CANCELLED
- `unit_price`: Unit price
- `total_price`: Line total

#### Receipt Entity (`/entity/receipt`)

**Primary Key**: `id`

**Key Fields**:

- `receipt_nbr`: Receipt number (unique)
- `status`: CREATED, CONFIRMED, PUTAWAY_COMPLETE, CLOSED
- `receipt_type`: PO, ASN, RETURN, TRANSFER, etc.
- `supplier_id`: Supplier reference
- `po_nbr`: Purchase order number
- `asn_nbr`: Advanced shipping notice number
- `receipt_date`: Receipt date
- `expected_date`: Expected receipt date

#### Receipt Detail Entity (`/entity/receipt_detail`)

**Primary Key**: `id`

**Key Fields**:

- `receipt_id`: Reference to receipt header
- `line_nbr`: Line number
- `item_id`: Received item
- `expected_qty`: Expected quantity
- `received_qty`: Actually received quantity
- `putaway_qty`: Quantity put away
- `batch_nbr`: Batch/lot number
- `expiry_date`: Expiration date

### Task Management Entities

#### Task Entity (`/entity/task`)

**Primary Key**: `id`

**Key Fields**:

- `task_nbr`: Task number (unique)
- `task_type`: PUTAWAY, PICK, MOVE, COUNT, etc.
- `status`: CREATED, ASSIGNED, IN_PROGRESS, COMPLETED, CANCELLED
- `priority`: Task priority
- `user_id`: Assigned user
- `from_location_id`: Source location
- `to_location_id`: Destination location
- `item_id`: Item being handled
- `qty`: Task quantity
- `create_ts`: Task creation time
- `assign_ts`: Task assignment time
- `complete_ts`: Task completion time

#### Wave Entity (`/entity/wave`)

**Primary Key**: `id`

**Key Fields**:

- `wave_nbr`: Wave number (unique)
- `status`: CREATED, RELEASED, PICKED, COMPLETED
- `wave_type`: SINGLE_ORDER, BATCH, ZONE, etc.
- `priority`: Wave priority
- `planned_start_time`: Planned start time
- `actual_start_time`: Actual start time
- `planned_end_time`: Planned completion time
- `actual_end_time`: Actual completion time

## Special Endpoints

### Data Extract API (Oracle WMS 25B+)

For large-scale data extraction to cloud object stores:

```http
POST /wms/lgfapi/v10/data_extract/push_to_object_store
Content-Type: application/json

{
  "entity_name": "inventory",
  "filters": {
    "create_ts__gte": "2024-01-01T00:00:00Z"
  },
  "format": "CSV",
  "compression": "GZIP",
  "file_size_mb": 100,
  "destination": {
    "provider": "OCI",
    "bucket": "wms-data-extract",
    "prefix": "inventory/2024/01/"
  }
}
```

**Response:**

```json
{
  "job_id": "extract_job_12345",
  "status": "SUBMITTED",
  "estimated_completion": "2024-01-15T11:00:00Z",
  "status_url": "/async/status/extract_job_12345"
}
```

### Async Status API

Check asynchronous operation status:

```http
GET /async/status/{job_id}
```

**Response:**

```json
{
  "job_id": "extract_job_12345",
  "status": "COMPLETED",
  "progress": 100,
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T10:45:00Z",
  "result": {
    "files_created": 5,
    "total_records": 50000,
    "file_urls": [
      "https://objectstorage.../inventory_001.csv.gz",
      "https://objectstorage.../inventory_002.csv.gz"
    ]
  }
}
```

### Bulk Operations

**Maximum objects per request**: User's "Rows per Page" setting (10-125 by default)

#### Bulk Create

```http
POST /entity/{entity_name}/bulk?commit_frequency=0
Content-Type: application/json

[
  {
    "code": "ITEM001",
    "description": "Item 1",
    "status": "ACTIVE"
  },
  {
    "code": "ITEM002",
    "description": "Item 2",
    "status": "ACTIVE"
  }
]
```

**Commit Frequency Options:**

- `0`: All or nothing (default) - entire batch succeeds or fails
- `1`: Commit per resource - each record processed independently
- `>1`: Advanced scenarios - commit after N successful records

**Response:**

```json
{
  "record_count": 2,
  "success_count": 2,
  "failure_count": 0,
  "results": [
    { "id": 12345, "code": "ITEM001", "status": "success" },
    { "id": 12346, "code": "ITEM002", "status": "success" }
  ],
  "errors": []
}
```

#### Bulk Update

```http
PATCH /entity/{entity_name}/bulk
Content-Type: application/json

[
  {
    "id": 12345,
    "description": "Updated Item 1"
  },
  {
    "id": 12346,
    "description": "Updated Item 2"
  }
]
```

### Entity Relationships

Get related entity data:

```http
GET /entity/order_hdr/12345/order_dtl
```

**Response**: All order details for order 12345.

### Entity Operations

Entity operations are business-specific actions that can be performed on entities.

**Operation URL Format:**

- Single entity: `/entity/{entity_name}/{id}/{operation_name}/`
- Bulk operation: `/entity/{entity_name}/{operation_name}/`

#### Example: Container Operations

```http
# Lock a container
POST /entity/container/12345/lock/
Content-Type: application/json

{
  "lock_code": "QUALITY_CHECK",
  "reason": "Pending inspection"
}

# Palletize containers
POST /entity/container/palletize/
Content-Type: application/json

{
  "container_ids": [123, 124, 125],
  "pallet_nbr": "PLT001"
}
```

#### Example: Cycle Count Operations

```http
# Confirm LPN count
POST /entity/cycle_count/cc_confirm_lpn_count/
Content-Type: application/json

{
  "location_barcode": "LOC001",
  "lpn_nbr": "LPN12345",
  "qty": 100
}
```

#### Example: Order Allocation

```http
POST /entity/order_hdr/12345/allocate/
Content-Type: application/json

{
  "allocation_strategy": "FIFO",
  "partial_allocation": true
}
```

## HTTP Status Codes

| Code | Description           | When Used                                       |
| ---- | --------------------- | ----------------------------------------------- |
| 200  | OK                    | Successful GET, PUT, PATCH                      |
| 201  | Created               | Successful POST (creation)                      |
| 204  | No Content            | Successful DELETE                               |
| 400  | Bad Request           | Invalid request format, missing required fields |
| 401  | Unauthorized          | Authentication failed or missing                |
| 403  | Forbidden             | Insufficient permissions for operation          |
| 404  | Not Found             | Entity, record, or endpoint not found           |
| 409  | Conflict              | Duplicate key, constraint violation             |
| 422  | Unprocessable Entity  | Validation error, business rule violation       |
| 429  | Too Many Requests     | Rate limit exceeded                             |
| 500  | Internal Server Error | System error                                    |
| 502  | Bad Gateway           | Upstream service error                          |
| 503  | Service Unavailable   | System maintenance or overload                  |

## Rate Limiting

Oracle WMS may implement rate limiting to ensure system stability and fair resource usage. Rate limits vary by environment and are configured by system administrators.

**When Rate Limiting is Active:**

If rate limiting is enforced, the API will return HTTP status code 429 (Too Many Requests).

**Rate Limit Response (429):**

```json
{
  "error": "rate_limit_exceeded",
  "message": "API rate limit exceeded. Please reduce request frequency.",
  "retry_after": 60
}
```

**Best Practices:**

- Implement exponential backoff for retries
- Use cursor-based pagination for large data exports
- Optimize queries to reduce API calls
- Monitor response times and adjust request rates accordingly
- Consider implementing local request queuing

## Pagination Details

### Default Page Size

The default page size is determined by the requesting user's configuration of the "Rows per Page" field in the WMS UI. This setting:

- Has an allowed range of 10 to 125 results per page
- Applies to both UI and API requests
- Also determines the maximum object count for bulk operations

### Page Size Override

You can override the default with the `page_size` query parameter:

- Maximum value: 1250 records
- Recommended range: 100-1000 records
- Example: `?page_size=500`

**Warning**: Excessive use of large page sizes for concurrent queries may degrade system performance.

### Pagination Modes Comparison

| Feature                       | Standard (Paged)     | Cursor (Sequenced) |
| ----------------------------- | -------------------- | ------------------ |
| Total count available         | Yes                  | No                 |
| Jump to specific page         | Yes                  | No                 |
| Performance on large datasets | Degrades with offset | Consistent         |
| Stability during data changes | May miss/duplicate   | Stable             |
| Use case                      | Interactive UIs      | Data exports       |

## Performance Optimization

### Pagination Best Practices

1. **Use cursor-based pagination for large datasets:**

   ```http
   GET /entity/inventory?page_mode=sequenced&page_size=1000
   ```

2. **Limit field selection:**

   ```http
   GET /entity/item?fields=id,code,description
   ```

3. **Use appropriate page sizes:**
   - Small entities: 100-500 records
   - Large entities: 50-100 records
   - Maximum: 1250 records

### Filtering Best Practices

1. **Use indexed fields for filtering:**

   - Primary keys (`id`)
   - Unique fields (`code`, `order_nbr`)
   - Status fields
   - Date fields (`create_ts`, `update_ts`)

2. **Combine filters efficiently:**

   ```http
   # Good: Use indexed fields first
   GET /entity/inventory?location_id=LOC001&status=AVAILABLE&on_hand_qty__gt=0

   # Avoid: Complex string operations on large datasets
   GET /entity/item?description__contains=widget
   ```

### Caching Strategies

1. **Cache entity schemas** (rarely change)
2. **Cache master data** (items, locations, customers)
3. **Use ETags for conditional requests:**

   ```http
   GET /entity/item/12345
   If-None-Match: "abc123def456"
   ```

## Error Handling

### Common Error Patterns

#### Validation Errors

```json
{
  "error": "ValidationError",
  "message": "Field validation failed",
  "details": [
    {
      "field": "code",
      "error": "This field is required"
    },
    {
      "field": "status",
      "error": "Invalid choice. Must be one of: ACTIVE, INACTIVE"
    }
  ]
}
```

#### Business Rule Violations

```json
{
  "error": "BusinessRuleViolation",
  "message": "Cannot delete item with active inventory",
  "error_code": "WMS_ITEM_001",
  "details": {
    "item_id": 12345,
    "inventory_locations": ["LOC001", "LOC002"]
  }
}
```

#### Constraint Violations

```json
{
  "error": "IntegrityError",
  "message": "Duplicate key violation",
  "details": {
    "field": "code",
    "value": "ITEM001",
    "constraint": "unique_item_code"
  }
}
```

### Error Recovery Strategies

1. **Retry with exponential backoff** for 5xx errors
2. **Check rate limits** for 429 errors
3. **Validate data** before retry for 4xx errors
4. **Log errors** with correlation IDs for debugging

## Oracle Official References

This API reference is based on Oracle's official documentation:

### Primary References

- **[Oracle WMS REST API Guide 25B](https://docs.oracle.com/en/cloud/saas/warehouse-management/25b/owmre/)** - Complete API reference
- **[Oracle WMS Web Service APIs](https://docs.oracle.com/en/cloud/saas/warehouse-management/24a/owmap/)** - Integration patterns
- **[Oracle Cloud REST API Standards](https://docs.oracle.com/en/cloud/saas/applications-common/24a/farca/)** - Standard patterns

### Specific Documentation Sections

- **Chapter 2: Authentication** - Security and authentication methods
- **Chapter 3: HTTP Response** - Response formats and status codes
- **Chapter 4: Entity Module** - Entity operations and schemas
- **Chapter 5: Supported Entities** - Complete entity reference
- **Chapter 6: Query Capabilities** - Filtering, sorting, pagination
- **Chapter 7: Error Handling** - Error codes and recovery patterns

### Oracle Blogs and Resources

- **[Oracle WMS Cloud API Best Practices](https://blogs.oracle.com/scm/post/oracle-wms-cloud-api-best-practices)** - Performance optimization
- **[Oracle Cloud Integration Patterns](https://blogs.oracle.com/cloud-infrastructure/post/oracle-cloud-integration-patterns)** - Integration strategies

---

_Last updated: Based on Oracle WMS Cloud 25B REST API Guide (June 2025)_

# Oracle WMS Data Extraction Patterns

## Overview

Oracle WMS provides sophisticated data extraction capabilities designed for both real-time integrations and bulk data movement. This guide covers pagination strategies, filtering, sorting, field selection, and performance optimization techniques.

## Pagination Strategies

### Standard Offset-Based Pagination

The default pagination method uses page numbers and size:

```http
GET /entity/item?page=1&page_size=100
```

**Response Structure:**

```json
{
  "results": [...],
  "result_count": 50000,    // Total records
  "page_count": 500,        // Total pages
  "page_nbr": 1,           // Current page
  "hasMore": true,         // More pages exist
  "next_page": "https://.../entity/item?page=2&page_size=100",
  "previous_page": null
}
```

**Advantages:**

- Simple to implement
- Allows jumping to specific pages
- Shows total record count
- Good for small to medium datasets

**Disadvantages:**

- Performance degrades with large offsets
- Can miss/duplicate records if data changes
- Count queries are expensive for large tables

### Cursor-Based Pagination (Recommended)

For large datasets, use cursor-based pagination:

```http
GET /entity/item?page_mode=sequenced&page_size=1000
```

**Response Structure:**

```json
{
  "results": [...],
  "next_page": "https://.../entity/item?cursor=cD0yMDAw&page_mode=sequenced",
  "previous_page": "https://.../entity/item?cursor=cD0w&page_mode=sequenced"
}
```

**Advantages:**

- Consistent performance regardless of position
- No expensive count queries
- Stable iteration (no missed/duplicate records)
- Better for large datasets (millions of records)

**Disadvantages:**

- Sequential access only
- No total count available
- Cannot jump to specific pages

### Implementation Example

```python
async def extract_with_cursor_pagination(entity_name: str):
    """Extract all records using cursor pagination."""
    next_url = f"/entity/{entity_name}?page_mode=sequenced&page_size=1000"

    while next_url:
        response = await client.get(next_url)
        data = response.json()

        # Process records
        for record in data.get("results", []):
            yield record

        # Get next page URL
        next_url = data.get("next_page")
        if next_url:
            # Extract just the path and query
            next_url = urlparse(next_url).path + "?" + urlparse(next_url).query
```

## Filtering Capabilities

### Basic Filtering

Exact match filtering:

```http
GET /entity/item?status=ACTIVE&facility_id=1
```

### Advanced Filtering Operators

| Operator       | Description                           | Example                           |
| -------------- | ------------------------------------- | --------------------------------- |
| `__contains`   | Contains substring (case-sensitive)   | `?description__contains=widget`   |
| `__icontains`  | Contains substring (case-insensitive) | `?description__icontains=WIDGET`  |
| `__startswith` | Starts with string                    | `?code__startswith=PROD`          |
| `__endswith`   | Ends with string                      | `?code__endswith=001`             |
| `__gte`        | Greater than or equal                 | `?create_ts__gte=2024-01-01`      |
| `__gt`         | Greater than                          | `?qty__gt=100`                    |
| `__lte`        | Less than or equal                    | `?update_ts__lte=2024-12-31`      |
| `__lt`         | Less than                             | `?qty__lt=10`                     |
| `__in`         | Value in list                         | `?status__in=ACTIVE,PENDING,HOLD` |
| `__range`      | Between two values                    | `?qty__range=10,100`              |
| `__isnull`     | Is null or not null                   | `?deleted_ts__isnull=true`        |
| `__regex`      | Regular expression match              | `?code__regex=^PROD[0-9]+$`       |

### Negation

Add `!` after the operator to negate:

```http
GET /entity/item?status__in!=CANCELLED,DELETED
GET /entity/location?zone__contains!=QUARANTINE
```

### Complex Filtering Examples

1. **Date Range Filtering:**

```http
GET /entity/order_hdr?create_ts__gte=2024-01-01&create_ts__lt=2024-02-01
```

2. **Multiple Conditions:**

```http
GET /entity/inventory?location_id__in=100,101,102&on_hand_qty__gt=0&item_id__status=ACTIVE
```

3. **Pattern Matching:**

```http
GET /entity/item?code__regex=^(PROD|COMP)-[A-Z]{3}-[0-9]{4}$
```

## Field Selection

### Basic Field Selection

Return only specific fields to reduce payload size:

```http
GET /entity/item?fields=id,code,description,status
```

### Nested Field Selection

Access related entity fields:

```http
GET /entity/order_dtl?fields=id,line_nbr,item_id__code,item_id__description
```

### Values List Mode

Return data as arrays instead of objects:

```http
GET /entity/item?values_list=id,code,description
```

**Response:**

```json
{
  "results": [
    [1, "ITEM001", "Product 1"],
    [2, "ITEM002", "Product 2"]
  ]
}
```

### Values List with Aliases

Rename fields in the response:

```http
GET /entity/order_dtl?values_list=id:order_line_id,item_id__code:sku,ordered_qty:quantity
```

**Response:**

```json
{
  "results": [
    { "order_line_id": 1, "sku": "ITEM001", "quantity": 10 },
    { "order_line_id": 2, "sku": "ITEM002", "quantity": 5 }
  ]
}
```

## Sorting

### Single Field Sorting

```http
GET /entity/item?ordering=code
GET /entity/item?ordering=-create_ts  # Descending with - prefix
```

### Multiple Field Sorting

```http
GET /entity/inventory?ordering=-on_hand_qty,location_id,item_id
```

### Sorting on Related Fields

```http
GET /entity/order_dtl?ordering=order_id__order_date,-line_nbr
```

## Distinct Values

Get unique values for specific fields:

```http
GET /entity/order_hdr?values_list=status&distinct=1
```

**Response:**

```json
{
  "results": ["PENDING", "PROCESSING", "SHIPPED", "CANCELLED"]
}
```

## Performance Optimization

### 1. Use Appropriate Page Size

```python
def get_optimal_page_size(entity_name: str) -> int:
    """Determine optimal page size based on entity type."""
    # Large entities with few fields
    if entity_name in ["inventory", "allocation", "task"]:
        return 1000
    # Complex entities with many fields
    elif entity_name in ["order_hdr", "shipment"]:
        return 250
    # Default
    return 500
```

### 2. Parallel Extraction

Extract multiple entities concurrently:

```python
async def parallel_extraction(entity_names: List[str]):
    """Extract multiple entities in parallel."""
    tasks = []
    for entity in entity_names:
        task = extract_entity(entity)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return dict(zip(entity_names, results))
```

### 3. Incremental Extraction

Extract only changed records:

```python
async def incremental_extract(entity_name: str, last_sync: datetime):
    """Extract records modified since last sync."""
    filters = {
        "update_ts__gte": last_sync.isoformat(),
        "page_mode": "sequenced",
        "page_size": 1000
    }

    async for record in paginate_entity(entity_name, filters):
        yield record
```

### 4. Field Optimization

Only request needed fields:

```http
GET /entity/item?fields=id,code,description,status
```

### 5. Values List for Efficient Data Transfer

Use `values_list` for lightweight data extraction:

```http
# Get as arrays (most efficient)
GET /entity/item?values_list=id,code,status

Response:
[
  [1, "ITEM001", "ACTIVE"],
  [2, "ITEM002", "ACTIVE"]
]

# Get with field aliases
GET /entity/item?values_list=id:item_id,code:item_code

Response:
[
  {"item_id": 1, "item_code": "ITEM001"},
  {"item_id": 2, "item_code": "ITEM002"}
]

# Get distinct values
GET /entity/item?values_list=status&distinct=1

Response:
["ACTIVE", "INACTIVE", "PENDING"]
```

**Use Cases:**

- Building lookup dictionaries
- Extracting specific fields for reporting
- Getting unique values for filters
- Reducing network overhead

```python
def get_essential_fields(entity_name: str) -> List[str]:
    """Get minimal field set for entity."""
    base_fields = ["id", "code", "status", "update_ts"]

    entity_fields = {
        "item": ["description", "item_type"],
        "inventory": ["item_id", "location_id", "on_hand_qty"],
        "order_hdr": ["order_nbr", "customer_id", "order_date"],
        # ... more entities
    }

    return base_fields + entity_fields.get(entity_name, [])
```

## Bulk Data Export

For very large extractions, use the Data Extract API:

```http
POST /entity/{entity_name}/extract
Content-Type: application/json

{
  "filters": {
    "create_ts__gte": "2024-01-01"
  },
  "fields": ["id", "code", "description"],
  "format": "csv",
  "compression": "gzip",
  "chunk_size": 100000,
  "destination": {
    "type": "object_storage",
    "bucket": "wms-exports",
    "prefix": "items/"
  }
}
```

Monitor extraction progress:

```http
GET /async/status/{job_id}
```

## Query Optimization Tips

### 1. Use Indexes

Filter on indexed fields when possible:

- Primary keys (`id`)
- Unique codes (`code`, `order_nbr`)
- Foreign keys (`item_id`, `location_id`)
- Date fields (`create_ts`, `update_ts`)

### 2. Avoid Expensive Operations

- Limit use of `__contains` on large text fields
- Avoid `distinct` on high-cardinality fields
- Use `page_mode=sequenced` for large extracts

### 3. Batch Related Queries

Instead of:

```python
for order in orders:
    details = await get_order_details(order["id"])
```

Use:

```python
order_ids = [o["id"] for o in orders]
details = await get_entity("order_dtl", {"order_id__in": order_ids})
```

## Error Handling

### Retry Strategy

```python
async def extract_with_retry(entity_name: str, max_retries: int = 3):
    """Extract with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            async for record in extract_entity(entity_name):
                yield record
            break
        except HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            else:
                raise
```

### Handle Partial Failures

```python
async def robust_extraction(entity_name: str):
    """Extract with checkpoint recovery."""
    checkpoint = load_checkpoint(entity_name)
    filters = {}

    if checkpoint:
        filters["id__gt"] = checkpoint["last_id"]
        filters["ordering"] = "id"

    try:
        async for record in extract_entity(entity_name, filters):
            yield record
            update_checkpoint(entity_name, {"last_id": record["id"]})
    except Exception as e:
        logger.error(f"Extraction failed at checkpoint: {checkpoint}")
        raise
```

## Monitoring Extraction

### Progress Tracking

```python
class ExtractionProgress:
    def __init__(self, entity_name: str, total_count: int = None):
        self.entity_name = entity_name
        self.total_count = total_count
        self.processed = 0
        self.start_time = time.time()

    def update(self, count: int):
        self.processed += count
        elapsed = time.time() - self.start_time
        rate = self.processed / elapsed

        if self.total_count:
            eta = (self.total_count - self.processed) / rate
            logger.info(f"{self.entity_name}: {self.processed}/{self.total_count} "
                       f"({self.processed/self.total_count*100:.1f}%) "
                       f"Rate: {rate:.0f}/s ETA: {eta:.0f}s")
        else:
            logger.info(f"{self.entity_name}: {self.processed} processed "
                       f"Rate: {rate:.0f}/s")
```

## Best Practices Summary

1. **Use cursor pagination** for large datasets (>10,000 records)
2. **Select only required fields** to minimize payload
3. **Filter at the source** rather than post-processing
4. **Use appropriate page sizes** (100-1000 depending on entity)
5. **Implement incremental extraction** for regular syncs
6. **Handle errors gracefully** with retries and checkpoints
7. **Monitor extraction progress** for visibility
8. **Cache reference data** that changes infrequently
9. **Use bulk export** for initial loads or full refreshes
10. **Test with production-like data volumes** during development

## Oracle WMS 25B Data Extract for Cloud Object Store

### Overview

Oracle WMS 25B introduces a new REST API for extracting data directly to cloud object stores, supporting CSV, JSON, and Parquet formats. This feature provides high-performance bulk data extraction capabilities.

### Supported Cloud Storage Providers

| Provider                          | Required Parameters            |
| --------------------------------- | ------------------------------ |
| Oracle Cloud Infrastructure (OCI) | Namespace, Bucket Name, Region |
| Google Cloud Storage (GCS)        | Bucket URL                     |
| Amazon S3                         | User Role ARN, Bucket URL      |
| Azure Blob Storage                | Tenant ID, Bucket URL          |

### Configuration Requirements

#### Endpoints UI Configuration

1. Configure "Objectstore for Data Extract" interface protocol
2. Set up cloud storage provider credentials
3. Configure provider-specific parameters

#### User Permissions

- Enable "async data extract" flag for users
- Only ADMIN role users can set/unset the async data extract flag
- Users need access to RF Device Connection details

### API Usage

#### Push to Object Store

```python
import requests
import json

def extract_to_object_store(entities_config, endpoint_config):
    """
    Extract data to cloud object store using Oracle WMS 25B API
    """
    url = f"{base_url}/wms/lgfapi/v10/data_extract/push_to_object_store"

    payload = {
        "options": {
            "endpoint": {
                "name": endpoint_config["name"],
                "object_store_path": endpoint_config.get("path", "")
            },
            "file_format": endpoint_config.get("format", "CSV"),  # CSV, JSON, or parquet
            "file_size_in_mb": endpoint_config.get("file_size", 10),  # 10MB to 1GB
            "compressed": str(endpoint_config.get("compressed", True)).lower(),
            "unique_identifier": endpoint_config["unique_identifier"]
        },
        "parameters": {
            "entities": entities_config
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Example usage
entities_config = [
    {
        "entity": "inventory",
        "fields": "item_id,location_id,qty,create_ts",
        "filter": {
            "create_ts__gt": "2024-10-01T00:00:00.000",
            "status_id__lt": 90
        }
    },
    {
        "entity": "container",
        "fields": "container_nbr,rcvd_ts,curr_location_id",
        "filter": {
            "mod_ts__gt": "2024-10-01T00:00:00.000",
            "status_id__lt": 90
        }
    }
]

endpoint_config = {
    "name": "production_endpoint",
    "path": "data_extracts/daily",
    "format": "CSV",
    "file_size": 100,  # 100MB files
    "compressed": True,
    "unique_identifier": f"extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
}

result = extract_to_object_store(entities_config, endpoint_config)
```

#### Monitor Extraction Status

```python
def check_extraction_status(unique_identifier):
    """
    Check the status of data extraction job
    """
    url = f"{base_url}/wms/lgfapi/v10/data_extract/export_async_status"
    params = {"unique_identifier": unique_identifier}

    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Monitor extraction progress
status = check_extraction_status("extract_20241219_143022")
print(f"Status: {status['cummulative_status']}")
print(f"Duration: {status['total_duration']} seconds")

for entity_info in status['entities']:
    for entity_name, details in entity_info.items():
        print(f"{entity_name}: {details['status']} - {details['file_prefix']}")
```

#### Entity-Level Task Status

```python
def get_entity_task_status(task_id):
    """
    Get detailed status for specific entity extraction task
    """
    url = f"{base_url}/lgfapi/v10/entity/lgf_async_task/{task_id}"
    response = requests.get(url, headers=headers)
    return response.json()

# Check specific task
task_status = get_entity_task_status("b3cae633-b893-4e40-aefe-c037b79c2b81")
```

### Supported Filters

The Data Extract API supports three specific filters:

| Filter          | Description                         | Usage                                  |
| --------------- | ----------------------------------- | -------------------------------------- |
| `create_ts__gt` | Records created after timestamp     | Cannot be used with `mod_ts__gt`       |
| `mod_ts__gt`    | Records modified after timestamp    | Cannot be used with `create_ts__gt`    |
| `status_id__lt` | Records with status less than value | Can be combined with timestamp filters |

**Important Notes:**

- Timestamps must be in UTC format
- At least one timestamp filter (`create_ts__gt` or `mod_ts__gt`) is mandatory
- Timestamp filters are mutually exclusive per entity

### File Format Options

#### CSV Format

- Default format
- Suitable for most data analysis tools
- Efficient for tabular data

#### JSON Format

- Preserves complex data structures
- Better for nested entity relationships
- Larger file sizes

#### Parquet Format

- Columnar storage format
- Excellent compression ratios
- Optimized for analytics workloads

### Performance Considerations

#### File Size Optimization

- Configure file sizes between 10MB and 1GB
- Larger files reduce API calls but increase memory usage
- Consider downstream processing capabilities

#### Compression Benefits

- Enable compression for reduced storage costs
- Faster transfer times for large datasets
- Minimal CPU overhead

#### Parallel Processing

- Use unique identifiers to run multiple extractions
- Monitor system resources and API rate limits
- Coordinate with Oracle WMS administrators

## Incremental Data Extraction

### Change Data Capture Pattern

```python
def incremental_extract(entity_name, last_extract_time):
    """
    Extract only changed records since last extraction
    """
    current_time = datetime.utcnow()

    # For traditional API
    response = requests.get(
        f"{base_url}/lgfapi/v10/entity/{entity_name}/",
        headers=headers,
        params={
            "mod_ts__gt": last_extract_time.isoformat(),
            "ordering": "mod_ts"
        }
    )

    # For Object Store API
    entities_config = [{
        "entity": entity_name,
        "fields": "all",  # or specify required fields
        "filter": {
            "mod_ts__gt": last_extract_time.strftime("%Y-%m-%dT%H:%M:%S.000")
        }
    }]

    return current_time  # Save as last_extract_time for next run
```

### Watermark Management

```python
class ExtractionWatermark:
    def __init__(self, storage_path):
        self.storage_path = storage_path

    def get_last_extract_time(self, entity_name):
        """Get the last successful extraction timestamp"""
        try:
            with open(f"{self.storage_path}/{entity_name}_watermark.txt", 'r') as f:
                return datetime.fromisoformat(f.read().strip())
        except FileNotFoundError:
            return datetime(2020, 1, 1)  # Default start date

    def update_watermark(self, entity_name, timestamp):
        """Update the watermark after successful extraction"""
        with open(f"{self.storage_path}/{entity_name}_watermark.txt", 'w') as f:
            f.write(timestamp.isoformat())
```

## Error Handling and Retry Logic

### Robust Extraction Function

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_robust_session():
    """Create session with retry logic"""
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

def extract_with_retry(entity_name, max_retries=3):
    """Extract data with exponential backoff retry"""
    session = create_robust_session()

    for attempt in range(max_retries):
        try:
            response = session.get(
                f"{base_url}/lgfapi/v10/entity/{entity_name}/",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
```

## Data Quality and Validation

### Schema Validation

```python
def validate_extracted_data(data, entity_name):
    """Validate extracted data against expected schema"""
    required_fields = {
        'inventory': ['item_id', 'location_id', 'qty'],
        'container': ['container_nbr', 'status_id'],
        'order': ['order_nbr', 'facility_code']
    }

    if entity_name in required_fields:
        for record in data:
            for field in required_fields[entity_name]:
                if field not in record:
                    raise ValueError(f"Missing required field: {field}")

    return True
```

### Data Completeness Checks

```python
def verify_extraction_completeness(entity_name, expected_count=None):
    """Verify that extraction captured all expected records"""

    # Get total count from API
    response = requests.get(
        f"{base_url}/lgfapi/v10/entity/{entity_name}/",
        headers=headers,
        params={"limit": 1}  # Just get count
    )

    total_available = response.json().get('count', 0)

    if expected_count and total_available != expected_count:
        print(f"Warning: Expected {expected_count} records, found {total_available}")

    return total_available
```

---

## Oracle Official References

This data extraction guide is based on Oracle's official documentation:

### Primary References

- **[Oracle WMS 25B Data Extract](https://docs.oracle.com/en/cloud/saas/warehouse-management/25b/owmre/data-extract1.html)** - Complete Data Extract for Cloud Object Store documentation
- **[Oracle WMS REST API Guide](https://docs.oracle.com/en/cloud/saas/warehouse-management/25b/owmre/)** - Traditional REST API patterns and pagination
- **[Oracle WMS What's New 25B](https://docs.oracle.com/en/cloud/saas/readiness/logistics/25b/wms25b/25B-wms-wn-f36618.htm)** - New Data Extract features

### Cross-References

- [WMS Architecture](wms-architecture.md) - System architecture and data flow patterns
- [Performance Tuning](performance-tuning.md) - Optimization strategies for large-scale extraction
- [Authentication Guide](wms-authentication.md) - Security and authentication requirements
- [Entity Discovery](wms-entity-discovery.md) - Available entities and their schemas

### Version Compatibility

- **Oracle WMS 25B**: Full Data Extract for Cloud Object Store support
- **Oracle WMS 24C+**: Traditional REST API patterns
- **Oracle WMS 24A+**: Basic entity extraction and pagination

---

**Last Updated**: 2025-06-15
**Oracle WMS Version**: 25B
**API Version**: v10

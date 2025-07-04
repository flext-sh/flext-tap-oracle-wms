# Oracle WMS Tap Usage Guide

## Quick Start

### Installation

```bash
pip install flext-tap-oracle-wms
```

### Basic Configuration

Create a `config.json` file:

```json
{
  "base_url": "https://wms.example.com",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "wms_version": "23.3.3"
}
```

### Running the Tap

```bash
# Discover available entities
tap-oracle-wms --config config.json --discover > catalog.json

# Run a sync
tap-oracle-wms --config config.json --catalog catalog.json

# Run with state for incremental sync
tap-oracle-wms --config config.json --state state.json
```

## Configuration Examples

### Minimal Configuration

```json
{
  "base_url": "https://wms.company.com",
  "client_id": "wms_client",
  "client_secret": "${WMS_CLIENT_SECRET}"
}
```

### Production Configuration

```json
{
  "base_url": "https://wms-prod.company.com",
  "client_id": "prod_wms_client",
  "client_secret": "${WMS_CLIENT_SECRET}",
  "wms_version": "23.3.3",

  "page_size": 2000,
  "request_timeout": 600,
  "max_parallel_pages": 10,

  "entities": ["customer", "order", "inventory", "shipment"],
  "exclude_entities": ["*_temp", "test_*"],

  "cache_enabled": true,
  "cache_ttl": 1800,

  "flattening_enabled": true,
  "flattening_max_depth": 3,

  "start_date": "2024-01-01T00:00:00Z"
}
```

### High-Performance Configuration

```json
{
  "base_url": "https://wms.company.com",
  "client_id": "high_perf_client",
  "client_secret": "${WMS_CLIENT_SECRET}",

  "page_size": 5000,
  "max_parallel_pages": 20,
  "request_timeout": 900,

  "cache_enabled": true,
  "cache_ttl": 3600,

  "entities": ["allocation", "inventory", "order"],

  "flattening_enabled": false,
  "stream_maps": {}
}
```

## Entity Discovery

### Automatic Discovery

The tap automatically discovers available entities:

```bash
# Discover all entities
tap-oracle-wms --config config.json --discover

# Output includes all discovered entities with schemas
```

### Filtering Entities

Control which entities to sync:

```json
{
  "entities": ["customer", "order", "inventory"],
  "exclude_entities": ["temp_*", "*_archive"]
}
```

### Entity Patterns

Use patterns to include/exclude entities:

```json
{
  "entity_filter": "^(customer|order|inventory)$",
  "exclude_entities": ["*_history", "*_temp"]
}
```

## Schema Management

### Automatic Schema Generation

Schemas are generated from:
1. WMS API metadata
2. Sample data inference
3. Hybrid approach (both)

```json
{
  "infer_schema_from_samples": true,
  "sample_size": 10
}
```

### Schema Flattening

Flatten nested objects for easier consumption:

```json
{
  "flattening_enabled": true,
  "flattening_max_depth": 3
}
```

**Example transformation:**
```json
// Before flattening
{
  "order_id": "12345",
  "customer": {
    "id": "CUST001",
    "name": "Acme Corp",
    "address": {
      "street": "123 Main St",
      "city": "Springfield"
    }
  }
}

// After flattening
{
  "order_id": "12345",
  "customer_id": "CUST001",
  "customer_name": "Acme Corp",
  "customer_address_street": "123 Main St",
  "customer_address_city": "Springfield"
}
```

## Incremental Sync

### Setting Up Incremental Sync

1. **Initial Full Sync**:
```bash
tap-oracle-wms --config config.json > state.json
```

2. **Subsequent Incremental Syncs**:
```bash
tap-oracle-wms --config config.json --state state.json > new_state.json
mv new_state.json state.json
```

### Configuring Replication

```json
{
  "start_date": "2024-01-01T00:00:00Z",
  "lookback_window": 300
}
```

### State Management

State format example:
```json
{
  "bookmarks": {
    "customer": {
      "replication_key_value": "2024-03-15T10:30:00Z",
      "partitions": []
    },
    "order": {
      "replication_key_value": "2024-03-15T10:45:00Z",
      "partitions": []
    }
  }
}
```

## Performance Optimization

### Page Size Tuning

Adjust based on API performance:

```json
{
  "page_size": 2000
}
```

**Guidelines:**
- Small entities: 5000 records/page
- Large entities: 1000 records/page
- Complex entities: 500 records/page

### Parallel Processing

Enable concurrent page fetching:

```json
{
  "max_parallel_pages": 10
}
```

**Guidelines:**
- API rate limits permitting
- Monitor API response times
- Adjust based on network conditions

### Caching Strategy

Configure caching for better performance:

```json
{
  "cache_enabled": true,
  "cache_ttl": 3600,
  "cache_types": ["entity", "schema", "metadata"]
}
```

## Authentication

### OAuth2 Setup

1. **Register OAuth2 Application** in WMS
2. **Get Client Credentials**
3. **Configure Tap**:

```json
{
  "client_id": "your_client_id",
  "client_secret": "${WMS_CLIENT_SECRET}",
  "oauth_scopes": "read:wms"
}
```

### Token Management

The tap automatically:
- Obtains access tokens
- Refreshes expired tokens
- Retries on 401 errors

## Error Handling

### Retry Configuration

```json
{
  "max_retries": 5,
  "retry_backoff_factor": 2,
  "retry_status_codes": [429, 500, 502, 503, 504]
}
```

### Error Recovery

The tap implements:
- Exponential backoff
- Circuit breaker pattern
- Automatic reconnection

### Common Errors

**Rate Limiting (429)**:
```json
{
  "rate_limit_backoff": 60,
  "adaptive_rate_limiting": true
}
```

**Timeout Errors**:
```json
{
  "request_timeout": 600,
  "connect_timeout": 30
}
```

## Monitoring

### Logging Configuration

```json
{
  "log_level": "INFO",
  "log_requests": false,
  "log_response_bodies": false
}
```

### Metrics

Monitor key metrics:
- Records extracted per entity
- API requests per second
- Cache hit rate
- Error rate

### Progress Tracking

The tap logs progress:
```
INFO Starting sync for entity: customer
INFO Extracted 1000 records from customer (page 1/10)
INFO Extracted 2000 records from customer (page 2/10)
INFO Completed sync for customer: 10000 records in 45.3s
```

## Best Practices

### 1. Start with Discovery

Always run discovery first:
```bash
tap-oracle-wms --config config.json --discover > catalog.json
# Review and edit catalog.json
```

### 2. Test with Small Datasets

Start with limited entities:
```json
{
  "entities": ["customer"],
  "page_size": 100
}
```

### 3. Monitor API Usage

Track API consumption:
```json
{
  "log_api_usage": true,
  "api_usage_limit": 10000
}
```

### 4. Use Incremental Sync

For large datasets:
```json
{
  "start_date": "2024-01-01T00:00:00Z",
  "lookback_window": 300
}
```

### 5. Optimize for Your Use Case

**Real-time sync**:
```json
{
  "page_size": 500,
  "cache_enabled": false,
  "lookback_window": 600
}
```

**Batch sync**:
```json
{
  "page_size": 5000,
  "cache_enabled": true,
  "max_parallel_pages": 20
}
```

## Troubleshooting

### Connection Issues

**Error**: `ConnectionError: Failed to connect to WMS API`

**Solutions**:
1. Verify base_url is correct
2. Check network connectivity
3. Verify firewall rules

### Authentication Failures

**Error**: `401 Unauthorized`

**Solutions**:
1. Verify client credentials
2. Check OAuth scopes
3. Ensure token endpoint is correct

### Schema Errors

**Error**: `Schema validation failed`

**Solutions**:
1. Enable schema inference
2. Increase sample size
3. Check for data type mismatches

### Performance Issues

**Symptom**: Slow extraction

**Solutions**:
1. Increase page size
2. Enable parallel processing
3. Use caching
4. Filter unnecessary entities

## Advanced Usage

### Custom Stream Maps

Transform data during extraction:

```json
{
  "stream_maps": {
    "customer": {
      "full_name": "first_name + ' ' + last_name",
      "is_active": "status == 'ACTIVE'"
    }
  }
}
```

### Partition Strategy

For large entities:

```json
{
  "state_partitioning_keys": ["facility_id"],
  "partition_query_params": {
    "facility_id": ["DC01", "DC02", "DC03"]
  }
}
```

### Custom Authentication

Extend authentication:

```python
from tap_oracle_wms import TapOracleWMS

class CustomWMSTap(TapOracleWMS):
    def get_authenticator(self):
        # Custom authentication logic
        return CustomAuthenticator(self.config)
```

### Environment Variables

Use environment variables for sensitive data:

```bash
export WMS_CLIENT_SECRET=your_secret
export WMS_BASE_URL=https://wms.company.com

tap-oracle-wms --config config.json
```

Config file:
```json
{
  "base_url": "${WMS_BASE_URL}",
  "client_secret": "${WMS_CLIENT_SECRET}"
}
```

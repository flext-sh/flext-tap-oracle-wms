# tap-oracle-wms Configuration Reference

Complete reference for all configuration options available in tap-oracle-wms.

## Configuration Structure

tap-oracle-wms accepts configuration through:

1. JSON configuration file
2. Environment variables
3. Command-line arguments (for Meltano)

## Core Configuration

### Base URL

**Required**: Yes
**Type**: String
**Description**: Oracle WMS instance URL

```json
{
  "base_url": "https://your-instance.wms.ocs.oraclecloud.com/your-tenant"
}
```

Environment variable: `TAP_ORACLE_WMS_BASE_URL`

### Authentication

#### Method Selection

**Required**: Yes
**Type**: String
**Options**: `basic`, `oauth2`
**Default**: `basic`

```json
{
  "auth_method": "basic"
}
```

#### Basic Authentication

```json
{
  "auth_method": "basic",
  "username": "integration_user",
  "password": "secure_password"
}
```

Environment variables:

- `TAP_ORACLE_WMS_USERNAME`
- `TAP_ORACLE_WMS_PASSWORD`

#### OAuth 2.0 Authentication

```json
{
  "auth_method": "oauth2",
  "oauth_client_id": "your_client_id",
  "oauth_client_secret": "your_client_secret",
  "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token",
  "oauth_scope": "https://instance.wms.ocs.oraclecloud.com:443/urn:opc:resource:consumer::all"
}
```

Environment variables:

- `TAP_ORACLE_WMS_OAUTH_CLIENT_ID`
- `TAP_ORACLE_WMS_OAUTH_CLIENT_SECRET`
- `TAP_ORACLE_WMS_OAUTH_TOKEN_URL`
- `TAP_ORACLE_WMS_OAUTH_SCOPE`

### WMS Context

**Required**: Yes
**Description**: WMS-specific context headers

```json
{
  "company_code": "ACME",
  "facility_code": "DC01"
}
```

Environment variables:

- `TAP_ORACLE_WMS_COMPANY_CODE`
- `TAP_ORACLE_WMS_FACILITY_CODE`

## Data Selection

### Entity Selection

#### Automatic Discovery (Default)

```json
{
  "discover_entities": true
}
```

#### Specific Entities

```json
{
  "entities": ["item", "inventory", "location", "order_hdr", "order_dtl"]
}
```

#### Entity Patterns

```json
{
  "entity_patterns": {
    "include": ["order_*", "item*"],
    "exclude": ["*_history", "*_archive"]
  }
}
```

### Field Selection

#### Global Field Selection

```json
{
  "select_fields_by_default": true,
  "default_fields": ["id", "code", "status", "update_ts"]
}
```

#### Per-Entity Field Selection

```json
{
  "field_selection": {
    "item": ["id", "code", "description", "status", "item_type"],
    "inventory": [
      "id",
      "item_id",
      "location_id",
      "on_hand_qty",
      "allocated_qty"
    ],
    "order_hdr": ["id", "order_nbr", "status", "customer_id", "order_date"]
  }
}
```

## Replication Configuration

### Start Date

**Required**: Yes
**Type**: ISO 8601 DateTime
**Description**: Initial data extraction date

```json
{
  "start_date": "2024-01-01T00:00:00Z"
}
```

### Replication Method

**Type**: String
**Options**: `INCREMENTAL`, `FULL_TABLE`
**Default**: `INCREMENTAL`

```json
{
  "replication_method": "INCREMENTAL",
  "replication_key_preference": ["update_ts", "modify_ts", "create_ts"]
}
```

### Lookback Window

**Type**: Integer
**Default**: 0
**Description**: Days to look back for incremental replication

```json
{
  "lookback_days": 7
}
```

## Performance Configuration

### Pagination

#### Mode

**Type**: String
**Options**: `offset`, `cursor`
**Default**: `offset`

```json
{
  "pagination_mode": "cursor"
}
```

#### Page Size

**Type**: Integer
**Range**: 1-1250
**Default**: 100

```json
{
  "page_size": 500
}
```

### Parallelization

```json
{
  "max_parallel_streams": 5,
  "max_parallel_requests": 10
}
```

### Request Configuration

```json
{
  "request_timeout": 300,
  "retry_count": 3,
  "retry_wait_multiplier": 2,
  "retry_max_wait": 60
}
```

### Rate Limiting

```json
{
  "rate_limit_requests_per_minute": 600,
  "rate_limit_burst": 100,
  "respect_rate_limit_headers": true
}
```

## Advanced Configuration

### Schema Discovery

```json
{
  "schema_discovery_method": "auto",
  "schema_cache_ttl": 3600,
  "discover_schema_on_error": true,
  "infer_schema_from_samples": true,
  "schema_sample_size": 5
}
```

### Filtering

#### Global Filters

```json
{
  "global_filters": {
    "status": "ACTIVE",
    "facility_id": "${facility_code}"
  }
}
```

#### Entity-Specific Filters

```json
{
  "entity_filters": {
    "inventory": {
      "on_hand_qty__gt": 0
    },
    "order_hdr": {
      "status__in": ["PENDING", "PROCESSING"],
      "order_date__gte": "${start_date}"
    }
  }
}
```

### Ordering

```json
{
  "default_ordering": "id",
  "entity_ordering": {
    "inventory": "-update_ts,location_id",
    "order_hdr": "-order_date,order_nbr"
  }
}
```

## Logging Configuration

### Log Level

**Type**: String
**Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
**Default**: `INFO`

```json
{
  "log_level": "DEBUG"
}
```

Environment variable: `TAP_ORACLE_WMS_LOG_LEVEL`

### Log Format

```json
{
  "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "log_to_file": true,
  "log_file_path": "tap-oracle-wms.log",
  "log_rotation": {
    "max_bytes": 10485760,
    "backup_count": 5
  }
}
```

## State Management

### State Persistence

```json
{
  "state_persistence": {
    "enabled": true,
    "backend": "file",
    "path": "state.json",
    "checkpoint_interval": 1000
  }
}
```

### State Partitioning

```json
{
  "state_partitioning": {
    "enabled": true,
    "partition_keys": ["company_code", "facility_code"]
  }
```

## Error Handling

### Error Tolerance

```json
{
  "error_handling": {
    "max_errors_per_stream": 10,
    "continue_on_error": true,
    "error_log_file": "errors.log",
    "quarantine_failed_records": true
  }
}
```

### Dead Letter Queue

```json
{
  "dead_letter_queue": {
    "enabled": true,
    "path": "failed_records/",
    "retry_failed_records": true,
    "retry_interval_hours": 24
  }
}
```

## Monitoring & Metrics

### Metrics Collection

```json
{
  "metrics": {
    "enabled": true,
    "interval_seconds": 60,
    "include_entity_metrics": true,
    "include_performance_metrics": true
  }
}
```

### Progress Reporting

```json
{
  "progress_reporting": {
    "enabled": true,
    "interval_records": 1000,
    "show_eta": true,
    "show_throughput": true
  }
}
```

## Complete Configuration Example

### Development Configuration

```json
{
  "base_url": "https://dev.wms.ocs.oraclecloud.com/dev-tenant",
  "auth_method": "basic",
  "username": "${WMS_DEV_USER}",
  "password": "${WMS_DEV_PASS}",
  "company_code": "DEV_COMPANY",
  "facility_code": "DEV_DC",
  "start_date": "2024-01-01T00:00:00Z",
  "entities": ["item", "inventory"],
  "pagination_mode": "offset",
  "page_size": 100,
  "log_level": "DEBUG",
  "request_timeout": 60
}
```

### Production Configuration

```json
{
  "base_url": "https://prod.wms.ocs.oraclecloud.com/prod-tenant",
  "auth_method": "oauth2",
  "oauth_client_id": "${WMS_OAUTH_CLIENT_ID}",
  "oauth_client_secret": "${WMS_OAUTH_CLIENT_SECRET}",
  "oauth_token_url": "${WMS_OAUTH_TOKEN_URL}",
  "oauth_scope": "wms.read",
  "company_code": "${WMS_COMPANY}",
  "facility_code": "${WMS_FACILITY}",
  "start_date": "2024-01-01T00:00:00Z",
  "discover_entities": true,
  "entity_patterns": {
    "exclude": ["*_test", "*_temp", "*_archive"]
  },
  "pagination_mode": "cursor",
  "page_size": 1000,
  "max_parallel_streams": 10,
  "rate_limit_requests_per_minute": 600,
  "replication_method": "INCREMENTAL",
  "lookback_days": 1,
  "log_level": "INFO",
  "error_handling": {
    "continue_on_error": true,
    "max_errors_per_stream": 5
  },
  "metrics": {
    "enabled": true
  }
}
```

## Environment Variable Reference

All configuration options can be set via environment variables using the pattern:
`TAP_ORACLE_WMS_{OPTION_NAME}`

Common environment variables:

```bash
# Authentication
export TAP_ORACLE_WMS_BASE_URL="https://wms.example.com/tenant"
export TAP_ORACLE_WMS_AUTH_METHOD="oauth2"
export TAP_ORACLE_WMS_OAUTH_CLIENT_ID="client_id"
export TAP_ORACLE_WMS_OAUTH_CLIENT_SECRET="client_secret"

# WMS Context
export TAP_ORACLE_WMS_COMPANY_CODE="ACME"
export TAP_ORACLE_WMS_FACILITY_CODE="DC01"

# Performance
export TAP_ORACLE_WMS_PAGINATION_MODE="cursor"
export TAP_ORACLE_WMS_PAGE_SIZE="1000"
export TAP_ORACLE_WMS_MAX_PARALLEL_STREAMS="5"

# Logging
export TAP_ORACLE_WMS_LOG_LEVEL="DEBUG"
```

## Meltano Configuration

### meltano.yml

```yaml
plugins:
  extractors:
    - name: tap-oracle-wms
      namespace: tap_oracle_wms
      pip_url: tap-oracle-wms
      executable: tap-oracle-wms
      capabilities:
        - catalog
        - discover
        - properties
        - state
      settings:
        - name: base_url
          kind: string
          description: Oracle WMS instance URL
          sensitive: false
        - name: auth_method
          kind: options
          options:
            - label: Basic
              value: basic
            - label: OAuth2
              value: oauth2
        - name: username
          kind: string
          sensitive: true
        - name: password
          kind: password
          sensitive: true
      config:
        base_url: ${TAP_ORACLE_WMS_BASE_URL}
        auth_method: ${TAP_ORACLE_WMS_AUTH_METHOD}
        start_date: "2024-01-01T00:00:00Z"
```

### Environment-Specific Configuration

```yaml
environments:
  - name: dev
    config:
      plugins:
        extractors:
          - name: tap-oracle-wms
            config:
              base_url: https://dev.wms.example.com/dev
              pagination_mode: offset
              page_size: 100
  - name: prod
    config:
      plugins:
        extractors:
          - name: tap-oracle-wms
            config:
              base_url: https://prod.wms.example.com/prod
              pagination_mode: cursor
              page_size: 1000
```

## Configuration Validation

tap-oracle-wms validates configuration on startup:

1. **Required fields**: Ensures all required fields are present
2. **Type validation**: Verifies correct data types
3. **Range validation**: Checks numeric values are within limits
4. **Connectivity test**: Optionally tests WMS connection
5. **Permission check**: Verifies API access permissions

Enable validation:

```json
{
  "validate_config": true,
  "test_connection": true
}
```

## Best Practices

1. **Use environment variables** for sensitive data
2. **Enable cursor pagination** for large datasets
3. **Set appropriate page sizes** based on entity size
4. **Configure retry logic** for resilience
5. **Enable metrics** for monitoring
6. **Use field selection** to reduce data transfer
7. **Set up proper logging** for troubleshooting
8. **Configure state management** for incremental replication
9. **Test configuration** in development first
10. **Document custom configurations** for team reference

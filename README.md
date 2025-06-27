# 📤 Tap Oracle WMS - Enterprise Data Extraction for Warehouse Management

> **Function**: Production-grade Singer tap for Oracle WMS data extraction with dynamic discovery | **Audience**: Data Engineers, ETL Developers | **Status**: Production Ready

[![Singer](https://img.shields.io/badge/singer-tap-blue.svg)](https://www.singer.io/)
[![Oracle](https://img.shields.io/badge/oracle-WMS-red.svg)](https://www.oracle.com/cx/retail/warehouse-management/)
[![Meltano](https://img.shields.io/badge/meltano-compatible-green.svg)](https://meltano.com/)
[![Python](https://img.shields.io/badge/python-3.9%2B-orange.svg)](https://www.python.org/)

Enterprise Singer tap for extracting warehouse data from Oracle WMS with dynamic entity discovery, incremental sync, and production-grade reliability.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../README.md) → **📂 Current**: Tap Oracle WMS

---

## 🎯 **Core Purpose**

This Singer tap provides enterprise-grade data extraction from Oracle Warehouse Management System, enabling real-time analytics, data warehousing, and business intelligence. It implements the Singer specification with advanced features for high-volume warehouse data extraction.

### **Key Capabilities**

- **Dynamic Discovery**: Automatic entity and schema discovery via WMS APIs
- **Incremental Sync**: Efficient change data capture with state management
- **Flexible Authentication**: OAuth2, Basic Auth, and API key support
- **Advanced Filtering**: Entity-level and field-level filtering
- **Performance Optimized**: Cursor pagination, parallel extraction, caching

### **Production Features**

- **Error Recovery**: Automatic retry with exponential backoff
- **Monitoring**: Built-in metrics and performance tracking
- **Data Quality**: Schema validation and data type enforcement
- **Enterprise Scale**: Handles millions of records efficiently

---

## 🚀 **Quick Start**

### **Installation**

```bash
# Install via pip (recommended for production)
pip install tap-oracle-wms

# Install via Meltano
meltano add extractor tap-oracle-wms

# Install from source
git clone https://github.com/datacosmos-br/tap-oracle-wms
cd tap-oracle-wms
poetry install
```

### **Basic Configuration**

```json
{
  "base_url": "https://wms.company.com/tenant",
  "username": "data_extract_user",
  "password": "secure_password",
  "company_code": "*",
  "facility_code": "*",
  "start_date": "2024-01-01T00:00:00Z",
  "pagination_mode": "sequenced",
  "page_size": 1000,
  "request_timeout": 7200
}
```

### **Running the Tap**

```bash
# Discover available streams
tap-oracle-wms --config config.json --discover > catalog.json

# Run extraction
tap-oracle-wms --config config.json --catalog catalog.json

# With state management
tap-oracle-wms --config config.json --catalog catalog.json --state state.json

# Pipe to target
tap-oracle-wms --config config.json | target-postgres --config target-config.json
```

---

## 🏗️ **Architecture**

### **Singer Specification Compliance**

```text
┌─────────────────────────────────────────┐
│          Oracle WMS API                 │
│      (Source Data System)               │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Tap Oracle WMS                  │
│    (Singer Data Extractor)              │
├─────────────────────────────────────────┤
│ • Dynamic Discovery Engine              │
│ • Schema Generator                      │
│ • Stream Processors                     │
│ • State Management                      │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Singer Protocol                  │
│    (JSON Lines Output)                  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     Target System (Any)                 │
│  (Database, Data Lake, etc.)            │
└─────────────────────────────────────────┘
```

### **Component Structure**

```text
tap-oracle-wms/
├── src/tap_oracle_wms/
│   ├── __init__.py          # Package initialization
│   ├── tap.py               # Main tap class
│   ├── client.py            # WMS API client
│   ├── streams.py           # Stream definitions
│   ├── discovery.py         # Dynamic discovery
│   ├── auth.py              # Authentication
│   ├── pagination.py        # Pagination strategies
│   └── schemas/             # JSON schemas
├── tests/                   # Test suite
├── examples/                # Usage examples
└── meltano.yml             # Meltano config
```

---

## 🔧 **Core Features**

### **1. Dynamic Entity Discovery**

Automatic discovery of all available WMS entities:

```python
# discovery.py functionality
tap = TapOracleWMS(config=config)
catalog = tap.discover_streams()

# Discovered entities include:
# - inventory
# - orders (order_hdr, order_dtl)
# - shipments
# - locations
# - items
# - allocations
# - waves
# ... and more
```

### **2. Incremental Synchronization**

Efficient change data capture with bookmark support:

```json
{
  "bookmarks": {
    "inventory": {
      "replication_key": "last_update_date",
      "replication_key_value": "2024-06-19T10:30:00Z"
    },
    "orders": {
      "replication_key": "modified_date",
      "replication_key_value": "2024-06-19T09:45:00Z"
    }
  }
}
```

### **3. Advanced Filtering**

Entity-specific and global filtering capabilities:

```json
{
  "filters": {
    "inventory": {
      "facility_id": "DC001",
      "item_status": "ACTIVE"
    },
    "orders": {
      "order_status": ["ALLOCATED", "RELEASED"],
      "order_date": {
        "gte": "2024-06-01",
        "lte": "2024-06-19"
      }
    }
  },
  "selected_fields": {
    "inventory": ["item_id", "location", "quantity", "last_update_date"],
    "orders": ["order_id", "customer_id", "total_amount", "status"]
  }
}
```

### **4. Performance Optimization**

Built-in performance features:

```json
{
  "performance": {
    "pagination_mode": "sequenced",
    "page_size": 1000,
    "max_parallel_streams": 4,
    "company_code": "*",
    "facility_code": "*",
    "request_timeout": 7200,
    "retry_count": 3,
    "backoff_factor": 2
  }
}
```

### **5. Stream Selection**

Flexible stream selection and configuration:

```json
{
  "metadata": [
    {
      "breadcrumb": ["properties", "inventory"],
      "metadata": {
        "inclusion": "available",
        "selected": true,
        "replication-method": "INCREMENTAL",
        "replication-key": "last_update_date"
      }
    },
    {
      "breadcrumb": ["properties", "orders"],
      "metadata": {
        "inclusion": "available",
        "selected": true,
        "replication-method": "FULL_TABLE"
      }
    }
  ]
}
```

---

## 📊 **Supported Streams**

### **Core Warehouse Streams**

| Stream        | Description              | Replication Method | Key              |
| ------------- | ------------------------ | ------------------ | ---------------- |
| `inventory`   | Current inventory levels | INCREMENTAL        | last_update_date |
| `locations`   | Warehouse locations      | FULL_TABLE         | -                |
| `items`       | Item master data         | INCREMENTAL        | modified_date    |
| `order_hdr`   | Order headers            | INCREMENTAL        | modified_date    |
| `order_dtl`   | Order details            | INCREMENTAL        | modified_date    |
| `allocations` | Inventory allocations    | INCREMENTAL        | allocation_date  |
| `shipments`   | Shipment records         | INCREMENTAL        | ship_date        |
| `waves`       | Pick wave data           | INCREMENTAL        | wave_date        |

### **Extended Streams**

| Stream         | Description           | Replication Method | Key             |
| -------------- | --------------------- | ------------------ | --------------- |
| `adjustments`  | Inventory adjustments | INCREMENTAL        | adjustment_date |
| `cycle_counts` | Cycle count records   | INCREMENTAL        | count_date      |
| `receipts`     | Receiving records     | INCREMENTAL        | receipt_date    |
| `tasks`        | Warehouse tasks       | INCREMENTAL        | task_date       |
| `users`        | WMS users             | FULL_TABLE         | -               |
| `facilities`   | Facility data         | FULL_TABLE         | -               |

---

## 🔐 **Authentication**

### **OAuth2 Configuration**

```json
{
  "auth_method": "oauth2",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "token_url": "https://identity.oraclecloud.com/oauth2/v1/token",
  "scope": "wms.read"
}
```

### **Basic Authentication**

```json
{
  "auth_method": "basic",
  "username": "wms_user",
  "password": "secure_password"
}
```

### **API Key Authentication**

```json
{
  "auth_method": "api_key",
  "api_key": "your-api-key",
  "api_key_header": "X-API-Key"
}
```

---

## 🧪 **Testing**

### **Test Coverage**

- Unit Tests: 95%+ coverage
- Integration Tests: Mock WMS server
- End-to-End Tests: Real WMS sandbox
- Performance Tests: Load scenarios

### **Running Tests**

```bash
# Unit tests
poetry run pytest tests/unit

# Integration tests
poetry run pytest tests/integration

# E2E tests (requires WMS access)
poetry run pytest tests/e2e --wms-sandbox

# All tests with coverage
poetry run pytest --cov=tap_oracle_wms
```

---

## 📚 **Usage Examples**

### **Basic Extraction**

```python
# examples/basic_extraction.py
import json
from tap_oracle_wms import TapOracleWMS

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Create tap instance
tap = TapOracleWMS(config=config)

# Run discovery
catalog = tap.discover_streams()

# Select specific streams
for stream in catalog.streams:
    if stream.tap_stream_id in ['inventory', 'orders']:
        stream.selected = True

# Run sync
tap.sync(catalog)
```

### **Incremental Sync with State**

```python
# examples/incremental_sync.py
import json
from tap_oracle_wms import TapOracleWMS

# Load state from previous run
with open('state.json') as f:
    state = json.load(f)

# Configure tap
config = {
    "base_url": "https://wms.company.com",
    "username": "user",
    "password": "pass",
    "start_date": "2024-01-01T00:00:00Z"
}

tap = TapOracleWMS(config=config, state=state)

# Run incremental sync
tap.sync_all()

# Save updated state
with open('state.json', 'w') as f:
    json.dump(tap.state, f)
```

### **Meltano Integration**

```yaml
# meltano.yml
project_id: warehouse_analytics
environments:
  - name: prod
    config:
      plugins:
        extractors:
          - name: tap-oracle-wms
            variant: datacosmos
            pip_url: tap-oracle-wms
            config:
              base_url: ${WMS_BASE_URL}
              username: ${WMS_USERNAME}
              password: ${WMS_PASSWORD}
              start_date: "2024-01-01T00:00:00Z"
            select:
              - inventory.*
              - orders.*
              - shipments.*
```

---

## 🔗 **Integration Ecosystem**

### **Compatible Targets**

| Target             | Purpose                   | Status    |
| ------------------ | ------------------------- | --------- |
| `target-postgres`  | PostgreSQL data warehouse | ✅ Tested |
| `target-snowflake` | Snowflake cloud warehouse | ✅ Tested |
| `target-bigquery`  | Google BigQuery           | ✅ Tested |
| `target-redshift`  | Amazon Redshift           | ✅ Tested |
| `target-s3`        | S3 data lake              | ✅ Tested |

### **PyAuto Integration**

| Component                                            | Integration     | Purpose                  |
| ---------------------------------------------------- | --------------- | ------------------------ |
| [flx-http-oracle-wms](../flx-http-oracle-wms/)       | Shared client   | WMS API communication    |
| [target-oracle-wms](../target-oracle-wms/)           | Round-trip sync | WMS data synchronization |
| [flx-meltano-enterprise](../flx-meltano-enterprise/) | Orchestration   | Enterprise data platform |

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Discovery Timeout**

   - **Symptom**: Discovery process times out
   - **Solution**: Increase `discovery_timeout` setting

2. **Memory Issues with Large Datasets**

   - **Symptom**: Out of memory errors
   - **Solution**: Reduce `page_size`, enable streaming mode

3. **Authentication Failures**
   - **Symptom**: 401/403 errors
   - **Solution**: Verify credentials and permissions

### **Debug Mode**

```bash
# Enable debug logging
export TAP_ORACLE_WMS_LOG_LEVEL=DEBUG

# Run with verbose output
tap-oracle-wms --config config.json -v

# Log API requests
export TAP_ORACLE_WMS_LOG_REQUESTS=true
```

---

## 🛠️ **CLI Reference**

```bash
# Discovery
tap-oracle-wms --config config.json --discover > catalog.json

# Full sync
tap-oracle-wms --config config.json --catalog catalog.json

# Incremental sync
tap-oracle-wms --config config.json --catalog catalog.json --state state.json

# Select specific streams
tap-oracle-wms --config config.json --catalog catalog.json \
  --properties inventory,orders

# Test connection
tap-oracle-wms --config config.json --test

# Version info
tap-oracle-wms --version
```

---

## 📖 **Configuration Reference**

### **Required Settings**

| Setting    | Type   | Description      | Default |
| ---------- | ------ | ---------------- | ------- |
| `base_url` | string | WMS API base URL | -       |
| `username` | string | WMS username     | -       |
| `password` | string | WMS password     | -       |

### **Optional Settings**

| Setting           | Type    | Description                 | Default    |
| ----------------- | ------- | --------------------------- | ---------- |
| `company_code`    | string  | WMS company code            | \*         |
| `facility_code`   | string  | WMS facility code           | \*         |
| `start_date`      | string  | Sync start date             | 2020-01-01 |
| `pagination_mode` | string  | Pagination: sequenced/paged | sequenced  |
| `page_size`       | integer | Records per page            | 1000       |
| `request_timeout` | integer | Request timeout (seconds)   | 7200       |
| `retry_count`     | integer | Retry attempts              | 3          |

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Singer Specification](https://hub.meltano.com/singer/spec) - Singer protocol specification
- [Meltano SDK Documentation](https://sdk.meltano.com/) - SDK reference
- [Oracle WMS API Docs](https://docs.oracle.com/en/cloud/saas/warehouse-management/) - WMS API reference

### **Next Steps**

- [Data Pipeline Setup](../docs/guides/pipeline-setup.md) - Complete pipeline configuration
- [Performance Tuning](../docs/guides/tap-performance.md) - Optimization strategies
- [Production Deployment](../docs/deployment/tap-deployment.md) - Production setup

### **Related Topics**

- [Singer Best Practices](../docs/patterns/singer.md) - Singer tap patterns
- [ETL Patterns](../docs/patterns/etl.md) - ETL design patterns
- [Data Quality](../docs/guides/data-quality.md) - Ensuring data quality

---

**📂 Component**: Tap Oracle WMS | **🏠 Root**: [PyAuto Home](../README.md) | **Framework**: Singer SDK 0.45.0+ | **Updated**: 2025-06-19

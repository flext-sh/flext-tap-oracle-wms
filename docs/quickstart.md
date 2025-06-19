# tap-oracle-wms Quick Start Guide

Get up and running with tap-oracle-wms in minutes! This guide walks you through installation, configuration, and your first data extraction.

## Prerequisites

- Python 3.8 or higher
- Oracle WMS Cloud access with API credentials
- Basic familiarity with command line

## Installation

### Using pip

```bash
pip install tap-oracle-wms
```

### Using pipx (Recommended)

```bash
pipx install tap-oracle-wms
```

### From Source

```bash
git clone https://github.com/your-org/tap-oracle-wms.git
cd tap-oracle-wms
pip install -e .
```

## Configuration

### 1. Create Configuration File

Create a `config.json` file with your WMS credentials:

```json
{
  "base_url": "https://your-instance.wms.ocs.oraclecloud.com/your-tenant",
  "auth_method": "basic",
  "username": "your_username",
  "password": "your_password",
  "company_code": "YOUR_COMPANY",
  "facility_code": "YOUR_FACILITY",
  "start_date": "2025-01-01T00:00:00Z"
}
```

### 2. Environment Variables (Recommended)

For security, use environment variables:

```bash
export TAP_ORACLE_WMS_USERNAME="your_username"
export TAP_ORACLE_WMS_PASSWORD="your_password"
```

Then reference in config:

```json
{
  "base_url": "https://your-instance.wms.ocs.oraclecloud.com/your-tenant",
  "auth_method": "basic",
  "username": "${TAP_ORACLE_WMS_USERNAME}",
  "password": "${TAP_ORACLE_WMS_PASSWORD}",
  "company_code": "YOUR_COMPANY",
  "facility_code": "YOUR_FACILITY",
  "start_date": "2025-01-01T00:00:00Z"
}
```

## Basic Usage

### 1. Discover Available Entities

First, discover what data is available:

```bash
tap-oracle-wms --config config.json --discover > catalog.json
```

This creates a catalog of all available entities and their schemas.

### 2. Select Entities to Extract

Edit `catalog.json` to enable desired streams:

```json
{
  "streams": [
    {
      "tap_stream_id": "item",
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "selected": true, // Enable this stream
            "replication-method": "INCREMENTAL",
            "replication-key": "update_ts"
          }
        }
      ]
    }
  ]
}
```

### 3. Run the Tap

Extract data to stdout:

```bash
tap-oracle-wms --config config.json --catalog catalog.json
```

## Common Use Cases

### Extract Inventory Data

```bash
# Configure for inventory extraction
cat > inventory_config.json << EOF
{
  "base_url": "https://wms.example.com/tenant",
  "auth_method": "basic",
  "username": "${WMS_USER}",
  "password": "${WMS_PASS}",
  "company_code": "ACME",
  "facility_code": "DC01",
  "start_date": "2025-01-01T00:00:00Z",
  "entities": ["inventory", "item", "location"]
}
EOF

# Run extraction
tap-oracle-wms --config inventory_config.json | target-jsonl
```

### Daily Order Sync

```bash
# Extract today's orders
cat > daily_orders.json << EOF
{
  "base_url": "https://wms.example.com/tenant",
  "auth_method": "basic",
  "username": "${WMS_USER}",
  "password": "${WMS_PASS}",
  "company_code": "ACME",
  "facility_code": "DC01",
  "start_date": "$(date -u +%Y-%m-%d)T00:00:00Z",
  "entities": ["order_hdr", "order_dtl"]
}
EOF

tap-oracle-wms --config daily_orders.json
```

### Real-time Monitoring

```python
#!/usr/bin/env python3
"""Monitor WMS changes in real-time."""

import json
import subprocess
import time

def extract_recent_changes():
    """Extract changes from last 5 minutes."""
    config = {
        "base_url": "https://wms.example.com/tenant",
        "auth_method": "basic",
        "username": os.environ["WMS_USER"],
        "password": os.environ["WMS_PASS"],
        "company_code": "ACME",
        "facility_code": "DC01",
        "start_date": (datetime.now() - timedelta(minutes=5)).isoformat() + "Z",
        "entities": ["inventory", "allocation", "task"]
    }

    with open("temp_config.json", "w") as f:
        json.dump(config, f)

    result = subprocess.run(
        ["tap-oracle-wms", "--config", "temp_config.json"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.splitlines():
        data = json.loads(line)
        if data["type"] == "RECORD":
            process_change(data)

def process_change(record):
    """Process a change record."""
    print(f"Change detected: {record['stream']} - {record['record']['id']}")

# Run every 5 minutes
while True:
    extract_recent_changes()
    time.sleep(300)
```

## Integration with Meltano

### 1. Add to Meltano Project

```bash
meltano add extractor tap-oracle-wms
```

### 2. Configure in meltano.yml

```yaml
project_id: your_project
environments:
  - name: dev
  - name: prod

plugins:
  extractors:
    - name: tap-oracle-wms
      pip_url: tap-oracle-wms
      config:
        base_url: ${TAP_ORACLE_WMS_BASE_URL}
        auth_method: basic
        username: ${TAP_ORACLE_WMS_USERNAME}
        password: ${TAP_ORACLE_WMS_PASSWORD}
        company_code: ${TAP_ORACLE_WMS_COMPANY}
        facility_code: ${TAP_ORACLE_WMS_FACILITY}
        start_date: "2024-01-01T00:00:00Z"
      select:
        - item.*
        - inventory.*
        - location.*
        - order_hdr.*
        - order_dtl.*
```

### 3. Run with Meltano

```bash
# Install
meltano install

# Test connection
meltano invoke tap-oracle-wms --discover

# Run pipeline
meltano run tap-oracle-wms target-postgres
```

## OAuth 2.0 Configuration

For production environments using OAuth:

```json
{
  "base_url": "https://your-instance.wms.ocs.oraclecloud.com/your-tenant",
  "auth_method": "oauth2",
  "oauth_client_id": "${WMS_OAUTH_CLIENT_ID}",
  "oauth_client_secret": "${WMS_OAUTH_CLIENT_SECRET}",
  "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token",
  "company_code": "YOUR_COMPANY",
  "facility_code": "YOUR_FACILITY",
  "start_date": "2025-01-01T00:00:00Z"
}
```

## Performance Optimization

### 1. Use Cursor Pagination

For large datasets, enable cursor pagination:

```json
{
  "pagination_mode": "cursor",
  "page_size": 1000
}
```

### 2. Select Only Needed Fields

```json
{
  "field_selection": {
    "item": ["id", "code", "description", "status"],
    "inventory": ["id", "item_id", "location_id", "on_hand_qty"]
  }
}
```

### 3. Parallel Extraction

```json
{
  "max_parallel_streams": 5,
  "entities": ["item", "inventory", "location", "order_hdr", "order_dtl"]
}
```

## Troubleshooting

### Connection Issues

Test connection:

```bash
tap-oracle-wms --config config.json --discover | head -n 10
```

Enable debug logging:

```bash
export TAP_ORACLE_WMS_LOG_LEVEL=DEBUG
tap-oracle-wms --config config.json
```

### Authentication Errors

Verify credentials:

```bash
curl -u username:password \
  -H "X-WMS-Company: YOUR_COMPANY" \
  -H "X-WMS-Facility: YOUR_FACILITY" \
  https://your-instance.wms.ocs.oraclecloud.com/your-tenant/wms/lgfapi/v10/entity
```

### Performance Issues

For slow extractions:

1. Enable cursor pagination
2. Increase page size
3. Use field selection
4. Extract entities in parallel

## Next Steps

1. Read the [Configuration Reference](configuration.md) for all options
2. Learn about [Entity Discovery](wms-entity-discovery.md)
3. Optimize with [Performance Tuning](performance-tuning.md)
4. Set up [Monitoring](monitoring.md)

## Getting Help

- Documentation: [Full Documentation](README.md)
- Issues: [GitHub Issues](https://github.com/your-org/tap-oracle-wms/issues)
- Community: [Meltano Slack](https://meltano.com/slack)

## Example Scripts

### Inventory Snapshot

```bash
#!/bin/bash
# Daily inventory snapshot

DATE=$(date +%Y%m%d)
OUTPUT_DIR="inventory_snapshots"

mkdir -p $OUTPUT_DIR

tap-oracle-wms \
  --config config.json \
  --catalog catalog.json \
  --state state.json \
  | target-csv \
  --config '{"destination_path": "'$OUTPUT_DIR'/'$DATE'"}' \
  > state.json.new

mv state.json.new state.json
echo "Inventory snapshot saved to $OUTPUT_DIR/$DATE"
```

### Change Detection

```python
#!/usr/bin/env python3
"""Detect and alert on inventory changes."""

import json
import sys
from datetime import datetime

previous_state = {}

for line in sys.stdin:
    message = json.loads(line)

    if message["type"] == "RECORD":
        stream = message["stream"]
        record = message["record"]
        key = f"{stream}:{record['id']}"

        if key in previous_state:
            old_record = previous_state[key]
            changes = {
                k: {"old": old_record.get(k), "new": v}
                for k, v in record.items()
                if old_record.get(k) != v
            }

            if changes:
                print(f"Changes detected in {stream} ID {record['id']}:")
                print(json.dumps(changes, indent=2))

        previous_state[key] = record

    # Pass through all messages
    print(line, end='')
```

Use it:

```bash
tap-oracle-wms --config config.json | python3 change_detector.py | target-jsonl
```

Happy extracting! 🚀

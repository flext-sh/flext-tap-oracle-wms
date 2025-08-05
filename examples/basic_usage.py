#!/usr/bin/env python3
"""Basic usage example for FLEXT Tap Oracle WMS.

Shows how to use the tap with flext-oracle-wms integration.
"""

import json
import os
import sys
from pathlib import Path

from flext_tap_oracle_wms import FlextTapOracleWMS, FlextTapOracleWMSConfig


def main():
    """Run basic example."""
    # Configuration from environment or hardcoded
    config = FlextTapOracleWMSConfig(
        base_url=os.getenv("ORACLE_WMS_BASE_URL", "https://ta29.wms.ocs.oraclecloud.com/raizen_test"),
        username=os.getenv("ORACLE_WMS_USERNAME", "USER_WMS_INTEGRA"),
        password=os.getenv("ORACLE_WMS_PASSWORD", "your_password"),
        api_version="v10",
        page_size=100,
        verify_ssl=True,
        # Optional: filter specific entities
        include_entities=["inventory", "locations", "orders"],
        # Optional: enable request logging for debugging
        enable_request_logging=True,
    )

    # Create tap
    tap = FlextTapOracleWMS(config=config)

    # Example 1: Validate configuration
    print("1. Validating configuration...")
    validation_result = tap.validate_configuration()
    if validation_result.is_success:
        print(f"✓ Configuration valid: {validation_result.value}")
    else:
        print(f"✗ Configuration invalid: {validation_result.error}")
        return 1

    # Example 2: Discover catalog
    print("\n2. Discovering catalog...")
    catalog_result = tap.discover_catalog()
    if catalog_result.is_success:
        catalog = catalog_result.value
        print(f"✓ Discovered {len(catalog['streams'])} streams:")
        for stream in catalog["streams"]:
            print(f"  - {stream['stream']}")
            if "schema" in stream and "properties" in stream["schema"]:
                print(f"    Fields: {', '.join(stream['schema']['properties'].keys())}")
    else:
        print(f"✗ Discovery failed: {catalog_result.error}")
        return 1

    # Example 3: Discover available streams
    print("\n3. Discovering available streams...")
    streams = tap.discover_streams()
    print(f"✓ Found {len(streams)} streams:")
    for stream in streams:
        print(f"  - {stream.name} (PK: {stream.primary_keys}, RK: {stream.replication_key})")

    # Example 4: Get implementation info
    print("\n4. Implementation information:")
    print(f"  Name: {tap.get_implementation_name()}")
    print(f"  Version: {tap.get_implementation_version()}")

    metrics_result = tap.get_implementation_metrics()
    if metrics_result.is_success:
        print(f"  Metrics: {json.dumps(metrics_result.value, indent=2)}")

    # Example 5: Extract data (commented out to avoid actual API calls)
    """
    print("\n5. Extracting data...")

    # Option A: Run the tap normally (outputs to stdout)
    tap.run()

    # Option B: Process specific streams
    for stream in streams[:1]:  # Just first stream as example
        print(f"\nExtracting from {stream.name}...")
        record_count = 0
        for record in stream.get_records(context=None):
            print(json.dumps(record))
            record_count += 1
            if record_count >= 5:  # Limit to 5 records for example
                break
        print(f"Extracted {record_count} records from {stream.name}")
    """

    print("\n✓ Example completed successfully!")
    print("\nTo run the tap for real data extraction:")
    print("  python -m flext_tap_oracle_wms | target-postgres --config postgres_config.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())

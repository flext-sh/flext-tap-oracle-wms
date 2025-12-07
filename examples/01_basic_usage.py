#!/usr/bin/env python3
"""Basic usage example for FLEXT Tap Oracle WMS.

Shows how to use the tap with flext-oracle-wms integration.
"""

import os
import sys

# from pydantic import SecretStr  # Not needed
from flext_tap_oracle_wms import (
    FlextTapOracleWms,
    FlextTapOracleWmsConfig,
)


def main() -> int:
    """Run basic example.

    Returns:
      int: Description.

    """  # Configuration from environment or hardcoded
    config = FlextTapOracleWmsConfig(
        base_url=os.getenv(
            "ORACLE_WMS_BASE_URL",
            "https://invalid.wms.ocs.oraclecloud.com/company_unknow",
        ),
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
    tap = FlextTapOracleWms(config=config)

    # Example 1: Validate configuration
    validation_result = tap.validate_configuration()
    if not validation_result.is_success:
        return 1

    # Example 2: Discover catalog
    catalog_result = tap.discover_catalog()
    if catalog_result.is_success:
        catalog = catalog_result.value
        if (
            catalog is not None
            and isinstance(catalog, dict)
            and "streams" in catalog
            and isinstance(catalog["streams"], list)
        ):
            for stream in catalog["streams"]:
                if (
                    isinstance(stream, dict)
                    and "schema" in stream
                    and "properties" in stream["schema"]
                ):
                    pass
    else:
        return 1

    # Example 3: Discover available streams
    streams = tap.discover_streams()
    for _stream in streams:
        pass

    # Example 4: Get implementation info

    metrics_result = tap.get_implementation_metrics()
    if metrics_result.is_success:
        pass

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

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Basic usage example for FLEXT Tap Oracle WMS.

Shows how to use the tap with flext-oracle-wms integration.
"""

from __future__ import annotations

import os
import sys

from flext_tap_oracle_wms import FlextTapOracleWms, FlextTapOracleWmsSettings


def main() -> int:
    """Run basic example.

    Returns:
      int: Description.

    """
    config = FlextTapOracleWmsSettings(
        base_url=os.getenv(
            "ORACLE_WMS_BASE_URL",
            "https://invalid.wms.ocs.oraclecloud.com/company_unknow",
        ),
        username=os.getenv("ORACLE_WMS_USERNAME", "USER_WMS_INTEGRA"),
        password=os.getenv("ORACLE_WMS_PASSWORD", "your_password"),
        api_version="v10",
        page_size=100,
        verify_ssl=True,
        include_entities=["inventory", "locations", "orders"],
        enable_request_logging=True,
    )
    tap = FlextTapOracleWms(config=config)
    validation_result = tap.validate_configuration()
    if not validation_result.is_success:
        return 1
    catalog_result = tap.discover_catalog()
    if catalog_result.is_success:
        catalog = catalog_result.value
        if (
            catalog is not None
            and isinstance(catalog, dict)
            and ("streams" in catalog)
            and isinstance(catalog["streams"], list)
        ):
            for stream in catalog["streams"]:
                if (
                    isinstance(stream, dict)
                    and "schema" in stream
                    and ("properties" in stream["schema"])
                ):
                    pass
    else:
        return 1
    streams = tap.discover_streams()
    for _stream in streams:
        pass
    metrics_result = tap.get_implementation_metrics()
    if metrics_result.is_success:
        pass
    '\n    print("\n5. Extracting data...")\n\n    # Option A: Run the tap normally (outputs to stdout)\n    tap.run()\n\n    # Option B: Process specific streams\n    for stream in streams[:1]:  # Just first stream as example\n      print(f"\nExtracting from {stream.name}...")\n      record_count = 0\n      for record in stream.get_records(context=None):\n          print(json.dumps(record))\n          record_count += 1\n          if record_count >= 5:  # Limit to 5 records for example\n              break\n      print(f"Extracted {record_count} records from {stream.name}")\n    '
    return 0


if __name__ == "__main__":
    sys.exit(main())

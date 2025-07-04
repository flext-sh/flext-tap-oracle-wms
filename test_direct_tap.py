#!/usr/bin/env python3
"""Example test script for Oracle WMS tap.

This demonstrates how to test the tap directly without going through Meltano.
Replace the configuration values with your actual Oracle WMS instance details.
"""

import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_tap_directly() -> None:
    """Test tap discovery and extraction directly."""
    # Example configuration - replace with your WMS instance details
    config = {
        "base_url": "https://your-wms-instance.example.com",  # Your Oracle WMS URL
        "username": "your_username",
        "password": "your_password",
        "company_code": "*",  # Or specific company code
        "facility_code": "*",  # Or specific facility code
        "entities": ["allocation", "order_hdr", "order_dtl"],  # WMS entities to extract
        "page_size": 10,  # Small page size for testing
        "start_date": "2025-01-01T00:00:00Z",
    }

    try:
        # Import tap
        from tap_oracle_wms.tap import TapOracleWMS

        # Create tap instance
        print("Creating tap instance...")
        tap = TapOracleWMS(config=config)

        # Test discovery
        print("Discovering available streams...")
        catalog = tap.discover_streams()

        if catalog:
            print(f"Found {len(catalog)} streams:")
            for stream in catalog:
                print(f"  - {stream.name}")
        else:
            print("No streams discovered")
            return

        # Test extraction for allocation
        print("\nTesting extraction for 'allocation' stream...")
        allocation_stream = None
        for stream in catalog:
            if stream.name == "allocation":
                allocation_stream = stream
                break

        if not allocation_stream:
            print("Allocation stream not found")
            return

        print("Extracting records...")
        records = list(allocation_stream.get_records(None))

        if records:
            print(f"Successfully extracted {len(records)} records")
            # Print first record as example
            if records:
                print("\nFirst record example:")
                print(records[0])
        else:
            print("No records extracted")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_tap_directly()

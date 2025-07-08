#!/usr/bin/env python3
"""Example test script for Oracle WMS tap.

This demonstrates how to test the tap directly without going through Meltano.
Replace the configuration values with your actual Oracle WMS instance details.
"""

from __future__ import annotations

from pathlib import Path
import sys

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
        tap = TapOracleWMS(config=config)

        # Test discovery
        catalog = tap.discover_streams()

        if catalog:
            for stream in catalog:
                pass
        else:
            return

        # Test extraction for allocation
        allocation_stream = None
        for stream in catalog:
            if stream.name == "allocation":
                allocation_stream = stream
                break

        if not allocation_stream:
            return

        records = list(allocation_stream.get_records(None))

        if records:
            # Print first record as example
            if records:
                pass

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_tap_directly()

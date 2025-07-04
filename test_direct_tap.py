#!/usr/bin/env python3
"""Test direto do tap para verificar o problema."""

import sys

# Add path for imports
sys.path.insert(0, "/home/marlonsc/flext/flext-tap-oracle-wms/src")


def test_tap_directly() -> None:
    """Test tap discovery and extraction directly."""
    # Configuração básica
    config = {
        "base_url": "https://client-a.client-b.io:9043",  # WMS API URL
        "client_id": "client-b_external",
        "client_secret": "client-b@2024!Secure",
        "username": "client-b_EXTERNAL",
        "password": "client-b@2024!External",
        "company_code": "*",
        "facility_code": "*",
        "entities": ["allocation", "order_hdr", "order_dtl"],
        "page_size": 10,
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
            pass

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_tap_directly()

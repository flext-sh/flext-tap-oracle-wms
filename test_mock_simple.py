#!/usr/bin/env python3
"""Simple mock test script."""

import asyncio
import time

from mock_wms_server import start_mock_server
from tap_oracle_wms.discovery import EntityDiscovery


def test_mock():
    server = start_mock_server(8888)
    time.sleep(1)

    config = {
        "base_url": "http://localhost:8888",
        "username": "test",
        "password": "test",
        "verify_ssl": False
    }

    discovery = EntityDiscovery(config)
    result = asyncio.run(discovery.discover_entities())

    print(f"✅ SUCCESS: Found {len(result)} entities")
    for i, entity in enumerate(list(result.keys())[:5], 1):
        print(f"  {i}. {entity}")
    if len(result) > 5:
        print(f"  ... and {len(result) - 5} more")

    server.shutdown()
    return len(result) > 0

if __name__ == "__main__":
    success = test_mock()
    import sys
    sys.exit(0 if success else 1)

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
        "verify_ssl": False,
    }

    discovery = EntityDiscovery(config)
    result = asyncio.run(discovery.discover_entities())

    for _i, _entity in enumerate(list(result.keys())[:5], 1):
        pass
    if len(result) > 5:
        pass

    server.shutdown()
    return len(result) > 0


if __name__ == "__main__":
    success = test_mock()
    import sys

    sys.exit(0 if success else 1)

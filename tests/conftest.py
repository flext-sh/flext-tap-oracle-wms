"""Test configuration and fixtures for FLEXT Tap Oracle WMS."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from flext_core import FlextResult
from pydantic import SecretStr

from flext_tap_oracle_wms import (
    FlextTapOracleWMS,
    FlextTapOracleWMSConfig,
)

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session")
def oracle_wms_environment() -> None:
    """Set Oracle WMS environment variables for tests."""
    # Load from .env if exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with env_file.open(encoding="utf-8") as f:
            for file_line in f:
                line = file_line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value


@pytest.fixture
def sample_config() -> FlextTapOracleWMSConfig:
    """Sample configuration for tests."""
    return FlextTapOracleWMSConfig(
        base_url="https://test.wms.example.com",
        username="test_user",
        password=SecretStr("test_password"),
        api_version="v10",
        page_size=100,
        timeout=30,
        max_retries=3,
        verify_ssl=False,
    )


@pytest.fixture
def real_config(oracle_wms_environment: None) -> FlextTapOracleWMSConfig:
    """Real configuration from environment."""
    return FlextTapOracleWMSConfig(
        base_url=os.environ.get("ORACLE_WMS_BASE_URL", ""),
        username=os.environ.get("ORACLE_WMS_USERNAME", ""),
        password=SecretStr(os.environ.get("ORACLE_WMS_PASSWORD", "")),
        api_version=os.environ.get("ORACLE_WMS_API_VERSION", "v10"),
        page_size=int(os.environ.get("ORACLE_WMS_PAGE_SIZE", "100")),
        timeout=int(os.environ.get("ORACLE_WMS_TIMEOUT", "30")),
        verify_ssl=os.environ.get("ORACLE_WMS_VERIFY_SSL", "true").lower() == "true",
    )


@pytest.fixture
def mock_wms_client() -> MagicMock:
    """Mock Oracle WMS client."""
    client = MagicMock()

    # Mock successful connection
    client.connect.return_value = FlextResult.ok(None)

    # Mock list entities
    client.list_entities.return_value = FlextResult.ok(
        [
            "inventory",
            "locations",
            "shipments",
            "receipts",
        ],
    )

    # Mock get records
    client.get_records.return_value = FlextResult.ok(
        [
            {"id": "1", "name": "Test Item 1", "quantity": 100},
            {"id": "2", "name": "Test Item 2", "quantity": 200},
        ],
    )

    # Mock get entity metadata
    client.get_entity_metadata.return_value = FlextResult.ok(
        {
            "display_name": "Inventory",
            "description": "Inventory data",
            "primary_key": ["inventory_id"],
            "replication_key": "mod_ts",
        },
    )

    return client


@pytest.fixture
def tap_instance(sample_config: FlextTapOracleWMSConfig) -> FlextTapOracleWMS:
    """Create tap instance with sample config."""
    return FlextTapOracleWMS(config=sample_config)


# Removed fixtures for authenticator and discovery_instance
# as these classes were moved to flext-oracle-wms


@pytest.fixture
def sample_catalog() -> dict[str, object]:
    """Sample Singer catalog."""
    return {
        "type": "CATALOG",
        "streams": [
            {
                "tap_stream_id": "inventory",
                "stream": "inventory",
                "schema": {
                    "type": "object",
                    "properties": {
                        "inventory_id": {"type": "string"},
                        "item_id": {"type": "string"},
                        "quantity": {"type": "number"},
                        "mod_ts": {"type": "string", "format": "date-time"},
                    },
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "forced-replication-method": "INCREMENTAL",
                            "table-key-properties": ["inventory_id"],
                            "replication-key": "mod_ts",
                        },
                    },
                ],
            },
        ],
    }


@pytest.fixture
def sample_state() -> dict[str, object]:
    """Sample Singer state."""
    return {
        "bookmarks": {
            "inventory": {
                "replication_key_value": "2024-01-01T00:00:00Z",
                "version": 1,
            },
        },
    }


@pytest.fixture
def mock_response() -> MagicMock:
    """Mock HTTP response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "data": [
            {"id": "1", "name": "Item 1"},
            {"id": "2", "name": "Item 2"},
        ],
        "_links": {
            "next": "https://test.wms.example.com/api/v10/inventory?page=2",
        },
    }
    response.text = '{"data": []}'
    return response


@pytest.fixture
def mock_request() -> MagicMock:
    """Mock HTTP request."""
    request = MagicMock()
    request.auth = None
    request.headers = {}
    return request


# Marker for tests requiring real Oracle WMS
def pytest_collection_modifyitems(config: object, items: list[object]) -> None:
    """Add markers to tests based on their location."""
    for item in items:
        # Add oracle_wms marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.oracle_wms)

        # Add slow marker to e2e and performance tests
        if any(x in str(item.fspath) for x in ["e2e", "performance"]):
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
def reset_environment() -> Generator[None]:
    """Reset environment after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)

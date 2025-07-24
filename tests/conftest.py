"""Pytest configuration for Oracle WMS tap tests."""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from pathlib import Path

import pytest

# Load environment if needed (optional)
project_root = Path(__file__).parent.parent


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "e2e: mark test as end-to-end test requiring real WMS instance",
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test",
    )
    config.addinivalue_line(
        "markers",
        "unit: mark test as unit test",
    )


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options."""
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="run end-to-end tests against real WMS instance",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Modify test collection to skip E2E tests by default."""
    if not config.getoption("--run-e2e"):
        skip_e2e = pytest.mark.skip(reason="need --run-e2e option to run")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)


@pytest.fixture(scope="session")
def test_project_root() -> Path:
    """Get project root directory.

    Returns:
        Path to project root directory.

    """
    return Path(__file__).parent.parent


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> None:
    """Setup test environment variables."""
    import os

    # Set mandatory environment variables for tests
    os.environ["TAP_ORACLE_WMS_USE_METADATA_ONLY"] = "true"
    os.environ["TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE"] = "0"


@pytest.fixture(scope="session")
def mock_wms_config() -> dict[str, object]:
    """Mock WMS configuration for unit tests."""
    import os

    # Set additional environment for tests
    os.environ["TAP_ORACLE_WMS_ENTITIES"] = "allocation,order_hdr,order_dtl,item"
    return {
        "base_url": "https://mock-wms.example.com",
        "username": "test_user",
        "password": "test_pass",
        "company_code": "*",
        "facility_code": "*",
        "page_size": 100,
        "request_timeout": 30,
        "verify_ssl": False,
        "entities": ["allocation", "order_hdr", "order_dtl"],
        "auth_method": "basic",
        "enable_incremental": True,
        "replication_key": "mod_ts",
    }


@pytest.fixture
def sample_wms_response() -> dict[str, object]:
    """Sample WMS API response for testing."""
    return {
        "results": [
            {
                "id": 1,
                "code": "ITEM001",
                "description": "Test Item 1",
                "mod_ts": "2024-01-01T10:00:00Z",
                "create_ts": "2024-01-01T09:00:00Z",
            },
            {
                "id": 2,
                "code": "ITEM002",
                "description": "Test Item 2",
                "mod_ts": "2024-01-01T11:00:00Z",
                "create_ts": "2024-01-01T09:30:00Z",
            },
        ],
        "next_page": "https://mock-wms.example.com/entity/item?cursor=abc123",
        "page_nbr": 1,
        "page_count": 5,
        "result_count": 10,
    }


@pytest.fixture
def sample_metadata() -> dict[str, object]:
    """Sample WMS entity metadata for testing."""
    return {
        "parameters": ["id", "code", "description", "mod_ts", "create_ts"],
        "fields": {
            "id": {"type": "integer", "required": True},
            "code": {"type": "string", "max_length": 50, "required": True},
            "description": {"type": "string", "required": False},
            "mod_ts": {"type": "datetime", "required": False},
            "create_ts": {"type": "datetime", "required": False},
        },
    }


@pytest.fixture
def sample_entity_dict() -> dict[str, str]:
    """Sample entity discovery response as dictionary."""
    return {
        "allocation": "/entity/allocation",
        "order_hdr": "/entity/order_hdr",
        "order_dtl": "/entity/order_dtl",
        "item": "/entity/item",
        "location": "/entity/location",
        "inventory": "/entity/inventory",
    }

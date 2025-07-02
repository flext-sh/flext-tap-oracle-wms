"""Pytest configuration for Oracle WMS tap tests."""

from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test requiring real WMS instance"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="run end-to-end tests against real WMS instance"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip E2E tests by default."""
    if not config.getoption("--run-e2e"):
        skip_e2e = pytest.mark.skip(reason="need --run-e2e option to run")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def mock_wms_config():
    """Mock WMS configuration for unit tests."""
    return {
        "base_url": "https://mock-wms.example.com",
        "username": "test_user",
        "password": "test_pass",
        "company_code": "*",
        "facility_code": "*",
        "page_size": 100,
        "request_timeout": 30,
        "verify_ssl": False,
    }


@pytest.fixture
def sample_wms_response():
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
            }
        ],
        "next_page": "https://mock-wms.example.com/entity/item?cursor=abc123",
        "page_nbr": 1,
        "page_count": 5,
        "result_count": 10
    }


@pytest.fixture
def sample_entity_list():
    """Sample entity discovery response."""
    return [
        "item",
        "location",
        "inventory",
        "order_header",
        "order_detail",
        "allocation",
        "pick",
        "shipment",
        "receipt",
        "user",
        "company",
        "facility"
    ]

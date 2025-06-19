"""Pytest configuration and shared fixtures for tap-oracle-wms tests."""

import os
from pathlib import Path
from typing import Any, Optional

import httpx
import pytest
from dotenv import load_dotenv


# Load environment variables for tests
load_dotenv()


@pytest.fixture(scope="session")
def project_root() -> Any:
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def src_root(project_root) -> Any:
    """Get source directory."""
    return project_root / "src"


@pytest.fixture(autouse=True)
def add_src_to_path(src_root) -> None:
    """Add src directory to Python path for imports."""
    import sys

    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))


@pytest.fixture
def sample_config() -> Any:
    """Sample configuration for testing."""
    return {
        "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
        "auth_method": "basic",
        "username": "test_user",
        "password": "test_pass",
        "company_code": "RAIZEN",
        "facility_code": "*",
        "start_date": "2024-01-01T00:00:00Z",
        "pagination_mode": "offset",
        "page_size": 10,
        "entities": ["facility"],
    }


@pytest.fixture
def live_config() -> Any:
    """Live configuration using environment variables."""
    username = os.getenv("WMS_USERNAME")
    password = os.getenv("WMS_PASSWORD")

    if not username or not password:
        pytest.skip("Live credentials not available (WMS_USERNAME, WMS_PASSWORD)")

    return {
        "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
        "auth_method": "basic",
        "username": username,
        "password": password,
        "company_code": "RAIZEN",
        "facility_code": "*",
        "start_date": "2024-01-01T00:00:00Z",
        "pagination_mode": "offset",
        "page_size": 5,
        "entities": ["facility"],
    }


@pytest.fixture
def sample_wms_response() -> Any:
    """Sample WMS API response data for testing validation."""
    return {
        "result_count": 3,
        "page_count": 2,
        "page_nbr": 1,
        "next_page": "https://example.com?page=2",
        "previous_page": None,
        "results": [
            {
                "id": 1,
                "code": "99001",
                "name": "Cajamar",
                "city": "Cajamar",
                "state": "SP",
                "create_ts": "2024-01-01T10:00:00-03:00",
                "mod_ts": "2024-07-24T15:08:49.257715-03:00",
            },
            {
                "id": 2,
                "code": "1085820",
                "name": "OXXO OROZIMBO MAIA",
                "city": "CAMPINAS",
                "state": "SP",
                "create_ts": "2024-01-02T10:00:00-03:00",
                "mod_ts": "2025-04-15T12:47:14.297556-03:00",
            },
            {
                "id": 3,
                "code": "1086824",
                "name": "OXXO MALL VIEIRA",
                "city": "CAMPINAS",
                "state": "SP",
                "create_ts": "2024-01-03T10:00:00-03:00",
                "mod_ts": "2025-04-15T12:49:34.377418-03:00",
            },
        ],
    }


@pytest.fixture
def mock_entity_list() -> Any:
    """Mock entity discovery response."""
    return ["facility", "item", "location", "inventory", "order_hdr", "allocation"]


@pytest.fixture
def mock_schema() -> Any:
    """Mock JSON schema for facility entity."""
    return {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "code": {"type": "string"},
            "name": {"type": "string"},
            "city": {"type": "string"},
            "state": {"type": "string"},
            "create_ts": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "format": "date-time",
                "default": "now",
            },
            "mod_ts": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "format": "date-time",
                "default": "now",
            },
        },
        "required": ["id", "code", "name"],
        "additionalProperties": False,
    }


@pytest.fixture
def mock_describe_response() -> Any:
    """Mock describe endpoint response."""
    return {
        "name": "facility",
        "fields": [
            {"name": "id", "type": "integer", "nullable": False},
            {"name": "code", "type": "string", "nullable": False},
            {"name": "name", "type": "string", "nullable": False},
            {"name": "city", "type": "string", "nullable": True},
            {"name": "state", "type": "string", "nullable": True},
            {"name": "create_ts", "type": "datetime", "nullable": True},
            {"name": "mod_ts", "type": "datetime", "nullable": True},
        ],
    }


@pytest.fixture
def mock_http_client() -> Any:
    """Mock HTTP client with common responses."""
    client = Mock(spec=httpx.Client)

    def get_response(url, **kwargs) -> Any:
        response = Mock(spec=httpx.Response)
        response.status_code = 200

        if "/entity/" in url and url.endswith("/entity/"):
            # Entity discovery
            response.json.return_value = ["facility", "item", "location", "inventory"]
        elif "/describe/" in url:
            # Entity describe
            response.json.return_value = {
                "name": "facility",
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "code", "type": "string"},
                    {"name": "mod_ts", "type": "datetime"},
                ],
            }
        else:
            # Data query
            response.json.return_value = {
                "result_count": 1,
                "page_count": 1,
                "page_nbr": 1,
                "results": [
                    {"id": 1, "code": "TEST", "mod_ts": "2024-01-01T10:00:00Z"}
                ],
            }

        return response

    client.get.side_effect = get_response
    return client


@pytest.fixture
def captured_messages() -> Any:
    """Capture Singer messages during test execution."""
    messages = []

    def capture_message(message) -> None:
        if hasattr(message, "to_dict"):
            messages.append(message.to_dict())
        else:
            messages.append({"type": message.__class__.__name__, "value": str(message)})

    return messages, capture_message


class WMSTestHelper:
    """Helper class for WMS testing utilities."""

    @staticmethod
    def create_mock_response(data: dict[str, Any], status_code: int = 200) -> Mock:
        """Create a mock HTTP response."""
        response = Mock(spec=httpx.Response)
        response.status_code = status_code
        response.json.return_value = data
        return response

    @staticmethod
    def create_paginated_response(
        results: list,
        page: int = 1,
        page_size: int = 10,
        total_results: Optional[int] = None,
    ) -> dict[str, Any]:
        """Create a paginated WMS API response."""
        if total_results is None:
            total_results = len(results)

        total_pages = (total_results + page_size - 1) // page_size

        return {
            "result_count": len(results),
            "page_count": total_pages,
            "page_nbr": page,
            "next_page": (
                f"https://example.com?page={page + 1}" if page < total_pages else None
            ),
            "previous_page": (
                f"https://example.com?page={page - 1}" if page > 1 else None
            ),
            "results": results,
        }

    @staticmethod
    def validate_singer_message(message: dict[str, Any], expected_type: str) -> bool:
        """Validate Singer protocol message format."""
        if message.get("type") != expected_type:
            return False

        if expected_type == "SCHEMA":
            return "stream" in message and "schema" in message
        if expected_type == "RECORD":
            return "stream" in message and "record" in message
        if expected_type == "STATE":
            return "value" in message

        return False


@pytest.fixture
def wms_test_helper() -> Any:
    """WMS testing helper utilities."""
    return WMSTestHelper


# Markers for different test categories
def pytest_configure(config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "live: Tests requiring live WMS connection")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "auth: Authentication tests")
    config.addinivalue_line("markers", "discovery: Entity discovery tests")
    config.addinivalue_line("markers", "pagination: Pagination tests")
    config.addinivalue_line("markers", "state: State management tests")
    config.addinivalue_line("markers", "extraction: Data extraction tests")


def pytest_collection_modifyitems(config, items) -> None:
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "test_unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_live" in item.nodeid:
            item.add_marker(pytest.mark.live)

        # Add markers based on test function names
        if "auth" in item.name:
            item.add_marker(pytest.mark.auth)
        elif "discovery" in item.name:
            item.add_marker(pytest.mark.discovery)
        elif "pagination" in item.name:
            item.add_marker(pytest.mark.pagination)
        elif "state" in item.name:
            item.add_marker(pytest.mark.state)
        elif "extraction" in item.name:
            item.add_marker(pytest.mark.extraction)

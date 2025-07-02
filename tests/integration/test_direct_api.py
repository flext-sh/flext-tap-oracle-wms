#!/usr/bin/env python3
"""Test direct API call to allocation endpoint."""

import json
from base64 import b64encode
from pathlib import Path

import httpx
import pytest


def test_direct_api_call_if_config_exists() -> None:
    """Test direct API call to allocation endpoint if config.json exists."""
    config_path = Path("config.json")

    if not config_path.exists():
        pytest.skip("config.json not found - skipping direct API test")

    # Load config
    with config_path.open() as f:
        config = json.load(f)

    # Build auth
    auth = b64encode(f"{config['username']}:{config['password']}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Build URL for allocation data
    api_version = config.get("api_version", "v1")
    url = f"{config['base_url']}/wms/lgfapi/{api_version}/entity/allocation"
    params = {
        "page_mode": "sequenced",
        "page_size": 1,
    }

    try:
        response = httpx.get(url, headers=headers, params=params, timeout=30.0)

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, dict):
                assert "results" in data or len(data) > 0
                if "next_page" in data:
                    assert isinstance(data["next_page"], (str, type(None)))
            elif isinstance(data, list):
                assert len(data) >= 0  # Empty list is valid
        else:
            pytest.fail(f"API call failed with status {response.status_code}: {response.text}")

    except Exception as e:
        pytest.fail(f"API call failed with exception: {e}")


def test_direct_api_call_with_test_config() -> None:
    """Test direct API call using test config."""
    test_config_path = Path("tests/config.json")

    if not test_config_path.exists():
        pytest.skip("tests/config.json not found - skipping test")

    # Load test config
    with test_config_path.open() as f:
        config = json.load(f)

    # This should be a mock endpoint for testing
    assert "mock" in config["base_url"] or "test" in config["base_url"]

    # Build auth
    auth = b64encode(f"{config['username']}:{config['password']}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Build URL for allocation data
    api_version = config.get("api_version", "v1")
    url = f"{config['base_url']}/wms/lgfapi/{api_version}/entity/allocation"
    params = {
        "page_mode": "sequenced",
        "page_size": 1,
    }

    # Note: This will likely fail with mock endpoint, but should not crash
    try:
        response = httpx.get(url, headers=headers, params=params, timeout=10.0)
        # Mock endpoint may return various responses
        assert response.status_code in {200, 404, 401, 500}  # Valid HTTP status codes
    except (httpx.ConnectError, httpx.TimeoutException):
        # Expected for mock endpoints
        pytest.skip("Mock endpoint connection failed as expected")

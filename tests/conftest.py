"""Test configuration and fixtures for FLEXT Tap Oracle WMS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch as _patch

import pytest
from flext_tests import reset_settings as _shared_reset_settings

from flext_tap_oracle_wms.settings import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.tap import FlextTapOracleWms

if TYPE_CHECKING:
    from collections.abc import Generator

    from tests.typings import t

reset_settings = _shared_reset_settings


@pytest.fixture(scope="session")
def oracle_wms_environment() -> None:
    """Set Oracle WMS environment variables for tests."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with env_file.open(encoding="utf-8") as f:
            for file_line in f:
                line = file_line.strip()
                if line and (not line.startswith("#")):
                    key, value = line.split("=", 1)
                    os.environ[key] = value


@pytest.fixture(autouse=True)
def isolate_tap_oracle_wms_env(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
    reset_settings: None,
) -> None:
    """Keep unit tests deterministic regardless of host FLEXT_TAP_ORACLE_WMS_* env."""
    _ = reset_settings
    if request.node.get_closest_marker(
        "integration",
    ) or request.node.get_closest_marker("real"):
        return
    for key in [key for key in os.environ if key.startswith("FLEXT_TAP_ORACLE_WMS_")]:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def sample_config() -> FlextTapOracleWmsSettings:
    """Sample configuration for tests."""
    return FlextTapOracleWmsSettings(
        base_url="https://test.wms.example.com",
        username="test_user",
        password="test_password",
        api_version="v10",
        page_size=100,
        timeout=30,
        max_retries=3,
        verify_ssl=False,
    )


@pytest.fixture
def real_config(oracle_wms_environment: None) -> FlextTapOracleWmsSettings:
    """Real configuration from environment."""
    _ = oracle_wms_environment
    return FlextTapOracleWmsSettings(
        base_url=os.environ.get("ORACLE_WMS_BASE_URL", ""),
        username=os.environ.get("ORACLE_WMS_USERNAME", ""),
        password=os.environ.get("ORACLE_WMS_PASSWORD", ""),
        api_version=os.environ.get("ORACLE_WMS_API_VERSION", "v10"),
        page_size=int(os.environ.get("ORACLE_WMS_PAGE_SIZE", "100")),
        timeout=int(os.environ.get("ORACLE_WMS_TIMEOUT", "30")),
        verify_ssl=os.environ.get("ORACLE_WMS_VERIFY_SSL", "true").lower() == "true",
    )


@pytest.fixture
def tap_instance(sample_config: FlextTapOracleWmsSettings) -> FlextTapOracleWms:
    """Create tap instance with sample settings (mocked discovery)."""
    with _patch.object(FlextTapOracleWms, "discover_streams", return_value=[]):
        return FlextTapOracleWms(settings=sample_config.model_dump(mode="json"))


@pytest.fixture
def real_tap_instance(real_config: FlextTapOracleWmsSettings) -> FlextTapOracleWms:
    """Real tap instance for integration tests."""
    return FlextTapOracleWms(settings=real_config.model_dump(mode="json"))


@pytest.fixture
def test_config_extraction() -> t.JsonMapping:
    """Test configuration for extraction tests."""
    return {
        "base_url": "https://test.wms.example.com",
        "username": "test_user",
        "password": "test_password",
        "entities": ["inventory"],
        "page_size": 10,
    }


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: t.SequenceOf[pytest.Item],
) -> None:
    """Add markers to tests based on their location."""
    _ = config
    for item in items:
        if hasattr(item, "fspath") and "integration" in str(item.fspath):
            item.add_marker(pytest.mark.oracle_wms)
        if hasattr(item, "fspath") and any(
            x in str(item.fspath) for x in ["e2e", "performance"]
        ):
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
def reset_environment() -> Generator[None]:
    """Reset environment after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)

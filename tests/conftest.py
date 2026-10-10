"""Test configuration and fixtures for FLEXT Tap Oracle WMS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from flext_tap_oracle_wms import FlextTapOracleWmsSettings, m
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from flext_tests import u

if TYPE_CHECKING:
    from collections.abc import Generator

    from tests import t


_ORACLE_WMS_REQUIRED_VARS = (
    "FLEXT_TAP_ORACLE_WMS_BASE_URL",
    "FLEXT_TAP_ORACLE_WMS_USERNAME",
    "FLEXT_TAP_ORACLE_WMS_PASSWORD",
)


@pytest.fixture(scope="session")
def oracle_wms_environment() -> None:
    """Load only an explicitly configured, reachable local test environment."""
    env_file = Path(__file__).parent.parent / ".env"
    u.Tests.skip_if_no_external_environment(
        _ORACLE_WMS_REQUIRED_VARS, env_file,
        url_var=_ORACLE_WMS_REQUIRED_VARS[0],
    )


@pytest.fixture(scope="session")
def oracle_wms_available(oracle_wms_environment: None) -> bool:
    """Check if Oracle WMS external environment is available for integration tests.

    Returns:
        True if all required environment variables are set, False otherwise.
    """
    _ = oracle_wms_environment
    return True


@pytest.fixture
def sample_config() -> FlextTapOracleWmsSettings:
    """Sample configuration for tests.

    Returns:
        The resulting ``FlextTapOracleWmsSettings``.
    """
    # NOTE (multi-agent): mro-u3eu — ADR-005 namespaces project fields under
    # settings.TapOracleWms.*; construct via the namespace payload.
    return FlextTapOracleWmsSettings.model_validate({
        "TapOracleWms": {
            "base_url": "https://test.wms.example.com",
            "username": "test_user",
            "password": "p" + "4" * 12,
            "api_version": "v10",
            "page_size": 100,
            "timeout": 30,
            "max_retries": 3,
            "verify_ssl": False,
        },
    })


@pytest.fixture
def real_config(oracle_wms_available: bool) -> FlextTapOracleWmsSettings:
    """Real configuration resolved from the canonical FLEXT_TAP_ORACLE_WMS_* env.

    The settings model declares ``env_prefix="FLEXT_TAP_ORACLE_WMS_"``, so
    pydantic-settings loads the live credentials directly; no parallel env
    mapping is introduced here.

    Returns:
        The resulting ``FlextTapOracleWmsSettings``.

    Raises:
        pytest.skip: If Oracle WMS environment is not available.
    """
    if not oracle_wms_available:
        pytest.skip("Oracle WMS external environment not configured")
    return FlextTapOracleWmsSettings()


@pytest.fixture
def sample_catalog() -> m.Meltano.SingerCatalog:
    """A real Singer catalog model so tap construction skips WMS discovery.

    Returns:
        The resulting ``m.Meltano.SingerCatalog``.
    """
    catalog: m.Meltano.SingerCatalog = m.Meltano.SingerCatalog.model_validate({
        "streams": [
            {
                "tap_stream_id": "inventory",
                "stream": "inventory",
                "schema": {"type": "object"},
                "metadata": [],
                "key_properties": ["id"],
            },
        ],
    })
    return catalog


@pytest.fixture
def tap_instance(
    sample_config: FlextTapOracleWmsSettings,
    sample_catalog: m.Meltano.SingerCatalog,
) -> FlextTapOracleWms:
    """Create a tap from typed settings + a typed catalog (no WMS discovery).

    Returns:
        The resulting ``FlextTapOracleWms``.
    """
    return FlextTapOracleWms.from_settings(sample_config, catalog=sample_catalog)


@pytest.fixture
def real_tap_instance(
    real_config: FlextTapOracleWmsSettings,
    oracle_wms_available: bool,
) -> FlextTapOracleWms:
    """Real tap instance for integration tests.

    Returns:
        The resulting ``FlextTapOracleWms``.

    Raises:
        pytest.skip: If Oracle WMS environment is not available.
    """
    if not oracle_wms_available:
        pytest.skip("Oracle WMS external environment not configured")
    return FlextTapOracleWms.from_settings(real_config)


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: t.SequenceOf[pytest.Item],
) -> None:
    """Declare connectivity by fixture dependency, never integration location."""
    _ = config
    for item in items:
        item_path = str(item.path)
        if "integration" in item_path:
            item.add_marker(pytest.mark.integration)
        if any(x in item_path for x in ["e2e", "performance"]):
            item.add_marker(pytest.mark.slow)
        if any(name in item.fixturenames for name in ("real_config", "real_tap_instance")):
            item.add_marker(pytest.mark.connectivity(
                required_vars=_ORACLE_WMS_REQUIRED_VARS,
                url_var=_ORACLE_WMS_REQUIRED_VARS[0],
            ))


@pytest.fixture
def reset_environment() -> Generator[None]:
    """Reset environment after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)

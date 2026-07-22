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
from flext_tests import reset_settings as _shared_reset_settings

if TYPE_CHECKING:
    from collections.abc import Generator

    from tests import t

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


@pytest.fixture
def isolate_tap_oracle_wms_env(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
    reset_settings: None,
) -> None:
    """Keep unit tests deterministic regardless of host FLEXT_TAP_ORACLE_WMS_* env."""
    _ = reset_settings
    if request.node.get_closest_marker(
        "integration"
    ) or request.node.get_closest_marker("real"):
        return
    for key in [key for key in os.environ if key.startswith("FLEXT_TAP_ORACLE_WMS_")]:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def sample_config() -> FlextTapOracleWmsSettings:
    """Sample configuration for tests."""
    # NOTE (multi-agent): mro-u3eu — ADR-005 namespaces project fields under
    # settings.TapOracleWms.*; construct via the namespace payload.
    return FlextTapOracleWmsSettings.model_validate({
        "TapOracleWms": {
            "base_url": "https://test.wms.example.com",
            "username": "test_user",
            "password": "test_password",
            "api_version": "v10",
            "page_size": 100,
            "timeout": 30,
            "max_retries": 3,
            "verify_ssl": False,
        }
    })


@pytest.fixture
def real_config() -> FlextTapOracleWmsSettings:
    """Real configuration resolved from the canonical FLEXT_TAP_ORACLE_WMS_* env.

    The settings model declares ``env_prefix="FLEXT_TAP_ORACLE_WMS_"``, so
    pydantic-settings loads the live credentials directly; no parallel env
    mapping is introduced here.
    """
    return FlextTapOracleWmsSettings()


@pytest.fixture
def sample_catalog() -> m.Meltano.SingerCatalog:
    """A real Singer catalog model so tap construction skips WMS discovery."""
    catalog: m.Meltano.SingerCatalog = m.Meltano.SingerCatalog.model_validate({
        "streams": [
            {
                "tap_stream_id": "inventory",
                "stream": "inventory",
                "schema": {"type": "object"},
                "metadata": [],
                "key_properties": ["id"],
            }
        ]
    })
    return catalog


@pytest.fixture
def tap_instance(
    sample_config: FlextTapOracleWmsSettings,
    sample_catalog: m.Meltano.SingerCatalog,
) -> FlextTapOracleWms:
    """Create a tap from typed settings + a typed catalog (no WMS discovery)."""
    return FlextTapOracleWms.from_settings(sample_config, catalog=sample_catalog)


@pytest.fixture(scope="session")
def oracle_wms_online(oracle_wms_environment: None) -> bool:
    """Whether online Oracle WMS tests are explicitly enabled for this session.

    Online tests reach the live Oracle WMS Cloud. They run only when the
    operator opts in via ``FLEXT_TAP_ORACLE_WMS_ONLINE`` (a truthy value) and
    the canonical credentials are present. This is a pure settings/env check
    evaluated once per session; it never touches the network, so offline runs
    skip the online suites deterministically instead of erroring.
    """
    _ = oracle_wms_environment
    if os.environ.get("FLEXT_TAP_ORACLE_WMS_ONLINE", "").strip().lower() not in {
        "1",
        "true",
        "yes",
    }:
        return False
    settings = FlextTapOracleWmsSettings()
    return bool(
        settings.TapOracleWms.base_url
        and settings.TapOracleWms.username
        and settings.TapOracleWms.password
    )


@pytest.fixture
def real_tap_instance(real_config: FlextTapOracleWmsSettings) -> FlextTapOracleWms:
    """Real tap instance for integration tests."""
    return FlextTapOracleWms.from_settings(real_config)


def pytest_collection_modifyitems(
    config: pytest.Config, items: t.SequenceOf[pytest.Item]
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
def skip_when_oracle_wms_offline(request: pytest.FixtureRequest) -> None:
    """Skip online-gated tests when the real Oracle WMS is not enabled.

    The ``oracle_wms`` and ``slow`` markers are applied at collection to the
    integration, e2e and performance suites. When online access is not enabled
    they are skipped here — validated once at session start — rather than
    reaching the network during each test's setup.
    """
    online_markers = ("oracle_wms", "slow", "integration", "e2e", "performance")
    requires_online = any(
        request.node.get_closest_marker(marker) is not None
        for marker in online_markers
    )
    if not requires_online:
        return
    if not request.getfixturevalue("oracle_wms_online"):
        pytest.skip(
            "[env-gated] Oracle WMS online tests disabled "
            "(set FLEXT_TAP_ORACLE_WMS_ONLINE=1)",
        )


@pytest.fixture
def reset_environment() -> Generator[None]:
    """Reset environment after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)

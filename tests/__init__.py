# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_tests import td, tf, tk, tm, tv

    from flext_tap_oracle_wms import d, e, h, r, s, x
    from tests.constants import TestsFlextTapOracleWmsConstants, c
    from tests.e2e.test_e2e import TestOracleWMSE2EComplete
    from tests.integration.test_functional import TestOracleWMSFunctionalComplete
    from tests.integration.test_streams_functional import TestStreamsFunctional
    from tests.integration.test_wms import TestRealWmsIntegration
    from tests.integration.test_wms_connection import (
        TestFilteringAndSelection,
        TestIntegration,
        TestRealConnection,
        TestRealDataExtraction,
    )
    from tests.models import TestsFlextTapOracleWmsModels, m
    from tests.performance.test_extraction_performance import (
        TestExtractionPerformance,
        TestRateLimitingPerformance,
    )
    from tests.protocols import TestsFlextTapOracleWmsProtocols, p
    from tests.typings import TestsFlextTapOracleWmsTypes, t
    from tests.unit.test_cli import TestsFlextTapOracleWmsCli
    from tests.unit.test_config import TestsFlextTapOracleWmsConfig
    from tests.unit.test_config_validation import TestsFlextTapOracleWmsConfigValidation
    from tests.unit.test_tap import TestsFlextTapOracleWmsTap
    from tests.unit.test_tap_initialization import (
        TestsFlextTapOracleWmsTapInitialization,
    )
    from tests.utilities import TestsFlextTapOracleWmsUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (
        ".e2e",
        ".integration",
        ".performance",
        ".unit",
    ),
    build_lazy_import_map(
        {
            ".constants": (
                "TestsFlextTapOracleWmsConstants",
                "c",
            ),
            ".e2e.test_e2e": ("TestOracleWMSE2EComplete",),
            ".integration.test_functional": ("TestOracleWMSFunctionalComplete",),
            ".integration.test_streams_functional": ("TestStreamsFunctional",),
            ".integration.test_wms": ("TestRealWmsIntegration",),
            ".integration.test_wms_connection": (
                "TestFilteringAndSelection",
                "TestIntegration",
                "TestRealConnection",
                "TestRealDataExtraction",
            ),
            ".models": (
                "TestsFlextTapOracleWmsModels",
                "m",
            ),
            ".performance.test_extraction_performance": (
                "TestExtractionPerformance",
                "TestRateLimitingPerformance",
            ),
            ".protocols": (
                "TestsFlextTapOracleWmsProtocols",
                "p",
            ),
            ".typings": (
                "TestsFlextTapOracleWmsTypes",
                "t",
            ),
            ".unit.test_cli": ("TestsFlextTapOracleWmsCli",),
            ".unit.test_config": ("TestsFlextTapOracleWmsConfig",),
            ".unit.test_config_validation": ("TestsFlextTapOracleWmsConfigValidation",),
            ".unit.test_tap": ("TestsFlextTapOracleWmsTap",),
            ".unit.test_tap_initialization": (
                "TestsFlextTapOracleWmsTapInitialization",
            ),
            ".utilities": (
                "TestsFlextTapOracleWmsUtilities",
                "u",
            ),
            "flext_tap_oracle_wms": (
                "d",
                "e",
                "h",
                "r",
                "s",
                "x",
            ),
            "flext_tests": (
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
            ),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "TestExtractionPerformance",
    "TestFilteringAndSelection",
    "TestIntegration",
    "TestOracleWMSE2EComplete",
    "TestOracleWMSFunctionalComplete",
    "TestRateLimitingPerformance",
    "TestRealConnection",
    "TestRealDataExtraction",
    "TestRealWmsIntegration",
    "TestStreamsFunctional",
    "TestsFlextTapOracleWmsCli",
    "TestsFlextTapOracleWmsConfig",
    "TestsFlextTapOracleWmsConfigValidation",
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsTap",
    "TestsFlextTapOracleWmsTapInitialization",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
]

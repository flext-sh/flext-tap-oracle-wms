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
    from flext_tests import td as td, tf as tf, tk as tk, tv as tv

    from flext_tap_oracle_wms import d as d, e as e, h as h, r as r, x as x
    from tests.base import (
        TestsFlextTapOracleWmsServiceBase as TestsFlextTapOracleWmsServiceBase,
        s as s,
    )
    from tests.constants import (
        TestsFlextTapOracleWmsConstants as TestsFlextTapOracleWmsConstants,
        c as c,
    )
    from tests.e2e.test_e2e import (
        TestsFlextTapOracleWmsE2e as TestsFlextTapOracleWmsE2e,
    )
    from tests.integration.test_functional import (
        TestsFlextTapOracleWmsFunctional as TestsFlextTapOracleWmsFunctional,
    )
    from tests.integration.test_streams_functional import (
        TestsFlextTapOracleWmsStreamsFunctional as TestsFlextTapOracleWmsStreamsFunctional,
    )
    from tests.integration.test_wms import (
        TestsFlextTapOracleWmsWms as TestsFlextTapOracleWmsWms,
    )
    from tests.integration.test_wms_connection import (
        TestsFlextTapOracleWmsWmsConnection as TestsFlextTapOracleWmsWmsConnection,
    )
    from tests.models import (
        TestsFlextTapOracleWmsModels as TestsFlextTapOracleWmsModels,
        m as m,
    )
    from tests.performance.test_extraction_performance import (
        TestsFlextTapOracleWmsExtractionPerformance as TestsFlextTapOracleWmsExtractionPerformance,
    )
    from tests.protocols import (
        TestsFlextTapOracleWmsProtocols as TestsFlextTapOracleWmsProtocols,
        p as p,
    )
    from tests.settings import (
        TestsFlextTapOracleWmsSettings as TestsFlextTapOracleWmsSettings,
    )
    from tests.typings import (
        TestsFlextTapOracleWmsTypes as TestsFlextTapOracleWmsTypes,
        t as t,
    )
    from tests.unit.test_cli import (
        TestsFlextTapOracleWmsCli as TestsFlextTapOracleWmsCli,
    )
    from tests.unit.test_config import (
        TestsFlextTapOracleWmsConfig as TestsFlextTapOracleWmsConfig,
    )
    from tests.unit.test_config_validation import (
        TestsFlextTapOracleWmsConfigValidation as TestsFlextTapOracleWmsConfigValidation,
    )
    from tests.unit.test_tap import (
        TestsFlextTapOracleWmsTap as TestsFlextTapOracleWmsTap,
    )
    from tests.unit.test_tap_initialization import (
        TestsFlextTapOracleWmsTapInitialization as TestsFlextTapOracleWmsTapInitialization,
    )
    from tests.utilities import (
        TestsFlextTapOracleWmsUtilities as TestsFlextTapOracleWmsUtilities,
        u as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (
        ".e2e",
        ".integration",
        ".performance",
        ".unit",
    ),
    build_lazy_import_map(
        {
            ".base": (
                "TestsFlextTapOracleWmsServiceBase",
                "s",
            ),
            ".constants": (
                "TestsFlextTapOracleWmsConstants",
                "c",
            ),
            ".e2e.test_e2e": ("TestsFlextTapOracleWmsE2e",),
            ".integration.test_functional": ("TestsFlextTapOracleWmsFunctional",),
            ".integration.test_streams_functional": (
                "TestsFlextTapOracleWmsStreamsFunctional",
            ),
            ".integration.test_wms": ("TestsFlextTapOracleWmsWms",),
            ".integration.test_wms_connection": (
                "TestsFlextTapOracleWmsWmsConnection",
            ),
            ".models": (
                "TestsFlextTapOracleWmsModels",
                "m",
            ),
            ".performance.test_extraction_performance": (
                "TestsFlextTapOracleWmsExtractionPerformance",
            ),
            ".protocols": (
                "TestsFlextTapOracleWmsProtocols",
                "p",
            ),
            ".settings": ("TestsFlextTapOracleWmsSettings",),
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
                "x",
            ),
            "flext_tests": (
                "td",
                "tf",
                "tk",
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
    "TestsFlextTapOracleWmsCli",
    "TestsFlextTapOracleWmsConfig",
    "TestsFlextTapOracleWmsConfigValidation",
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsE2e",
    "TestsFlextTapOracleWmsExtractionPerformance",
    "TestsFlextTapOracleWmsFunctional",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsServiceBase",
    "TestsFlextTapOracleWmsSettings",
    "TestsFlextTapOracleWmsStreamsFunctional",
    "TestsFlextTapOracleWmsTap",
    "TestsFlextTapOracleWmsTapInitialization",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
    "TestsFlextTapOracleWmsWms",
    "TestsFlextTapOracleWmsWmsConnection",
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
    "tv",
    "u",
    "x",
]

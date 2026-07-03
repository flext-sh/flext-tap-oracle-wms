# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_tests import (
        d as d,
        e as e,
        h as h,
        r as r,
        td as td,
        tf as tf,
        tk as tk,
        tm as tm,
        tv as tv,
        x as x,
    )

    from flext_tap_oracle_wms.tests.base import (
        TestsFlextTapOracleWmsServiceBase as TestsFlextTapOracleWmsServiceBase,
        s as s,
    )
    from flext_tap_oracle_wms.tests.constants import (
        TestsFlextTapOracleWmsConstants as TestsFlextTapOracleWmsConstants,
        c as c,
    )
    from flext_tap_oracle_wms.tests.e2e.test_e2e import (
        TestsFlextTapOracleWmsE2e as TestsFlextTapOracleWmsE2e,
    )
    from flext_tap_oracle_wms.tests.integration.test_functional import (
        TestsFlextTapOracleWmsFunctional as TestsFlextTapOracleWmsFunctional,
    )
    from flext_tap_oracle_wms.tests.integration.test_streams_functional import (
        TestsFlextTapOracleWmsStreamsFunctional as TestsFlextTapOracleWmsStreamsFunctional,
    )
    from flext_tap_oracle_wms.tests.integration.test_wms import (
        TestsFlextTapOracleWmsWms as TestsFlextTapOracleWmsWms,
    )
    from flext_tap_oracle_wms.tests.integration.test_wms_connection import (
        TestsFlextTapOracleWmsWmsConnection as TestsFlextTapOracleWmsWmsConnection,
    )
    from flext_tap_oracle_wms.tests.models import (
        TestsFlextTapOracleWmsModels as TestsFlextTapOracleWmsModels,
        m as m,
    )
    from flext_tap_oracle_wms.tests.performance.test_extraction_performance import (
        TestsFlextTapOracleWmsExtractionPerformance as TestsFlextTapOracleWmsExtractionPerformance,
    )
    from flext_tap_oracle_wms.tests.protocols import (
        TestsFlextTapOracleWmsProtocols as TestsFlextTapOracleWmsProtocols,
        p as p,
    )
    from flext_tap_oracle_wms.tests.settings import (
        TestsFlextTapOracleWmsSettings as TestsFlextTapOracleWmsSettings,
    )
    from flext_tap_oracle_wms.tests.typings import (
        TestsFlextTapOracleWmsTypes as TestsFlextTapOracleWmsTypes,
        t as t,
    )
    from flext_tap_oracle_wms.tests.unit.test_cli import (
        TestsFlextTapOracleWmsCli as TestsFlextTapOracleWmsCli,
    )
    from flext_tap_oracle_wms.tests.unit.test_config import (
        TestsFlextTapOracleWmsConfig as TestsFlextTapOracleWmsConfig,
    )
    from flext_tap_oracle_wms.tests.unit.test_config_validation import (
        TestsFlextTapOracleWmsConfigValidation as TestsFlextTapOracleWmsConfigValidation,
    )
    from flext_tap_oracle_wms.tests.unit.test_tap import (
        TestsFlextTapOracleWmsTap as TestsFlextTapOracleWmsTap,
    )
    from flext_tap_oracle_wms.tests.unit.test_tap_initialization import (
        TestsFlextTapOracleWmsTapInitialization as TestsFlextTapOracleWmsTapInitialization,
    )
    from flext_tap_oracle_wms.tests.utilities import (
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
            ".conftest": ("conftest",),
            ".constants": (
                "TestsFlextTapOracleWmsConstants",
                "c",
            ),
            ".e2e": ("e2e",),
            ".e2e.test_e2e": ("TestsFlextTapOracleWmsE2e",),
            ".integration": ("integration",),
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
            ".performance": ("performance",),
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
            ".unit": ("unit",),
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
            "flext_tests": (
                "d",
                "e",
                "h",
                "r",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
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


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

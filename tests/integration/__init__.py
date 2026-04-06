# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Integration package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.integration.test_functional as _tests_integration_test_functional

    test_functional = _tests_integration_test_functional
    import tests.integration.test_streams_functional as _tests_integration_test_streams_functional
    from tests.integration.test_functional import TestOracleWMSFunctionalComplete

    test_streams_functional = _tests_integration_test_streams_functional
    import tests.integration.test_wms as _tests_integration_test_wms
    from tests.integration.test_streams_functional import TestStreamsFunctional, logger

    test_wms = _tests_integration_test_wms
    import tests.integration.test_wms_connection as _tests_integration_test_wms_connection
    from tests.integration.test_wms import TestRealWmsIntegration

    test_wms_connection = _tests_integration_test_wms_connection
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
    from tests.integration.test_wms_connection import (
        TestFilteringAndSelection,
        TestIntegration,
        TestRealConnection,
        TestRealDataExtraction,
        env_path,
        real_config,
        tap,
    )
_LAZY_IMPORTS = {
    "TestFilteringAndSelection": (
        "tests.integration.test_wms_connection",
        "TestFilteringAndSelection",
    ),
    "TestIntegration": ("tests.integration.test_wms_connection", "TestIntegration"),
    "TestOracleWMSFunctionalComplete": (
        "tests.integration.test_functional",
        "TestOracleWMSFunctionalComplete",
    ),
    "TestRealConnection": (
        "tests.integration.test_wms_connection",
        "TestRealConnection",
    ),
    "TestRealDataExtraction": (
        "tests.integration.test_wms_connection",
        "TestRealDataExtraction",
    ),
    "TestRealWmsIntegration": ("tests.integration.test_wms", "TestRealWmsIntegration"),
    "TestStreamsFunctional": (
        "tests.integration.test_streams_functional",
        "TestStreamsFunctional",
    ),
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "env_path": ("tests.integration.test_wms_connection", "env_path"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "logger": ("tests.integration.test_streams_functional", "logger"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "real_config": ("tests.integration.test_wms_connection", "real_config"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "tap": ("tests.integration.test_wms_connection", "tap"),
    "test_functional": "tests.integration.test_functional",
    "test_streams_functional": "tests.integration.test_streams_functional",
    "test_wms": "tests.integration.test_wms",
    "test_wms_connection": "tests.integration.test_wms_connection",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "TestFilteringAndSelection",
    "TestIntegration",
    "TestOracleWMSFunctionalComplete",
    "TestRealConnection",
    "TestRealDataExtraction",
    "TestRealWmsIntegration",
    "TestStreamsFunctional",
    "c",
    "d",
    "e",
    "env_path",
    "h",
    "logger",
    "m",
    "p",
    "r",
    "real_config",
    "s",
    "t",
    "tap",
    "test_functional",
    "test_streams_functional",
    "test_wms",
    "test_wms_connection",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

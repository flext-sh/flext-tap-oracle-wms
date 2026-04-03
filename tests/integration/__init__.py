# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Integration package."""

from __future__ import annotations

import typing as _t

from flext_core.constants import FlextConstants as c
from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports
from flext_core.mixins import FlextMixins as x
from flext_core.models import FlextModels as m
from flext_core.protocols import FlextProtocols as p
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from flext_core.typings import FlextTypes as t
from flext_core.utilities import FlextUtilities as u
from tests.integration.test_functional import TestOracleWMSFunctionalComplete
from tests.integration.test_streams_functional import TestStreamsFunctional, logger
from tests.integration.test_wms import TestRealWmsIntegration
from tests.integration.test_wms_connection import (
    TestFilteringAndSelection,
    TestIntegration,
    TestRealConnection,
    TestRealDataExtraction,
    env_path,
    real_config,
    tap,
)

if _t.TYPE_CHECKING:
    import tests.integration.test_functional as _tests_integration_test_functional

    test_functional = _tests_integration_test_functional
    import tests.integration.test_streams_functional as _tests_integration_test_streams_functional

    test_streams_functional = _tests_integration_test_streams_functional
    import tests.integration.test_wms as _tests_integration_test_wms

    test_wms = _tests_integration_test_wms
    import tests.integration.test_wms_connection as _tests_integration_test_wms_connection

    test_wms_connection = _tests_integration_test_wms_connection

    _ = (
        TestFilteringAndSelection,
        TestIntegration,
        TestOracleWMSFunctionalComplete,
        TestRealConnection,
        TestRealDataExtraction,
        TestRealWmsIntegration,
        TestStreamsFunctional,
        c,
        d,
        e,
        env_path,
        h,
        logger,
        m,
        p,
        r,
        real_config,
        s,
        t,
        tap,
        test_functional,
        test_streams_functional,
        test_wms,
        test_wms_connection,
        u,
        x,
    )
_LAZY_IMPORTS = {
    "TestFilteringAndSelection": "tests.integration.test_wms_connection",
    "TestIntegration": "tests.integration.test_wms_connection",
    "TestOracleWMSFunctionalComplete": "tests.integration.test_functional",
    "TestRealConnection": "tests.integration.test_wms_connection",
    "TestRealDataExtraction": "tests.integration.test_wms_connection",
    "TestRealWmsIntegration": "tests.integration.test_wms",
    "TestStreamsFunctional": "tests.integration.test_streams_functional",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "env_path": "tests.integration.test_wms_connection",
    "h": ("flext_core.handlers", "FlextHandlers"),
    "logger": "tests.integration.test_streams_functional",
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "real_config": "tests.integration.test_wms_connection",
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "tap": "tests.integration.test_wms_connection",
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

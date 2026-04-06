# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.unit.test_cli as _tests_unit_test_cli

    test_cli = _tests_unit_test_cli
    import tests.unit.test_config as _tests_unit_test_config
    from tests.unit.test_cli import TestCLI

    test_config = _tests_unit_test_config
    import tests.unit.test_config_validation as _tests_unit_test_config_validation
    from tests.unit.test_config import TestFlextTapOracleWmsSettings

    test_config_validation = _tests_unit_test_config_validation
    import tests.unit.test_tap as _tests_unit_test_tap
    from tests.unit.test_config_validation import TestConfigValidation

    test_tap = _tests_unit_test_tap
    import tests.unit.test_tap_initialization as _tests_unit_test_tap_initialization
    from tests.unit.test_tap import TestFlextTapOracleWms

    test_tap_initialization = _tests_unit_test_tap_initialization
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
    from tests.unit.test_tap_initialization import TestTapInitialization
_LAZY_IMPORTS = {
    "TestCLI": ("tests.unit.test_cli", "TestCLI"),
    "TestConfigValidation": (
        "tests.unit.test_config_validation",
        "TestConfigValidation",
    ),
    "TestFlextTapOracleWms": ("tests.unit.test_tap", "TestFlextTapOracleWms"),
    "TestFlextTapOracleWmsSettings": (
        "tests.unit.test_config",
        "TestFlextTapOracleWmsSettings",
    ),
    "TestTapInitialization": (
        "tests.unit.test_tap_initialization",
        "TestTapInitialization",
    ),
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "test_cli": "tests.unit.test_cli",
    "test_config": "tests.unit.test_config",
    "test_config_validation": "tests.unit.test_config_validation",
    "test_tap": "tests.unit.test_tap",
    "test_tap_initialization": "tests.unit.test_tap_initialization",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "TestCLI",
    "TestConfigValidation",
    "TestFlextTapOracleWms",
    "TestFlextTapOracleWmsSettings",
    "TestTapInitialization",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "test_cli",
    "test_config",
    "test_config_validation",
    "test_tap",
    "test_tap_initialization",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

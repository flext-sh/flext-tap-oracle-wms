# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
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
    from flext_tap_oracle_wms import (
        test_cli,
        test_config,
        test_config_validation,
        test_tap,
        test_tap_initialization,
    )
    from flext_tap_oracle_wms.test_cli import TestCLI
    from flext_tap_oracle_wms.test_config import TestFlextTapOracleWmsSettings
    from flext_tap_oracle_wms.test_config_validation import TestConfigValidation
    from flext_tap_oracle_wms.test_tap import TestFlextTapOracleWms
    from flext_tap_oracle_wms.test_tap_initialization import TestTapInitialization

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "TestCLI": "flext_tap_oracle_wms.test_cli",
    "TestConfigValidation": "flext_tap_oracle_wms.test_config_validation",
    "TestFlextTapOracleWms": "flext_tap_oracle_wms.test_tap",
    "TestFlextTapOracleWmsSettings": "flext_tap_oracle_wms.test_config",
    "TestTapInitialization": "flext_tap_oracle_wms.test_tap_initialization",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "test_cli": "flext_tap_oracle_wms.test_cli",
    "test_config": "flext_tap_oracle_wms.test_config",
    "test_config_validation": "flext_tap_oracle_wms.test_config_validation",
    "test_tap": "flext_tap_oracle_wms.test_tap",
    "test_tap_initialization": "flext_tap_oracle_wms.test_tap_initialization",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

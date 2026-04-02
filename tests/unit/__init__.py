# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Test module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from tests.unit import (
        test_cli,
        test_config,
        test_config_validation,
        test_tap,
        test_tap_initialization,
    )
    from tests.unit.test_cli import TestCLI
    from tests.unit.test_config import TestFlextTapOracleWmsSettings
    from tests.unit.test_config_validation import TestConfigValidation
    from tests.unit.test_tap import TestFlextTapOracleWms
    from tests.unit.test_tap_initialization import TestTapInitialization

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "TestCLI": "tests.unit.test_cli",
    "TestConfigValidation": "tests.unit.test_config_validation",
    "TestFlextTapOracleWms": "tests.unit.test_tap",
    "TestFlextTapOracleWmsSettings": "tests.unit.test_config",
    "TestTapInitialization": "tests.unit.test_tap_initialization",
    "test_cli": "tests.unit.test_cli",
    "test_config": "tests.unit.test_config",
    "test_config_validation": "tests.unit.test_config_validation",
    "test_tap": "tests.unit.test_tap",
    "test_tap_initialization": "tests.unit.test_tap_initialization",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

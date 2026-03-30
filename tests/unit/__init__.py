# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Test module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.unit import (
        test_cli as test_cli,
        test_config as test_config,
        test_config_validation as test_config_validation,
        test_tap as test_tap,
        test_tap_initialization as test_tap_initialization,
    )
    from tests.unit.test_cli import TestCLI as TestCLI
    from tests.unit.test_config import (
        TestFlextTapOracleWmsSettings as TestFlextTapOracleWmsSettings,
    )
    from tests.unit.test_config_validation import (
        TestConfigValidation as TestConfigValidation,
    )
    from tests.unit.test_tap import TestFlextTapOracleWms as TestFlextTapOracleWms
    from tests.unit.test_tap_initialization import (
        TestTapInitialization as TestTapInitialization,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestCLI": ["tests.unit.test_cli", "TestCLI"],
    "TestConfigValidation": [
        "tests.unit.test_config_validation",
        "TestConfigValidation",
    ],
    "TestFlextTapOracleWms": ["tests.unit.test_tap", "TestFlextTapOracleWms"],
    "TestFlextTapOracleWmsSettings": [
        "tests.unit.test_config",
        "TestFlextTapOracleWmsSettings",
    ],
    "TestTapInitialization": [
        "tests.unit.test_tap_initialization",
        "TestTapInitialization",
    ],
    "test_cli": ["tests.unit.test_cli", ""],
    "test_config": ["tests.unit.test_config", ""],
    "test_config_validation": ["tests.unit.test_config_validation", ""],
    "test_tap": ["tests.unit.test_tap", ""],
    "test_tap_initialization": ["tests.unit.test_tap_initialization", ""],
}

_EXPORTS: Sequence[str] = [
    "TestCLI",
    "TestConfigValidation",
    "TestFlextTapOracleWms",
    "TestFlextTapOracleWmsSettings",
    "TestTapInitialization",
    "test_cli",
    "test_config",
    "test_config_validation",
    "test_tap",
    "test_tap_initialization",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)

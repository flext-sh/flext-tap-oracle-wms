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

    from tests.unit.test_cli import *
    from tests.unit.test_config import *
    from tests.unit.test_config_validation import *
    from tests.unit.test_tap import *
    from tests.unit.test_tap_initialization import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
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

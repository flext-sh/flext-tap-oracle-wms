# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
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
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_cli": ("TestsFlextTapOracleWmsCli",),
        ".test_config": ("TestsFlextTapOracleWmsConfig",),
        ".test_config_validation": ("TestsFlextTapOracleWmsConfigValidation",),
        ".test_tap": ("TestsFlextTapOracleWmsTap",),
        ".test_tap_initialization": ("TestsFlextTapOracleWmsTapInitialization",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

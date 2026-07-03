# AUTO-GENERATED FILE — Regenerate with: make gen
"""E2e package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_oracle_wms.tests.e2e.test_e2e import (
        TestsFlextTapOracleWmsE2e as TestsFlextTapOracleWmsE2e,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_e2e": ("TestsFlextTapOracleWmsE2e",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

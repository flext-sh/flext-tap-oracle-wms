# AUTO-GENERATED FILE — Regenerate with: make gen
"""Integration package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
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
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_functional": ("TestsFlextTapOracleWmsFunctional",),
        ".test_streams_functional": ("TestsFlextTapOracleWmsStreamsFunctional",),
        ".test_wms": ("TestsFlextTapOracleWmsWms",),
        ".test_wms_connection": ("TestsFlextTapOracleWmsWmsConnection",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Oracle Wms package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports
from flext_tap_oracle_wms.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)

if TYPE_CHECKING:
    from flext_meltano import d as d, e as e, h as h, r as r, s as s, x as x
    from flext_tap_oracle_wms.api import (
        FlextTapOracleWmsService as FlextTapOracleWmsService,
        tap_oracle_wms as tap_oracle_wms,
    )
    from flext_tap_oracle_wms.cli import main as main
    from flext_tap_oracle_wms.constants import (
        FlextTapOracleWmsConstants as FlextTapOracleWmsConstants,
        c as c,
    )
    from flext_tap_oracle_wms.models import (
        FlextTapOracleWmsModels as FlextTapOracleWmsModels,
        m as m,
    )
    from flext_tap_oracle_wms.protocols import (
        FlextTapOracleWmsProtocols as FlextTapOracleWmsProtocols,
        p as p,
    )
    from flext_tap_oracle_wms.tap import FlextTapOracleWms as FlextTapOracleWms
    from flext_tap_oracle_wms.typings import (
        FlextTapOracleWmsTypes as FlextTapOracleWmsTypes,
        t as t,
    )
    from flext_tap_oracle_wms.utilities import (
        FlextTapOracleWmsUtilities as FlextTapOracleWmsUtilities,
        u as u,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        "._settings": ("FlextTapOracleWmsSettings", "settings"),
        ".api": (
            "FlextTapOracleWmsService",
            "tap_oracle_wms",
        ),
        ".cli": ("main",),
        ".constants": (
            "FlextTapOracleWmsConstants",
            "c",
        ),
        ".models": (
            "FlextTapOracleWmsModels",
            "m",
        ),
        ".protocols": (
            "FlextTapOracleWmsProtocols",
            "p",
        ),
        ".tap": ("FlextTapOracleWms",),
        ".typings": (
            "FlextTapOracleWmsTypes",
            "t",
        ),
        ".utilities": (
            "FlextTapOracleWmsUtilities",
            "u",
        ),
        "flext_meltano": (
            "d",
            "e",
            "h",
            "r",
            "s",
            "x",
        ),
    },
)


__all__: tuple[str, ...] = (
    "FlextTapOracleWms",
    "FlextTapOracleWmsConstants",
    "FlextTapOracleWmsModels",
    "FlextTapOracleWmsProtocols",
    "FlextTapOracleWmsService",
    "FlextTapOracleWmsSettings",
    "FlextTapOracleWmsTypes",
    "FlextTapOracleWmsUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "tap_oracle_wms",
    "u",
    "x",
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=__all__,
)

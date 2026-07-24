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
    from flext_meltano import d, e, h, r, s, x

    from ._settings import FlextTapOracleWmsSettings, settings
    from .api import FlextTapOracleWmsService, tap_oracle_wms
    from .cli import main
    from .constants import FlextTapOracleWmsConstants, FlextTapOracleWmsConstants as c
    from .models import FlextTapOracleWmsModels, FlextTapOracleWmsModels as m
    from .protocols import FlextTapOracleWmsProtocols, FlextTapOracleWmsProtocols as p
    from .tap import FlextTapOracleWms
    from .typings import FlextTapOracleWmsTypes, FlextTapOracleWmsTypes as t
    from .utilities import FlextTapOracleWmsUtilities, FlextTapOracleWmsUtilities as u

    _ = (
        c,
        FlextTapOracleWmsConstants,
        t,
        FlextTapOracleWmsTypes,
        p,
        FlextTapOracleWmsProtocols,
        m,
        FlextTapOracleWmsModels,
        u,
        FlextTapOracleWmsUtilities,
        d,
        e,
        h,
        r,
        s,
        x,
        main,
        FlextTapOracleWmsSettings,
        settings,
        FlextTapOracleWmsService,
        tap_oracle_wms,
        FlextTapOracleWms,
    )


_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._settings": ("FlextTapOracleWmsSettings", "settings"),
    ".api": ("FlextTapOracleWmsService", "tap_oracle_wms"),
    ".cli": ("main",),
    ".constants": ("FlextTapOracleWmsConstants", "c"),
    ".models": ("FlextTapOracleWmsModels", "m"),
    ".protocols": ("FlextTapOracleWmsProtocols", "p"),
    ".tap": ("FlextTapOracleWms",),
    ".typings": ("FlextTapOracleWmsTypes", "t"),
    ".utilities": ("FlextTapOracleWmsUtilities", "u"),
    "flext_meltano": ("d", "e", "h", "r", "s", "x"),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_DIRECT_IMPORTS: tuple[str, ...] = (
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
    "build_lazy_import_map",
    "c",
    "d",
    "e",
    "h",
    "install_lazy_exports",
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

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
    from flext_tap_oracle_wms.api import FlextTapOracleWmsService
    from flext_tap_oracle_wms.cli import main
    from flext_tap_oracle_wms.constants import FlextTapOracleWmsConstants, c
    from flext_tap_oracle_wms.models import FlextTapOracleWmsModels, m
    from flext_tap_oracle_wms.protocols import FlextTapOracleWmsProtocols, p
    from flext_tap_oracle_wms.settings import FlextTapOracleWmsSettings
    from flext_tap_oracle_wms.tap import FlextTapOracleWms
    from flext_tap_oracle_wms.typings import FlextTapOracleWmsTypes, t
    from flext_tap_oracle_wms.utilities import FlextTapOracleWmsUtilities, u
_LAZY_IMPORTS = build_lazy_import_map(
    {
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
        ".settings": ("FlextTapOracleWmsSettings",),
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

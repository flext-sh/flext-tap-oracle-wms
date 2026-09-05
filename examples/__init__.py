# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_core import (
        FlextTapOracleWmsConstants,
        FlextTapOracleWmsConstants as c,
        d,
        e,
        h,
        m,
        p,
        r,
        s,
        t,
        u,
        x,
    )

    from .constants import ExamplesFlextTapOracleWmsConstants
    from .models import ExamplesFlextTapOracleWmsModels
    from .protocols import ExamplesFlextTapOracleWmsProtocols
    from .typings import ExamplesFlextTapOracleWmsTypes
    from .utilities import ExamplesFlextTapOracleWmsUtilities
__all__: tuple[str, ...] = (
    "ExamplesFlextTapOracleWmsConstants",
    "ExamplesFlextTapOracleWmsModels",
    "ExamplesFlextTapOracleWmsProtocols",
    "ExamplesFlextTapOracleWmsTypes",
    "ExamplesFlextTapOracleWmsUtilities",
    "FlextTapOracleWmsConstants",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".constants": ("ExamplesFlextTapOracleWmsConstants",),
            ".models": ("ExamplesFlextTapOracleWmsModels",),
            ".protocols": ("ExamplesFlextTapOracleWmsProtocols",),
            ".typings": ("ExamplesFlextTapOracleWmsTypes",),
            ".utilities": ("ExamplesFlextTapOracleWmsUtilities",),
            "flext_core": (
                "FlextTapOracleWmsConstants",
                "c",
                "d",
                "e",
                "h",
                "m",
                "p",
                "r",
                "s",
                "t",
                "u",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

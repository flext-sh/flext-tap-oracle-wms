# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_meltano import s
    from flext_oracle_wms import e

    from flext_core import d, h, r, x
    from flext_tap_oracle_wms import FlextTapOracleWmsConstants

    from .constants import (
        ExamplesFlextTapOracleWmsConstants,
        ExamplesFlextTapOracleWmsConstants as c,
    )
    from .models import (
        ExamplesFlextTapOracleWmsModels,
        ExamplesFlextTapOracleWmsModels as m,
    )
    from .protocols import (
        ExamplesFlextTapOracleWmsProtocols,
        ExamplesFlextTapOracleWmsProtocols as p,
    )
    from .typings import (
        ExamplesFlextTapOracleWmsTypes,
        ExamplesFlextTapOracleWmsTypes as t,
    )
    from .utilities import (
        ExamplesFlextTapOracleWmsUtilities,
        ExamplesFlextTapOracleWmsUtilities as u,
    )
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
            ".constants": ("ExamplesFlextTapOracleWmsConstants", "c"),
            ".models": ("ExamplesFlextTapOracleWmsModels", "m"),
            ".protocols": ("ExamplesFlextTapOracleWmsProtocols", "p"),
            ".typings": ("ExamplesFlextTapOracleWmsTypes", "t"),
            ".utilities": ("ExamplesFlextTapOracleWmsUtilities", "u"),
            "flext_core": ("d", "h", "r", "x"),
            "flext_meltano": ("s",),
            "flext_oracle_wms": ("e",),
            "flext_tap_oracle_wms": ("FlextTapOracleWmsConstants",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

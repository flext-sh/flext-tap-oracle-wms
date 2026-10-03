# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_meltano import s
    from flext_oracle_wms import e
    from flext_tap_oracle_wms import c, d, h, m, p, r, t, u, x

    from examples.constants import ExamplesFlextTapOracleWmsConstants
    from examples.models import ExamplesFlextTapOracleWmsModels
    from examples.protocols import ExamplesFlextTapOracleWmsProtocols
    from examples.typings import ExamplesFlextTapOracleWmsTypes
    from examples.utilities import ExamplesFlextTapOracleWmsUtilities


__all__: tuple[str, ...] = (
    "ExamplesFlextTapOracleWmsConstants",
    "ExamplesFlextTapOracleWmsModels",
    "ExamplesFlextTapOracleWmsProtocols",
    "ExamplesFlextTapOracleWmsTypes",
    "ExamplesFlextTapOracleWmsUtilities",
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
            "flext_meltano": ("s",),
            "flext_oracle_wms": ("e",),
            "flext_tap_oracle_wms": ("c", "d", "h", "m", "p", "r", "t", "u", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Oracle Wms package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports
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
    from flext_meltano import d, h, r, s, x
    from flext_oracle_wms import e

    from flext_tap_oracle_wms._config import FlextTapOracleWmsConfig, config
    from flext_tap_oracle_wms._settings import FlextTapOracleWmsSettings, settings
    from flext_tap_oracle_wms.api import FlextTapOracleWmsService, tap_oracle_wms
    from flext_tap_oracle_wms.cli import main
    from flext_tap_oracle_wms.constants import FlextTapOracleWmsConstants, c
    from flext_tap_oracle_wms.models import FlextTapOracleWmsModels, m
    from flext_tap_oracle_wms.protocols import FlextTapOracleWmsProtocols, p
    from flext_tap_oracle_wms.typings import FlextTapOracleWmsTypes, t
    from flext_tap_oracle_wms.utilities import FlextTapOracleWmsUtilities, u


__all__: tuple[str, ...] = (
    "FlextTapOracleWmsConfig",
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
    "config",
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

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._config": ("FlextTapOracleWmsConfig", "config"),
            "._settings": ("FlextTapOracleWmsSettings", "settings"),
            ".api": ("FlextTapOracleWmsService", "tap_oracle_wms"),
            ".cli": ("main",),
            ".constants": ("FlextTapOracleWmsConstants", "c"),
            ".models": ("FlextTapOracleWmsModels", "m"),
            ".protocols": ("FlextTapOracleWmsProtocols", "p"),
            ".typings": ("FlextTapOracleWmsTypes", "t"),
            ".utilities": ("FlextTapOracleWmsUtilities", "u"),
            "flext_meltano": ("d", "h", "r", "s", "x"),
            "flext_oracle_wms": ("e",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

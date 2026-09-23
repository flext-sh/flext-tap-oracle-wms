# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Oracle Wms package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

from .__version__ import (
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
)

if TYPE_CHECKING:
    from flext_meltano import (
        cli,
        core,
        d,
        h,
        lazy_attribute,
        meltano,
        r,
        s,
        services,
        x,
    )
    from flext_oracle_wms import api, e, oracle_wms, web

    from ._config import FlextTapOracleWmsConfig, config
    from ._settings import FlextTapOracleWmsSettings, settings
    from .api import FlextTapOracleWmsService, tap_oracle_wms
    from .cli import main
    from .constants import FlextTapOracleWmsConstants, c
    from .models import FlextTapOracleWmsModels, m
    from .protocols import FlextTapOracleWmsProtocols, p
    from .typings import FlextTapOracleWmsTypes, t
    from .utilities import FlextTapOracleWmsUtilities, u


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
    "api",
    "c",
    "cli",
    "config",
    "core",
    "d",
    "e",
    "h",
    "lazy_attribute",
    "m",
    "main",
    "meltano",
    "oracle_wms",
    "p",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "tap_oracle_wms",
    "u",
    "web",
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
            "flext_meltano": (
                "cli",
                "core",
                "d",
                "h",
                "lazy_attribute",
                "meltano",
                "r",
                "s",
                "services",
                "x",
            ),
            "flext_oracle_wms": ("api", "e", "oracle_wms", "web"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

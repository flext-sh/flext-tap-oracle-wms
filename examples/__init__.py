# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_meltano import s
    from flext_oracle_wms import e

    from examples.constants import ExamplesFlextTapOracleWmsConstants
    from examples.models import ExamplesFlextTapOracleWmsModels
    from examples.protocols import ExamplesFlextTapOracleWmsProtocols
    from examples.typings import ExamplesFlextTapOracleWmsTypes
    from examples.utilities import ExamplesFlextTapOracleWmsUtilities, u
    from flext_tap_oracle_wms import (
        api,
        build_lazy_import_map,
        c,
        cleanup_submodule_namespace,
        cli,
        config,
        core,
        d,
        h,
        install_lazy_exports,
        lazy,
        lazy_getattr,
        lazy_member,
        m,
        main,
        meltano,
        merge_lazy_imports,
        normalize_lazy_imports,
        oracle_wms,
        p,
        r,
        resolve_lazy_members,
        settings,
        t,
        tap_oracle_wms,
        web,
        x,
    )


__all__: tuple[str, ...] = (
    "ExamplesFlextTapOracleWmsConstants",
    "ExamplesFlextTapOracleWmsModels",
    "ExamplesFlextTapOracleWmsProtocols",
    "ExamplesFlextTapOracleWmsTypes",
    "ExamplesFlextTapOracleWmsUtilities",
    "api",
    "build_lazy_import_map",
    "c",
    "cleanup_submodule_namespace",
    "cli",
    "config",
    "core",
    "d",
    "e",
    "h",
    "install_lazy_exports",
    "lazy",
    "lazy_getattr",
    "lazy_member",
    "m",
    "main",
    "meltano",
    "merge_lazy_imports",
    "normalize_lazy_imports",
    "oracle_wms",
    "p",
    "r",
    "resolve_lazy_members",
    "s",
    "settings",
    "t",
    "tap_oracle_wms",
    "u",
    "web",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "ExamplesFlextTapOracleWmsConstants": ".constants",
        "ExamplesFlextTapOracleWmsModels": ".models",
        "ExamplesFlextTapOracleWmsProtocols": ".protocols",
        "ExamplesFlextTapOracleWmsTypes": ".typings",
        "ExamplesFlextTapOracleWmsUtilities": ".utilities",
        "api": "flext_tap_oracle_wms",
        "build_lazy_import_map": "flext_tap_oracle_wms",
        "c": "flext_tap_oracle_wms",
        "cleanup_submodule_namespace": "flext_tap_oracle_wms",
        "cli": "flext_tap_oracle_wms",
        "config": "flext_tap_oracle_wms",
        "core": "flext_tap_oracle_wms",
        "d": "flext_tap_oracle_wms",
        "e": "flext_oracle_wms",
        "h": "flext_tap_oracle_wms",
        "install_lazy_exports": "flext_tap_oracle_wms",
        "lazy": "flext_tap_oracle_wms",
        "lazy_getattr": "flext_tap_oracle_wms",
        "lazy_member": "flext_tap_oracle_wms",
        "m": "flext_tap_oracle_wms",
        "main": "flext_tap_oracle_wms",
        "meltano": "flext_tap_oracle_wms",
        "merge_lazy_imports": "flext_tap_oracle_wms",
        "normalize_lazy_imports": "flext_tap_oracle_wms",
        "oracle_wms": "flext_tap_oracle_wms",
        "p": "flext_tap_oracle_wms",
        "r": "flext_tap_oracle_wms",
        "resolve_lazy_members": "flext_tap_oracle_wms",
        "s": "flext_meltano",
        "settings": "flext_tap_oracle_wms",
        "t": "flext_tap_oracle_wms",
        "tap_oracle_wms": "flext_tap_oracle_wms",
        "u": ".utilities",
        "web": "flext_tap_oracle_wms",
        "x": "flext_tap_oracle_wms",
    }),
    public_exports=__all__,
)

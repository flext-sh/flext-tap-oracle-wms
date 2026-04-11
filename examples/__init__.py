# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_cli.base import s

    from flext_core.decorators import d
    from flext_core.exceptions import e
    from flext_core.handlers import h
    from flext_core.mixins import x
    from flext_core.result import r
    from flext_tap_oracle_wms.constants import c
    from flext_tap_oracle_wms.models import m
    from flext_tap_oracle_wms.protocols import p
    from flext_tap_oracle_wms.typings import t
    from flext_tap_oracle_wms.utilities import u
_LAZY_IMPORTS = build_lazy_import_map(
    {
        "flext_cli.base": ("s",),
        "flext_core.decorators": ("d",),
        "flext_core.exceptions": ("e",),
        "flext_core.handlers": ("h",),
        "flext_core.mixins": ("x",),
        "flext_core.result": ("r",),
        "flext_tap_oracle_wms.constants": ("c",),
        "flext_tap_oracle_wms.models": ("m",),
        "flext_tap_oracle_wms.protocols": ("p",),
        "flext_tap_oracle_wms.typings": ("t",),
        "flext_tap_oracle_wms.utilities": ("u",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__ = [
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
]

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Oracle Wms package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports
from flext_tap_oracle_wms.__version__ import *

if _t.TYPE_CHECKING:
    from flext_core.decorators import d
    from flext_core.exceptions import e
    from flext_core.handlers import h
    from flext_core.mixins import x
    from flext_core.result import r
    from flext_tap_oracle_wms.api import (
        FlextTapOracleWmsService,
        FlextTapOracleWmsService as s,
    )
    from flext_tap_oracle_wms.cli import FlextTapOracleWmsCli, main
    from flext_tap_oracle_wms.constants import (
        FlextTapOracleWmsConstants,
        FlextTapOracleWmsConstants as c,
    )
    from flext_tap_oracle_wms.errors import (
        FlextTapOracleWmsConfigurationError,
        FlextTapOracleWmsConnectionError,
        FlextTapOracleWmsError,
        FlextTapOracleWmsValidationError,
    )
    from flext_tap_oracle_wms.models import (
        FlextTapOracleWmsModels,
        FlextTapOracleWmsModels as m,
    )
    from flext_tap_oracle_wms.protocols import (
        FlextTapOracleWmsProtocols,
        FlextTapOracleWmsProtocols as p,
    )
    from flext_tap_oracle_wms.settings import FlextTapOracleWmsSettings
    from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
    from flext_tap_oracle_wms.tap import FlextTapOracleWms, FlextTapOracleWmsPlugin
    from flext_tap_oracle_wms.typings import (
        FlextTapOracleWmsTypes,
        FlextTapOracleWmsTypes as t,
    )
    from flext_tap_oracle_wms.utilities import (
        FlextTapOracleWmsUtilities,
        FlextTapOracleWmsUtilities as u,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".__version__": (
            "__author__",
            "__author_email__",
            "__description__",
            "__license__",
            "__title__",
            "__url__",
            "__version__",
            "__version_info__",
        ),
        ".api": ("FlextTapOracleWmsService",),
        ".cli": (
            "FlextTapOracleWmsCli",
            "main",
        ),
        ".constants": ("FlextTapOracleWmsConstants",),
        ".errors": (
            "FlextTapOracleWmsConfigurationError",
            "FlextTapOracleWmsConnectionError",
            "FlextTapOracleWmsError",
            "FlextTapOracleWmsValidationError",
        ),
        ".models": ("FlextTapOracleWmsModels",),
        ".protocols": ("FlextTapOracleWmsProtocols",),
        ".settings": ("FlextTapOracleWmsSettings",),
        ".streams": ("FlextTapOracleWmsStream",),
        ".tap": (
            "FlextTapOracleWms",
            "FlextTapOracleWmsPlugin",
        ),
        ".typings": ("FlextTapOracleWmsTypes",),
        ".utilities": ("FlextTapOracleWmsUtilities",),
        "flext_core.decorators": ("d",),
        "flext_core.exceptions": ("e",),
        "flext_core.handlers": ("h",),
        "flext_core.mixins": ("x",),
        "flext_core.result": ("r",),
    },
    alias_groups={
        ".api": (("s", "FlextTapOracleWmsService"),),
        ".constants": (("c", "FlextTapOracleWmsConstants"),),
        ".models": (("m", "FlextTapOracleWmsModels"),),
        ".protocols": (("p", "FlextTapOracleWmsProtocols"),),
        ".typings": (("t", "FlextTapOracleWmsTypes"),),
        ".utilities": (("u", "FlextTapOracleWmsUtilities"),),
    },
)

__all__ = [
    "FlextTapOracleWms",
    "FlextTapOracleWmsCli",
    "FlextTapOracleWmsConfigurationError",
    "FlextTapOracleWmsConnectionError",
    "FlextTapOracleWmsConstants",
    "FlextTapOracleWmsError",
    "FlextTapOracleWmsModels",
    "FlextTapOracleWmsPlugin",
    "FlextTapOracleWmsProtocols",
    "FlextTapOracleWmsService",
    "FlextTapOracleWmsSettings",
    "FlextTapOracleWmsStream",
    "FlextTapOracleWmsTypes",
    "FlextTapOracleWmsUtilities",
    "FlextTapOracleWmsValidationError",
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
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

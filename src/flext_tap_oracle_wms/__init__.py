# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Oracle Wms package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports
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
from flext_tap_oracle_wms._exports import FLEXT_TAP_ORACLE_WMS_LAZY_IMPORTS

if TYPE_CHECKING:
    from flext_meltano import d as d, e as e, h as h, r as r, s as s, x as x
    from flext_tap_oracle_wms.api import (
        FlextTapOracleWmsService as FlextTapOracleWmsService,
        tap_oracle_wms as tap_oracle_wms,
    )
    from flext_tap_oracle_wms.cli import main as main
    from flext_tap_oracle_wms.constants import (
        FlextTapOracleWmsConstants as FlextTapOracleWmsConstants,
        c as c,
    )
    from flext_tap_oracle_wms.models import (
        FlextTapOracleWmsModels as FlextTapOracleWmsModels,
        m as m,
    )
    from flext_tap_oracle_wms.protocols import (
        FlextTapOracleWmsProtocols as FlextTapOracleWmsProtocols,
        p as p,
    )
    from flext_tap_oracle_wms.settings import (
        FlextTapOracleWmsSettings as FlextTapOracleWmsSettings,
    )
    from flext_tap_oracle_wms.tap import FlextTapOracleWms as FlextTapOracleWms
    from flext_tap_oracle_wms.typings import (
        FlextTapOracleWmsTypes as FlextTapOracleWmsTypes,
        t as t,
    )
    from flext_tap_oracle_wms.utilities import (
        FlextTapOracleWmsUtilities as FlextTapOracleWmsUtilities,
        u as u,
    )


_LAZY_IMPORTS = FLEXT_TAP_ORACLE_WMS_LAZY_IMPORTS


_EAGER_EXPORTS = (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)


_PUBLIC_EXPORTS: tuple[str, ...] = (
    "FlextTapOracleWms",
    "FlextTapOracleWmsConstants",
    "FlextTapOracleWmsModels",
    "FlextTapOracleWmsProtocols",
    "FlextTapOracleWmsService",
    "FlextTapOracleWmsSettings",
    "FlextTapOracleWmsTypes",
    "FlextTapOracleWmsUtilities",
    "tap_oracle_wms",
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
    public_exports=_PUBLIC_EXPORTS,
)

# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_meltano import d, e, h, r, s, x

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
    from flext_tap_oracle_wms.cli import main
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
    from flext_tap_oracle_wms.tap import (
        FlextTapOracleWms,
        FlextTapOracleWmsPlugin,
        logger,
    )
    from flext_tap_oracle_wms.typings import (
        FlextTapOracleWmsTypes,
        FlextTapOracleWmsTypes as t,
    )
    from flext_tap_oracle_wms.utilities import (
        FlextTapOracleWmsUtilities,
        FlextTapOracleWmsUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextTapOracleWms": ["flext_tap_oracle_wms.tap", "FlextTapOracleWms"],
    "FlextTapOracleWmsConfigurationError": [
        "flext_tap_oracle_wms.errors",
        "FlextTapOracleWmsConfigurationError",
    ],
    "FlextTapOracleWmsConnectionError": [
        "flext_tap_oracle_wms.errors",
        "FlextTapOracleWmsConnectionError",
    ],
    "FlextTapOracleWmsConstants": [
        "flext_tap_oracle_wms.constants",
        "FlextTapOracleWmsConstants",
    ],
    "FlextTapOracleWmsError": ["flext_tap_oracle_wms.errors", "FlextTapOracleWmsError"],
    "FlextTapOracleWmsModels": [
        "flext_tap_oracle_wms.models",
        "FlextTapOracleWmsModels",
    ],
    "FlextTapOracleWmsPlugin": ["flext_tap_oracle_wms.tap", "FlextTapOracleWmsPlugin"],
    "FlextTapOracleWmsProtocols": [
        "flext_tap_oracle_wms.protocols",
        "FlextTapOracleWmsProtocols",
    ],
    "FlextTapOracleWmsSettings": [
        "flext_tap_oracle_wms.settings",
        "FlextTapOracleWmsSettings",
    ],
    "FlextTapOracleWmsStream": [
        "flext_tap_oracle_wms.streams",
        "FlextTapOracleWmsStream",
    ],
    "FlextTapOracleWmsTypes": [
        "flext_tap_oracle_wms.typings",
        "FlextTapOracleWmsTypes",
    ],
    "FlextTapOracleWmsUtilities": [
        "flext_tap_oracle_wms.utilities",
        "FlextTapOracleWmsUtilities",
    ],
    "FlextTapOracleWmsValidationError": [
        "flext_tap_oracle_wms.errors",
        "FlextTapOracleWmsValidationError",
    ],
    "__author__": ["flext_tap_oracle_wms.__version__", "__author__"],
    "__author_email__": ["flext_tap_oracle_wms.__version__", "__author_email__"],
    "__description__": ["flext_tap_oracle_wms.__version__", "__description__"],
    "__license__": ["flext_tap_oracle_wms.__version__", "__license__"],
    "__title__": ["flext_tap_oracle_wms.__version__", "__title__"],
    "__url__": ["flext_tap_oracle_wms.__version__", "__url__"],
    "__version__": ["flext_tap_oracle_wms.__version__", "__version__"],
    "__version_info__": ["flext_tap_oracle_wms.__version__", "__version_info__"],
    "c": ["flext_tap_oracle_wms.constants", "FlextTapOracleWmsConstants"],
    "d": ["flext_meltano", "d"],
    "e": ["flext_meltano", "e"],
    "h": ["flext_meltano", "h"],
    "logger": ["flext_tap_oracle_wms.tap", "logger"],
    "m": ["flext_tap_oracle_wms.models", "FlextTapOracleWmsModels"],
    "main": ["flext_tap_oracle_wms.cli", "main"],
    "p": ["flext_tap_oracle_wms.protocols", "FlextTapOracleWmsProtocols"],
    "r": ["flext_meltano", "r"],
    "s": ["flext_meltano", "s"],
    "t": ["flext_tap_oracle_wms.typings", "FlextTapOracleWmsTypes"],
    "u": ["flext_tap_oracle_wms.utilities", "FlextTapOracleWmsUtilities"],
    "x": ["flext_meltano", "x"],
}

__all__ = [
    "FlextTapOracleWms",
    "FlextTapOracleWmsConfigurationError",
    "FlextTapOracleWmsConnectionError",
    "FlextTapOracleWmsConstants",
    "FlextTapOracleWmsError",
    "FlextTapOracleWmsModels",
    "FlextTapOracleWmsPlugin",
    "FlextTapOracleWmsProtocols",
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
    "logger",
    "m",
    "main",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

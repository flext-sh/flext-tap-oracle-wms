# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_tap_oracle_wms.__version__ import (
        __all__,
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
    from flext_tap_oracle_wms.constants import c
    from flext_tap_oracle_wms.exceptions import (
        FlextTapOracleWmsConfigurationError,
        FlextTapOracleWmsConnectionError,
        FlextTapOracleWmsError,
        FlextTapOracleWmsValidationError,
    )
    from flext_tap_oracle_wms.models import FlextTapOracleWmsModels, m
    from flext_tap_oracle_wms.protocols import FlextTapOracleWmsProtocols, p
    from flext_tap_oracle_wms.settings import (
        FlextTapOracleWmsConstants,
        FlextTapOracleWmsSettings,
    )
    from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
    from flext_tap_oracle_wms.tap import (
        FlextTapOracleWms,
        FlextTapOracleWmsPlugin,
        logger,
    )
    from flext_tap_oracle_wms.typings import FlextTapOracleWmsTypes, t
    from flext_tap_oracle_wms.utilities import (
        FlextTapOracleWmsUtilities,
        FlextTapOracleWmsUtilities as u,
    )
    from flext_tap_oracle_wms.version import VERSION, FlextTapOracleWmsVersion

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextTapOracleWms": ("flext_tap_oracle_wms.tap", "FlextTapOracleWms"),
    "FlextTapOracleWmsConfigurationError": (
        "flext_tap_oracle_wms.exceptions",
        "FlextTapOracleWmsConfigurationError",
    ),
    "FlextTapOracleWmsConnectionError": (
        "flext_tap_oracle_wms.exceptions",
        "FlextTapOracleWmsConnectionError",
    ),
    "FlextTapOracleWmsConstants": (
        "flext_tap_oracle_wms.settings",
        "FlextTapOracleWmsConstants",
    ),
    "FlextTapOracleWmsError": (
        "flext_tap_oracle_wms.exceptions",
        "FlextTapOracleWmsError",
    ),
    "FlextTapOracleWmsModels": (
        "flext_tap_oracle_wms.models",
        "FlextTapOracleWmsModels",
    ),
    "FlextTapOracleWmsPlugin": ("flext_tap_oracle_wms.tap", "FlextTapOracleWmsPlugin"),
    "FlextTapOracleWmsProtocols": (
        "flext_tap_oracle_wms.protocols",
        "FlextTapOracleWmsProtocols",
    ),
    "FlextTapOracleWmsSettings": (
        "flext_tap_oracle_wms.settings",
        "FlextTapOracleWmsSettings",
    ),
    "FlextTapOracleWmsStream": (
        "flext_tap_oracle_wms.streams",
        "FlextTapOracleWmsStream",
    ),
    "FlextTapOracleWmsTypes": (
        "flext_tap_oracle_wms.typings",
        "FlextTapOracleWmsTypes",
    ),
    "FlextTapOracleWmsUtilities": (
        "flext_tap_oracle_wms.utilities",
        "FlextTapOracleWmsUtilities",
    ),
    "FlextTapOracleWmsValidationError": (
        "flext_tap_oracle_wms.exceptions",
        "FlextTapOracleWmsValidationError",
    ),
    "FlextTapOracleWmsVersion": (
        "flext_tap_oracle_wms.version",
        "FlextTapOracleWmsVersion",
    ),
    "VERSION": ("flext_tap_oracle_wms.version", "VERSION"),
    "__all__": ("flext_tap_oracle_wms.__version__", "__all__"),
    "__author__": ("flext_tap_oracle_wms.__version__", "__author__"),
    "__author_email__": ("flext_tap_oracle_wms.__version__", "__author_email__"),
    "__description__": ("flext_tap_oracle_wms.__version__", "__description__"),
    "__license__": ("flext_tap_oracle_wms.__version__", "__license__"),
    "__title__": ("flext_tap_oracle_wms.__version__", "__title__"),
    "__url__": ("flext_tap_oracle_wms.__version__", "__url__"),
    "__version__": ("flext_tap_oracle_wms.__version__", "__version__"),
    "__version_info__": ("flext_tap_oracle_wms.__version__", "__version_info__"),
    "c": ("flext_tap_oracle_wms.constants", "c"),
    "logger": ("flext_tap_oracle_wms.tap", "logger"),
    "m": ("flext_tap_oracle_wms.models", "m"),
    "main": ("flext_tap_oracle_wms.cli", "main"),
    "p": ("flext_tap_oracle_wms.protocols", "p"),
    "t": ("flext_tap_oracle_wms.typings", "t"),
    "u": ("flext_tap_oracle_wms.utilities", "FlextTapOracleWmsUtilities"),
}

__all__ = [
    "VERSION",
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
    "FlextTapOracleWmsVersion",
    "__all__",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "logger",
    "m",
    "main",
    "p",
    "t",
    "u",
]


def __getattr__(name: str) -> t.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

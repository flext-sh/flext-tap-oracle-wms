"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core._utilities.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextLogger, FlextResult, t
    from flext_meltano import (
        FlextMeltanoBridge,
        FlextMeltanoService,
        FlextMeltanoSettings,
    )

    from flext_tap_oracle_wms.cli import main
    from flext_tap_oracle_wms.constants import (
        FlextTapOracleWmsConstants,
        FlextTapOracleWmsConstants as c,
    )
    from flext_tap_oracle_wms.exceptions import (
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
    from flext_tap_oracle_wms.typings import FlextTapOracleWmsTypes
    from flext_tap_oracle_wms.utilities import FlextTapOracleWmsUtilities, u
    from flext_tap_oracle_wms.version import (
        VERSION,
        VERSION as PROJECT_VERSION,
        FlextTapOracleWmsVersion,
        __version__,
        __version_info__,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextLogger": ("flext_core", "FlextLogger"),
    "FlextMeltanoBridge": ("flext_meltano", "FlextMeltanoBridge"),
    "FlextMeltanoService": ("flext_meltano", "FlextMeltanoService"),
    "FlextMeltanoSettings": ("flext_meltano", "FlextMeltanoSettings"),
    "FlextResult": ("flext_core", "FlextResult"),
    "FlextTapOracleWms": ("flext_tap_oracle_wms.tap", "FlextTapOracleWms"),
    "FlextTapOracleWmsConfigurationError": ("flext_tap_oracle_wms.exceptions", "FlextTapOracleWmsConfigurationError"),
    "FlextTapOracleWmsConnectionError": ("flext_tap_oracle_wms.exceptions", "FlextTapOracleWmsConnectionError"),
    "FlextTapOracleWmsConstants": ("flext_tap_oracle_wms.constants", "FlextTapOracleWmsConstants"),
    "FlextTapOracleWmsError": ("flext_tap_oracle_wms.exceptions", "FlextTapOracleWmsError"),
    "FlextTapOracleWmsModels": ("flext_tap_oracle_wms.models", "FlextTapOracleWmsModels"),
    "FlextTapOracleWmsPlugin": ("flext_tap_oracle_wms.tap", "FlextTapOracleWmsPlugin"),
    "FlextTapOracleWmsProtocols": ("flext_tap_oracle_wms.protocols", "FlextTapOracleWmsProtocols"),
    "FlextTapOracleWmsSettings": ("flext_tap_oracle_wms.settings", "FlextTapOracleWmsSettings"),
    "FlextTapOracleWmsStream": ("flext_tap_oracle_wms.streams", "FlextTapOracleWmsStream"),
    "FlextTapOracleWmsTypes": ("flext_tap_oracle_wms.typings", "FlextTapOracleWmsTypes"),
    "FlextTapOracleWmsUtilities": ("flext_tap_oracle_wms.utilities", "FlextTapOracleWmsUtilities"),
    "FlextTapOracleWmsValidationError": ("flext_tap_oracle_wms.exceptions", "FlextTapOracleWmsValidationError"),
    "FlextTapOracleWmsVersion": ("flext_tap_oracle_wms.version", "FlextTapOracleWmsVersion"),
    "PROJECT_VERSION": ("flext_tap_oracle_wms.version", "VERSION"),
    "VERSION": ("flext_tap_oracle_wms.version", "VERSION"),
    "__version__": ("flext_tap_oracle_wms.version", "__version__"),
    "__version_info__": ("flext_tap_oracle_wms.version", "__version_info__"),
    "c": ("flext_tap_oracle_wms.constants", "FlextTapOracleWmsConstants"),
    "m": ("flext_tap_oracle_wms.models", "FlextTapOracleWmsModels"),
    "main": ("flext_tap_oracle_wms.cli", "main"),
    "p": ("flext_tap_oracle_wms.protocols", "FlextTapOracleWmsProtocols"),
    "t": ("flext_core", "t"),
    "u": ("flext_tap_oracle_wms.utilities", "u"),
}

__all__ = [
    "PROJECT_VERSION",
    "VERSION",
    "FlextLogger",
    "FlextMeltanoBridge",
    "FlextMeltanoService",
    "FlextMeltanoSettings",
    "FlextResult",
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
    "__version__",
    "__version_info__",
    "c",
    "m",
    "main",
    "p",
    "t",
    "u",
]


def __getattr__(name: str) -> Any:  # noqa: ANN401
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

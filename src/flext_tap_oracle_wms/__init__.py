"""FLEXT Tap Oracle WMS - Oracle Warehouse Management System Data Extraction with simplified imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.7.0 - Tap Oracle WMS with simplified public API:
- All common imports available from root: from flext_tap_oracle_wms import TapOracleWMS
- Built on flext-core foundation for robust Oracle WMS data extraction
- Deprecation warnings for internal imports
"""

from __future__ import annotations

import contextlib
import importlib.metadata
import warnings

# Foundation patterns - ALWAYS from flext-core
from flext_core import (
    BaseConfig as WMSBaseConfig,  # Configuration base
    DomainBaseModel as BaseModel,  # Base for WMS models
    DomainError as WMSError,  # WMS-specific errors
    ServiceResult,  # WMS operation results
    ValidationError,  # Validation errors
)

try:
    __version__ = importlib.metadata.version("flext-tap-oracle-wms")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.7.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())


class FlextTapOracleWmsDeprecationWarning(DeprecationWarning):
    """Custom deprecation warning for FLEXT TAP ORACLE WMS import changes."""


def _show_deprecation_warning(old_import: str, new_import: str) -> None:
    """Show deprecation warning for import paths."""
    message_parts = [
        f"⚠️  DEPRECATED IMPORT: {old_import}",
        f"✅ USE INSTEAD: {new_import}",
        "🔗 This will be removed in version 1.0.0",
        "📖 See FLEXT TAP ORACLE WMS docs for migration guide",
    ]
    warnings.warn(
        "\n".join(message_parts),
        FlextTapOracleWmsDeprecationWarning,
        stacklevel=3,
    )


# ================================
# SIMPLIFIED PUBLIC API EXPORTS
# ================================

# Foundation patterns - imported at top of file

# Singer Tap exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.tap import TapOracleWMS

# WMS Client exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.client import (
        WMSAuthenticator,
        WMSClient,
    )

# WMS Streams exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.streams import (
        InventoryStream,
        LocationsStream,
        ReceiptsStream,
        ShipmentsStream,
    )

# WMS Discovery exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.discovery import (
        WMSEntityDiscovery,
        WMSSchemaGenerator,
    )

# ================================
# PUBLIC API EXPORTS
# ================================

__all__ = [
    "BaseModel",  # from flext_tap_oracle_wms import BaseModel
    # Deprecation utilities
    "FlextTapOracleWmsDeprecationWarning",
    # WMS Streams (simplified access)
    "InventoryStream",  # from flext_tap_oracle_wms import InventoryStream
    "LocationsStream",  # from flext_tap_oracle_wms import LocationsStream
    "ReceiptsStream",  # from flext_tap_oracle_wms import ReceiptsStream
    "ServiceResult",  # from flext_tap_oracle_wms import ServiceResult
    "ShipmentsStream",  # from flext_tap_oracle_wms import ShipmentsStream
    # Main Singer Tap (simplified access)
    "TapOracleWMS",  # from flext_tap_oracle_wms import TapOracleWMS
    "ValidationError",  # from flext_tap_oracle_wms import ValidationError
    # WMS Authentication (simplified access)
    "WMSAuthenticator",  # from flext_tap_oracle_wms import WMSAuthenticator
    # Core Patterns (from flext-core)
    "WMSBaseConfig",  # from flext_tap_oracle_wms import WMSBaseConfig
    # WMS Client (simplified access)
    "WMSClient",  # from flext_tap_oracle_wms import WMSClient
    # WMS Discovery (simplified access)
    "WMSEntityDiscovery",  # from flext_tap_oracle_wms import WMSEntityDiscovery
    "WMSError",  # from flext_tap_oracle_wms import WMSError
    "WMSSchemaGenerator",  # from flext_tap_oracle_wms import WMSSchemaGenerator
    # Version
    "__version__",
    "__version_info__",
]

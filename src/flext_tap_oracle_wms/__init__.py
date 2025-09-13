"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

import importlib.metadata

from flext_core import FlextLogger, FlextModels, FlextResult, FlextTypes
from flext_meltano import FlextMeltanoBridge, FlextMeltanoConfig, FlextMeltanoTapService

from flext_tap_oracle_wms.models import (
    CatalogStream,
    OracleWMSEntityModel,
    StreamMetadata,
    StreamSchema,
)
from flext_tap_oracle_wms.tap_client import FlextTapOracleWMS, FlextTapOracleWMSPlugin
from flext_tap_oracle_wms.tap_config import (
    FlextTapOracleWMSConfig,
    FlextTapOracleWMSConstants,
)
from flext_tap_oracle_wms.tap_exceptions import (
    FlextTapOracleWMSConnectionError,
    FlextTapOracleWMSError,
    FlextTapOracleWMSValidationError,
)
from flext_tap_oracle_wms.tap_streams import FlextTapOracleWMSStream

try:
    __version__ = importlib.metadata.version("flext-tap-oracle-wms")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

__all__: FlextTypes.Core.StringList = [
    # Models
    "CatalogStream",
    # FLEXT ecosystem integration
    "FlextLogger",
    # Meltano integration
    "FlextMeltanoBridge",
    "FlextMeltanoConfig",
    "FlextMeltanoTapService",
    "FlextModels",
    "FlextResult",
    # Core tap functionality
    "FlextTapOracleWMS",
    # Configuration
    "FlextTapOracleWMSConfig",
    # Exceptions
    "FlextTapOracleWMSConnectionError",
    "FlextTapOracleWMSConstants",
    "FlextTapOracleWMSError",
    "FlextTapOracleWMSPlugin",
    "FlextTapOracleWMSStream",
    "FlextTapOracleWMSValidationError",
    "FlextTypes",
    "OracleWMSEntityModel",
    "StreamMetadata",
    "StreamSchema",
    # Version info
    "__version__",
    "__version_info__",
]

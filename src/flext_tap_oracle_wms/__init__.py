"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

import importlib.metadata

from flext_core import FlextLogger, FlextModels, FlextResult, FlextTypes
from flext_meltano import FlextMeltanoBridge, FlextMeltanoConfig, FlextMeltanoService
from flext_tap_oracle_wms.cli import main
from flext_tap_oracle_wms.client import FlextTapOracleWMS, FlextTapOracleWMSPlugin
from flext_tap_oracle_wms.config import (
    FlextTapOracleWMSConfig,
    FlextTapOracleWMSConstants,
)
from flext_tap_oracle_wms.exceptions import (
    FlextTapOracleWMSConfigurationError,
    FlextTapOracleWMSConnectionError,
    FlextTapOracleWMSError,
    FlextTapOracleWMSValidationError,
)
from flext_tap_oracle_wms.models import (
    CatalogStream,
    OracleWMSEntityModel,
    StreamMetadata,
    StreamSchema,
)
from flext_tap_oracle_wms.streams import FlextTapOracleWMSStream

try:
    __version__ = importlib.metadata.version("flext-tap-oracle-wms")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

__all__: FlextTypes.Core.StringList = [
    "CatalogStream",
    "FlextLogger",
    "FlextMeltanoBridge",
    "FlextMeltanoConfig",
    "FlextMeltanoService",
    "FlextModels",
    "FlextResult",
    "FlextTapOracleWMS",
    "FlextTapOracleWMSConfig",
    "FlextTapOracleWMSConfigurationError",
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
    "__version__",
    "__version_info__",
    "main",
]

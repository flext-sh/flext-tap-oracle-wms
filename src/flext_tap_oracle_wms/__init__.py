"""FLEXT Tap Oracle WMS - Singer tap for Oracle WMS data extraction.

Simple, clean implementation following FLEXT patterns.
Uses flext-oracle-wms for all Oracle WMS operations.
"""

from __future__ import annotations

import importlib.metadata

from flext_core import FlextResult, FlextValueObject, get_logger

from flext_tap_oracle_wms.config import FlextTapOracleWMSConfig
from flext_tap_oracle_wms.exceptions import (
    FlextTapOracleWMSAuthenticationError,
    FlextTapOracleWMSConfigurationError,
    FlextTapOracleWMSConnectionError,
    FlextTapOracleWMSDataValidationError,
    FlextTapOracleWMSDiscoveryError,
    FlextTapOracleWMSError,
    FlextTapOracleWMSPaginationError,
    FlextTapOracleWMSRateLimitError,
    FlextTapOracleWMSRetryableError,
    FlextTapOracleWMSStreamError,
)
from flext_tap_oracle_wms.streams import FlextTapOracleWMSStream
from flext_tap_oracle_wms.tap import FlextTapOracleWMS

# Version handling
try:
    __version__ = importlib.metadata.version("flext-tap-oracle-wms")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

__all__ = [
    # Re-exports from flext-core
    "FlextResult",
    "FlextTapOracleWMS",
    "FlextTapOracleWMSAuthenticationError",
    # Configuration
    "FlextTapOracleWMSConfig",
    "FlextTapOracleWMSConfigurationError",
    "FlextTapOracleWMSConnectionError",
    "FlextTapOracleWMSDataValidationError",
    "FlextTapOracleWMSDiscoveryError",
    "FlextTapOracleWMSError",
    "FlextTapOracleWMSPaginationError",
    "FlextTapOracleWMSRateLimitError",
    "FlextTapOracleWMSRetryableError",
    "FlextTapOracleWMSStream",
    "FlextTapOracleWMSStreamError",
    "FlextValueObject",
    "__version__",
    "__version_info__",
    "get_logger",
]

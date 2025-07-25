"""Oracle WMS Client Module - REFACTORED to eliminate code duplication.

Uses FlextOracleWmsClient from flext-oracle-wms library instead of reimplementing.
This eliminates 236 lines of duplicated WMS client functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from flext_core import get_logger
from flext_oracle_wms import (
    FlextOracleWmsAuthenticationError,
    FlextOracleWmsClient,
    FlextOracleWmsClientError,
    FlextOracleWmsConnectionError,
)

logger = get_logger(__name__)

# Use library client instead of reimplementing
WMSClient = FlextOracleWmsClient

# Re-export exceptions from library for backward compatibility
WMSClientError = FlextOracleWmsClientError
AuthenticationError = FlextOracleWmsAuthenticationError
WMSConnectionError = FlextOracleWmsConnectionError

__all__ = [
    "AuthenticationError",
    "WMSClient",
    "WMSClientError",
    "WMSConnectionError",
]

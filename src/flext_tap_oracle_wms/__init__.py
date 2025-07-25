"""FLEXT Tap Oracle WMS - Oracle WMS Data Extraction with simplified imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.7.0 - Tap Oracle WMS with simplified public API:
- All common imports available from root: from flext_tap_oracle_wms import TapOracleWMS
- Built on flext-core foundation for robust Oracle WMS data extraction
- Modern namespace imports from flext-core
"""

from __future__ import annotations

import contextlib
import importlib.metadata

# Import from flext-core for foundational patterns (standardized)
from flext_core import (
    FlextCoreSettings as BaseConfig,
    FlextEntity as DomainEntity,
    FlextField as Field,
    FlextResult as FlextResult,
    FlextValueObject as BaseModel,
    FlextValueObject as FlextDomainBaseModel,
    FlextValueObject as FlextValueObject,
)

# Import from flext-oracle-wms for centralized Oracle WMS patterns
from flext_oracle_wms import (
    FlextOracleWmsAuth,
    FlextOracleWmsClient,
    FlextOracleWmsConfig,
    FlextOracleWmsDeflattener,
    FlextOracleWmsFlattener,
    FlextOracleWmsTypeMapper,
    flext_oracle_wms_format_wms_record,
    flext_oracle_wms_sanitize_entity_name,
    flext_oracle_wms_validate_connection,
)

try:
    __version__ = importlib.metadata.version("flext-tap-oracle-wms")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.7.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())


# ================================
# SIMPLIFIED PUBLIC API EXPORTS
# ================================

# Singer Tap exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.tap import TapOracleWMS

# WMS Client exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.client import WMSClient

# WMS Auth exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.auth import WMSBasicAuthenticator as WMSAuthenticator

# WMS Streams exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.streams import (
        WMSStream,
        WMSStream as InventoryStream,
        WMSStream as LocationsStream,
        WMSStream as ReceiptsStream,
        WMSStream as ShipmentsStream,
    )

# WMS Discovery exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.infrastructure.entity_discovery import (
        EntityDiscovery as WMSEntityDiscovery,
    )
    from flext_tap_oracle_wms.infrastructure.schema_generator import (
        SchemaGenerator as WMSSchemaGenerator,
    )

# Simple API
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.simple_api import setup_wms_tap as create_wms_tap

# ================================
# PUBLIC API EXPORTS
# ================================

__all__ = [
    # Core patterns from flext-core
    "BaseConfig",
    "BaseModel",
    "DomainEntity",
    "Field",
    "FlextDomainBaseModel",
    # Centralized Oracle WMS patterns from flext-oracle-wms
    "FlextOracleWmsAuth",
    "FlextOracleWmsClient",
    "FlextOracleWmsConfig",
    "FlextOracleWmsDeflattener",
    "FlextOracleWmsFlattener",
    "FlextOracleWmsTypeMapper",
    "FlextResult",
    "FlextValueObject",
    # WMS Streams
    "InventoryStream",
    "LocationsStream",
    "ReceiptsStream",
    "ShipmentsStream",
    # Main Singer Tap
    "TapOracleWMS",
    # WMS Authentication (legacy)
    "WMSAuthenticator",
    # WMS Client (legacy)
    "WMSClient",
    # WMS Discovery
    "WMSEntityDiscovery",
    "WMSSchemaGenerator",
    "WMSStream",
    # Metadata
    "__version__",
    "__version_info__",
    # Simple API
    "create_wms_tap",
    # Helper functions from flext-oracle-wms
    "flext_oracle_wms_format_wms_record",
    "flext_oracle_wms_sanitize_entity_name",
    "flext_oracle_wms_validate_connection",
]

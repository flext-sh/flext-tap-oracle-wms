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
    FlextBaseSettings as BaseConfig,
    FlextEntity as DomainEntity,
    FlextFields as Field,
    FlextResult as FlextResult,
    FlextValueObject as BaseModel,
    FlextValueObject as FlextDomainBaseModel,
    FlextValueObject as FlextValueObject,
)

# Import from flext-oracle-wms for centralized Oracle WMS patterns
from flext_oracle_wms import (
    FlextOracleWmsClient,
    FlextOracleWmsClientConfig,
    FlextOracleWmsEntityDiscovery,
    FlextOracleWmsModuleConfig,
    flext_oracle_wms_create_entity_discovery,
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
    from flext_tap_oracle_wms.entity_discovery import (
        EntityDiscovery as WMSEntityDiscovery,
    )
    from flext_tap_oracle_wms.schema_generator import (
        SchemaGenerator as WMSSchemaGenerator,
    )

# Simple API
with contextlib.suppress(ImportError):
    from flext_tap_oracle_wms.simple_api import setup_wms_tap as create_wms_tap

# ================================
# PUBLIC API EXPORTS
# ================================

__all__ = [
    "BaseConfig",
    "BaseModel",
    "DomainEntity",
    "Field",
    "FlextDomainBaseModel",
    "FlextOracleWmsClient",
    "FlextOracleWmsClientConfig",
    "FlextOracleWmsEntityDiscovery",
    "FlextOracleWmsModuleConfig",
    "FlextResult",
    "FlextValueObject",
    "InventoryStream",
    "LocationsStream",
    "ReceiptsStream",
    "ShipmentsStream",
    "TapOracleWMS",
    "WMSAuthenticator",
    "WMSClient",
    "WMSEntityDiscovery",
    "WMSSchemaGenerator",
    "WMSStream",
    "__version__",
    "__version_info__",
    "create_wms_tap",
    "flext_oracle_wms_create_entity_discovery",
]

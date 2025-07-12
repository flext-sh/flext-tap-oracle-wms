"""Singer tap for Oracle Warehouse Management System (WMS) Cloud."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from flext_tap_oracle_wms.__version__ import __version__
from flext_tap_oracle_wms.tap import TapOracleWMS

__all__ = ["TapOracleWMS", "__version__"]

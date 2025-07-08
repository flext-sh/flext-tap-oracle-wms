"""Singer tap for Oracle Warehouse Management System (WMS) Cloud."""

from __future__ import annotations

from tap_oracle_wms.__version__ import __version__
from tap_oracle_wms.tap import TapOracleWMS

__all__ = ["TapOracleWMS", "__version__"]

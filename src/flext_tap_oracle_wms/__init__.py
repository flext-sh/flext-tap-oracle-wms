"""Singer tap for Oracle Warehouse Management System (WMS) Cloud."""

from flext_tap_oracle_wms.__version__ import __version__
from flext_tap_oracle_wms.tap import TapOracleWMS


__all__ = ["TapOracleWMS", "__version__"]

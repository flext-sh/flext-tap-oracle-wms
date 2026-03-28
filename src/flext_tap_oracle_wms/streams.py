"""Re-export shim — canonical implementation lives in _utilities.streams."""

from __future__ import annotations

from flext_tap_oracle_wms._utilities.streams import FlextTapOracleWmsStream, logger

__all__ = ["FlextTapOracleWmsStream", "logger"]

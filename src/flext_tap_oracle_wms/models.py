"""Pydantic models used by Oracle WMS tap compatibility layers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_tap_oracle_wms/models
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_meltano import FlextMeltanoModels
from flext_oracle_wms import FlextOracleWmsModels


class FlextTapOracleWmsModels(FlextMeltanoModels, FlextOracleWmsModels):
    """Container for stream schema and metadata payload models."""

    class TapOracleWms:
        """TapOracleWms domain namespace.

        Local Singer catalog compatibility types were removed in favor of the
        canonical ``m.Meltano.SingerCatalog*`` Pydantic models plus explicit
        serialization at the Singer dict boundary.
        """


m = FlextTapOracleWmsModels

__all__: list[str] = ["FlextTapOracleWmsModels", "m"]

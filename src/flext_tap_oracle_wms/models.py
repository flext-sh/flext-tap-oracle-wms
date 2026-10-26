# AUTO-GENERATED FILE — Regenerate with: make gen
"""Pydantic models used by Oracle WMS tap compatibility layers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_tap_oracle_wms/models
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_meltano import m
from flext_oracle_wms import m as flext_oracle_wms_m

from flext_tap_oracle_wms._models import FlextTapOracleWmsModelsBase


class FlextTapOracleWmsModels(m, flext_oracle_wms_m):
    """Container for stream schema and metadata payload models."""

    class TapOracleWms(FlextTapOracleWmsModelsBase):
        """TapOracleWms domain namespace.

        Local Singer catalog compatibility types were removed in favor of the
        canonical ``m.Meltano.SingerCatalog*`` Pydantic models plus explicit
        serialization at the Singer dict boundary.
        """


m = FlextTapOracleWmsModels
__all__: list[str] = ["FlextTapOracleWmsModels", "m"]

"""Base models for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import m


class FlextTapOracleWmsModelsBase:
    """Base models for flext-tap-oracle-wms."""

    class TapOracleWmsNamespace(m.BaseModel):
        """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

        model_config = m.ConfigDict(extra="allow", frozen=True)


__all__: list[str] = ["FlextTapOracleWmsModelsBase"]

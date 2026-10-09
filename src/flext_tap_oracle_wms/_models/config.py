"""FLEXT Tap Oracle WMS models - Config namespace models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import m


class FlextTapOracleWmsModelsConfig:
    """Config namespace models for model-less ``config/*.yaml`` exposure."""

    class TapOracleWmsNamespace(m.BaseModel):
        """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

        model_config = m.ConfigDict(extra="allow", frozen=True)


__all__: list[str] = ["FlextTapOracleWmsModelsConfig"]

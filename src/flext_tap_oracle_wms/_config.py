"""FlextTapOracleWmsConfig — frozen config singleton for flext-tap-oracle-wms (ADR-005 §7).

Model-less: business rules live in ``config/*.yaml`` under the ``TapOracleWms:`` key and
are exposed through the open ``config.TapOracleWms`` namespace (``extra="allow"``), with
no per-domain model. Access is ``config.TapOracleWms.<domain>[<key>...]``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from flext_meltano import FlextMeltanoConfig


class _TapOracleWmsNamespace(BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = ConfigDict(extra="allow", frozen=True)


class FlextTapOracleWmsConfig(FlextMeltanoConfig):
    """TapOracleWms config auto-loaded model-less from ``config/*.yaml``."""

    TapOracleWms: _TapOracleWmsNamespace = _TapOracleWmsNamespace()


config: FlextTapOracleWmsConfig = FlextTapOracleWmsConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_tap_oracle_wms import config``."""

__all__: list[str] = ["FlextTapOracleWmsConfig", "config"]

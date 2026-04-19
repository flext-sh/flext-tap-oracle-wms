"""FLEXT service orchestrator for tap-oracle-wms.

Thin facade — all infrastructure from ``FlextMeltanoTapServiceBase`` via MRO.
Only domain-specific tap creation defined here.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, override

from flext_core import u
from flext_meltano import FlextMeltanoSingerTapAdapter, FlextMeltanoTapServiceBase
from flext_tap_oracle_wms import FlextTapOracleWms, p, t


class FlextTapOracleWmsService(FlextMeltanoTapServiceBase):
    """Orchestrator for tap-oracle-wms. All behavior from base via MRO."""

    tap_name: Annotated[
        t.NonEmptyStr,
        u.Field(description="Canonical Singer tap identifier."),
    ] = "tap-oracle-wms"

    @override
    def create_tap_instance(
        self,
        settings: Mapping[str, t.Container] | None = None,
    ) -> p.Meltano.SingerTapInstance:
        """Create the internal tap runtime backed by Singer SDK."""
        raw_config = dict(settings) if settings is not None else None
        return FlextMeltanoSingerTapAdapter(FlextTapOracleWms(config=raw_config))


tap_oracle_wms = FlextTapOracleWmsService

__all__: list[str] = ["FlextTapOracleWmsService", "tap_oracle_wms"]

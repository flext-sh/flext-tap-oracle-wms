"""FLEXT service orchestrator for tap-oracle-wms.

from flext_tap_oracle_wms import u
Thin facade — all infrastructure from ``FlextMeltanoTapServiceBase`` via MRO.
Only domain-specific tap creation defined here.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, override

from flext_meltano.services.consumer_bases.tap_service_base import (
    FlextMeltanoTapServiceBase,
)
from flext_meltano.services.singer_sdk import FlextMeltanoSingerTapAdapter
from flext_tap_oracle_wms import p, t, u
from flext_tap_oracle_wms.tap import FlextTapOracleWms


class FlextTapOracleWmsService(FlextMeltanoTapServiceBase):
    """Orchestrator for tap-oracle-wms. All behavior from base via MRO."""

    tap_name: Annotated[
        t.NonEmptyStr,
        u.Field(description="Canonical Singer tap identifier."),
    ] = "tap-oracle-wms"

    @override
    def create_tap_instance(
        self,
        settings: t.JsonMapping | None = None,
    ) -> p.Meltano.SingerTapInstance:
        """Create the internal tap runtime backed by Singer SDK.

        Built config-free (``validate_config=False``) so the flat Singer CLI
        (``get_singer_command``) parses and validates ``--config`` itself instead
        of crashing at construction when no config is pre-supplied.
        """
        raw_config = (
            t.json_dict_adapter().validate_python(settings)
            if settings is not None
            else None
        )
        return FlextMeltanoSingerTapAdapter(
            FlextTapOracleWms(config=raw_config, validate_config=False),
        )


tap_oracle_wms = FlextTapOracleWmsService

__all__: list[str] = ["FlextTapOracleWmsService", "tap_oracle_wms"]

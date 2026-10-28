# AUTO-GENERATED FILE — Regenerate with: make gen
"""Singer Oracle WMS tap protocols for FLEXT ecosystem.

Only ``TapOracleWms.TapWithWmsClient`` and ``TapOracleWms.TapWithWmsClientSettings``
exist: ``streams.py`` consumes both through ``isinstance`` runtime dispatch.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_meltano import p as flext_meltano_p
from flext_oracle_wms import p as flext_oracle_wms_p

from flext_tap_oracle_wms._protocols import FlextTapOracleWmsProtocolsBase


class FlextTapOracleWmsProtocols(flext_meltano_p, flext_oracle_wms_p):
    """Singer Oracle WMS tap protocols facade — composes Meltano + OracleWms."""

    class TapOracleWms(FlextTapOracleWmsProtocolsBase):
        """Singer Tap Oracle WMS structural protocols (consumer surface)."""


p = FlextTapOracleWmsProtocols
__all__: list[str] = ["FlextTapOracleWmsProtocols", "p"]

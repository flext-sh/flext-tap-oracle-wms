"""Singer Oracle WMS tap protocols for FLEXT ecosystem.

Of the 9 inner ``TapOracleWms.*`` Protocol classes that previously lived
here, 7 had **zero workspace consumers** (per AGENTS.md §3.5 + STRICT YAGNI
they were deleted). Only ``TapOracleWms.OracleWms.TapWithWmsClient`` and
``TapWithWmsClientSettings`` remain (consumed by ``streams.py`` via
``isinstance`` runtime dispatch).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_meltano import p as meltano_p
from flext_oracle_wms import FlextOracleWmsProtocols
from flext_oracle_wms.utilities import FlextOracleWmsUtilities
from flext_tap_oracle_wms import t


class FlextTapOracleWmsProtocols(meltano_p, FlextOracleWmsProtocols):
    """Singer Oracle WMS tap protocols facade — composes Meltano + OracleWms."""

    class TapOracleWms:
        """Singer Tap Oracle WMS structural protocols (consumer surface)."""

        class OracleWms:
            """OracleWms-rooted protocol cluster used by stream isinstance dispatch."""

            @runtime_checkable
            class TapWithWmsClient(Protocol):
                """Protocol for tap instances that provide ``wms_client``."""

                wms_client: FlextOracleWmsUtilities.OracleWms.Client

            @runtime_checkable
            class TapWithWmsClientSettings(TapWithWmsClient, Protocol):
                """Protocol for tap instances with WMS client and settings."""

                settings: t.JsonMapping


p = FlextTapOracleWmsProtocols
__all__: list[str] = ["FlextTapOracleWmsProtocols", "p"]

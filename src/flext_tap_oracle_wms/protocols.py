"""Singer Oracle WMS tap protocols for FLEXT ecosystem.

Only ``TapOracleWms.TapWithWmsClient`` and ``TapOracleWms.TapWithWmsClientSettings``
exist: ``streams.py`` consumes both through ``isinstance`` runtime dispatch.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_meltano import FlextMeltanoProtocols
from flext_oracle_wms import FlextOracleWmsProtocols

if TYPE_CHECKING:
    from flext_oracle_wms import u as _oracle_wms_u

    from flext_tap_oracle_wms import t


class FlextTapOracleWmsProtocols(FlextMeltanoProtocols, FlextOracleWmsProtocols):
    """Singer Oracle WMS tap protocols facade — composes Meltano + OracleWms."""

    class TapOracleWms:
        """Singer Tap Oracle WMS structural protocols (consumer surface)."""

        @runtime_checkable
        class TapWithWmsClient(Protocol):
            """Protocol for tap instances that provide ``wms_client``."""

            wms_client: _oracle_wms_u.OracleWms.Client

        @runtime_checkable
        class TapWithWmsClientSettings(TapWithWmsClient, Protocol):
            """Protocol for tap instances with WMS client and settings."""

            settings: t.JsonMapping


p = FlextTapOracleWmsProtocols
__all__: list[str] = ["FlextTapOracleWmsProtocols", "p"]

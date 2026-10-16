"""Singer Oracle WMS tap protocol contracts.

``streams.py`` consumes both contracts through ``isinstance`` runtime dispatch.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_oracle_wms import u as _oracle_wms_u

    from flext_tap_oracle_wms import t


class FlextTapOracleWmsProtocolsBase:
    """Singer Tap Oracle WMS structural protocol contracts for ``p.TapOracleWms``."""

    @runtime_checkable
    class TapWithWmsClient(Protocol):
        """Protocol for tap instances that provide ``wms_client``."""

        wms_client: _oracle_wms_u.OracleWms.Client

    @runtime_checkable
    class TapWithWmsClientSettings(TapWithWmsClient, Protocol):
        """Protocol for tap instances with WMS client and settings."""

        settings: t.JsonMapping


__all__: list[str] = [
    "FlextTapOracleWmsProtocolsBase",
]

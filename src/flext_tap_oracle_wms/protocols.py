"""Singer Oracle WMS tap protocols for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    Sequence,
)
from typing import Protocol, runtime_checkable

from flext_meltano import m, p as meltano_p
from flext_oracle_wms import FlextOracleWmsProtocols, FlextOracleWmsUtilitiesClient

from flext_tap_oracle_wms import t


class FlextTapOracleWmsProtocols(meltano_p, FlextOracleWmsProtocols):
    """Singer Tap Oracle WMS protocols extending OracleWms protocols.

    Extends FlextOracleWmsProtocols via inheritance
    to inherit all Oracle WMS protocols and foundation protocols.

    Architecture:
    - EXTENDS: FlextOracleWmsProtocols (inherits .OracleWms.* protocols)
    - ADDS: Tap Oracle WMS-specific protocols in TapOracleWms namespace
    - PROVIDES: Root-level alias ``p`` for convenient access
    """

    class TapOracleWms:
        """Singer Tap domain protocols."""

        class OracleWms:
            """Singer Tap Oracle WMS domain protocols for Oracle Warehouse Management System extraction."""

            @runtime_checkable
            class WmsConnection(FlextOracleWmsProtocols.Service[t.Container], Protocol):
                """Protocol for Oracle WMS connection operations."""

                def establish_wms_connection(
                    self,
                    settings: m.ConfigMap,
                ) -> FlextOracleWmsProtocols.Result[t.Container]:
                    """Establish connection to Oracle WMS."""
                    ...

            @runtime_checkable
            class InventoryDiscovery(
                FlextOracleWmsProtocols.Service[t.Container],
                Protocol,
            ):
                """Protocol for WMS inventory discovery."""

                def discover_inventory(
                    self,
                    settings: m.ConfigMap,
                ) -> FlextOracleWmsProtocols.Result[Sequence[m.ConfigMap]]:
                    """Discover WMS inventory."""
                    ...

            @runtime_checkable
            class OrderProcessing(
                FlextOracleWmsProtocols.Service[t.Container],
                Protocol,
            ):
                """Protocol for WMS order processing."""

                def process_orders(
                    self,
                    settings: m.ConfigMap,
                ) -> FlextOracleWmsProtocols.Result[Sequence[m.ConfigMap]]:
                    """Process WMS orders."""
                    ...

            @runtime_checkable
            class WarehouseOperations(
                FlextOracleWmsProtocols.Service[t.Container],
                Protocol,
            ):
                """Protocol for WMS warehouse operations."""

                def get_warehouse_operations(
                    self,
                    settings: m.ConfigMap,
                ) -> FlextOracleWmsProtocols.Result[Sequence[m.ConfigMap]]:
                    """Get WMS warehouse operations."""
                    ...

            @runtime_checkable
            class StreamGeneration(
                FlextOracleWmsProtocols.Service[t.Container],
                Protocol,
            ):
                """Protocol for Singer stream generation."""

                def generate_catalog(
                    self,
                    settings: m.ConfigMap,
                ) -> FlextOracleWmsProtocols.Result[m.Meltano.SingerCatalog]:
                    """Generate Singer catalog."""
                    ...

            @runtime_checkable
            class Performance(FlextOracleWmsProtocols.Service[t.Container], Protocol):
                """Protocol for WMS extraction performance."""

                def optimize_query(
                    self,
                    query: str,
                ) -> FlextOracleWmsProtocols.Result[str]:
                    """Optimize WMS query."""
                    ...

            @runtime_checkable
            class Validation(FlextOracleWmsProtocols.Service[t.Container], Protocol):
                """Protocol for WMS data validation."""

                def validate_config(
                    self,
                    settings: m.ConfigMap,
                ) -> FlextOracleWmsProtocols.Result[bool]:
                    """Validate WMS configuration."""
                    ...

            @runtime_checkable
            class Monitoring(FlextOracleWmsProtocols.Service[t.Container], Protocol):
                """Protocol for WMS extraction monitoring."""

                def track_progress(
                    self,
                    entity: str,
                    records: int,
                ) -> FlextOracleWmsProtocols.Result[bool]:
                    """Track WMS extraction progress."""
                    ...

            @runtime_checkable
            class TapWithWmsClient(Protocol):
                """Protocol for tap instances that provide wms_client."""

                wms_client: FlextOracleWmsUtilitiesClient.Client

            @runtime_checkable
            class TapWithWmsClientSettings(TapWithWmsClient, Protocol):
                """Protocol for tap instances with WMS client and settings."""

                settings: Mapping[str, t.Container]


p = FlextTapOracleWmsProtocols
__all__: list[str] = ["FlextTapOracleWmsProtocols", "p"]

"""Singer Oracle WMS tap protocols for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_oracle_wms import FlextOracleWmsClient

from flext_core import FlextProtocols, t
from flext_meltano import FlextMeltanoProtocols, m
from flext_oracle_wms.protocols import FlextOracleWmsProtocols


class FlextTapOracleWmsProtocols(FlextMeltanoProtocols, FlextOracleWmsProtocols):
    """Singer Tap Oracle WMS protocols extending OracleWms and Meltano protocols.

    Extends both FlextOracleWmsProtocols and FlextMeltanoProtocols via multiple inheritance
    to inherit all Oracle WMS protocols, Meltano protocols, and foundation protocols.

    Architecture:
    - EXTENDS: FlextOracleWmsProtocols (inherits .OracleWms.* protocols)
    - EXTENDS: FlextMeltanoProtocols (inherits .Meltano.* protocols)
    - ADDS: Tap Oracle WMS-specific protocols in TapOracleWms namespace
    - PROVIDES: Root-level alias `p` for convenient access

    Usage:
    from flext_tap_oracle_wms.protocols import p

    # Foundation protocols (inherited)
    result: p.Result[str]
    service: p.Service[str]

    # Oracle WMS protocols (inherited)
    wms: p.OracleWms.*

    # Meltano protocols (inherited)
    tap: p.Meltano.TapProtocol

    # Tap Oracle WMS-specific protocols
    wms_connection: p.TapOracleWms.OracleWms.WmsConnectionProtocol
    """

    class TapOracleWms:
        """Singer Tap domain protocols."""

        class OracleWms:
            """Singer Tap Oracle WMS domain protocols for Oracle Warehouse Management System extraction."""

            @runtime_checkable
            class WmsConnectionProtocol(FlextProtocols.Service[t.JsonValue], Protocol):
                """Protocol for Oracle WMS connection operations."""

                def establish_wms_connection(
                    self,
                    config: t.ConfigMap,
                ) -> FlextProtocols.Result[t.JsonValue]:
                    """Establish connection to Oracle WMS."""
                    ...

            @runtime_checkable
            class InventoryDiscoveryProtocol(
                FlextProtocols.Service[t.JsonValue],
                Protocol,
            ):
                """Protocol for WMS inventory discovery."""

                def discover_inventory(
                    self,
                    config: t.ConfigMap,
                ) -> FlextProtocols.Result[list[t.ConfigMap]]:
                    """Discover WMS inventory."""
                    ...

            @runtime_checkable
            class OrderProcessingProtocol(
                FlextProtocols.Service[t.JsonValue],
                Protocol,
            ):
                """Protocol for WMS order processing."""

                def process_orders(
                    self,
                    config: t.ConfigMap,
                ) -> FlextProtocols.Result[list[t.ConfigMap]]:
                    """Process WMS orders."""
                    ...

            @runtime_checkable
            class WarehouseOperationsProtocol(
                FlextProtocols.Service[t.JsonValue],
                Protocol,
            ):
                """Protocol for WMS warehouse operations."""

                def get_warehouse_operations(
                    self,
                    config: t.ConfigMap,
                ) -> FlextProtocols.Result[list[t.ConfigMap]]:
                    """Get WMS warehouse operations."""
                    ...

            @runtime_checkable
            class StreamGenerationProtocol(
                FlextProtocols.Service[t.JsonValue],
                Protocol,
            ):
                """Protocol for Singer stream generation."""

                def generate_catalog(
                    self,
                    config: t.ConfigMap,
                ) -> FlextProtocols.Result[m.Meltano.SingerCatalog]:
                    """Generate Singer catalog."""
                    ...

            @runtime_checkable
            class PerformanceProtocol(FlextProtocols.Service[t.JsonValue], Protocol):
                """Protocol for WMS extraction performance."""

                def optimize_query(self, query: str) -> FlextProtocols.Result[str]:
                    """Optimize WMS query."""
                    ...

            @runtime_checkable
            class ValidationProtocol(FlextProtocols.Service[t.JsonValue], Protocol):
                """Protocol for WMS data validation."""

                def validate_config(
                    self,
                    config: t.ConfigMap,
                ) -> FlextProtocols.Result[bool]:
                    """Validate WMS configuration."""
                    ...

            @runtime_checkable
            class MonitoringProtocol(FlextProtocols.Service[t.JsonValue], Protocol):
                """Protocol for WMS extraction monitoring."""

                def track_progress(
                    self,
                    entity: str,
                    records: int,
                ) -> FlextProtocols.Result[bool]:
                    """Track WMS extraction progress."""
                    ...

            @runtime_checkable
            class TapWithWmsClientProtocol(Protocol):
                """Protocol for tap instances that provide wms_client."""

                wms_client: FlextOracleWmsClient


# Runtime alias for simplified usage
p = FlextTapOracleWmsProtocols

__all__ = [
    "FlextTapOracleWmsProtocols",
    "p",
]

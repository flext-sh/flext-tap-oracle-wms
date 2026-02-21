"""Singer Oracle WMS tap protocols for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

from flext_core import FlextTypes as t
from flext_db_oracle.protocols import FlextDbOracleProtocols as p_db_oracle
from flext_meltano import FlextMeltanoModels as m
from flext_meltano.protocols import FlextMeltanoProtocols as p_meltano


class FlextTapOracleWmsProtocols(p_meltano, p_db_oracle):
    """Singer Tap Oracle WMS protocols extending Oracle and Meltano protocols.

    Extends both FlextDbOracleProtocols and FlextMeltanoProtocols via multiple inheritance
    to inherit all Oracle protocols, Meltano protocols, and foundation protocols.

    Architecture:
    - EXTENDS: FlextDbOracleProtocols (inherits .Database.* protocols)
    - EXTENDS: FlextMeltanoProtocols (inherits .Meltano.* protocols)
    - ADDS: Tap Oracle WMS-specific protocols in Tap.OracleWms namespace
    - PROVIDES: Root-level alias `p` for convenient access

    Usage:
    from flext_tap_oracle_wms.protocols import p

    # Foundation protocols (inherited)
    result: p.Result[str]
    service: p.Service[str]

    # Oracle protocols (inherited)
    connection: p.Database.ConnectionProtocol

    # Meltano protocols (inherited)
    tap: p.Meltano.TapProtocol

    # Tap Oracle WMS-specific protocols
    wms_connection: p.Tap.OracleWms.WmsConnectionProtocol
    """

    class TapOracleWms:
        """Singer Tap domain protocols."""

        class OracleWms:
            """Singer Tap Oracle WMS domain protocols for Oracle Warehouse Management System extraction."""

            @runtime_checkable
            class WmsConnectionProtocol(
                p_db_oracle.Service[t.GeneralValueType], Protocol
            ):
                """Protocol for Oracle WMS connection operations."""

                def establish_wms_connection(
                    self,
                    config: Mapping[str, t.GeneralValueType],
                ) -> p_meltano.Result[t.GeneralValueType]:
                    """Establish connection to Oracle WMS."""
                    ...

            @runtime_checkable
            class InventoryDiscoveryProtocol(
                p_db_oracle.Service[t.GeneralValueType],
                Protocol,
            ):
                """Protocol for WMS inventory discovery."""

                def discover_inventory(
                    self,
                    config: Mapping[str, t.GeneralValueType],
                ) -> p_meltano.Result[Sequence[Mapping[str, t.GeneralValueType]]]:
                    """Discover WMS inventory."""
                    ...

            @runtime_checkable
            class OrderProcessingProtocol(
                p_db_oracle.Service[t.GeneralValueType],
                Protocol,
            ):
                """Protocol for WMS order processing."""

                def process_orders(
                    self,
                    config: Mapping[str, t.GeneralValueType],
                ) -> p_meltano.Result[Sequence[Mapping[str, t.GeneralValueType]]]:
                    """Process WMS orders."""
                    ...

            @runtime_checkable
            class WarehouseOperationsProtocol(
                p_db_oracle.Service[t.GeneralValueType],
                Protocol,
            ):
                """Protocol for WMS warehouse operations."""

                def get_warehouse_operations(
                    self,
                    config: Mapping[str, t.GeneralValueType],
                ) -> p_meltano.Result[Sequence[Mapping[str, t.GeneralValueType]]]:
                    """Get WMS warehouse operations."""
                    ...

            @runtime_checkable
            class StreamGenerationProtocol(
                p_db_oracle.Service[t.GeneralValueType],
                Protocol,
            ):
                """Protocol for Singer stream generation."""

                def generate_catalog(
                    self,
                    config: Mapping[str, t.GeneralValueType],
                ) -> p_meltano.Result[m.Meltano.SingerCatalog]:
                    """Generate Singer catalog."""
                    ...

            @runtime_checkable
            class PerformanceProtocol(
                p_db_oracle.Service[t.GeneralValueType], Protocol
            ):
                """Protocol for WMS extraction performance."""

                def optimize_query(self, query: str) -> p_meltano.Result[str]:
                    """Optimize WMS query."""
                    ...

            @runtime_checkable
            class ValidationProtocol(p_db_oracle.Service[t.GeneralValueType], Protocol):
                """Protocol for WMS data validation."""

                def validate_config(
                    self,
                    config: Mapping[str, t.GeneralValueType],
                ) -> p_meltano.Result[bool]:
                    """Validate WMS configuration."""
                    ...

            @runtime_checkable
            class MonitoringProtocol(p_db_oracle.Service[t.GeneralValueType], Protocol):
                """Protocol for WMS extraction monitoring."""

                def track_progress(
                    self,
                    entity: str,
                    records: int,
                ) -> p_meltano.Result[bool]:
                    """Track WMS extraction progress."""
                    ...


# Runtime alias for simplified usage
p = FlextTapOracleWmsProtocols

__all__ = [
    "FlextTapOracleWmsProtocols",
    "p",
]

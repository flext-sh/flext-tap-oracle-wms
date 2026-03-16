"""Type aliases for the Oracle WMS tap package."""

from __future__ import annotations

from flext_meltano import FlextMeltanoTypes
from flext_oracle_wms import FlextOracleWmsTypes

from flext_tap_oracle_wms import c


class FlextTapOracleWmsTypes(FlextMeltanoTypes, FlextOracleWmsTypes):
    """Namespace for Oracle WMS tap type aliases."""

    class Project:
        """Project-level aliases and constrained literals."""

        type ProjectType = c.ProjectType
        type ReplicationMethodLiteral = c.ReplicationMethodLiteral
        type AuthenticationMethodLiteral = c.AuthenticationMethodLiteral
        type StreamInclusionLiteral = c.StreamInclusionLiteral
        type ErrorTypeLiteral = c.ErrorTypeLiteral
        type BackoffStrategyLiteral = c.BackoffStrategyLiteral


t = FlextTapOracleWmsTypes
__all__ = ["FlextTapOracleWmsTypes", "t"]

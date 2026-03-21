"""Type aliases for the Oracle WMS tap package."""

from __future__ import annotations

from flext_meltano import FlextMeltanoTypes
from flext_oracle_wms import FlextOracleWmsTypes

from flext_tap_oracle_wms.constants import FlextTapOracleWmsConstants as _c


class FlextTapOracleWmsTypes(FlextMeltanoTypes, FlextOracleWmsTypes):
    """Namespace for Oracle WMS tap type aliases."""

    class Project:
        """Project-level aliases and constrained literals."""

        type ProjectType = _c.ProjectType
        type ReplicationMethodLiteral = _c.ReplicationMethodLiteral
        type AuthenticationMethodLiteral = _c.AuthenticationMethodLiteral
        type StreamInclusionLiteral = _c.StreamInclusionLiteral
        type ErrorTypeLiteral = _c.ErrorTypeLiteral
        type BackoffStrategyLiteral = _c.BackoffStrategyLiteral


t = FlextTapOracleWmsTypes
__all__ = ["FlextTapOracleWmsTypes", "t"]

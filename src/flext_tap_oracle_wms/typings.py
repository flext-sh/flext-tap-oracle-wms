"""Type aliases for the Oracle WMS tap package."""

from __future__ import annotations

from flext_meltano import FlextMeltanoTypes
from flext_oracle_wms import FlextOracleWmsTypes

from flext_tap_oracle_wms.constants import (
    FlextTapOracleWmsConstants,
)


class FlextTapOracleWmsTypes(FlextMeltanoTypes, FlextOracleWmsTypes):
    """Namespace for Oracle WMS tap type aliases."""

    class Project:
        """Project-level aliases and constrained literals."""

        type ProjectType = FlextTapOracleWmsConstants.ProjectType
        type ReplicationMethodLiteral = (
            FlextTapOracleWmsConstants.ReplicationMethodLiteral
        )
        type AuthenticationMethodLiteral = (
            FlextTapOracleWmsConstants.AuthenticationMethodLiteral
        )
        type StreamInclusionLiteral = FlextTapOracleWmsConstants.StreamInclusionLiteral
        type ErrorTypeLiteral = FlextTapOracleWmsConstants.ErrorTypeLiteral
        type BackoffStrategyLiteral = FlextTapOracleWmsConstants.BackoffStrategyLiteral


t = FlextTapOracleWmsTypes
__all__ = ["FlextTapOracleWmsTypes", "t"]

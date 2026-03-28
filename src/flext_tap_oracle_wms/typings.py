"""Type aliases for the Oracle WMS tap package."""

from __future__ import annotations

from collections.abc import Callable

from flext_meltano import FlextMeltanoTypes
from flext_oracle_wms import FlextOracleWmsTypes
from pydantic import TypeAdapter

from flext_tap_oracle_wms.constants import (
    FlextTapOracleWmsConstants,
)


class FlextTapOracleWmsTypes(FlextMeltanoTypes, FlextOracleWmsTypes):
    """Namespace for Oracle WMS tap type aliases."""

    type ScalarNormalizer = Callable[
        [FlextMeltanoTypes.NormalizedValue], FlextMeltanoTypes.Scalar
    ]
    type ContainerValueMapAdapter = TypeAdapter[FlextMeltanoTypes.ContainerValueMapping]
    type ContainerValueListAdapter = TypeAdapter[FlextMeltanoTypes.ContainerValueList]

    class Project:
        """Project-level aliases and constrained literals."""

        type ProjectType = FlextTapOracleWmsConstants.TapOracleWms.TapProjectType
        type ReplicationMethodLiteral = (
            FlextTapOracleWmsConstants.TapOracleWms.ReplicationMethodLiteral
        )
        type AuthenticationMethodLiteral = (
            FlextTapOracleWmsConstants.TapOracleWms.AuthenticationMethodLiteral
        )
        type StreamInclusionLiteral = (
            FlextTapOracleWmsConstants.TapOracleWms.StreamInclusionLiteral
        )
        type ErrorTypeLiteral = FlextTapOracleWmsConstants.TapOracleWms.ErrorTypeLiteral
        type BackoffStrategyLiteral = (
            FlextTapOracleWmsConstants.TapOracleWms.BackoffStrategyLiteral
        )


t = FlextTapOracleWmsTypes
__all__ = ["FlextTapOracleWmsTypes", "t"]

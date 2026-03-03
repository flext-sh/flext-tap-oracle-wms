"""Type aliases for the Oracle WMS tap package."""

from __future__ import annotations

from typing import Literal

from flext_core import FlextTypes
from flext_meltano import FlextMeltanoTypes
from flext_oracle_wms import FlextOracleWmsTypes


class FlextTapOracleWmsTypes(FlextMeltanoTypes, FlextOracleWmsTypes):
    """Namespace for Oracle WMS tap type aliases."""

    class Core:
        """Core shared aliases for this package."""

        type Dict = dict[str, FlextTypes.GeneralValueType]
        type Headers = dict[str, str]

    class Project:
        """Project-level aliases and constrained literals."""

        type ProjectType = Literal[
            "library",
            "application",
            "service",
            "singer-tap",
            "wms-extractor",
            "warehouse-extractor",
            "singer-tap-oracle-wms",
            "tap-oracle-wms",
            "wms-connector",
            "warehouse-connector",
            "singer-protocol",
            "wms-integration",
            "oracle-wms",
            "warehouse-management",
            "singer-stream",
            "etl-tap",
            "data-pipeline",
            "wms-tap",
            "singer-integration",
        ]
        type ReplicationMethodLiteral = Literal["FULL_TABLE", "INCREMENTAL"]
        type AuthenticationMethodLiteral = Literal["basic", "oauth2"]
        type StreamInclusionLiteral = Literal["available", "automatic", "unsupported"]
        type ErrorTypeLiteral = Literal[
            "AUTHENTICATION",
            "AUTHORIZATION",
            "RATE_LIMIT",
            "TIMEOUT",
            "SERVER_ERROR",
            "NETWORK",
            "VALIDATION",
        ]
        type BackoffStrategyLiteral = Literal["linear", "exponential", "fixed"]


t = FlextTapOracleWmsTypes

__all__ = ["FlextTapOracleWmsTypes", "t"]

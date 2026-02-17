from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from flext_core import FlextTypes


class FlextMeltanoTapOracleWmsTypes(FlextTypes):
    class Core:
        type Dict = Mapping[str, FlextTypes.GeneralValueType]
        type Headers = Mapping[str, str]

    class Project:
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


t = FlextMeltanoTapOracleWmsTypes

__all__ = ["FlextMeltanoTapOracleWmsTypes", "t"]

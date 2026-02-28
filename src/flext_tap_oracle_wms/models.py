"""Pydantic models used by Oracle WMS tap compatibility layers."""

from __future__ import annotations

from flext_core import t
from flext_meltano import FlextMeltanoModels
from flext_oracle_wms import FlextOracleWmsModels
from pydantic import BaseModel, Field


class FlextMeltanoTapOracleWmsModels(FlextMeltanoModels, FlextOracleWmsModels):
    """Container for stream schema and metadata payload models."""

    class TapOracleWms:
        """TapOracleWms domain namespace."""

        class WmsStreamSchema(BaseModel):
            """Singer stream schema shape."""

            type: str = Field(default="object")
            properties: dict[str, t.GeneralValueType] = Field(default_factory=dict)

        class WmsStreamMetadata(BaseModel):
            """Singer stream metadata entry."""

            breadcrumb: list[str] = Field(default_factory=list)
            metadata: dict[str, t.GeneralValueType] = Field(default_factory=dict)

        class WmsStreamDefinition(BaseModel):
            """Singer stream definition payload."""

            tap_stream_id: str
            stream: str
            schema_: FlextMeltanoTapOracleWmsModels.TapOracleWms.WmsStreamSchema = Field(
                alias="schema"
            )
            metadata: list[FlextMeltanoTapOracleWmsModels.TapOracleWms.WmsStreamMetadata] = Field(
                default_factory=list,
            )


m = FlextMeltanoTapOracleWmsModels

__all__ = ["FlextMeltanoTapOracleWmsModels", "m"]

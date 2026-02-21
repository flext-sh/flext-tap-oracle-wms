"""Pydantic models used by Oracle WMS tap compatibility layers."""

from __future__ import annotations

from flext_core import FlextModels, FlextTypes as t
from flext_meltano import FlextMeltanoModels
from pydantic import BaseModel, Field


class FlextTapOracleWmsModels(FlextMeltanoModels, FlextModels):
    """Container for stream schema and metadata payload models."""

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
        schema_: FlextTapOracleWmsModels.WmsStreamSchema = Field(alias="schema")
        metadata: list[FlextTapOracleWmsModels.WmsStreamMetadata] = Field(
            default_factory=list,
        )


m = FlextTapOracleWmsModels
m_tap_oracle_wms = FlextTapOracleWmsModels

__all__ = ["FlextTapOracleWmsModels", "m", "m_tap_oracle_wms"]

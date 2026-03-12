"""Pydantic models used by Oracle WMS tap compatibility layers."""

from __future__ import annotations

from flext_meltano import FlextMeltanoModels
from flext_oracle_wms import FlextOracleWmsModels
from pydantic import BaseModel, Field


class FlextTapOracleWmsModels(FlextMeltanoModels, FlextOracleWmsModels):
    """Container for stream schema and metadata payload models."""

    class TapOracleWms:
        """TapOracleWms domain namespace."""

        class WmsStreamSchema(BaseModel):
            """Singer stream schema shape."""

            type: str = Field(default="object")
            properties: dict[str, object] = Field(default_factory=dict)

        class WmsStreamMetadata(BaseModel):
            """Singer stream metadata entry."""

            breadcrumb: list[str] = Field(default_factory=list)
            metadata: dict[str, object] = Field(default_factory=dict)

        class WmsStreamDefinition(BaseModel):
            """Singer stream definition payload."""

            tap_stream_id: str
            stream: str
            schema_: FlextTapOracleWmsModels.TapOracleWms.WmsStreamSchema = Field(
                alias="schema"
            )
            metadata: list[FlextMeltanoModels.Meltano.SingerCatalogMetadata] = Field(
                default_factory=lambda: list[
                    FlextMeltanoModels.Meltano.SingerCatalogMetadata
                ](),
            )


m = FlextTapOracleWmsModels

__all__ = ["FlextTapOracleWmsModels", "m"]

"""Pydantic models used by Oracle WMS tap compatibility layers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, TypedDict

from flext_meltano import FlextMeltanoModels
from flext_oracle_wms import FlextOracleWmsModels
from pydantic import BaseModel, Field

from flext_tap_oracle_wms import t


class FlextTapOracleWmsModels(FlextMeltanoModels, FlextOracleWmsModels):
    """Container for stream schema and metadata payload models."""

    class TapOracleWms:
        """TapOracleWms domain namespace."""

        class SingerMetadataEntry(TypedDict):
            """Singer catalog metadata entry."""

            breadcrumb: list[str]
            metadata: dict[str, t.ContainerValue]

        class SingerStreamEntry(TypedDict):
            """Singer catalog stream entry."""

            tap_stream_id: str
            stream: str
            schema: dict[str, t.ContainerValue]
            metadata: list[FlextTapOracleWmsModels.TapOracleWms.SingerMetadataEntry]

        class SingerCatalogDict(TypedDict):
            """Singer catalog dict with typed streams."""

            streams: list[FlextTapOracleWmsModels.TapOracleWms.SingerStreamEntry]

        class WmsStreamSchema(BaseModel):
            """Singer stream schema shape."""

            type: Annotated[str, Field(default="object")]
            properties: t.ContainerMapping = Field(default_factory=dict)

        class WmsStreamMetadata(BaseModel):
            """Singer stream metadata entry."""

            breadcrumb: t.StrSequence = Field(default_factory=list)
            metadata: t.ContainerMapping = Field(default_factory=dict)

        class WmsStreamDefinition(BaseModel):
            """Singer stream definition payload."""

            tap_stream_id: str
            stream: str
            schema_: Annotated[
                FlextTapOracleWmsModels.TapOracleWms.WmsStreamSchema,
                Field(alias="schema"),
            ]
            metadata: Sequence[FlextMeltanoModels.Meltano.SingerCatalogMetadata] = (
                Field(
                    default_factory=lambda: list[
                        FlextMeltanoModels.Meltano.SingerCatalogMetadata
                    ]()
                )
            )


m = FlextTapOracleWmsModels

__all__ = ["FlextTapOracleWmsModels", "m"]

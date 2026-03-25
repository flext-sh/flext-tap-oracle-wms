"""Pydantic models used by Oracle WMS tap compatibility layers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated

from flext_meltano import FlextMeltanoModels
from flext_oracle_wms import FlextOracleWmsModels
from pydantic import BaseModel, Field

from flext_tap_oracle_wms import t


class FlextTapOracleWmsModels(FlextMeltanoModels, FlextOracleWmsModels):
    """Container for stream schema and metadata payload models."""

    class TapOracleWms:
        """TapOracleWms domain namespace."""

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
                Field(default_factory=list)
            )


m = FlextTapOracleWmsModels

__all__ = ["FlextTapOracleWmsModels", "m"]

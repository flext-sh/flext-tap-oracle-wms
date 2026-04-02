"""Pydantic models used by Oracle WMS tap compatibility layers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, TypedDict

from pydantic import BaseModel, Field

from flext_meltano import FlextMeltanoModels
from flext_oracle_wms import FlextOracleWmsModels
from flext_tap_oracle_wms import t


class FlextTapOracleWmsModels(FlextMeltanoModels, FlextOracleWmsModels):
    """Container for stream schema and metadata payload models."""

    class TapOracleWms:
        """TapOracleWms domain namespace."""

        # --- Singer SDK dict contracts ---
        # These TypedDicts remain intentionally: the Singer SDK protocol
        # exchanges raw dicts (catalog_dict, metadata entries) and
        # consumers (tests, SDK internals) access them with dict syntax
        # (catalog["streams"], stream["tap_stream_id"]).
        # Converting to Pydantic would break the SDK contract boundary.

        class SingerMetadataEntry(TypedDict):
            """Singer catalog metadata entry (Singer SDK dict contract)."""

            breadcrumb: list[str]
            metadata: dict[str, t.ContainerValue]

        class SingerStreamEntry(TypedDict):
            """Singer catalog stream entry (Singer SDK dict contract)."""

            tap_stream_id: str
            stream: str
            schema: dict[str, t.ContainerValue]
            metadata: list[FlextTapOracleWmsModels.TapOracleWms.SingerMetadataEntry]

        class SingerCatalogDict(TypedDict):
            """Singer catalog dict with typed streams (Singer SDK dict contract)."""

            streams: list[FlextTapOracleWmsModels.TapOracleWms.SingerStreamEntry]

        # --- Internal Pydantic models ---

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

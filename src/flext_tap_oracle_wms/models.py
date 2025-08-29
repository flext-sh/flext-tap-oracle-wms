"""Oracle WMS Tap Data Models.

Data models for Oracle WMS tap-specific structures and schema definitions.
Following PEP8 patterns for model organization.
"""

from __future__ import annotations

object

from flext_core import FlextModels.Value
from pydantic import BaseModel, Field


class OracleWMSEntityModel(BaseModel):
    """Base model for Oracle WMS entities."""

    id: str | None = Field(default=None, description="Entity identifier")
    name: str | None = Field(default=None, description="Entity name")
    created_at: str | None = Field(default=None, description="Creation timestamp")
    updated_at: str | None = Field(default=None, description="Last update timestamp")


class StreamMetadata(FlextModels.Value):
    """Stream metadata for Oracle WMS streams."""

    stream_name: str
    primary_keys: list[str]
    replication_method: str = "FULL_TABLE"
    replication_key: str | None = None
    inclusion: str = "available"

    def to_singer_metadata(self) -> list[dict[str, object]]:
        """Convert to Singer metadata format.

        Returns:
            List of Singer metadata entries

        """
        metadata: list[dict[str, object]] = [
            {
                "breadcrumb": [],
                "metadata": {
                    "inclusion": self.inclusion,
                    "forced-replication-method": self.replication_method,
                    "table-key-properties": self.primary_keys,
                },
            },
        ]

        if self.replication_key:
            metadata[0]["metadata"]["replication-key"] = self.replication_key

        return metadata


class StreamSchema(FlextModels.Value):
    """Schema definition for Oracle WMS streams."""

    stream_name: str
    properties: dict[str, dict[str, object]]

    def to_singer_schema(self) -> dict[str, object]:
        """Convert to Singer schema format.

        Returns:
            Singer schema dictionary

        """
        return {
            "type": "object",
            "properties": self.properties,
        }


class CatalogStream(FlextModels.Value):
    """Complete catalog stream definition."""

    tap_stream_id: str
    stream_name: str
    stream_schema: StreamSchema  # Renamed to avoid conflict with BaseModel.schema
    metadata: StreamMetadata

    def to_singer_catalog_entry(self) -> dict[str, object]:
        """Convert to Singer catalog entry format.

        Returns:
            Singer catalog stream entry

        """
        return {
            "tap_stream_id": self.tap_stream_id,
            "stream": self.stream_name,
            "schema": self.stream_schema.to_singer_schema(),
            "metadata": self.metadata.to_singer_metadata(),
        }


__all__ = [
    "CatalogStream",
    "OracleWMSEntityModel",
    "StreamMetadata",
    "StreamSchema",
]

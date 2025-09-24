"""Oracle WMS Tap Data Models.

Data models for Oracle WMS tap-specific structures and schema definitions.
Following PEP8 patterns for model organization.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import Field

from flext_core import FlextModels, FlextTypes


class OracleWMSEntityModel(FlextModels.Entity):
    """Base model for Oracle WMS entities."""

    entity_id: str = Field(..., description="Entity identifier")
    name: str | None = Field(default=None, description="Entity name")
    # Note: created_at and updated_at are inherited from Entity as datetime objects
    # Use oracle_created_at and oracle_updated_at for string timestamps if needed


class StreamMetadata(FlextModels.Config):
    """Stream metadata for Oracle WMS streams."""

    stream_name: str
    primary_keys: FlextTypes.Core.StringList
    replication_method: str = "FULL_TABLE"
    replication_key: str | None = None
    inclusion: str = "available"

    def to_singer_metadata(self: object) -> list[dict[str, object]]:
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
            # Type assertion to help MyPy understand the structure
            metadata_dict = metadata[0]["metadata"]
            if isinstance(metadata_dict, dict):
                metadata_dict["replication-key"] = self.replication_key

        return metadata


class StreamSchema(FlextModels.Config):
    """Schema definition for Oracle WMS streams."""

    stream_name: str
    properties: dict[str, FlextTypes.Core.Dict]

    def to_singer_schema(self: object) -> dict[str, object]:
        """Convert to Singer schema format.

        Returns:
            Singer schema dictionary

        """
        return {
            "type": "object",
            "properties": self.properties,
        }


class CatalogStream(FlextModels.Config):
    """Complete catalog stream definition."""

    tap_stream_id: str
    stream_name: str
    stream_schema: StreamSchema  # Renamed to avoid conflict with BaseModel.schema
    metadata: StreamMetadata

    def to_singer_catalog_entry(self: object) -> dict[str, object]:
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

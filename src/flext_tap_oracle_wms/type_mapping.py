"""Oracle WMS Type Mapping - Uses centralized flext-oracle-wms functionality.

REFACTORED: Uses centralized type mapping - NO DUPLICATION.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from typing import Any

from flext_oracle_wms import (
    flext_oracle_wms_create_type_mapper,
    flext_oracle_wms_map_oracle_to_singer,
)

# Use centralized type mapping - NO DUPLICATION
_type_mapper = flext_oracle_wms_create_type_mapper()


def convert_metadata_type_to_singer(
    wms_type: str,
    format_hint: str | None = None,
) -> str:
    """Convert Oracle WMS metadata type to Singer schema type.

    Args:
        wms_type: Type from Oracle WMS API metadata.
        format_hint: Optional format hint for better type detection.

    Returns:
        Singer schema type string.

    """
    # Use centralized mapping function
    singer_schema = flext_oracle_wms_map_oracle_to_singer(wms_type)
    # Return the primary type (first in the type array)
    return (
        singer_schema["type"][0]
        if isinstance(singer_schema["type"], list)
        else singer_schema["type"]
    )


def get_singer_type_with_metadata(
    wms_type: str,
    field_name: str | None = None,
    format_hint: str | None = None,
) -> dict[str, Any]:
    """Get complete Singer schema type with metadata.

    Args:
        wms_type: Type from Oracle WMS API metadata.
        field_name: Optional field name for field-specific mapping.
        format_hint: Optional format hint for better type detection.

    Returns:
        Complete Singer schema type definition.

    """
    # Use centralized type mapper
    if field_name:
        return _type_mapper.flext_oracle_wms_map_field_by_name(field_name, wms_type)
    return _type_mapper.flext_oracle_wms_map_oracle_type(wms_type)


def get_oracle_to_singer_mapping() -> dict[str, dict[str, Any]]:
    """Get the complete Oracle to Singer type mapping.

    Returns:
        Dictionary mapping Oracle types to Singer schema definitions.

    """
    # Use centralized mapping
    return _type_mapper.type_mappings


# Backward compatibility aliases for existing code
API_METADATA_TO_SINGER = get_oracle_to_singer_mapping()
convert_to_singer_type = convert_metadata_type_to_singer
get_singer_schema = get_singer_type_with_metadata

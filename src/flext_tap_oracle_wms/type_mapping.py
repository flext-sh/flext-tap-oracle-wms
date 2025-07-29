"""Oracle WMS Type Mapping - Uses centralized flext-oracle-wms functionality.

REFACTORED: Uses centralized type mapping - NO DUPLICATION.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from typing import Any

# Import type mapping system from flext-oracle-wms
from flext_oracle_wms.type_mapping import FLEXT_ORACLE_WMS_TYPE_MAPPINGS


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
    # Use centralized mapping
    wms_type_lower = wms_type.lower()
    singer_schema = FLEXT_ORACLE_WMS_TYPE_MAPPINGS.get(wms_type_lower, {"type": "string"})
    # Return the primary type (first in the type array)
    singer_type = singer_schema["type"]
    if isinstance(singer_type, list):
        return str(singer_type[0])
    return str(singer_type)


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
    # Use centralized type mapping
    wms_type_lower = wms_type.lower()
    return FLEXT_ORACLE_WMS_TYPE_MAPPINGS.get(wms_type_lower, {"type": "string"})


def get_oracle_to_singer_mapping() -> dict[str, dict[str, Any]]:
    """Get the complete Oracle to Singer type mapping.

    Returns:
        Dictionary mapping Oracle types to Singer schema definitions.

    """
    # Use centralized mapping
    return FLEXT_ORACLE_WMS_TYPE_MAPPINGS


# Backward compatibility aliases for existing code
API_METADATA_TO_SINGER = get_oracle_to_singer_mapping()
convert_to_singer_type = convert_metadata_type_to_singer
get_singer_schema = get_singer_type_with_metadata

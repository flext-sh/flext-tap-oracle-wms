"""Centralized Type Mapping Module - Metadata-First Pattern.

Ensures consistent type conversion across discovery, table creation, and data sync.
Singer SDK compatible format.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import re
from typing import Any

# API Metadata Type Mappings (Priority 1 - Most Accurate) -> Singer Schema Format
API_METADATA_TO_SINGER: dict[str, dict[str, Any]] = {
    # Primary keys are integers but nullable in Singer
    "pk": {"type": ["integer", "null"]},
    # String fields are unlimited per Singer SDK specification
    "varchar": {"type": ["string", "null"]},
    "text": {"type": ["string", "null"]},
    "string": {"type": ["string", "null"]},
    "char": {"type": ["string", "null"]},
    # Numeric types
    "integer": {"type": ["integer", "null"]},
    "int": {"type": ["integer", "null"]},
    "bigint": {"type": ["integer", "null"]},
    "smallint": {"type": ["integer", "null"]},
    "number": {"type": ["number", "null"]},
    "decimal": {"type": ["number", "null"]},
    "float": {"type": ["number", "null"]},
    "double": {"type": ["number", "null"]},
    # Boolean types
    "boolean": {"type": ["boolean", "null"]},
    "bool": {"type": ["boolean", "null"]},
    # Date/time types
    "date": {"type": ["string", "null"], "format": "date"},
    "datetime": {"type": ["string", "null"], "format": "date-time"},
    "timestamp": {"type": ["string", "null"], "format": "date-time"},
    "time": {"type": ["string", "null"], "format": "time"},
    # JSON/Object types
    "json": {"type": ["object", "string", "null"]},
    "object": {"type": ["object", "null"]},
    # Array types
    "array": {"type": ["array", "null"]},
    # Binary data
    "blob": {"type": ["string", "null"]},
    "binary": {"type": ["string", "null"]},
    # UUID
    "uuid": {
        "type": ["string", "null"],
        "pattern": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    },
}

# Format-specific mappings for better type detection
FORMAT_TO_SINGER: dict[str, dict[str, Any]] = {
    "date-time": {"type": ["string", "null"], "format": "date-time"},
    "date": {"type": ["string", "null"], "format": "date"},
    "time": {"type": ["string", "null"], "format": "time"},
    "email": {"type": ["string", "null"], "format": "email"},
    "uri": {"type": ["string", "null"], "format": "uri"},
    "uuid": {"type": ["string", "null"], "format": "uuid"},
}

# Oracle WMS specific type mappings
WMS_SPECIFIC_TYPES: dict[str, dict[str, Any]] = {
    "facility_code": {"type": ["string", "null"], "maxLength": 10},
    "company_code": {"type": ["string", "null"], "maxLength": 10},
    "item_number": {"type": ["string", "null"], "maxLength": 50},
    "location_id": {"type": ["string", "null"], "maxLength": 20},
    "lot_number": {"type": ["string", "null"], "maxLength": 30},
    "serial_number": {"type": ["string", "null"], "maxLength": 50},
    "order_number": {"type": ["string", "null"], "maxLength": 30},
    "shipment_number": {"type": ["string", "null"], "maxLength": 30},
    "mod_ts": {"type": ["string", "null"], "format": "date-time"},
    "created_dttm": {"type": ["string", "null"], "format": "date-time"},
    "updated_dttm": {"type": ["string", "null"], "format": "date-time"},
}


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
    # Normalize type name
    normalized_type = wms_type.lower().strip()

    # Check format hint first
    if format_hint:
        format_mapping = FORMAT_TO_SINGER.get(format_hint.lower())
        if format_mapping:
            primary_type = format_mapping["type"][0]
            return str(primary_type)  # Return primary type as string

    # Check WMS-specific types
    if normalized_type in WMS_SPECIFIC_TYPES:
        primary_type = WMS_SPECIFIC_TYPES[normalized_type]["type"][0]
        return str(primary_type)

    # Check general API metadata mappings
    if normalized_type in API_METADATA_TO_SINGER:
        primary_type = API_METADATA_TO_SINGER[normalized_type]["type"][0]
        return str(primary_type)

    # Pattern-based type detection
    if re.search(r"(date|time)", normalized_type, re.IGNORECASE):
        if "time" in normalized_type and "date" not in normalized_type:
            return "string"  # time format
        return "string"  # date or datetime format

    if re.search(r"(int|num|dec|float|double)", normalized_type, re.IGNORECASE):
        if "int" in normalized_type:
            return "integer"
        return "number"

    if re.search(r"(bool|flag)", normalized_type, re.IGNORECASE):
        return "boolean"

    # Default to string for unknown types
    return "string"


def get_full_singer_schema(
    wms_type: str,
    format_hint: str | None = None,
    *,
    nullable: bool = True,
) -> dict[str, Any]:
    """Get complete Singer schema definition for a WMS type.

    Args:
        wms_type: Type from Oracle WMS API metadata.
        format_hint: Optional format hint for better type detection.
        nullable: Whether the field should be nullable.

    Returns:
        Complete Singer schema definition.

    """
    # Get base schema from different sources
    schema = _get_base_schema_for_type(wms_type, format_hint)

    # Apply nullable setting and return
    return _apply_nullable_to_schema(schema, nullable=nullable)


def _get_base_schema_for_type(wms_type: str, format_hint: str | None) -> dict[str, Any]:
    """Get base schema from different type mapping sources.

    Args:
        wms_type: Type from Oracle WMS API metadata
        format_hint: Optional format hint for better type detection

    Returns:
        Base schema dictionary for the specified type

    """
    normalized_type = wms_type.lower().strip()

    # Check format hint first
    if format_hint:
        format_mapping = FORMAT_TO_SINGER.get(format_hint.lower())
        if format_mapping:
            return format_mapping.copy()

    # Check WMS-specific types
    if normalized_type in WMS_SPECIFIC_TYPES:
        return WMS_SPECIFIC_TYPES[normalized_type].copy()

    # Check general API metadata mappings
    if normalized_type in API_METADATA_TO_SINGER:
        return API_METADATA_TO_SINGER[normalized_type].copy()

    # Fallback to basic type conversion
    base_type = convert_metadata_type_to_singer(wms_type, format_hint)
    return {"type": base_type}


def _apply_nullable_to_schema(
    schema: dict[str, Any],
    *,
    nullable: bool,
) -> dict[str, Any]:
    """Apply nullable setting to schema.

    Args:
        schema: Base schema dictionary to modify
        nullable: Whether the field should be nullable

    Returns:
        Schema dictionary with nullable setting applied

    """
    if not nullable and isinstance(schema["type"], list) and "null" in schema["type"]:
        # Remove null from type array
        schema["type"] = [t for t in schema["type"] if t != "null"]
        if len(schema["type"]) == 1:
            schema["type"] = schema["type"][0]
    elif nullable and isinstance(schema["type"], str):
        # Add null to single type
        schema["type"] = [schema["type"], "null"]

    return schema


def is_timestamp_field(field_name: str) -> bool:
    """Check if field name indicates a timestamp field.

    Args:
        field_name: Name of the field to check.

    Returns:
        True if field appears to be a timestamp field.

    """
    timestamp_patterns = [
        r".*_ts$",
        r".*_dttm$",
        r".*_date$",
        r".*_time$",
        r"^mod_ts$",
        r"^created_dttm$",
        r"^updated_dttm$",
        r"^last_modified$",
    ]

    field_lower = field_name.lower()
    return any(re.search(pattern, field_lower) for pattern in timestamp_patterns)


def get_primary_key_schema() -> dict[str, Any]:
    """Get schema definition for primary key fields.

    Returns:
        Singer schema definition for primary keys.

    """
    return {"type": ["integer", "null"]}


def get_replication_key_schema() -> dict[str, Any]:
    """Get schema definition for replication key fields (timestamps).

    Returns:
        Singer schema definition for replication keys.

    """
    return {"type": ["string", "null"], "format": "date-time"}

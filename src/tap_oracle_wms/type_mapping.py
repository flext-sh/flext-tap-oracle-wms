#!/usr/bin/env python3
"""Centralized Type Mapping Module - Metadata-First Pattern.

Ensures consistent type conversion across discovery, table creation, and data sync.
Singer SDK compatible format.
"""

from __future__ import annotations

import re
from typing import Any

# API Metadata Type Mappings (Priority 1 - Most Accurate) -> Singer Schema Format
API_METADATA_TO_SINGER: dict[str, dict[str, Any]] = {
    "pk": {
        "type": ["integer", "null"],
    },  # Primary keys are integers but nullable in Singer
    "varchar": {
        "type": ["string", "null"],
        # NO maxLength - String fields are unlimited per Singer SDK specification
    },
    "char": {
        "type": ["string", "null"],
        # NO maxLength - String fields are unlimited per Singer SDK specification
    },
    "number": {"type": ["number", "null"]},
    "decimal": {"type": ["number", "null"]},
    "integer": {"type": ["integer", "null"]},
    "boolean": {"type": ["boolean", "null"]},
    "datetime": {"type": ["string", "null"], "format": "date-time"},
    "date": {"type": ["string", "null"], "format": "date"},
    "time": {"type": ["string", "null"], "format": "time"},
    "text": {
        "type": ["string", "null"]
    },  # NO maxLength - unlimited per Singer SDK specification
    "clob": {
        "type": ["string", "null"]
    },  # NO maxLength - unlimited per Singer SDK specification
    "relation": {
        "type": ["string", "null"],
        # NO maxLength - relationship fields are unlimited per Singer SDK specification
    },
}

# Target-specific mappings are handled by the target/sink - this is source-agnostic

# Field Name Patterns (Priority 2 - Fallback) -> Singer Schema Format
FIELD_PATTERNS_TO_SINGER: dict[str, dict[str, Any]] = {
    # ID fields
    "id_patterns": {"type": ["integer", "null"]},
    "key_patterns": {
        "type": ["string", "null"],
        # NO maxLength - key fields are unlimited per Singer SDK specification
    },
    # Quantity and numeric fields
    "qty_patterns": {"type": ["number", "null"]},
    "price_patterns": {"type": ["number", "null"]},
    "weight_patterns": {"type": ["number", "null"]},
    # Date/time fields
    "date_patterns": {"type": ["string", "null"], "format": "date-time"},
    # Boolean flags
    "flag_patterns": {"type": ["boolean", "null"]},
    # Text fields
    "desc_patterns": {
        "type": ["string", "null"],
    },  # NO maxLength - unlimited per Singer SDK specification
    "code_patterns": {
        "type": ["string", "null"],
    },  # NO maxLength - unlimited per Singer SDK specification
    "name_patterns": {
        "type": ["string", "null"],
    },  # NO maxLength - unlimited per Singer SDK specification
    "addr_patterns": {
        "type": ["string", "null"],
    },  # NO maxLength - unlimited per Singer SDK specification
}

# Pattern matching rules
FIELD_PATTERN_RULES: dict[str, list[str]] = {
    "id_patterns": ["*_id", "id"],
    "key_patterns": ["*_key"],
    "qty_patterns": ["*_qty", "*_quantity", "*_count", "*_amount"],
    "price_patterns": ["*_price", "*_cost", "*_rate", "*_percent"],
    "weight_patterns": ["*_weight", "*_volume", "*_length", "*_width", "*_height"],
    "date_patterns": ["*_date", "*_time", "*_ts", "*_timestamp"],
    "flag_patterns": ["*_flg", "*_flag", "*_enabled", "*_active"],
    "desc_patterns": ["*_desc", "*_description", "*_note", "*_comment"],
    "code_patterns": ["*_code", "*_status", "*_type"],
    "name_patterns": ["*_name", "*_title"],
    "addr_patterns": ["*_addr", "*_address"],
}

# Removed Oracle field patterns - moved to table_creator.py and target_oracle


def convert_metadata_type_to_singer(
    metadata_type: str | None = None,
    column_name: str = "",
    max_length: int | None = None,
) -> dict[str, Any]:
    """Convert WMS metadata type to Singer schema using ONLY metadata and patterns.

    🚨 CRITICAL: Uses ONLY metadata and field name patterns - NO other methods allowed

    Priority:
    1. WMS metadata types (REQUIRED)
    2. Field name patterns (IF metadata missing)
    3. ABORT if neither available

    Args:
        metadata_type: WMS metadata type ('varchar', 'number', etc.)
        column_name: Field name for pattern matching
        max_length: IGNORED - no artificial limits allowed

    Returns:
        Singer schema dict with type information in Singer SDK format

    """
    # Priority 1: WMS metadata types
    if metadata_type and metadata_type.lower() in API_METADATA_TO_SINGER:
        return _create_schema_from_metadata(metadata_type, max_length)

    # Priority 2: Field name patterns
    pattern_schema = _match_field_pattern(column_name, max_length)
    if pattern_schema:
        return pattern_schema

    # 🚨 CRITICAL: NO fallbacks allowed - ABORT if metadata and pattern both fail
    raise SystemExit(
        f"🚨 ABORT: Cannot determine type for field '{column_name}' - "
        f"metadata_type='{metadata_type}' not found and no pattern match. "
        "Schema discovery MUST use ONLY API metadata!"
    )


def _create_schema_from_metadata(
    metadata_type: str,
    max_length: int | None,
) -> dict[str, Any]:
    """Create schema from WMS metadata type."""
    base_schema = API_METADATA_TO_SINGER[metadata_type.lower()]
    schema = {
        "type": base_schema["type"][:],  # Create copy of type array
    }

    # Copy other properties
    if "format" in base_schema:
        schema["format"] = base_schema["format"]
    # NO artificial maxLength limits - removed base schema maxLength
    # NO max_length override - Singer SDK allows unlimited strings
    # WMS API max_length is ignored to prevent artificial limitations

    return schema


def _match_field_pattern(
    column_name: str,
    max_length: int | None,
) -> dict[str, Any] | None:
    """Match field name against patterns and return schema."""
    column_lower = column_name.lower()
    for pattern_key, patterns in FIELD_PATTERN_RULES.items():
        for pattern in patterns:
            if _pattern_matches(pattern, column_lower):
                return _create_pattern_schema(pattern_key, max_length)
    return None


def _pattern_matches(pattern: str, column_lower: str) -> bool:
    """Check if pattern matches column name."""
    pattern_clean = pattern.replace("*_", "").replace("*", "")
    return (
        (pattern.startswith("*_") and column_lower.endswith("_" + pattern_clean))
        or (pattern.endswith("_*") and column_lower.startswith(pattern_clean + "_"))
        or (pattern == column_lower)
    )


def _create_pattern_schema(pattern_key: str, max_length: int | None) -> dict[str, Any]:
    """Create schema from pattern key."""
    pattern_schema = FIELD_PATTERNS_TO_SINGER[pattern_key]
    schema = {
        "type": pattern_schema["type"][:],  # Create copy of type array
    }

    # Copy other properties
    if "format" in pattern_schema:
        schema["format"] = pattern_schema["format"]
    # NO artificial maxLength limits - removed pattern schema maxLength
    # NO max_length override - Singer SDK allows unlimited strings
    # Pattern max_length is ignored to prevent artificial limitations

    return schema


# Oracle conversion functions moved to table_creator.py and target_oracle


def infer_type_enhanced(
    metadata_type: str | None = None,
    column_name: str = "",
) -> dict[str, Any]:
    """🚨 CRITICAL: Enhanced type inference using ONLY metadata and patterns.

    This function provides metadata-only logic for tap discovery consistency.
    Returns Singer SDK compatible schema.

    Args:
        metadata_type: WMS metadata type (REQUIRED priority 1)
        column_name: Field name for pattern matching (priority 2)

    Returns:
        Complete Singer schema dict with type and format information

    """
    # Get base schema from metadata-only conversion
    schema = convert_metadata_type_to_singer(
        metadata_type=metadata_type,
        column_name=column_name,
    )

    # Determine the inferred type for metadata traceability
    inferred_type = metadata_type
    inferred_from = "metadata"

    # If no metadata type, try pattern only - NO other methods allowed
    if not metadata_type:
        if column_name:
            inferred_type = _infer_type_from_pattern(column_name)
            inferred_from = "pattern"
        else:
            # 🚨 CRITICAL: ABORT if no metadata and no pattern
            raise SystemExit(
                f"🚨 ABORT: Cannot infer type for field '{column_name}' - "
                "no metadata_type and no column_name for pattern matching. "
                "Schema discovery MUST use ONLY API metadata!"
            )

    # Add WMS metadata for traceability (Singer SDK allows custom properties)
    schema["x-wms-metadata"] = {
        "original_metadata_type": inferred_type,
        "inferred_from": inferred_from,
        "column_name": column_name,
    }

    return schema


def _infer_type_from_pattern(column_name: str) -> str:
    """Infer WMS-like type from field name pattern."""
    column_lower = column_name.lower()

    # ID patterns -> integer
    if any(
        column_lower.endswith("_" + p.replace("*_", "")) or column_lower == p
        for p in ["id", "*_id"]
    ):
        return "integer"

    # Key patterns -> varchar
    if any(column_lower.endswith("_" + p.replace("*_", "")) for p in ["key"]):
        return "varchar"

    # Quantity patterns -> number
    quantity_patterns = [
        "qty",
        "quantity",
        "count",
        "amount",
        "price",
        "cost",
        "rate",
        "percent",
        "weight",
        "volume",
    ]
    if any(column_lower.endswith("_" + p.replace("*_", "")) for p in quantity_patterns):
        return "number"

    # Date patterns -> datetime
    if any(
        column_lower.endswith("_" + p.replace("*_", "")) or p in column_lower
        for p in ["date", "time", "ts", "timestamp"]
    ):
        return "datetime"

    # Flag patterns -> boolean
    if any(
        column_lower.endswith("_" + p.replace("*_", ""))
        for p in ["flg", "flag", "enabled", "active"]
    ):
        return "boolean"

    # Default to varchar
    return "varchar"


# 🚨 FUNCTION PERMANENTLY DELETED: _infer_type_from_sample
# This function is FORBIDDEN and has been completely removed
# Schema discovery MUST use ONLY API metadata - NO other methods allowed


# 🚨 FUNCTION PERMANENTLY DELETED: _infer_from_sample
# This function is FORBIDDEN and has been completely removed
# Schema discovery MUST use ONLY API metadata - NO other methods allowed


# 🚨 FUNCTION PERMANENTLY DELETED: _infer_string_type
# This function is FORBIDDEN and has been completely removed
# Schema discovery MUST use ONLY API metadata - NO other methods allowed


# 🚨 FUNCTION PERMANENTLY DELETED: _infer_oracle_from_sample
# This function is FORBIDDEN and has been completely removed
# Oracle type mapping belongs in TARGET module, not TAP
# TAP must be GENERIC Singer SDK - doesn't know target is Oracle


def _looks_like_date(value: str) -> bool:
    """Check if string value looks like a date."""
    date_patterns = [
        r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
        r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO datetime
    ]

    return any(re.match(pattern, value) for pattern in date_patterns)


# Convenience functions for Singer SDK only
def get_singer_type(metadata_type: str | None, column_name: str = "") -> dict[str, Any]:
    """Get Singer schema type (backward compatibility)."""
    return convert_metadata_type_to_singer(metadata_type, column_name)


def singer_type_from_wms_metadata(
    metadata_type: str,
    column_name: str = "",
) -> dict[str, Any]:
    """Convert WMS metadata to Singer type in proper Singer SDK format.

    Returns nullable types by default as per Singer best practices.
    """
    return convert_metadata_type_to_singer(metadata_type, column_name)

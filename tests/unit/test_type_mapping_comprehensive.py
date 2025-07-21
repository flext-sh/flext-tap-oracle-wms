"""Comprehensive test suite for type_mapping module."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import pytest

from flext_tap_oracle_wms.type_mapping import (
    API_METADATA_TO_SINGER,
    FORMAT_TO_SINGER,
    WMS_SPECIFIC_TYPES,
    _apply_nullable_to_schema,
    _get_base_schema_for_type,
    convert_metadata_type_to_singer,
    get_full_singer_schema,
    get_primary_key_schema,
    get_replication_key_schema,
    is_timestamp_field,
)


class TestTypeMapping:
    """Test type mapping functionality."""

    def test_api_metadata_mappings(self) -> None:
        """Test API metadata type mappings."""
        # Test primary key mapping
        assert API_METADATA_TO_SINGER["pk"]["type"] == ["integer", "null"]

        # Test string types
        assert API_METADATA_TO_SINGER["varchar"]["type"] == ["string", "null"]
        assert API_METADATA_TO_SINGER["text"]["type"] == ["string", "null"]
        assert API_METADATA_TO_SINGER["string"]["type"] == ["string", "null"]

        # Test numeric types
        assert API_METADATA_TO_SINGER["integer"]["type"] == ["integer", "null"]
        assert API_METADATA_TO_SINGER["number"]["type"] == ["number", "null"]
        assert API_METADATA_TO_SINGER["decimal"]["type"] == ["number", "null"]

        # Test boolean types
        assert API_METADATA_TO_SINGER["boolean"]["type"] == ["boolean", "null"]
        assert API_METADATA_TO_SINGER["bool"]["type"] == ["boolean", "null"]

        # Test date/time types
        assert API_METADATA_TO_SINGER["date"]["format"] == "date"
        assert API_METADATA_TO_SINGER["datetime"]["format"] == "date-time"
        assert API_METADATA_TO_SINGER["timestamp"]["format"] == "date-time"

        # Test UUID type
        assert "pattern" in API_METADATA_TO_SINGER["uuid"]

    def test_format_mappings(self) -> None:
        """Test format-specific mappings."""
        assert FORMAT_TO_SINGER["date-time"]["format"] == "date-time"
        assert FORMAT_TO_SINGER["date"]["format"] == "date"
        assert FORMAT_TO_SINGER["time"]["format"] == "time"
        assert FORMAT_TO_SINGER["email"]["format"] == "email"
        assert FORMAT_TO_SINGER["uri"]["format"] == "uri"
        assert FORMAT_TO_SINGER["uuid"]["format"] == "uuid"

    def test_wms_specific_mappings(self) -> None:
        """Test WMS-specific type mappings."""
        # Test length constraints
        assert WMS_SPECIFIC_TYPES["facility_code"]["maxLength"] == 10
        assert WMS_SPECIFIC_TYPES["company_code"]["maxLength"] == 10
        assert WMS_SPECIFIC_TYPES["item_number"]["maxLength"] == 50
        assert WMS_SPECIFIC_TYPES["location_id"]["maxLength"] == 20

        # Test timestamp fields
        assert WMS_SPECIFIC_TYPES["mod_ts"]["format"] == "date-time"
        assert WMS_SPECIFIC_TYPES["created_dttm"]["format"] == "date-time"
        assert WMS_SPECIFIC_TYPES["updated_dttm"]["format"] == "date-time"

    def test_convert_metadata_type_to_singer_basic_types(self) -> None:
        """Test basic type conversion to Singer format."""
        # String types
        assert convert_metadata_type_to_singer("varchar") == "string"
        assert convert_metadata_type_to_singer("text") == "string"
        assert convert_metadata_type_to_singer("string") == "string"

        # Integer types
        assert convert_metadata_type_to_singer("integer") == "integer"
        assert convert_metadata_type_to_singer("int") == "integer"
        assert convert_metadata_type_to_singer("bigint") == "integer"

        # Number types
        assert convert_metadata_type_to_singer("number") == "number"
        assert convert_metadata_type_to_singer("decimal") == "number"
        assert convert_metadata_type_to_singer("float") == "number"

        # Boolean types
        assert convert_metadata_type_to_singer("boolean") == "boolean"
        assert convert_metadata_type_to_singer("bool") == "boolean"

    def test_convert_metadata_type_to_singer_with_format_hint(self) -> None:
        """Test type conversion with format hints."""
        assert convert_metadata_type_to_singer("string", "date-time") == "string"
        assert convert_metadata_type_to_singer("string", "date") == "string"
        assert convert_metadata_type_to_singer("string", "time") == "string"
        assert convert_metadata_type_to_singer("string", "email") == "string"
        assert convert_metadata_type_to_singer("string", "uri") == "string"
        assert convert_metadata_type_to_singer("string", "uuid") == "string"

    def test_convert_metadata_type_to_singer_wms_specific(self) -> None:
        """Test conversion of WMS-specific types."""
        assert convert_metadata_type_to_singer("facility_code") == "string"
        assert convert_metadata_type_to_singer("company_code") == "string"
        assert convert_metadata_type_to_singer("item_number") == "string"
        assert convert_metadata_type_to_singer("mod_ts") == "string"

    def test_convert_metadata_type_to_singer_pattern_based(self) -> None:
        """Test pattern-based type detection."""
        # Date/time patterns
        assert convert_metadata_type_to_singer("created_date") == "string"
        assert convert_metadata_type_to_singer("updated_time") == "string"
        assert convert_metadata_type_to_singer("modified_datetime") == "string"
        assert convert_metadata_type_to_singer("just_time") == "string"

        # Numeric patterns
        assert convert_metadata_type_to_singer("some_int") == "integer"
        assert convert_metadata_type_to_singer("some_num") == "number"
        assert convert_metadata_type_to_singer("some_dec") == "number"
        assert convert_metadata_type_to_singer("some_float") == "number"
        assert convert_metadata_type_to_singer("some_double") == "number"

        # Boolean patterns
        assert convert_metadata_type_to_singer("is_bool") == "boolean"
        assert convert_metadata_type_to_singer("flag_value") == "boolean"

    def test_convert_metadata_type_to_singer_case_insensitive(self) -> None:
        """Test case-insensitive type conversion."""
        assert convert_metadata_type_to_singer("VARCHAR") == "string"
        assert convert_metadata_type_to_singer("INTEGER") == "integer"
        assert convert_metadata_type_to_singer("BOOLEAN") == "boolean"
        assert convert_metadata_type_to_singer("Number") == "number"

    def test_convert_metadata_type_to_singer_whitespace(self) -> None:
        """Test type conversion with whitespace."""
        assert convert_metadata_type_to_singer("  varchar  ") == "string"
        assert convert_metadata_type_to_singer("\tinteger\n") == "integer"
        assert convert_metadata_type_to_singer(" boolean ") == "boolean"

    def test_convert_metadata_type_to_singer_unknown_type(self) -> None:
        """Test unknown type defaults to string."""
        assert convert_metadata_type_to_singer("unknown_type") == "string"
        assert convert_metadata_type_to_singer("custom_type") == "string"
        assert convert_metadata_type_to_singer("weird123") == "string"

    def test_get_full_singer_schema_basic(self) -> None:
        """Test getting full Singer schema for basic types."""
        # String type
        schema = get_full_singer_schema("varchar")
        assert schema["type"] == ["string", "null"]

        # Integer type
        schema = get_full_singer_schema("integer")
        assert schema["type"] == ["integer", "null"]

        # Boolean type
        schema = get_full_singer_schema("boolean")
        assert schema["type"] == ["boolean", "null"]

    def test_get_full_singer_schema_with_format(self) -> None:
        """Test getting full Singer schema with format hints."""
        schema = get_full_singer_schema("string", "date-time")
        assert schema["type"] == ["string", "null"]
        assert schema["format"] == "date-time"

        schema = get_full_singer_schema("string", "email")
        assert schema["type"] == ["string", "null"]
        assert schema["format"] == "email"

    def test_get_full_singer_schema_wms_specific(self) -> None:
        """Test getting full Singer schema for WMS-specific types."""
        schema = get_full_singer_schema("facility_code")
        assert schema["type"] == ["string", "null"]
        assert schema["maxLength"] == 10

        schema = get_full_singer_schema("item_number")
        assert schema["type"] == ["string", "null"]
        assert schema["maxLength"] == 50

    def test_get_full_singer_schema_nullable_true(self) -> None:
        """Test getting full Singer schema with nullable=True."""
        schema = get_full_singer_schema("varchar", nullable=True)
        assert "null" in schema["type"]

        schema = get_full_singer_schema("integer", nullable=True)
        assert "null" in schema["type"]

    def test_get_full_singer_schema_nullable_false(self) -> None:
        """Test getting full Singer schema with nullable=False."""
        schema = get_full_singer_schema("varchar", nullable=False)
        assert schema["type"] == "string"

        schema = get_full_singer_schema("integer", nullable=False)
        assert schema["type"] == "integer"

    def test_get_base_schema_for_type_format_hint(self) -> None:
        """Test getting base schema with format hint."""
        schema = _get_base_schema_for_type("string", "date-time")
        assert schema["format"] == "date-time"

        schema = _get_base_schema_for_type("string", "email")
        assert schema["format"] == "email"

    def test_get_base_schema_for_type_wms_specific(self) -> None:
        """Test getting base schema for WMS-specific types."""
        schema = _get_base_schema_for_type("facility_code", None)
        assert schema["maxLength"] == 10

        schema = _get_base_schema_for_type("mod_ts", None)
        assert schema["format"] == "date-time"

    def test_get_base_schema_for_type_api_metadata(self) -> None:
        """Test getting base schema for API metadata types."""
        schema = _get_base_schema_for_type("varchar", None)
        assert schema["type"] == ["string", "null"]

        schema = _get_base_schema_for_type("uuid", None)
        assert "pattern" in schema

    def test_get_base_schema_for_type_fallback(self) -> None:
        """Test getting base schema fallback behavior."""
        schema = _get_base_schema_for_type("unknown_type", None)
        assert schema["type"] == "string"

    def test_apply_nullable_to_schema_remove_null(self) -> None:
        """Test removing null from schema type array."""
        schema = {"type": ["string", "null"]}
        result = _apply_nullable_to_schema(schema, nullable=False)
        assert result["type"] == "string"

        schema = {"type": ["integer", "null", "string"]}
        result = _apply_nullable_to_schema(schema, nullable=False)
        assert result["type"] == ["integer", "string"]

    def test_apply_nullable_to_schema_add_null(self) -> None:
        """Test adding null to schema type."""
        schema = {"type": "string"}
        result = _apply_nullable_to_schema(schema, nullable=True)
        assert result["type"] == ["string", "null"]

        schema = {"type": "integer"}
        result = _apply_nullable_to_schema(schema, nullable=True)
        assert result["type"] == ["integer", "null"]

    def test_apply_nullable_to_schema_already_nullable(self) -> None:
        """Test applying nullable to already nullable schema."""
        schema = {"type": ["string", "null"]}
        result = _apply_nullable_to_schema(schema, nullable=True)
        assert result["type"] == ["string", "null"]

    def test_apply_nullable_to_schema_already_non_nullable(self) -> None:
        """Test applying non-nullable to already non-nullable schema."""
        schema = {"type": "string"}
        result = _apply_nullable_to_schema(schema, nullable=False)
        assert result["type"] == "string"

    def test_is_timestamp_field_basic_patterns(self) -> None:
        """Test timestamp field detection with basic patterns."""
        # Positive cases
        assert is_timestamp_field("update_ts") is True
        assert is_timestamp_field("created_dttm") is True
        assert is_timestamp_field("last_modified_date") is True
        assert is_timestamp_field("process_time") is True
        assert is_timestamp_field("mod_ts") is True
        assert is_timestamp_field("updated_dttm") is True
        assert is_timestamp_field("last_modified") is True

        # Negative cases
        assert is_timestamp_field("user_name") is False
        assert is_timestamp_field("item_id") is False
        assert is_timestamp_field("status") is False

    def test_is_timestamp_field_case_insensitive(self) -> None:
        """Test timestamp field detection is case-insensitive."""
        assert is_timestamp_field("UPDATE_TS") is True
        assert is_timestamp_field("Created_Dttm") is True
        assert is_timestamp_field("LAST_MODIFIED") is True
        assert is_timestamp_field("Process_Time") is True

    def test_is_timestamp_field_edge_cases(self) -> None:
        """Test timestamp field detection edge cases."""
        # Empty and None cases handled by pattern matching
        assert is_timestamp_field("") is False

        # Partial matches
        assert is_timestamp_field("timestamp") is False  # No exact pattern match
        assert is_timestamp_field("ts") is False  # Must end with _ts
        assert is_timestamp_field("dttm") is False  # Must end with _dttm

    def test_get_primary_key_schema(self) -> None:
        """Test primary key schema generation."""
        schema = get_primary_key_schema()
        assert schema["type"] == ["integer", "null"]

    def test_get_replication_key_schema(self) -> None:
        """Test replication key schema generation."""
        schema = get_replication_key_schema()
        assert schema["type"] == ["string", "null"]
        assert schema["format"] == "date-time"

    def test_type_mapping_constants_immutable(self) -> None:
        """Test that type mapping constants are properly defined."""
        # Verify that constants exist and have expected structure
        assert isinstance(API_METADATA_TO_SINGER, dict)
        assert isinstance(FORMAT_TO_SINGER, dict)
        assert isinstance(WMS_SPECIFIC_TYPES, dict)

        # Verify some key entries exist
        assert "varchar" in API_METADATA_TO_SINGER
        assert "date-time" in FORMAT_TO_SINGER
        assert "facility_code" in WMS_SPECIFIC_TYPES

    def test_schema_copy_behavior(self) -> None:
        """Test that schema modifications don't affect original mappings."""
        # Get schema for a WMS-specific type
        schema = _get_base_schema_for_type("facility_code", None)
        original_max_length = WMS_SPECIFIC_TYPES["facility_code"]["maxLength"]

        # Modify the returned schema
        schema["maxLength"] = 999

        # Verify original mapping is unchanged
        assert WMS_SPECIFIC_TYPES["facility_code"]["maxLength"] == original_max_length

    def test_integration_with_all_api_types(self) -> None:
        """Test integration with all API metadata types."""
        for wms_type in API_METADATA_TO_SINGER:
            # Should not raise exceptions
            singer_type = convert_metadata_type_to_singer(wms_type)
            assert isinstance(singer_type, str)

            # Should generate valid schema
            schema = get_full_singer_schema(wms_type)
            assert "type" in schema

    def test_integration_with_all_wms_types(self) -> None:
        """Test integration with all WMS-specific types."""
        for wms_type in WMS_SPECIFIC_TYPES:
            # Should not raise exceptions
            singer_type = convert_metadata_type_to_singer(wms_type)
            assert isinstance(singer_type, str)

            # Should generate valid schema
            schema = get_full_singer_schema(wms_type)
            assert "type" in schema

    def test_format_hint_priority(self) -> None:
        """Test that format hints take priority over type mappings."""
        # Even if the base type exists in mappings, format hint should win
        result = convert_metadata_type_to_singer("varchar", "date-time")
        assert result == "string"

        # Verify full schema also respects format hint priority
        schema = get_full_singer_schema("varchar", "date-time")
        assert schema["format"] == "date-time"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

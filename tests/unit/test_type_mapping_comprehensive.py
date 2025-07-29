"""Comprehensive test suite for type_mapping module."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import pytest

from flext_tap_oracle_wms.type_mapping import (
# Constants
EXPECTED_BULK_SIZE = 2

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
        if API_METADATA_TO_SINGER["pk"]["type"] != ["integer", "null"]:
            raise AssertionError(f"Expected {["integer", "null"]}, got {API_METADATA_TO_SINGER["pk"]["type"]}")

        # Test string types
        if API_METADATA_TO_SINGER["varchar"]["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {API_METADATA_TO_SINGER["varchar"]["type"]}")
        assert API_METADATA_TO_SINGER["text"]["type"] == ["string", "null"]
        if API_METADATA_TO_SINGER["string"]["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {API_METADATA_TO_SINGER["string"]["type"]}")

        # Test numeric types
        if API_METADATA_TO_SINGER["integer"]["type"] != ["integer", "null"]:
            raise AssertionError(f"Expected {["integer", "null"]}, got {API_METADATA_TO_SINGER["integer"]["type"]}")
        assert API_METADATA_TO_SINGER["number"]["type"] == ["number", "null"]
        if API_METADATA_TO_SINGER["decimal"]["type"] != ["number", "null"]:
            raise AssertionError(f"Expected {["number", "null"]}, got {API_METADATA_TO_SINGER["decimal"]["type"]}")

        # Test boolean types
        if API_METADATA_TO_SINGER["boolean"]["type"] != ["boolean", "null"]:
            raise AssertionError(f"Expected {["boolean", "null"]}, got {API_METADATA_TO_SINGER["boolean"]["type"]}")
        assert API_METADATA_TO_SINGER["bool"]["type"] == ["boolean", "null"]

        # Test date/time types
        if API_METADATA_TO_SINGER["date"]["format"] != "date":
            raise AssertionError(f"Expected {"date"}, got {API_METADATA_TO_SINGER["date"]["format"]}")
        assert API_METADATA_TO_SINGER["datetime"]["format"] == "date-time"
        if API_METADATA_TO_SINGER["timestamp"]["format"] != "date-time":
            raise AssertionError(f"Expected {"date-time"}, got {API_METADATA_TO_SINGER["timestamp"]["format"]}")

        # Test UUID type
        if "pattern" not in API_METADATA_TO_SINGER["uuid"]:
            raise AssertionError(f"Expected {"pattern"} in {API_METADATA_TO_SINGER["uuid"]}")

    def test_format_mappings(self) -> None:
        """Test format-specific mappings."""
        if FORMAT_TO_SINGER["date-time"]["format"] != "date-time":
            raise AssertionError(f"Expected {"date-time"}, got {FORMAT_TO_SINGER["date-time"]["format"]}")
        assert FORMAT_TO_SINGER["date"]["format"] == "date"
        if FORMAT_TO_SINGER["time"]["format"] != "time":
            raise AssertionError(f"Expected {"time"}, got {FORMAT_TO_SINGER["time"]["format"]}")
        assert FORMAT_TO_SINGER["email"]["format"] == "email"
        if FORMAT_TO_SINGER["uri"]["format"] != "uri":
            raise AssertionError(f"Expected {"uri"}, got {FORMAT_TO_SINGER["uri"]["format"]}")
        assert FORMAT_TO_SINGER["uuid"]["format"] == "uuid"

    def test_wms_specific_mappings(self) -> None:
        """Test WMS-specific type mappings."""
        # Test length constraints
        if WMS_SPECIFIC_TYPES["facility_code"]["maxLength"] != 10:
            raise AssertionError(f"Expected {10}, got {WMS_SPECIFIC_TYPES["facility_code"]["maxLength"]}")
        assert WMS_SPECIFIC_TYPES["company_code"]["maxLength"] == 10
        if WMS_SPECIFIC_TYPES["item_number"]["maxLength"] != 50:
            raise AssertionError(f"Expected {50}, got {WMS_SPECIFIC_TYPES["item_number"]["maxLength"]}")
        assert WMS_SPECIFIC_TYPES["location_id"]["maxLength"] == 20

        # Test timestamp fields
        if WMS_SPECIFIC_TYPES["mod_ts"]["format"] != "date-time":
            raise AssertionError(f"Expected {"date-time"}, got {WMS_SPECIFIC_TYPES["mod_ts"]["format"]}")
        assert WMS_SPECIFIC_TYPES["created_dttm"]["format"] == "date-time"
        if WMS_SPECIFIC_TYPES["updated_dttm"]["format"] != "date-time":
            raise AssertionError(f"Expected {"date-time"}, got {WMS_SPECIFIC_TYPES["updated_dttm"]["format"]}")

    def test_convert_metadata_type_to_singer_basic_types(self) -> None:
        """Test basic type conversion to Singer format."""
        # String types
        if convert_metadata_type_to_singer("varchar") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("varchar")}")
        assert convert_metadata_type_to_singer("text") == "string"
        if convert_metadata_type_to_singer("string") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("string")}")

        # Integer types
        if convert_metadata_type_to_singer("integer") != "integer":
            raise AssertionError(f"Expected {"integer"}, got {convert_metadata_type_to_singer("integer")}")
        assert convert_metadata_type_to_singer("int") == "integer"
        if convert_metadata_type_to_singer("bigint") != "integer":
            raise AssertionError(f"Expected {"integer"}, got {convert_metadata_type_to_singer("bigint")}")

        # Number types
        if convert_metadata_type_to_singer("number") != "number":
            raise AssertionError(f"Expected {"number"}, got {convert_metadata_type_to_singer("number")}")
        assert convert_metadata_type_to_singer("decimal") == "number"
        if convert_metadata_type_to_singer("float") != "number":
            raise AssertionError(f"Expected {"number"}, got {convert_metadata_type_to_singer("float")}")

        # Boolean types
        if convert_metadata_type_to_singer("boolean") != "boolean":
            raise AssertionError(f"Expected {"boolean"}, got {convert_metadata_type_to_singer("boolean")}")
        assert convert_metadata_type_to_singer("bool") == "boolean"

    def test_convert_metadata_type_to_singer_with_format_hint(self) -> None:
        """Test type conversion with format hints."""
        if convert_metadata_type_to_singer("string", "date-time") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("string", "date-time")}")
        assert convert_metadata_type_to_singer("string", "date") == "string"
        if convert_metadata_type_to_singer("string", "time") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("string", "time")}")
        assert convert_metadata_type_to_singer("string", "email") == "string"
        if convert_metadata_type_to_singer("string", "uri") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("string", "uri")}")
        assert convert_metadata_type_to_singer("string", "uuid") == "string"

    def test_convert_metadata_type_to_singer_wms_specific(self) -> None:
        """Test conversion of WMS-specific types."""
        if convert_metadata_type_to_singer("facility_code") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("facility_code")}")
        assert convert_metadata_type_to_singer("company_code") == "string"
        if convert_metadata_type_to_singer("item_number") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("item_number")}")
        assert convert_metadata_type_to_singer("mod_ts") == "string"

    def test_convert_metadata_type_to_singer_pattern_based(self) -> None:
        """Test pattern-based type detection."""
        # Date/time patterns
        if convert_metadata_type_to_singer("created_date") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("created_date")}")
        assert convert_metadata_type_to_singer("updated_time") == "string"
        if convert_metadata_type_to_singer("modified_datetime") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("modified_datetime")}")
        assert convert_metadata_type_to_singer("just_time") == "string"

        # Numeric patterns
        if convert_metadata_type_to_singer("some_int") != "integer":
            raise AssertionError(f"Expected {"integer"}, got {convert_metadata_type_to_singer("some_int")}")
        assert convert_metadata_type_to_singer("some_num") == "number"
        if convert_metadata_type_to_singer("some_dec") != "number":
            raise AssertionError(f"Expected {"number"}, got {convert_metadata_type_to_singer("some_dec")}")
        assert convert_metadata_type_to_singer("some_float") == "number"
        if convert_metadata_type_to_singer("some_double") != "number":
            raise AssertionError(f"Expected {"number"}, got {convert_metadata_type_to_singer("some_double")}")

        # Boolean patterns
        if convert_metadata_type_to_singer("is_bool") != "boolean":
            raise AssertionError(f"Expected {"boolean"}, got {convert_metadata_type_to_singer("is_bool")}")
        assert convert_metadata_type_to_singer("flag_value") == "boolean"

    def test_convert_metadata_type_to_singer_case_insensitive(self) -> None:
        """Test case-insensitive type conversion."""
        if convert_metadata_type_to_singer("VARCHAR") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("VARCHAR")}")
        assert convert_metadata_type_to_singer("INTEGER") == "integer"
        if convert_metadata_type_to_singer("BOOLEAN") != "boolean":
            raise AssertionError(f"Expected {"boolean"}, got {convert_metadata_type_to_singer("BOOLEAN")}")
        assert convert_metadata_type_to_singer("Number") == "number"

    def test_convert_metadata_type_to_singer_whitespace(self) -> None:
        """Test type conversion with whitespace."""
        if convert_metadata_type_to_singer("  varchar  ") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("  varchar  ")}")
        assert convert_metadata_type_to_singer("\tinteger\n") == "integer"
        if convert_metadata_type_to_singer(" boolean ") != "boolean":
            raise AssertionError(f"Expected {"boolean"}, got {convert_metadata_type_to_singer(" boolean ")}")

    def test_convert_metadata_type_to_singer_unknown_type(self) -> None:
        """Test unknown type defaults to string."""
        if convert_metadata_type_to_singer("unknown_type") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("unknown_type")}")
        assert convert_metadata_type_to_singer("custom_type") == "string"
        if convert_metadata_type_to_singer("weird123") != "string":
            raise AssertionError(f"Expected {"string"}, got {convert_metadata_type_to_singer("weird123")}")

    def test_get_full_singer_schema_basic(self) -> None:
        """Test getting full Singer schema for basic types."""
        # String type
        schema = get_full_singer_schema("varchar")
        if schema["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {schema["type"]}")

        # Integer type
        schema = get_full_singer_schema("integer")
        if schema["type"] != ["integer", "null"]:
            raise AssertionError(f"Expected {["integer", "null"]}, got {schema["type"]}")

        # Boolean type
        schema = get_full_singer_schema("boolean")
        if schema["type"] != ["boolean", "null"]:
            raise AssertionError(f"Expected {["boolean", "null"]}, got {schema["type"]}")

    def test_get_full_singer_schema_with_format(self) -> None:
        """Test getting full Singer schema with format hints."""
        schema = get_full_singer_schema("string", "date-time")
        if schema["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {schema["type"]}")
        assert schema["format"] == "date-time"

        schema = get_full_singer_schema("string", "email")
        if schema["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {schema["type"]}")
        assert schema["format"] == "email"

    def test_get_full_singer_schema_wms_specific(self) -> None:
        """Test getting full Singer schema for WMS-specific types."""
        schema = get_full_singer_schema("facility_code")
        if schema["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {schema["type"]}")
        assert schema["maxLength"] == 10

        schema = get_full_singer_schema("item_number")
        if schema["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {schema["type"]}")
        assert schema["maxLength"] == 50

    def test_get_full_singer_schema_nullable_true(self) -> None:
        """Test getting full Singer schema with nullable=True."""
        schema = get_full_singer_schema("varchar", nullable=True)
        if "null" not in schema["type"]:
            raise AssertionError(f"Expected {"null"} in {schema["type"]}")

        schema = get_full_singer_schema("integer", nullable=True)
        if "null" not in schema["type"]:
            raise AssertionError(f"Expected {"null"} in {schema["type"]}")

    def test_get_full_singer_schema_nullable_false(self) -> None:
        """Test getting full Singer schema with nullable=False."""
        schema = get_full_singer_schema("varchar", nullable=False)
        if schema["type"] != "string":
            raise AssertionError(f"Expected {"string"}, got {schema["type"]}")

        schema = get_full_singer_schema("integer", nullable=False)
        if schema["type"] != "integer":
            raise AssertionError(f"Expected {"integer"}, got {schema["type"]}")

    def test_get_base_schema_for_type_format_hint(self) -> None:
        """Test getting base schema with format hint."""
        schema = _get_base_schema_for_type("string", "date-time")
        if schema["format"] != "date-time":
            raise AssertionError(f"Expected {"date-time"}, got {schema["format"]}")

        schema = _get_base_schema_for_type("string", "email")
        if schema["format"] != "email":
            raise AssertionError(f"Expected {"email"}, got {schema["format"]}")

    def test_get_base_schema_for_type_wms_specific(self) -> None:
        """Test getting base schema for WMS-specific types."""
        schema = _get_base_schema_for_type("facility_code", None)
        if schema["maxLength"] != 10:
            raise AssertionError(f"Expected {10}, got {schema["maxLength"]}")

        schema = _get_base_schema_for_type("mod_ts", None)
        if schema["format"] != "date-time":
            raise AssertionError(f"Expected {"date-time"}, got {schema["format"]}")

    def test_get_base_schema_for_type_api_metadata(self) -> None:
        """Test getting base schema for API metadata types."""
        schema = _get_base_schema_for_type("varchar", None)
        if schema["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {schema["type"]}")

        schema = _get_base_schema_for_type("uuid", None)
        if "pattern" not in schema:
            raise AssertionError(f"Expected {"pattern"} in {schema}")

    def test_get_base_schema_for_type_fallback(self) -> None:
        """Test getting base schema fallback behavior."""
        schema = _get_base_schema_for_type("unknown_type", None)
        if schema["type"] != "string":
            raise AssertionError(f"Expected {"string"}, got {schema["type"]}")

    def test_apply_nullable_to_schema_remove_null(self) -> None:
        """Test removing null from schema type array."""
        schema = {"type": ["string", "null"]}
        result = _apply_nullable_to_schema(schema, nullable=False)
        if result["type"] != "string":
            raise AssertionError(f"Expected {"string"}, got {result["type"]}")

        schema = {"type": ["integer", "null", "string"]}
        result = _apply_nullable_to_schema(schema, nullable=False)
        if result["type"] != ["integer", "string"]:
            raise AssertionError(f"Expected {["integer", "string"]}, got {result["type"]}")

    def test_apply_nullable_to_schema_add_null(self) -> None:
        """Test adding null to schema type."""
        schema = {"type": "string"}
        result = _apply_nullable_to_schema(schema, nullable=True)
        if result["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {result["type"]}")

        schema = {"type": "integer"}
        result = _apply_nullable_to_schema(schema, nullable=True)
        if result["type"] != ["integer", "null"]:
            raise AssertionError(f"Expected {["integer", "null"]}, got {result["type"]}")

    def test_apply_nullable_to_schema_already_nullable(self) -> None:
        """Test applying nullable to already nullable schema."""
        schema = {"type": ["string", "null"]}
        result = _apply_nullable_to_schema(schema, nullable=True)
        if result["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {result["type"]}")

    def test_apply_nullable_to_schema_already_non_nullable(self) -> None:
        """Test applying non-nullable to already non-nullable schema."""
        schema = {"type": "string"}
        result = _apply_nullable_to_schema(schema, nullable=False)
        if result["type"] != "string":
            raise AssertionError(f"Expected {"string"}, got {result["type"]}")

    def test_is_timestamp_field_basic_patterns(self) -> None:
        """Test timestamp field detection with basic patterns."""
        # Positive cases
        if not (is_timestamp_field("update_ts")):
            raise AssertionError(f"Expected True, got {is_timestamp_field("update_ts")}")
        assert is_timestamp_field("created_dttm") is True
        if not (is_timestamp_field("last_modified_date")):
            raise AssertionError(f"Expected True, got {is_timestamp_field("last_modified_date")}")
        assert is_timestamp_field("process_time") is True
        if not (is_timestamp_field("mod_ts")):
            raise AssertionError(f"Expected True, got {is_timestamp_field("mod_ts")}")
        assert is_timestamp_field("updated_dttm") is True
        if not (is_timestamp_field("last_modified")):
            raise AssertionError(f"Expected True, got {is_timestamp_field("last_modified")}")

        # Negative cases
        if is_timestamp_field("user_name"):
            raise AssertionError(f"Expected False, got {is_timestamp_field("user_name")}")\ n        assert is_timestamp_field("item_id") is False
        if is_timestamp_field("status"):
            raise AssertionError(f"Expected False, got {is_timestamp_field("status")}")\ n
    def test_is_timestamp_field_case_insensitive(self) -> None:
        """Test timestamp field detection is case-insensitive."""
        if not (is_timestamp_field("UPDATE_TS")):
            raise AssertionError(f"Expected True, got {is_timestamp_field("UPDATE_TS")}")
        assert is_timestamp_field("Created_Dttm") is True
        if not (is_timestamp_field("LAST_MODIFIED")):
            raise AssertionError(f"Expected True, got {is_timestamp_field("LAST_MODIFIED")}")
        assert is_timestamp_field("Process_Time") is True

    def test_is_timestamp_field_edge_cases(self) -> None:
        """Test timestamp field detection edge cases."""
        # Empty and None cases handled by pattern matching
        if is_timestamp_field(""):
            raise AssertionError(f"Expected False, got {is_timestamp_field("")}")\ n
        # Partial matches
        assert is_timestamp_field("timestamp") is False  # No exact pattern match
        assert is_timestamp_field("ts") is False  # Must end with _ts
        assert is_timestamp_field("dttm") is False  # Must end with _dttm

    def test_get_primary_key_schema(self) -> None:
        """Test primary key schema generation."""
        schema = get_primary_key_schema()
        if schema["type"] != ["integer", "null"]:
            raise AssertionError(f"Expected {["integer", "null"]}, got {schema["type"]}")

    def test_get_replication_key_schema(self) -> None:
        """Test replication key schema generation."""
        schema = get_replication_key_schema()
        if schema["type"] != ["string", "null"]:
            raise AssertionError(f"Expected {["string", "null"]}, got {schema["type"]}")
        assert schema["format"] == "date-time"

    def test_type_mapping_constants_immutable(self) -> None:
        """Test that type mapping constants are properly defined."""
        # Verify that constants exist and have expected structure
        assert isinstance(API_METADATA_TO_SINGER, dict)
        assert isinstance(FORMAT_TO_SINGER, dict)
        assert isinstance(WMS_SPECIFIC_TYPES, dict)

        # Verify some key entries exist
        if "varchar" not in API_METADATA_TO_SINGER:
            raise AssertionError(f"Expected {"varchar"} in {API_METADATA_TO_SINGER}")
        assert "date-time" in FORMAT_TO_SINGER
        if "facility_code" not in WMS_SPECIFIC_TYPES:
            raise AssertionError(f"Expected {"facility_code"} in {WMS_SPECIFIC_TYPES}")

    def test_schema_copy_behavior(self) -> None:
        """Test that schema modifications don't affect original mappings."""
        # Get schema for a WMS-specific type
        schema = _get_base_schema_for_type("facility_code", None)
        original_max_length = WMS_SPECIFIC_TYPES["facility_code"]["maxLength"]

        # Modify the returned schema
        schema["maxLength"] = 999

        # Verify original mapping is unchanged
        if WMS_SPECIFIC_TYPES["facility_code"]["maxLength"] != original_max_length:
            raise AssertionError(f"Expected {original_max_length}, got {WMS_SPECIFIC_TYPES["facility_code"]["maxLength"]}")

    def test_integration_with_all_api_types(self) -> None:
        """Test integration with all API metadata types."""
        for wms_type in API_METADATA_TO_SINGER:
            # Should not raise exceptions
            singer_type = convert_metadata_type_to_singer(wms_type)
            assert isinstance(singer_type, str)

            # Should generate valid schema
            schema = get_full_singer_schema(wms_type)
            if "type" not in schema:
                raise AssertionError(f"Expected {"type"} in {schema}")

    def test_integration_with_all_wms_types(self) -> None:
        """Test integration with all WMS-specific types."""
        for wms_type in WMS_SPECIFIC_TYPES:
            # Should not raise exceptions
            singer_type = convert_metadata_type_to_singer(wms_type)
            assert isinstance(singer_type, str)

            # Should generate valid schema
            schema = get_full_singer_schema(wms_type)
            if "type" not in schema:
                raise AssertionError(f"Expected {"type"} in {schema}")

    def test_format_hint_priority(self) -> None:
        """Test that format hints take priority over type mappings."""
        # Even if the base type exists in mappings, format hint should win
        result = convert_metadata_type_to_singer("varchar", "date-time")
        if result != "string":
            raise AssertionError(f"Expected {"string"}, got {result}")

        # Verify full schema also respects format hint priority
        schema = get_full_singer_schema("varchar", "date-time")
        if schema["format"] != "date-time":
            raise AssertionError(f"Expected {"date-time"}, got {schema["format"]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

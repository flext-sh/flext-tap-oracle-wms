"""Comprehensive test suite for type_mapping module using refactored functionality.

Tests Oracle WMS type mapping using centralized flext-oracle-wms patterns.
"""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import pytest

from flext_tap_oracle_wms.type_mapping import (
    API_METADATA_TO_SINGER,
    FLEXT_ORACLE_WMS_TYPE_MAPPINGS,
    convert_metadata_type_to_singer,
    convert_to_singer_type,
    get_oracle_to_singer_mapping,
    get_singer_schema,
    get_singer_type_with_metadata,
)

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class TestOracleWMSTypeMappings:
    """Test Oracle WMS type mapping functionality."""

    def test_flext_oracle_wms_type_mappings_structure(self) -> None:
        """Test the structure of the type mappings dictionary."""
        assert isinstance(FLEXT_ORACLE_WMS_TYPE_MAPPINGS, dict)
        assert len(FLEXT_ORACLE_WMS_TYPE_MAPPINGS) > 0

        # Check that common Oracle types are present
        assert "string" in FLEXT_ORACLE_WMS_TYPE_MAPPINGS
        assert "varchar" in FLEXT_ORACLE_WMS_TYPE_MAPPINGS
        assert "varchar2" in FLEXT_ORACLE_WMS_TYPE_MAPPINGS
        assert "number" in FLEXT_ORACLE_WMS_TYPE_MAPPINGS
        assert "integer" in FLEXT_ORACLE_WMS_TYPE_MAPPINGS
        assert "date" in FLEXT_ORACLE_WMS_TYPE_MAPPINGS
        assert "timestamp" in FLEXT_ORACLE_WMS_TYPE_MAPPINGS

    def test_basic_string_types(self) -> None:
        """Test basic string type mappings."""
        string_types = ["string", "varchar", "varchar2", "char", "nvarchar", "nvarchar2", "nchar"]

        for oracle_type in string_types:
            mapping = FLEXT_ORACLE_WMS_TYPE_MAPPINGS[oracle_type]
            assert mapping["type"] == "string"

    def test_numeric_types(self) -> None:
        """Test numeric type mappings."""
        integer_types = ["integer", "int"]
        number_types = ["number", "decimal", "float", "double", "real"]

        for oracle_type in integer_types:
            mapping = FLEXT_ORACLE_WMS_TYPE_MAPPINGS[oracle_type]
            assert mapping["type"] == "integer"

        for oracle_type in number_types:
            mapping = FLEXT_ORACLE_WMS_TYPE_MAPPINGS[oracle_type]
            assert mapping["type"] == "number"

    def test_date_time_types(self) -> None:
        """Test date/time type mappings."""
        date_types = ["date", "timestamp", "timestamp_tz", "timestamp_ltz"]

        for oracle_type in date_types:
            mapping = FLEXT_ORACLE_WMS_TYPE_MAPPINGS[oracle_type]
            assert mapping["type"] == "string"
            assert mapping["format"] == "date-time"

    def test_boolean_type(self) -> None:
        """Test boolean type mapping."""
        mapping = FLEXT_ORACLE_WMS_TYPE_MAPPINGS["boolean"]
        assert mapping["type"] == "boolean"

    def test_blob_types(self) -> None:
        """Test binary/blob type mappings."""
        blob_types = ["clob", "nclob", "blob", "raw", "long", "long_raw"]

        for oracle_type in blob_types:
            mapping = FLEXT_ORACLE_WMS_TYPE_MAPPINGS[oracle_type]
            assert mapping["type"] == "string"


class TestConvertMetadataTypeToSinger:
    """Test convert_metadata_type_to_singer function."""

    def test_valid_oracle_types(self) -> None:
        """Test conversion of valid Oracle types to Singer types."""
        # String types
        assert convert_metadata_type_to_singer("VARCHAR2") == "string"
        assert convert_metadata_type_to_singer("varchar") == "string"
        assert convert_metadata_type_to_singer("CHAR") == "string"

        # Numeric types
        assert convert_metadata_type_to_singer("NUMBER") == "number"
        assert convert_metadata_type_to_singer("integer") == "integer"
        assert convert_metadata_type_to_singer("DECIMAL") == "number"

        # Date types
        assert convert_metadata_type_to_singer("DATE") == "string"
        assert convert_metadata_type_to_singer("timestamp") == "string"

        # Boolean
        assert convert_metadata_type_to_singer("BOOLEAN") == "boolean"

    def test_case_insensitive_conversion(self) -> None:
        """Test that type conversion is case-insensitive."""
        assert convert_metadata_type_to_singer("VARCHAR2") == "string"
        assert convert_metadata_type_to_singer("varchar2") == "string"
        assert convert_metadata_type_to_singer("VarChar2") == "string"

    def test_unknown_type_defaults_to_string(self) -> None:
        """Test that unknown types default to string."""
        assert convert_metadata_type_to_singer("UNKNOWN_TYPE") == "string"
        assert convert_metadata_type_to_singer("CUSTOM_TYPE") == "string"

    def test_with_format_hint(self) -> None:
        """Test conversion with format hint (currently unused but parameter exists)."""
        # Format hint is accepted but not currently used in implementation
        assert convert_metadata_type_to_singer("VARCHAR2", "email") == "string"
        assert convert_metadata_type_to_singer("NUMBER", "currency") == "number"


class TestGetSingerTypeWithMetadata:
    """Test get_singer_type_with_metadata function."""

    def test_complete_schema_for_varchar(self) -> None:
        """Test complete schema generation for VARCHAR type."""
        schema = get_singer_type_with_metadata("VARCHAR2")
        assert schema["type"] == "string"

    def test_complete_schema_for_date(self) -> None:
        """Test complete schema generation for DATE type."""
        schema = get_singer_type_with_metadata("DATE")
        assert schema["type"] == "string"
        assert schema["format"] == "date-time"

    def test_complete_schema_for_number(self) -> None:
        """Test complete schema generation for NUMBER type."""
        schema = get_singer_type_with_metadata("NUMBER")
        assert schema["type"] == "number"

    def test_with_field_name_and_format_hint(self) -> None:
        """Test schema generation with field name and format hint."""
        # Parameters are accepted but not currently used in implementation
        schema = get_singer_type_with_metadata("VARCHAR2", "email_field", "email")
        assert schema["type"] == "string"

    def test_case_insensitive_schema_generation(self) -> None:
        """Test that schema generation is case-insensitive."""
        schema1 = get_singer_type_with_metadata("VARCHAR2")
        schema2 = get_singer_type_with_metadata("varchar2")
        assert schema1 == schema2


class TestGetOracleToSingerMapping:
    """Test get_oracle_to_singer_mapping function."""

    def test_returns_complete_mapping(self) -> None:
        """Test that function returns the complete type mapping."""
        mapping = get_oracle_to_singer_mapping()

        assert isinstance(mapping, dict)
        assert mapping == FLEXT_ORACLE_WMS_TYPE_MAPPINGS

        # Verify it contains expected types
        assert "varchar2" in mapping
        assert "number" in mapping
        assert "date" in mapping
        assert "boolean" in mapping

    def test_mapping_is_immutable_reference(self) -> None:
        """Test that returned mapping is a reference to the original."""
        mapping = get_oracle_to_singer_mapping()

        # Should be the same object reference
        assert mapping is FLEXT_ORACLE_WMS_TYPE_MAPPINGS


class TestBackwardCompatibilityAliases:
    """Test backward compatibility aliases."""

    def test_api_metadata_to_singer_alias(self) -> None:
        """Test API_METADATA_TO_SINGER backward compatibility alias."""
        assert API_METADATA_TO_SINGER == FLEXT_ORACLE_WMS_TYPE_MAPPINGS

    def test_convert_to_singer_type_alias(self) -> None:
        """Test convert_to_singer_type backward compatibility alias."""
        # Should be the same function
        assert convert_to_singer_type("VARCHAR2") == "string"
        assert convert_to_singer_type("NUMBER") == "number"
        assert convert_to_singer_type("DATE") == "string"

    def test_get_singer_schema_alias(self) -> None:
        """Test get_singer_schema backward compatibility alias."""
        # Should be the same function
        schema = get_singer_schema("VARCHAR2")
        assert schema["type"] == "string"

        schema = get_singer_schema("DATE")
        assert schema["type"] == "string"
        assert schema["format"] == "date-time"


class TestTypeMappingIntegration:
    """Test type mapping integration scenarios."""

    def test_typical_oracle_wms_fields(self) -> None:
        """Test mapping for typical Oracle WMS field types."""
        # Typical WMS fields and their expected Singer types
        wms_field_types = {
            "ITEM_ID": ("VARCHAR2", "string"),
            "ITEM_DESC": ("VARCHAR2", "string"),
            "QTY_ON_HAND": ("NUMBER", "number"),
            "LOCATION_ID": ("VARCHAR2", "string"),
            "CREATED_DATE": ("DATE", "string"),
            "MODIFIED_DATE": ("TIMESTAMP", "string"),
            "IS_ACTIVE": ("BOOLEAN", "boolean"),
            "ITEM_COUNT": ("INTEGER", "integer"),
        }

        for field_name, (oracle_type, expected_singer_type) in wms_field_types.items():
            singer_type = convert_metadata_type_to_singer(oracle_type)
            assert singer_type == expected_singer_type, f"Field {field_name} with type {oracle_type} should map to {expected_singer_type}, got {singer_type}"

    def test_schema_generation_for_wms_table(self) -> None:
        """Test schema generation for a complete WMS table structure."""
        wms_table_structure = {
            "ITEM_ID": "VARCHAR2",
            "ITEM_DESC": "VARCHAR2",
            "QTY_ON_HAND": "NUMBER",
            "UNIT_COST": "DECIMAL",
            "CREATED_DATE": "DATE",
            "LAST_MODIFIED": "TIMESTAMP",
            "IS_SERIALIZED": "BOOLEAN",
        }

        generated_schema = {}
        for field_name, oracle_type in wms_table_structure.items():
            generated_schema[field_name] = get_singer_type_with_metadata(oracle_type)

        # Verify generated schema structure
        assert generated_schema["ITEM_ID"]["type"] == "string"
        assert generated_schema["QTY_ON_HAND"]["type"] == "number"
        assert generated_schema["CREATED_DATE"]["type"] == "string"
        assert generated_schema["CREATED_DATE"]["format"] == "date-time"
        assert generated_schema["IS_SERIALIZED"]["type"] == "boolean"

    def test_error_handling_for_malformed_input(self) -> None:
        """Test error handling for malformed or edge case inputs."""
        # Empty string
        assert convert_metadata_type_to_singer("") == "string"

        # Whitespace
        assert convert_metadata_type_to_singer("   ") == "string"

        # Mixed case with spaces (should be cleaned)
        # Note: Current implementation uses .lower() which handles spaces
        assert convert_metadata_type_to_singer(" VARCHAR2 ") == "string"

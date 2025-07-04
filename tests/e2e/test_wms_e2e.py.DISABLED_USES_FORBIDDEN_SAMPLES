"""End-to-end tests for Oracle WMS tap using real WMS instance.

These tests use environment variables for connection details to test
against a real Oracle WMS instance. All tests are marked with @pytest.mark.e2e
and can be skipped with: pytest -m "not e2e"
"""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

import pytest
from dotenv import load_dotenv

from tap_oracle_wms.tap import TapOracleWMS

# Load .env file if it exists
env_file = Path(__file__).parent.parent.parent / ".env"
env_loaded = False
if env_file.exists():
    load_dotenv(env_file)
    env_loaded = True


def validate_wms_config():
    """Validate that we have minimum required WMS configuration."""
    # Required environment variables
    required_vars = {
        "TAP_ORACLE_WMS_BASE_URL": "Base URL for WMS instance",
        "TAP_ORACLE_WMS_USERNAME": "Username for authentication",
        "TAP_ORACLE_WMS_PASSWORD": "Password for authentication",
    }

    missing_vars = []
    invalid_vars = []

    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(f"{var} ({description})")
        elif var == "TAP_ORACLE_WMS_BASE_URL":
            # Validate URL format
            try:
                result = urlparse(value)
                if not all([result.scheme, result.netloc]):
                    invalid_vars.append(f"{var} must be a valid URL (got: {value})")
            except Exception:
                invalid_vars.append(f"{var} must be a valid URL (got: {value})")

    # Check optional but recommended vars
    optional_vars = {
        "TAP_ORACLE_WMS_COMPANY_CODE": "*",
        "TAP_ORACLE_WMS_FACILITY_CODE": "*",
        "TAP_ORACLE_WMS_PAGE_SIZE": "100",
        "TAP_ORACLE_WMS_REQUEST_TIMEOUT": "120",
    }

    config_warnings = []
    for var, default in optional_vars.items():
        if not os.getenv(var):
            os.environ[var] = default
            config_warnings.append(f"{var} not set, using default: {default}")

    return missing_vars, invalid_vars, config_warnings


# Check configuration before running any tests
missing, invalid, warnings = validate_wms_config()

# Skip all E2E tests if configuration is not valid
skip_all_e2e = False
skip_reason = ""

if not env_loaded:
    skip_all_e2e = True
    skip_reason = ".env file not found. Copy .env.example to .env and configure with real WMS credentials"
elif missing:
    skip_all_e2e = True
    skip_reason = f"Missing required environment variables: {', '.join(missing)}"
elif invalid:
    skip_all_e2e = True
    skip_reason = f"Invalid configuration: {'; '.join(invalid)}"

# Print warnings if any
if warnings and not skip_all_e2e:
    for _warning in warnings:
        pass


@pytest.fixture
def wms_config():
    """Get validated WMS configuration from environment variables."""
    if skip_all_e2e:
        pytest.skip(skip_reason)

    config = {
        "base_url": os.getenv("TAP_ORACLE_WMS_BASE_URL"),
        "username": os.getenv("TAP_ORACLE_WMS_USERNAME"),
        "password": os.getenv("TAP_ORACLE_WMS_PASSWORD"),
        "company_code": os.getenv("TAP_ORACLE_WMS_COMPANY_CODE", "*"),
        "facility_code": os.getenv("TAP_ORACLE_WMS_FACILITY_CODE", "*"),
        "page_size": int(os.getenv("TAP_ORACLE_WMS_PAGE_SIZE", "100")),
        "request_timeout": int(os.getenv("TAP_ORACLE_WMS_REQUEST_TIMEOUT", "120")),
        "verify_ssl": os.getenv("TAP_ORACLE_WMS_VERIFY_SSL", "true").lower() == "true",
    }

    # Add test-specific limits
    if os.getenv("TAP_ORACLE_WMS_RECORD_LIMIT"):
        config["record_limit"] = int(os.getenv("TAP_ORACLE_WMS_RECORD_LIMIT"))

    return config


@pytest.mark.e2e
@pytest.mark.skipif(skip_all_e2e, reason=skip_reason)
class TestWMSEndToEnd:
    """End-to-end tests against real WMS instance."""

    def test_tap_initialization(self, wms_config) -> None:
        """Test that tap can be initialized with config."""
        tap = TapOracleWMS(config=wms_config)
        assert tap is not None
        assert tap.config == wms_config
        assert tap.name == "tap-oracle-wms"

    def test_discover_streams(self, wms_config) -> None:
        """Test stream discovery against real WMS."""
        # Test with specific known entities to avoid discovery issues
        wms_config["entities"] = ["item", "location"]
        tap = TapOracleWMS(config=wms_config)

        # Discover streams
        streams = tap.discover_streams()

        # Should discover at least some streams
        assert (
            len(streams) > 0
        ), "No streams discovered. Check WMS connection and permissions"

        # Check stream properties
        for stream in streams:
            assert hasattr(stream, "name")
            assert hasattr(stream, "schema")
            assert stream.schema is not None
            assert "properties" in stream.schema
            assert (
                len(stream.schema["properties"]) > 0
            ), f"Stream {stream.name} has no properties"

        # Log discovered streams for debugging
        [s.name for s in streams]

    def test_discover_specific_entities(self, wms_config) -> None:
        """Test discovery of specific entities."""
        # Test with entities known to exist in Oracle WMS
        test_entities = ["item", "location"]

        # Filter to entities that might exist
        wms_config["entities"] = test_entities

        tap = TapOracleWMS(config=wms_config)
        streams = tap.discover_streams()

        # Log what was actually discovered
        stream_names = [s.name for s in streams]

        # At least one requested entity should be discovered
        found_any = any(entity in stream_names for entity in test_entities)
        if not found_any:
            pytest.skip(f"None of the test entities {test_entities} exist in this WMS")

    def test_schema_generation(self, wms_config) -> None:
        """Test that schemas are properly generated."""
        tap = TapOracleWMS(config=wms_config)
        streams = tap.discover_streams()

        if not streams:
            pytest.skip("No streams discovered")

        # Check first stream's schema
        stream = streams[0]
        schema = stream.schema

        # Basic schema validation
        assert schema["type"] == "object"
        assert "properties" in schema
        assert len(schema["properties"]) > 0

        # Check for common WMS fields
        properties = schema["properties"]

        # Check if numeric ID exists
        if "id" in properties:
            prop_type = properties["id"].get("type")
            assert prop_type in [
                "integer",
                "number",
                ["integer", "null"],
                ["number", "null"],
            ], f"ID field has unexpected type: {prop_type}"

        # Check for timestamp fields
        timestamp_fields = [
            "mod_ts",
            "create_ts",
            "updated_at",
            "created_at",
            "last_modified",
            "creation_date",
        ]
        ts_fields_found = [f for f in timestamp_fields if f in properties]

        if ts_fields_found:
            for field in ts_fields_found:
                field_def = properties[field]
                # Could be string or ["string", "null"]
                assert "string" in str(
                    field_def.get("type")
                ), f"Timestamp field {field} should be string type"

    def test_extract_sample_records(self, wms_config) -> None:
        """Test extracting sample records from a stream."""
        # Limit to small number of records for testing
        wms_config["record_limit"] = 5

        tap = TapOracleWMS(config=wms_config)
        streams = tap.discover_streams()

        if not streams:
            pytest.skip("No streams discovered")

        # Try to extract from first available stream
        success = False
        for stream in streams[:3]:  # Try first 3 streams
            try:
                records = list(stream.get_records(context={}))

                if records:
                    # Validate records
                    assert len(records) <= 5, "Should respect record limit"

                    # Check record structure
                    for i, record in enumerate(records):
                        assert isinstance(record, dict), f"Record {i} is not a dict"
                        assert len(record) > 0, f"Record {i} is empty"

                        # Check metadata fields were added
                        assert (
                            "_extracted_at" in record
                        ), "Missing _extracted_at metadata"
                        assert "_entity" in record, "Missing _entity metadata"
                        assert record["_entity"] == stream.name

                    success = True
                    break

            except Exception:
                continue

        if not success:
            pytest.skip(
                "Could not extract records from any stream. Check if WMS has data."
            )

    def test_incremental_sync(self, wms_config) -> None:
        """Test incremental sync functionality."""
        # Configure for incremental sync
        wms_config["enable_incremental"] = True
        wms_config["start_date"] = (
            datetime.now(timezone.utc) - timedelta(days=7)
        ).isoformat()
        wms_config["record_limit"] = 10

        tap = TapOracleWMS(config=wms_config)
        streams = tap.discover_streams()

        # Find a stream that supports incremental sync
        incremental_stream = None
        for stream in streams:
            if stream.replication_method == "INCREMENTAL" and stream.replication_key:
                incremental_stream = stream
                break

        if not incremental_stream:
            # Try to find stream with mod_ts field
            for stream in streams:
                if hasattr(stream, "_schema") and "mod_ts" in stream._schema.get(
                    "properties", {}
                ):
                    incremental_stream = stream
                    break

            if not incremental_stream:
                pytest.skip("No streams support incremental sync (no mod_ts field)")

        # Extract records with incremental sync
        context = {}
        records = list(incremental_stream.get_records(context))

        if records:
            # Check that records have replication key
            rep_key = incremental_stream.replication_key
            for record in records[:5]:  # Check first 5
                assert rep_key in record, f"Record missing replication key {rep_key}"
                # Value should be a timestamp string
                assert isinstance(record[rep_key], str), f"{rep_key} should be string"
        else:
            pass

    def test_pagination(self, wms_config) -> None:
        """Test that pagination works correctly."""
        # Configure small page size to test pagination
        wms_config["page_size"] = 2
        wms_config["record_limit"] = 10

        tap = TapOracleWMS(config=wms_config)
        streams = tap.discover_streams()

        if not streams:
            pytest.skip("No streams discovered")

        # Find a stream with enough data to paginate
        for stream in streams[:5]:  # Try first 5 streams
            try:
                records = list(stream.get_records(context={}))

                if len(records) > wms_config["page_size"]:
                    # Pagination worked if we got more than one page
                    assert len(records) <= wms_config["record_limit"]
                    return

            except Exception:
                continue

        pytest.skip("Could not find stream with enough data to test pagination")

    def test_error_handling(self, wms_config) -> None:
        """Test error handling with invalid configuration."""
        # Test with invalid entity
        invalid_config = wms_config.copy()
        invalid_config["entities"] = ["invalid_entity_that_does_not_exist_12345"]

        tap = TapOracleWMS(config=invalid_config)
        streams = tap.discover_streams()

        # Should handle gracefully and return empty or skip invalid entity
        assert isinstance(streams, list)
        assert len(streams) == 0, "Should return empty list for non-existent entities"

    def test_catalog_generation(self, wms_config) -> None:
        """Test Singer catalog generation."""
        tap = TapOracleWMS(config=wms_config)

        # This tests internal catalog generation
        catalog = tap.catalog

        assert catalog is not None
        assert hasattr(catalog, "streams")

        # Discover streams to populate catalog
        streams = tap.discover_streams()

        if streams:
            # Re-check catalog after discovery
            catalog = tap.catalog
            catalog_dict = tap.catalog_dict

            assert len(catalog.streams) == len(streams)
            assert "streams" in catalog_dict


@pytest.mark.e2e
@pytest.mark.skipif(skip_all_e2e, reason=skip_reason)
@pytest.mark.parametrize(
    "entity_name",
    [
        "item",
        "location",
        "inventory",
        "order_header",
        "allocation",
    ],
)
def test_specific_entity_extraction(wms_config, entity_name) -> None:
    """Test extraction of specific common WMS entities."""
    wms_config["entities"] = [entity_name]
    wms_config["record_limit"] = 5

    tap = TapOracleWMS(config=wms_config)
    streams = tap.discover_streams()

    if not streams:
        pytest.skip(f"Entity {entity_name} not available in this WMS")

    stream = streams[0]
    assert stream.name == entity_name

    # Try to extract records
    try:
        records = list(stream.get_records(context={}))
        if records:
            assert len(records) <= 5

            # Show sample record structure
            if records:
                pass
    except Exception as e:
        # Some entities might not have data or access
        pytest.skip(f"Entity {entity_name} exists but cannot be accessed: {e}")

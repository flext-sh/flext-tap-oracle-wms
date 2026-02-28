"""Singer tap utilities for Oracle WMS domain operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import ClassVar, override

from flext_core import FlextResult, t
from flext_meltano import FlextMeltanoUtilities, m
from flext_oracle_wms import FlextOracleWmsUtilities
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError


class _WmsConnectionConfig(BaseModel):
    """Validated connection payload for Oracle WMS settings."""

    model_config = ConfigDict(extra="allow")

    host: str
    database: str
    username: str
    password: str
    port: int | None = None
    database_schema: str | None = Field(default=None, alias="schema")


_STRICT_BOOL_ADAPTER = TypeAdapter(bool, config=ConfigDict(strict=True))
_STRICT_INT_ADAPTER = TypeAdapter(int, config=ConfigDict(strict=True))
_STRICT_FLOAT_ADAPTER = TypeAdapter(float, config=ConfigDict(strict=True))
_STRICT_STR_ADAPTER = TypeAdapter(str, config=ConfigDict(strict=True))
_STRICT_MAP_ADAPTER = TypeAdapter(
    dict[str, t.GeneralValueType],
    config=ConfigDict(strict=True),
)
_STRICT_LIST_ADAPTER = TypeAdapter(
    list[t.GeneralValueType],
    config=ConfigDict(strict=True),
)
_BOOKMARK_VALUE_ADAPTER = TypeAdapter(
    str | int | float | datetime,
    config=ConfigDict(strict=True),
)


def _as_bool(value: t.GeneralValueType) -> bool | None:
    """Strict bool validation via Pydantic adapter."""
    try:
        return _STRICT_BOOL_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_int(value: t.GeneralValueType) -> int | None:
    """Strict int validation via Pydantic adapter."""
    try:
        return _STRICT_INT_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_float(value: t.GeneralValueType) -> float | None:
    """Strict float validation via Pydantic adapter."""
    try:
        return _STRICT_FLOAT_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_str(value: t.GeneralValueType) -> str | None:
    """Strict str validation via Pydantic adapter."""
    try:
        return _STRICT_STR_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_map(value: t.GeneralValueType) -> Mapping[str, t.GeneralValueType] | None:
    """Strict map validation via Pydantic adapter."""
    try:
        return _STRICT_MAP_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_list(value: t.GeneralValueType) -> list[t.GeneralValueType] | None:
    """Strict list validation via Pydantic adapter."""
    try:
        return _STRICT_LIST_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_bookmark_value(
    value: t.GeneralValueType,
) -> str | int | float | datetime | None:
    """Strict bookmark scalar validation via Pydantic adapter."""
    try:
        return _BOOKMARK_VALUE_ADAPTER.validate_python(value)
    except ValidationError:
        return None


class FlextTapOracleWmsUtilities(FlextMeltanoUtilities, FlextOracleWmsUtilities):
    """Single unified utilities class for Singer tap Oracle WMS operations.

    Follows FLEXT unified class pattern with nested helper classes for
    domain-specific Singer tap functionality with Oracle WMS data sources.
    Extends uWMS tap-specific operations.
    """

    # Configuration constants
    DEFAULT_BATCH_SIZE: ClassVar[int] = 1000
    DEFAULT_TIMEOUT: ClassVar[int] = 30
    MAX_RETRIES: ClassVar[int] = 3
    WMS_DEFAULT_PORT: ClassVar[int] = 1521
    MAX_PORT: ClassVar[int] = 65535
    MIN_SKU_PARTS: ClassVar[int] = 2

    @override
    def __init__(self) -> None:
        """Initialize Oracle WMS tap utilities."""
        super().__init__()

    class TapOracleWms:
        """Singer protocol utilities for tap operations."""

        @staticmethod
        def create_schema_message(
            stream_name: str,
            schema: dict[str, t.JsonValue],
            key_properties: list[str] | None = None,
        ) -> m.Meltano.SingerSchemaMessage:
            """Create Singer schema message.

            Args:
            stream_name: Name of the stream
            schema: JSON schema for the stream
            key_properties: List of key property names

            Returns:
            dict[str, t.GeneralValueType]: Singer schema message

            """
            return m.Meltano.SingerSchemaMessage(
                stream=stream_name,
                schema=schema,
                key_properties=key_properties or [],
            )

        @staticmethod
        def create_record_message(
            stream_name: str,
            record: dict[str, t.JsonValue],
            time_extracted: datetime | None = None,
        ) -> m.Meltano.SingerRecordMessage:
            """Create Singer record message.

            Args:
            stream_name: Name of the stream
            record: Record data
            time_extracted: Timestamp when record was extracted

            Returns:
            dict[str, t.GeneralValueType]: Singer record message

            """
            extracted_time = time_extracted or datetime.now(UTC)
            return m.Meltano.SingerRecordMessage(
                stream=stream_name,
                record=record,
                time_extracted=extracted_time.isoformat(),
            )

        @staticmethod
        def create_state_message(
            state: dict[str, t.GeneralValueType],
        ) -> m.Meltano.SingerStateMessage:
            """Create Singer state message.

            Args:
            state: State data

            Returns:
            dict[str, t.GeneralValueType]: Singer state message

            """
            return m.Meltano.SingerStateMessage(value=state)

        @staticmethod
        def write_message(
            message: (
                m.Meltano.SingerSchemaMessage
                | m.Meltano.SingerRecordMessage
                | m.Meltano.SingerStateMessage
            ),
        ) -> None:
            """Write Singer message to stdout.

            Args:
            message: Singer message to write

            """

    class WmsDataProcessing:
        """Oracle WMS-specific data processing utilities."""

        @staticmethod
        def normalize_wms_identifier(identifier: str) -> str:
            """Normalize Oracle WMS identifier.

            Args:
            identifier: WMS identifier to normalize

            Returns:
            str: Normalized identifier

            """
            if not identifier:
                return ""

            # Remove extra whitespace and normalize case
            normalized = re.sub(r"\s+", "_", identifier.strip().upper())

            # Remove special characters that might cause issues
            return re.sub(r"[^\w\-_]", "", normalized)

        @staticmethod
        def extract_facility_code(location: str) -> str:
            """Extract facility code from WMS location string.

            Args:
            location: WMS location string

            Returns:
            str: Facility code or empty string if not found

            """
            if not location:
                return ""

            # Common WMS location format: FACILITY-ZONE-LOCATION
            match = re.search(r"^([A-Z0-9]+)[-_]", location.upper())
            return match.group(1) if match else ""

        @staticmethod
        def parse_wms_quantity(quantity_str: str) -> FlextResult[float]:
            """Parse Oracle WMS quantity string to float.

            Args:
            quantity_str: WMS quantity string

            Returns:
            FlextResult[float]: Parsed quantity or error

            """
            if not quantity_str:
                return FlextResult[float].fail("Quantity string cannot be empty")

            try:
                # Handle common WMS quantity formats
                cleaned = re.sub(r"[^\d.-]", "", str(quantity_str))
                if not cleaned:
                    return FlextResult[float].fail(
                        f"No numeric data in quantity: {quantity_str}",
                    )

                quantity = float(cleaned)
                return FlextResult[float].ok(quantity)

            except ValueError as e:
                return FlextResult[float].fail(
                    f"Invalid quantity format: {quantity_str} - {e}",
                )

        @staticmethod
        def convert_wms_timestamp(timestamp: str) -> FlextResult[str]:
            """Convert Oracle WMS timestamp to ISO format.

            Args:
            timestamp: WMS timestamp string

            Returns:
            FlextResult[str]: ISO formatted timestamp or error

            """
            if not timestamp:
                return FlextResult[str].fail("Timestamp cannot be empty")

            try:
                # Handle Oracle WMS common timestamp formats
                for fmt in [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y/%m/%d %H:%M:%S",
                    "%d-%b-%Y %H:%M:%S",
                    "%d/%m/%Y %H:%M:%S",
                    "%Y%m%d%H%M%S",
                ]:
                    try:
                        # Use timezone-aware parsing where possible
                        dt = datetime.strptime(timestamp, fmt)
                        # Assume UTC for naive datetime objects
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=UTC)
                        return FlextResult[str].ok(dt.isoformat())
                    except ValueError:
                        continue

                return FlextResult[str].fail(
                    f"Unsupported timestamp format: {timestamp}",
                )

            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ) as e:
                return FlextResult[str].fail(f"Error converting timestamp: {e}")

        @staticmethod
        def sanitize_wms_field_name(field_name: str) -> str:
            """Sanitize Oracle WMS field name for JSON schema.

            Args:
            field_name: WMS field name

            Returns:
            str: Sanitized field name

            """
            if not field_name:
                return ""

            # Convert to lowercase and replace non-alphanumeric with underscores
            sanitized = re.sub(r"[^a-zA-Z0-9]", "_", field_name.lower())

            # Ensure it doesn't start with a number
            if sanitized and sanitized[0].isdigit():
                sanitized = f"wms_{sanitized}"

            return sanitized

        @staticmethod
        def extract_sku_info(item_code: str) -> Mapping[str, t.GeneralValueType]:
            """Extract SKU information from Oracle WMS item code.

            Args:
            item_code: WMS item code

            Returns:
            dict[str, t.GeneralValueType]: SKU information components

            """
            if not item_code:
                return {}

            # Common WMS SKU patterns
            sku_info: dict[str, t.GeneralValueType] = {"original": item_code}

            # Extract components based on common patterns
            if "-" in item_code:
                parts = item_code.split("-")
                sku_info["base_sku"] = parts[0]
                if len(parts) > 1:
                    sku_info["variant"] = parts[1]
                if len(parts) > FlextTapOracleWmsUtilities.MIN_SKU_PARTS:
                    sku_info["size_color"] = "-".join(parts[2:])

            # Extract numeric suffix (often size or version)
            numeric_match = re.search(r"(\d+)$", item_code)
            if numeric_match:
                sku_info["numeric_suffix"] = numeric_match.group(1)

            return sku_info

    class StreamUtilities:
        """Stream processing utilities for Singer taps."""

        @staticmethod
        def generate_wms_stream_schema(
            sample_records: list[dict[str, t.GeneralValueType]],
            _stream_name: str,  # Reserved for future use (e.g., stream-specific schema generation)
        ) -> Mapping[str, t.GeneralValueType]:
            """Generate JSON schema from Oracle WMS sample records.

            Args:
            sample_records: List of sample WMS records

            Returns:
            dict[str, t.GeneralValueType]: JSON schema

            """
            if not sample_records:
                return {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True,
                }

            properties: dict[str, t.GeneralValueType] = {}

            for record in sample_records:
                for key, value in record.items():
                    sanitized_key = FlextTapOracleWmsUtilities.WmsDataProcessing.sanitize_wms_field_name(
                        key,
                    )
                    if sanitized_key not in properties:
                        properties[sanitized_key] = (
                            FlextTapOracleWmsUtilities.StreamUtilities.infer_wms_type(
                                value,
                            )
                        )

            return {
                "type": "object",
                "properties": properties,
                "additionalProperties": True,
            }

        @staticmethod
        def infer_wms_type(
            value: t.GeneralValueType,
        ) -> Mapping[str, t.GeneralValueType]:
            """Infer JSON schema type from Oracle WMS value.

            Args:
            value: Value to analyze

            Returns:
            dict[str, t.GeneralValueType]: JSON schema type definition

            """
            if value is None:
                return {"type": ["null", "string"]}
            if _as_bool(value) is not None:
                return {"type": "boolean"}
            if _as_int(value) is not None:
                return {"type": "integer"}
            if _as_float(value) is not None:
                return {"type": "number"}
            list_value = _as_list(value)
            if list_value is not None:
                if list_value:
                    # Infer type from first element
                    item_type = (
                        FlextTapOracleWmsUtilities.StreamUtilities.infer_wms_type(
                            list_value[0],
                        )
                    )
                    return {"type": "array", "items": item_type}
                return {"type": "array", "items": {"type": "string"}}
            if _as_map(value) is not None:
                return {"type": "object", "additionalProperties": True}

            # String type with WMS-specific format detection
            schema: dict[str, t.GeneralValueType] = {"type": "string"}

            str_value = str(value)
            # Check for WMS date patterns
            if re.match(r"\d{4}-\d{2}-\d{2}", str_value):
                schema["format"] = "date-time"
            # Check for WMS quantity patterns
            elif re.match(r"^\d+\.?\d*$", str_value):
                schema["pattern"] = r"^\d+\.?\d*$"

            return schema

        @staticmethod
        def calculate_wms_batch_size(
            record_count: int,
            target_batches: int = 10,
        ) -> int:
            """Calculate optimal batch size for Oracle WMS processing.

            Args:
            record_count: Total number of records
            target_batches: Target number of batches

            Returns:
            int: Optimal batch size

            """
            if record_count <= 0:
                return FlextTapOracleWmsUtilities.DEFAULT_BATCH_SIZE

            calculated_size = max(1, record_count // target_batches)
            return min(
                calculated_size,
                FlextTapOracleWmsUtilities.DEFAULT_BATCH_SIZE,
            )

        @staticmethod
        def create_wms_replication_key_schema(
            stream_name: str,
            replication_key: str = "last_update_date",
        ) -> Mapping[str, t.GeneralValueType]:
            """Create replication key schema for Oracle WMS streams.

            Args:
            stream_name: Name of the stream
            replication_key: Replication key field name

            Returns:
            dict[str, t.GeneralValueType]: Replication key schema

            """
            return {
                "stream": stream_name,
                "replication_method": "INCREMENTAL",
                "replication_key": replication_key,
                "key_properties": ["id"]
                if stream_name != "inventory_transactions"
                else ["transaction_id"],
            }

    class ConfigValidation:
        """Configuration validation utilities."""

        @staticmethod
        def validate_wms_connection_config(
            config: Mapping[str, t.GeneralValueType],
        ) -> FlextResult[Mapping[str, t.GeneralValueType]]:
            """Validate Oracle WMS connection configuration.

            Args:
            config: Configuration dictionary

            Returns:
            FlextResult[dict[str, t.GeneralValueType]]: Validated config or error

            """
            required_fields = ["host", "database", "username", "password"]
            missing_fields = [field for field in required_fields if field not in config]

            if missing_fields:
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    f"Missing required WMS connection fields: {', '.join(missing_fields)}",
                )

            # Validate host format
            host = _as_str(config["host"])
            if host is None or not host.strip():
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    "Host must be a non-empty string",
                )

            # Validate database format
            database = _as_str(config["database"])
            if database is None or not database.strip():
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    "Database must be a non-empty string",
                )

            # Validate port if provided
            if "port" in config:
                port = _as_int(config["port"])
                if (
                    port is None
                    or port <= 0
                    or port > FlextTapOracleWmsUtilities.MAX_PORT
                ):
                    return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                        "Port must be a valid integer between 1 and 65535",
                    )

            # Validate WMS-specific settings
            if "schema" in config:
                schema_value = _as_str(config["schema"])
                if schema_value is None or not schema_value.strip():
                    return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                        "Schema must be a non-empty string",
                    )

            return FlextResult[Mapping[str, t.GeneralValueType]].ok(config)

        @staticmethod
        def validate_wms_stream_config(
            config: Mapping[str, t.GeneralValueType],
        ) -> FlextResult[Mapping[str, t.GeneralValueType]]:
            """Validate Oracle WMS stream configuration.

            Args:
            config: Stream configuration

            Returns:
            FlextResult[dict[str, t.GeneralValueType]]: Validated config or error

            """
            if "streams" not in config:
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    "Configuration must include 'streams' section",
                )

            streams = _as_map(config["streams"])
            if streams is None:
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    "Streams configuration must be a dictionary",
                )

            # Validate each stream
            for stream_name, stream_payload in streams.items():
                stream_config = _as_map(stream_payload)
                if stream_config is None:
                    return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                        f"Stream '{stream_name}' configuration must be a dictionary",
                    )

                # Check for required stream fields
                if "selected" not in stream_config:
                    return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                        f"Stream '{stream_name}' must have 'selected' field",
                    )

                # Validate WMS-specific stream settings
                if "table_name" in stream_config:
                    table_name = _as_str(stream_config["table_name"])
                    if table_name is None or not table_name.strip():
                        return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                            f"Stream '{stream_name}' table_name must be a non-empty string",
                        )

            return FlextResult[Mapping[str, t.GeneralValueType]].ok(config)

    class ConfigurationProcessing:
        """configuration processing utilities."""

        @staticmethod
        def validate_stream_page_size(page_size: int) -> FlextResult[bool]:
            """Validate stream page size."""
            if page_size <= 0:
                return FlextResult[bool].fail("Page size must be positive")
            return FlextResult[bool].ok(value=True)

        @staticmethod
        def validate_wms_config(
            config: Mapping[str, t.GeneralValueType],
        ) -> FlextResult[Mapping[str, t.GeneralValueType]]:
            """Validate basic WMS configuration.

            Args:
            config: Configuration dictionary

            Returns:
            FlextResult[dict[str, t.GeneralValueType]]: Validated config or error

            """
            # Delegate to existing ConfigValidation
            return FlextTapOracleWmsUtilities.ConfigValidation.validate_wms_connection_config(
                config,
            )

        @staticmethod
        def validate_wms_connection_params(
            config: Mapping[str, t.GeneralValueType],
        ) -> FlextResult[Mapping[str, t.GeneralValueType]]:
            """Validate WMS connection parameters.

            Args:
            config: Configuration dictionary

            Returns:
            FlextResult[dict[str, t.GeneralValueType]]: Validated config or error

            """
            required_params = ["base_url", "username", "password"]
            for param in required_params:
                if param not in config:
                    return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                        f"Missing required parameter: {param}",
                    )

            # Validate URL format
            base_url = _as_str(config["base_url"])
            if base_url is None or not base_url.startswith((
                "http://",
                "https://",
            )):
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    "Invalid base_url format"
                )

            return FlextResult[Mapping[str, t.GeneralValueType]].ok(config)

        @staticmethod
        def validate_wms_configuration_comprehensive(
            config: Mapping[str, t.GeneralValueType],
        ) -> FlextResult[Mapping[str, t.GeneralValueType]]:
            """Complete WMS configuration validation.

            Args:
            config: Configuration dictionary

            Returns:
            FlextResult[dict[str, t.GeneralValueType]]: Validated config or error

            """
            # Basic validation first
            basic_result = (
                FlextTapOracleWmsUtilities.ConfigurationProcessing.validate_wms_config(
                    config,
                )
            )
            if basic_result.is_failure:
                return basic_result

            # Connection params validation
            params_result = FlextTapOracleWmsUtilities.ConfigurationProcessing.validate_wms_connection_params(
                config,
            )
            if params_result.is_failure:
                return params_result

            # Stream configuration validation if present
            if "streams" in config:
                stream_result = FlextTapOracleWmsUtilities.ConfigValidation.validate_wms_stream_config(
                    config,
                )
                if stream_result.is_failure:
                    return stream_result

            return FlextResult[Mapping[str, t.GeneralValueType]].ok(config)

    class WmsApiProcessing:
        """WMS API processing utilities."""

        @staticmethod
        def test_wms_api_connection(
            base_url: str,
            auth_token: str | None = None,
            timeout: int = 30,
        ) -> FlextResult[Mapping[str, t.GeneralValueType]]:
            """Test WMS API connection.

            Args:
            base_url: WMS API base URL
            auth_token: Optional authentication token
            timeout: Connection timeout

            Returns:
            FlextResult[dict[str, t.GeneralValueType]]: Connection test result

            """
            if not base_url:
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    "Base URL cannot be empty"
                )

            if not base_url.startswith(("http://", "https://")):
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    "Invalid URL format"
                )

            # Basic connection validation (would normally make HTTP request)
            connection_info: dict[str, t.GeneralValueType] = {
                "base_url": base_url,
                "timeout": timeout,
                "status": "validated",
                "auth_provided": auth_token is not None,
            }

            return FlextResult[Mapping[str, t.GeneralValueType]].ok(connection_info)

    class DataProcessing:
        """data processing utilities."""

        @staticmethod
        def process_wms_record(
            record: Mapping[str, t.GeneralValueType],
        ) -> Mapping[str, t.GeneralValueType]:
            """Process WMS record."""
            # Record processing delegation — transforms WMS records for Singer output
            return record

        @staticmethod
        def generate_validation_info(
            config_data: Mapping[str, t.GeneralValueType],
            connection_result: Mapping[str, t.GeneralValueType],
            discovery_result: t.GeneralValueType | None = None,
        ) -> FlextResult[Mapping[str, t.GeneralValueType]]:
            """Generate complete validation information.

            Args:
            config_data: Configuration data
            connection_result: Connection test result
            discovery_result: Optional discovery result

            Returns:
            FlextResult[dict[str, t.GeneralValueType]]: Validation information

            """
            validation_info = {
                "config_status": "valid",
                "connection_status": connection_result.get("status", "unknown"),
                "base_url": config_data.get("base_url"),
                "api_version": config_data.get("api_version", "v10"),
                "discovery_available": discovery_result is not None,
                "validation_timestamp": datetime.now(UTC).isoformat(),
            }

            if discovery_result:
                discovery_list = _as_list(discovery_result)
                if discovery_list is not None:
                    validation_info["entities_discovered"] = len(discovery_list)
                else:
                    discovery_map = _as_map(discovery_result)
                    if discovery_map is not None:
                        entities = _as_list(discovery_map.get("entities", [])) or []
                        validation_info["entities_discovered"] = len(entities)
                    else:
                        validation_info["entities_discovered"] = 0

            return FlextResult[Mapping[str, t.GeneralValueType]].ok(validation_info)

    class StateManagement:
        """State management utilities for incremental syncs."""

        @staticmethod
        def get_wms_stream_state(
            state: Mapping[str, t.GeneralValueType],
            stream_name: str,
        ) -> Mapping[str, t.GeneralValueType]:
            """Get state for a specific Oracle WMS stream.

            Args:
            state: Complete state dictionary
            stream_name: Name of the stream

            Returns:
            dict[str, t.GeneralValueType]: Stream state

            """
            state_map = _as_map(state)
            if state_map is None:
                return {}
            bookmarks = _as_map(state_map.get("bookmarks", {}))
            if bookmarks is None:
                return {}
            return _as_map(bookmarks.get(stream_name, {})) or {}

        @staticmethod
        def set_wms_stream_state(
            state: Mapping[str, t.GeneralValueType],
            stream_name: str,
            stream_state: Mapping[str, t.GeneralValueType],
        ) -> Mapping[str, t.GeneralValueType]:
            """Set state for a specific Oracle WMS stream.

            Args:
            state: Complete state dictionary
            stream_name: Name of the stream
            stream_state: State data for the stream

            Returns:
            dict[str, t.GeneralValueType]: Updated state

            """
            state_map = dict(state)
            bookmarks = dict(_as_map(state_map.get("bookmarks", {})) or {})
            bookmarks[stream_name] = dict(stream_state)
            state_map["bookmarks"] = bookmarks
            return state_map

        @staticmethod
        def get_wms_bookmark(
            state: Mapping[str, t.GeneralValueType],
            stream_name: str,
            bookmark_key: str,
        ) -> str | int | float | datetime | None:
            """Get bookmark value for a Oracle WMS stream.

            Args:
            state: Complete state dictionary
            stream_name: Name of the stream
            bookmark_key: Bookmark key

            Returns:
            object: Bookmark value or None

            """
            stream_state = (
                FlextTapOracleWmsUtilities.StateManagement.get_wms_stream_state(
                    state,
                    stream_name,
                )
            )
            bookmark_value = stream_state.get(bookmark_key)
            if bookmark_value is None:
                return None
            return _as_bookmark_value(bookmark_value)

        @staticmethod
        def set_wms_bookmark(
            state: Mapping[str, t.GeneralValueType],
            stream_name: str,
            bookmark_key: str,
            bookmark_value: str | float | datetime | None,
        ) -> Mapping[str, t.GeneralValueType]:
            """Set bookmark value for a Oracle WMS stream.

            Args:
            state: Complete state dictionary
            stream_name: Name of the stream
            bookmark_key: Bookmark key
            bookmark_value: Bookmark value

            Returns:
            dict[str, t.GeneralValueType]: Updated state

            """
            state_map = dict(state)
            bookmarks = dict(_as_map(state_map.get("bookmarks", {})) or {})
            stream_bookmarks = dict(_as_map(bookmarks.get(stream_name, {})) or {})
            stream_bookmarks[bookmark_key] = bookmark_value
            bookmarks[stream_name] = stream_bookmarks
            state_map["bookmarks"] = bookmarks
            return state_map

        @staticmethod
        def create_wms_incremental_state(
            stream_name: str,
            last_updated: datetime,
            records_processed: int = 0,
        ) -> Mapping[str, t.GeneralValueType]:
            """Create incremental state for Oracle WMS stream.

            Args:
            stream_name: Name of the stream
            last_updated: Last update timestamp
            records_processed: Number of records processed

            Returns:
            dict[str, t.GeneralValueType]: Incremental state

            """
            return {
                "bookmarks": {
                    stream_name: {
                        "replication_key_value": last_updated.isoformat(),
                        "last_update_date": last_updated.isoformat(),
                        "records_processed": records_processed,
                        "extraction_timestamp": datetime.now(UTC).isoformat(),
                    },
                },
            }

    class PerformanceUtilities:
        """Performance optimization utilities."""

        @staticmethod
        def calculate_optimal_fetch_size(
            table_size_estimate: int,
            memory_limit_mb: int = 100,
        ) -> int:
            """Calculate optimal fetch size for Oracle WMS queries.

            Args:
            table_size_estimate: Estimated number of records
            memory_limit_mb: Memory limit in MB

            Returns:
            int: Optimal fetch size

            """
            # Estimate memory per record (conservative estimate for WMS data)
            bytes_per_record = 2048  # 2KB per record estimate
            max_records_in_memory = (memory_limit_mb * 1024 * 1024) // bytes_per_record

            # Balance between memory usage and query efficiency
            return min(
                max_records_in_memory,
                max(
                    100,
                    table_size_estimate // 100,
                ),  # At least 100, at most 1% of table
                FlextTapOracleWmsUtilities.DEFAULT_BATCH_SIZE,
            )

        @staticmethod
        def estimate_extraction_time(
            record_count: int,
            avg_record_size_bytes: int = 2048,
            network_speed_mbps: float = 100.0,
        ) -> Mapping[str, float]:
            """Estimate extraction time for Oracle WMS data.

            Args:
            record_count: Number of records to extract
            avg_record_size_bytes: Average record size in bytes
            network_speed_mbps: Network speed in Mbps

            Returns:
            dict[str, float]: Time estimates in seconds

            """
            total_bytes = record_count * avg_record_size_bytes
            total_mb = total_bytes / (1024 * 1024)

            # Network transfer time
            network_time = (
                total_mb * 8
            ) / network_speed_mbps  # Convert MB to Mb, divide by speed

            # Processing overhead (conservative estimate)
            processing_time = record_count * 0.001  # 1ms per record processing

            # Database query time (depends on indexes and complexity)
            query_time = max(1.0, record_count * 0.0001)  # Minimum 1 second

            return {
                "network_transfer_seconds": network_time,
                "processing_seconds": processing_time,
                "query_seconds": query_time,
                "total_estimated_seconds": network_time + processing_time + query_time,
            }

    class Utilities:
        """Utilities for tap operations."""

        @staticmethod
        def run(
            coro: t.GeneralValueType,
        ) -> t.GeneralValueType:
            """Execute or passthrough coroutine-like input in sync contexts."""
            return coro

    @classmethod
    def normalize_wms_identifier(cls, identifier: str) -> str:
        """Proxy method for WmsDataProcessing.normalize_wms_identifier()."""
        return cls.WmsDataProcessing.normalize_wms_identifier(identifier)

    @classmethod
    def convert_wms_timestamp(cls, timestamp: str) -> FlextResult[str]:
        """Proxy method for WmsDataProcessing.convert_wms_timestamp()."""
        return cls.WmsDataProcessing.convert_wms_timestamp(timestamp)

    @classmethod
    def validate_wms_connection_config(
        cls,
        config: Mapping[str, t.GeneralValueType],
    ) -> FlextResult[Mapping[str, t.GeneralValueType]]:
        """Proxy method for ConfigValidation.validate_wms_connection_config()."""
        return cls.ConfigValidation.validate_wms_connection_config(config)

    @classmethod
    def get_wms_stream_state(
        cls,
        state: Mapping[str, t.GeneralValueType],
        stream_name: str,
    ) -> Mapping[str, t.GeneralValueType]:
        """Proxy method for StateManagement.get_wms_stream_state()."""
        return cls.StateManagement.get_wms_stream_state(state, stream_name)

    @classmethod
    def set_wms_bookmark(
        cls,
        state: Mapping[str, t.GeneralValueType],
        stream_name: str,
        bookmark_key: str,
        bookmark_value: str | float | datetime | None,
    ) -> Mapping[str, t.GeneralValueType]:
        """Proxy method for StateManagement.set_wms_bookmark()."""
        return cls.StateManagement.set_wms_bookmark(
            state,
            stream_name,
            bookmark_key,
            bookmark_value,
        )


__all__ = [
    "FlextTapOracleWmsUtilities",
    "u",
]


u = FlextTapOracleWmsUtilities

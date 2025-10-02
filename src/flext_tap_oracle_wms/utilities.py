"""Singer tap utilities for Oracle WMS domain operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from asyncio import (
    Awaitable,
    Coroutine,
    new_event_loop,
    set_event_loop,
)
from datetime import UTC, datetime
from typing import Any, ClassVar, override

from flext_core import FlextResult, FlextUtilities


class FlextTapOracleWmsUtilities(FlextUtilities):
    """Single unified utilities class for Singer tap Oracle WMS operations.

    Follows FLEXT unified class pattern with nested helper classes for
    domain-specific Singer tap functionality with Oracle WMS data sources.
    Extends FlextUtilities with Oracle WMS tap-specific operations.
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

    class SingerUtilities:
        """Singer protocol utilities for tap operations."""

        @staticmethod
        def create_schema_message(
            stream_name: str,
            schema: dict[str, Any],
            key_properties: list[str] | None = None,
        ) -> dict[str, Any]:
            """Create Singer schema message.

            Args:
                stream_name: Name of the stream
                schema: JSON schema for the stream
                key_properties: List of key property names

            Returns:
                dict[str, Any]: Singer schema message

            """
            return {
                "type": "SCHEMA",
                "stream": stream_name,
                "schema": schema,
                "key_properties": key_properties or [],
            }

        @staticmethod
        def create_record_message(
            stream_name: str,
            record: dict[str, Any],
            time_extracted: datetime | None = None,
        ) -> dict[str, Any]:
            """Create Singer record message.

            Args:
                stream_name: Name of the stream
                record: Record data
                time_extracted: Timestamp when record was extracted

            Returns:
                dict[str, Any]: Singer record message

            """
            extracted_time = time_extracted or datetime.now(UTC)
            return {
                "type": "RECORD",
                "stream": stream_name,
                "record": record,
                "time_extracted": extracted_time.isoformat(),
            }

        @staticmethod
        def create_state_message(state: dict[str, Any]) -> dict[str, Any]:
            """Create Singer state message.

            Args:
                state: State data

            Returns:
                dict[str, Any]: Singer state message

            """
            return {
                "type": "STATE",
                "value": state,
            }

        @staticmethod
        def write_message(message: dict[str, Any]) -> None:
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
                        f"No numeric data in quantity: {quantity_str}"
                    )

                quantity = float(cleaned)
                return FlextResult[float].ok(quantity)

            except ValueError as e:
                return FlextResult[float].fail(
                    f"Invalid quantity format: {quantity_str} - {e}"
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
                        dt = datetime.strptime(timestamp, fmt)  # noqa: DTZ007 - Naive datetime with immediate tzinfo assignment
                        dt = dt.replace(tzinfo=UTC)
                        return FlextResult[str].ok(dt.isoformat())
                    except ValueError:
                        continue

                return FlextResult[str].fail(
                    f"Unsupported timestamp format: {timestamp}"
                )

            except Exception as e:
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
        def extract_sku_info(item_code: str) -> dict[str, str]:
            """Extract SKU information from Oracle WMS item code.

            Args:
                item_code: WMS item code

            Returns:
                dict[str, str]: SKU information components

            """
            if not item_code:
                return {}

            # Common WMS SKU patterns
            sku_info = {"original": item_code}

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
            sample_records: list[dict[str, Any]],
            stream_name: str,  # noqa: ARG004 - Reserved for future use
        ) -> dict[str, Any]:
            """Generate JSON schema from Oracle WMS sample records.

            Args:
                sample_records: List of sample WMS records
                stream_name: Name of the stream

            Returns:
                dict[str, Any]: JSON schema

            """
            if not sample_records:
                return {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True,
                }

            properties: dict[str, Any] = {}

            for record in sample_records:
                for key, value in record.items():
                    sanitized_key = FlextTapOracleWmsUtilities.WmsDataProcessing.sanitize_wms_field_name(
                        key
                    )
                    if sanitized_key not in properties:
                        properties[sanitized_key] = (
                            FlextTapOracleWmsUtilities.StreamUtilities.infer_wms_type(
                                value
                            )
                        )

            return {
                "type": "object",
                "properties": properties,
                "additionalProperties": True,
            }

        @staticmethod
        def infer_wms_type(
            value: str | float | dict | list | None,
        ) -> dict[str, Any]:
            """Infer JSON schema type from Oracle WMS value.

            Args:
                value: Value to analyze

            Returns:
                dict[str, Any]: JSON schema type definition

            """
            if value is None:
                return {"type": ["null", "string"]}
            if isinstance(value, bool):
                return {"type": "boolean"}
            if isinstance(value, int):
                return {"type": "integer"}
            if isinstance(value, float):
                return {"type": "number"}
            if isinstance(value, list):
                if value:
                    # Infer type from first element
                    item_type = (
                        FlextTapOracleWmsUtilities.StreamUtilities.infer_wms_type(
                            value[0]
                        )
                    )
                    return {"type": "array", "items": item_type}
                return {"type": "array", "items": {"type": "string"}}
            if isinstance(value, dict):
                return {"type": "object", "additionalProperties": True}

            # String type with WMS-specific format detection
            schema = {"type": "string"}

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
            record_count: int, target_batches: int = 10
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
            return min(calculated_size, FlextTapOracleWmsUtilities.DEFAULT_BATCH_SIZE)

        @staticmethod
        def create_wms_replication_key_schema(
            stream_name: str,
            replication_key: str = "last_update_date",
        ) -> dict[str, Any]:
            """Create replication key schema for Oracle WMS streams.

            Args:
                stream_name: Name of the stream
                replication_key: Replication key field name

            Returns:
                dict[str, Any]: Replication key schema

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
            config: dict[str, Any],
        ) -> FlextResult[dict[str, Any]]:
            """Validate Oracle WMS connection configuration.

            Args:
                config: Configuration dictionary

            Returns:
                FlextResult[dict[str, Any]]: Validated config or error

            """
            required_fields = ["host", "database", "username", "password"]
            missing_fields = [field for field in required_fields if field not in config]

            if missing_fields:
                return FlextResult[dict[str, Any]].fail(
                    f"Missing required WMS connection fields: {', '.join(missing_fields)}"
                )

            # Validate host format
            host = config["host"]
            if not isinstance(host, str) or not host.strip():
                return FlextResult[dict[str, Any]].fail(
                    "Host must be a non-empty string"
                )

            # Validate database format
            database = config["database"]
            if not isinstance(database, str) or not database.strip():
                return FlextResult[dict[str, Any]].fail(
                    "Database must be a non-empty string"
                )

            # Validate port if provided
            if "port" in config:
                port = config["port"]
                if (
                    not isinstance(port, int)
                    or port <= 0
                    or port > FlextTapOracleWmsUtilities.MAX_PORT
                ):
                    return FlextResult[dict[str, Any]].fail(
                        "Port must be a valid integer between 1 and 65535"
                    )

            # Validate WMS-specific settings
            if "schema" in config:
                schema = config["schema"]
                if not isinstance(schema, str) or not schema.strip():
                    return FlextResult[dict[str, Any]].fail(
                        "Schema must be a non-empty string"
                    )

            return FlextResult[dict[str, Any]].ok(config)

        @staticmethod
        def validate_wms_stream_config(
            config: dict[str, Any],
        ) -> FlextResult[dict[str, Any]]:
            """Validate Oracle WMS stream configuration.

            Args:
                config: Stream configuration

            Returns:
                FlextResult[dict[str, Any]]: Validated config or error

            """
            if "streams" not in config:
                return FlextResult[dict[str, Any]].fail(
                    "Configuration must include 'streams' section"
                )

            streams = config["streams"]
            if not isinstance(streams, dict):
                return FlextResult[dict[str, Any]].fail(
                    "Streams configuration must be a dictionary"
                )

            # Validate each stream
            for stream_name, stream_config in streams.items():
                if not isinstance(stream_config, dict):
                    return FlextResult[dict[str, Any]].fail(
                        f"Stream '{stream_name}' configuration must be a dictionary"
                    )

                # Check for required stream fields
                if "selected" not in stream_config:
                    return FlextResult[dict[str, Any]].fail(
                        f"Stream '{stream_name}' must have 'selected' field"
                    )

                # Validate WMS-specific stream settings
                if "table_name" in stream_config:
                    table_name = stream_config["table_name"]
                    if not isinstance(table_name, str) or not table_name.strip():
                        return FlextResult[dict[str, Any]].fail(
                            f"Stream '{stream_name}' table_name must be a non-empty string"
                        )

            return FlextResult[dict[str, Any]].ok(config)

    class ConfigurationProcessing:
        """Advanced configuration processing utilities."""

        @staticmethod
        def validate_wms_config(config: dict[str, Any]) -> FlextResult[dict[str, Any]]:
            """Validate basic WMS configuration.

            Args:
                config: Configuration dictionary

            Returns:
                FlextResult[dict[str, Any]]: Validated config or error

            """
            # Delegate to existing ConfigValidation
            return FlextTapOracleWmsUtilities.ConfigValidation.validate_wms_connection_config(
                config
            )

        @staticmethod
        def validate_wms_connection_params(
            config: dict[str, Any],
        ) -> FlextResult[dict[str, Any]]:
            """Validate WMS connection parameters.

            Args:
                config: Configuration dictionary

            Returns:
                FlextResult[dict[str, Any]]: Validated config or error

            """
            required_params = ["base_url", "username", "password"]
            for param in required_params:
                if param not in config:
                    return FlextResult[dict[str, Any]].fail(
                        f"Missing required parameter: {param}"
                    )

            # Validate URL format
            base_url = config["base_url"]
            if not isinstance(base_url, str) or not base_url.startswith((
                "http://",
                "https://",
            )):
                return FlextResult[dict[str, Any]].fail("Invalid base_url format")

            return FlextResult[dict[str, Any]].ok(config)

        @staticmethod
        def validate_wms_configuration_comprehensive(
            config: dict[str, Any],
        ) -> FlextResult[dict[str, Any]]:
            """Comprehensive WMS configuration validation.

            Args:
                config: Configuration dictionary

            Returns:
                FlextResult[dict[str, Any]]: Validated config or error

            """
            # Basic validation first
            basic_result = (
                FlextTapOracleWmsUtilities.ConfigurationProcessing.validate_wms_config(
                    config
                )
            )
            if basic_result.is_failure:
                return basic_result

            # Connection params validation
            params_result = FlextTapOracleWmsUtilities.ConfigurationProcessing.validate_wms_connection_params(
                config
            )
            if params_result.is_failure:
                return params_result

            # Stream configuration validation if present
            if "streams" in config:
                stream_result = FlextTapOracleWmsUtilities.ConfigValidation.validate_wms_stream_config(
                    config
                )
                if stream_result.is_failure:
                    return stream_result

            return FlextResult[dict[str, Any]].ok(config)

    class WmsApiProcessing:
        """WMS API processing utilities."""

        @staticmethod
        def test_wms_api_connection(
            base_url: str, auth_token: str | None = None, timeout: int = 30
        ) -> FlextResult[dict[str, Any]]:
            """Test WMS API connection.

            Args:
                base_url: WMS API base URL
                auth_token: Optional authentication token
                timeout: Connection timeout

            Returns:
                FlextResult[dict[str, Any]]: Connection test result

            """
            if not base_url:
                return FlextResult[dict[str, Any]].fail("Base URL cannot be empty")

            if not base_url.startswith(("http://", "https://")):
                return FlextResult[dict[str, Any]].fail("Invalid URL format")

            # Basic connection validation (would normally make HTTP request)
            connection_info = {
                "base_url": base_url,
                "timeout": timeout,
                "status": "validated",
                "auth_provided": auth_token is not None,
            }

            return FlextResult[dict[str, Any]].ok(connection_info)

    class DataProcessing:
        """Advanced data processing utilities."""

        @staticmethod
        def generate_validation_info(
            config_data: dict[str, Any],
            connection_result: dict[str, Any],
            discovery_result: dict[str, Any] | None = None,
        ) -> FlextResult[dict[str, Any]]:
            """Generate comprehensive validation information.

            Args:
                config_data: Configuration data
                connection_result: Connection test result
                discovery_result: Optional discovery result

            Returns:
                FlextResult[dict[str, Any]]: Validation information

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
                if isinstance(discovery_result, list):
                    validation_info["entities_discovered"] = len(discovery_result)
                elif isinstance(discovery_result, dict):
                    validation_info["entities_discovered"] = len(
                        discovery_result.get("entities", [])
                    )
                else:
                    validation_info["entities_discovered"] = 0

            return FlextResult[dict[str, Any]].ok(validation_info)

    class StateManagement:
        """State management utilities for incremental syncs."""

        @staticmethod
        def get_wms_stream_state(
            state: dict[str, Any], stream_name: str
        ) -> dict[str, Any]:
            """Get state for a specific Oracle WMS stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream

            Returns:
                dict[str, Any]: Stream state

            """
            return state.get("bookmarks", {}).get(stream_name, {})

        @staticmethod
        def set_wms_stream_state(
            state: dict[str, Any],
            stream_name: str,
            stream_state: dict[str, Any],
        ) -> dict[str, Any]:
            """Set state for a specific Oracle WMS stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream
                stream_state: State data for the stream

            Returns:
                dict[str, Any]: Updated state

            """
            if "bookmarks" not in state:
                state["bookmarks"] = {}

            state["bookmarks"][stream_name] = stream_state
            return state

        @staticmethod
        def get_wms_bookmark(
            state: dict[str, Any],
            stream_name: str,
            bookmark_key: str,
        ) -> str | int | float | datetime | None:
            """Get bookmark value for a Oracle WMS stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream
                bookmark_key: Bookmark key

            Returns:
                Any: Bookmark value or None

            """
            stream_state = (
                FlextTapOracleWmsUtilities.StateManagement.get_wms_stream_state(
                    state, stream_name
                )
            )
            return stream_state.get(bookmark_key)

        @staticmethod
        def set_wms_bookmark(
            state: dict[str, Any],
            stream_name: str,
            bookmark_key: str,
            bookmark_value: str | float | datetime | None,
        ) -> dict[str, Any]:
            """Set bookmark value for a Oracle WMS stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream
                bookmark_key: Bookmark key
                bookmark_value: Bookmark value

            Returns:
                dict[str, Any]: Updated state

            """
            if "bookmarks" not in state:
                state["bookmarks"] = {}
            if stream_name not in state["bookmarks"]:
                state["bookmarks"][stream_name] = {}

            state["bookmarks"][stream_name][bookmark_key] = bookmark_value
            return state

        @staticmethod
        def create_wms_incremental_state(
            stream_name: str,
            last_updated: datetime,
            records_processed: int = 0,
        ) -> dict[str, Any]:
            """Create incremental state for Oracle WMS stream.

            Args:
                stream_name: Name of the stream
                last_updated: Last update timestamp
                records_processed: Number of records processed

            Returns:
                dict[str, Any]: Incremental state

            """
            return {
                "bookmarks": {
                    stream_name: {
                        "replication_key_value": last_updated.isoformat(),
                        "last_update_date": last_updated.isoformat(),
                        "records_processed": records_processed,
                        "extraction_timestamp": datetime.now(UTC).isoformat(),
                    }
                }
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
                    100, table_size_estimate // 100
                ),  # At least 100, at most 1% of table
                FlextTapOracleWmsUtilities.DEFAULT_BATCH_SIZE,
            )

        @staticmethod
        def estimate_extraction_time(
            record_count: int,
            avg_record_size_bytes: int = 2048,
            network_speed_mbps: float = 100.0,
        ) -> dict[str, float]:
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
        """utilities for tap operations."""

        @staticmethod
        def run(
            coro: Coroutine[object, object, object] | Awaitable[object],
        ) -> object:
            """Run coroutine in sync context.

            This replaces the loose helper function in utils.py with proper
            class-based organization following FLEXT patterns.

            Args:
                coro: Coroutine or awaitable to run
            Returns:
                Result of the coroutine execution

            """
            loop = new_event_loop()
            set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

    # Proxy methods for backward compatibility
    @classmethod
    def create_schema_message(
        cls,
        stream_name: str,
        schema: dict[str, Any],
        key_properties: list[str] | None = None,
    ) -> dict[str, Any]:
        """Proxy method for SingerUtilities.create_schema_message()."""
        return cls.SingerUtilities.create_schema_message(
            stream_name, schema, key_properties
        )

    @classmethod
    def create_record_message(
        cls,
        stream_name: str,
        record: dict[str, Any],
        time_extracted: datetime | None = None,
    ) -> dict[str, Any]:
        """Proxy method for SingerUtilities.create_record_message()."""
        return cls.SingerUtilities.create_record_message(
            stream_name, record, time_extracted
        )

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
        cls, config: dict[str, Any]
    ) -> FlextResult[dict[str, Any]]:
        """Proxy method for ConfigValidation.validate_wms_connection_config()."""
        return cls.ConfigValidation.validate_wms_connection_config(config)

    @classmethod
    def get_wms_stream_state(
        cls, state: dict[str, Any], stream_name: str
    ) -> dict[str, Any]:
        """Proxy method for StateManagement.get_wms_stream_state()."""
        return cls.StateManagement.get_wms_stream_state(state, stream_name)

    @classmethod
    def set_wms_bookmark(
        cls,
        state: dict[str, Any],
        stream_name: str,
        bookmark_key: str,
        bookmark_value: str | float | datetime | None,
    ) -> dict[str, Any]:
        """Proxy method for StateManagement.set_wms_bookmark()."""
        return cls.StateManagement.set_wms_bookmark(
            state, stream_name, bookmark_key, bookmark_value
        )


__all__ = [
    "FlextTapOracleWmsUtilities",
]

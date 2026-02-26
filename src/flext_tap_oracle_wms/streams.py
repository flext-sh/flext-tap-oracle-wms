"""Oracle WMS Stream implementations for Singer protocol.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import ClassVar, cast, override

from flext_core import FlextLogger, FlextResult, t, u

# Use FLEXT Meltano wrappers instead of direct singer_sdk imports (domain separation)
from flext_meltano import FlextMeltanoStream as Stream, FlextMeltanoTap as Tap
from flext_oracle_wms import FlextOracleWmsClient

from flext_tap_oracle_wms.protocols import p
from flext_tap_oracle_wms.utilities import FlextTapOracleWmsUtilities

logger = FlextLogger(__name__)


class FlextTapOracleWmsStream(Stream):
    """Dynamic stream for Oracle WMS entities.

    Uses flext-oracle-wms client for all data operations.
    This is a generic stream class that adapts to any Oracle WMS entity dynamically.
    """

    # Dynamic attributes - will be set at runtime based on discovery
    stream_primary_keys: ClassVar[list[str]] = []  # Will be set dynamically
    stream_replication_key: str | None = None  # Will be set dynamically

    @override
    def __init__(
        self,
        tap: Tap,
        name: str | None = None,
        schema: dict[str, t.JsonValue] | None = None,
        _path: str | None = None,
    ) -> None:
        """Initialize stream."""
        super().__init__(tap=tap, name=name or self.name, schema=schema)

        # Zero Tolerance FIX: Initialize utilities for ALL stream business logic
        self._utilities = FlextTapOracleWmsUtilities()

        # FlextOracleWmsClient - concrete type, dynamic import avoids circular deps
        self._client: FlextOracleWmsClient | None = None

        # Zero Tolerance FIX: Use utilities for stream configuration processing
        page_size_result = (
            self._utilities.ConfigurationProcessing.validate_stream_page_size(
                int(self.config.get("page_size", 100)),
            )
        )
        self._page_size = 100
        if page_size_result.is_success:
            self._page_size = int(self.config.get("page_size", 100))

    @property
    def client(self) -> FlextOracleWmsClient:
        """Get WMS client from tap."""
        if self._client is None:
            # Access WMS client from tap (FlextTapOracleWms)
            tap_instance = (self.tap if hasattr(self, "tap") else None) or (
                self._tap if hasattr(self, "_tap") else None
            )
            if tap_instance and u.Guards.is_type(
                tap_instance, p.TapOracleWms.OracleWms.TapWithWmsClientProtocol
            ):
                wms_tap = cast(
                    "p.TapOracleWms.OracleWms.TapWithWmsClientProtocol", tap_instance
                )
                self._client = cast("FlextOracleWmsClient", wms_tap.wms_client)
            else:
                msg = "WMS client not available - tap must be FlextTapOracleWms"
                raise RuntimeError(msg)

        if self._client is None:
            msg = "Client not available after initialization - this should not happen"
            raise RuntimeError(msg)
        return self._client

    def get_primary_keys(self) -> list[str]:
        """Get primary keys for this stream."""
        return list(self.stream_primary_keys)

    def get_replication_key(self) -> str | None:
        """Get replication key for this stream."""
        return self.stream_replication_key

    def _run(
        self,
        value: t.JsonValue,
    ) -> t.JsonValue:
        return value

    def get_records(
        self,
        context: Mapping[str, t.JsonValue] | None,
    ) -> Iterable[dict[str, t.JsonValue]]:
        """Get records from Oracle WMS."""
        page = 1
        has_more = True
        while has_more:
            try:
                # Get page data
                page_result = self._fetch_page_data(page, context)
                if page_result.is_failure:
                    logger.error(
                        "Failed to fetch page %s for %s: %s",
                        page,
                        self.name,
                        page_result.error,
                    )
                    break
                records, has_more = page_result.value
                # Process and yield records
                yield from self._process_page_records(records, context)
                # Move to next page
                page += 1
                # Break if no records found
                if not records:
                    break
            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ):
                logger.exception("Error getting records for %s", self.name)
                break

    def _fetch_page_data(
        self,
        page: int,
        context: Mapping[str, t.JsonValue] | None,
    ) -> FlextResult[tuple[list[dict[str, t.JsonValue]], bool]]:
        """Fetch data for a specific page."""
        # Build operation parameters
        operation_name = f"get_{self.name}"
        kwargs = self._build_operation_kwargs(page, context)
        execute_method = (
            self.client.execute if hasattr(self.client, "execute") else None
        )
        if execute_method is None:
            return FlextResult[tuple[list[dict[str, t.JsonValue]], bool]].fail(
                "WMS client must implement execute(operation, **kwargs)",
            )
        result = self._run(
            execute_method(operation_name, **kwargs),
        )
        # Check for failure
        match result:
            case FlextResult() as result_data:
                if result_data.is_failure:
                    return FlextResult[tuple[list[dict[str, t.JsonValue]], bool]].fail(
                        f"Failed to get records for {self.name}: {result_data.error}",
                    )
                data_raw = result_data.value
            case _:
                data_raw = result

        # Extract and process response data
        match data_raw:
            case str() | int() | float() | bool() | dict() | list() | None:
                data: t.JsonValue = data_raw
            case _:
                data = {}
        return FlextResult[tuple[list[dict[str, t.JsonValue]], bool]].ok(
            self._extract_records_from_response(data),
        )

    @staticmethod
    def _normalize_json_value(value: t.JsonValue) -> t.JsonValue:
        """Normalize arbitrary values into Singer-compatible JSON values."""
        match value:
            case str() | int() | float() | bool() | None:
                return value
            case list() | dict():
                return value
            case _:
                return str(value)

    def _build_operation_kwargs(
        self,
        page: int,
        context: Mapping[str, t.JsonValue] | None,
    ) -> Mapping[str, t.JsonValue]:
        """Build kwargs for the operation call."""
        kwargs: dict[str, t.JsonValue] = {
            "page": page,
            "limit": self._page_size,
        }
        # Add incremental replication filter if configured
        if self.stream_replication_key:
            starting_timestamp = self.get_starting_timestamp(context)
            if starting_timestamp:
                kwargs_filter = (
                    f"{self.stream_replication_key}>={starting_timestamp.isoformat()}"
                )
                kwargs["filter"] = kwargs_filter
        return kwargs

    def _extract_records_from_response(
        self,
        data: t.JsonValue,
    ) -> tuple[list[dict[str, t.JsonValue]], bool]:
        """Extract records and pagination info from API response."""
        match data:
            case dict() as data_dict:
                raw_records = data_dict.get(
                    "data",
                    data_dict.get("items", data_dict.get("results", [])),
                )
                has_more = bool(
                    data_dict.get("has_more", False)
                    or data_dict.get("next_page", False),
                )
            case list() as data_list:
                raw_records = data_list
                has_more = len(data_list) == self._page_size
            case _:
                raw_records = []
                has_more = False
        # Ensure records is always a list of JSON-compatible dictionaries
        match raw_records:
            case list() as records_list:
                coerced_records: list[dict[str, t.JsonValue]] = []
                for record in records_list:
                    match record:
                        case dict() as record_dict:
                            json_record: dict[str, t.JsonValue] = {}
                            for k, v in record_dict.items():
                                match v:
                                    case str() | int() | float() | bool() | None:
                                        json_record[k] = v
                                    case list() | dict():
                                        json_record[k] = v
                                    case _:
                                        json_record[k] = str(v)
                            coerced_records.append(json_record)
                        case _:
                            # Convert non-dict records to JSON row payload format
                            coerced_records.append({"value": "record"})
                records = coerced_records
            case _:
                records = []
        return records, has_more

    def _process_page_records(
        self,
        records: list[dict[str, t.JsonValue]],
        context: Mapping[str, t.JsonValue] | None,
    ) -> Iterable[dict[str, t.JsonValue]]:
        """Process and yield records from a page."""
        for record in records:
            record_dict: dict[str, t.JsonValue] = dict(record)
            processed_record = self._utilities.DataProcessing.process_wms_record(
                record=record_dict
            )
            match processed_record:
                case dict() as processed_dict:
                    json_row: dict[str, t.JsonValue] = {
                        str(k): self._normalize_json_value(cast("t.JsonValue", v))
                        for k, v in processed_dict.items()
                    }
                    final_record = self.post_process(json_row, context)
                    if final_record is not None:
                        yield final_record
                case _:
                    continue

    def post_process(
        self,
        row: dict[str, t.JsonValue],
        context: Mapping[str, t.JsonValue] | None = None,
    ) -> dict[str, t.JsonValue] | None:
        """Post-process a record."""
        # Apply column mappings if configured
        if self.config:
            column_mappings_raw = self.config.get("column_mappings", {})
            match column_mappings_raw:
                case dict() as column_mappings:
                    mappings = column_mappings.get(self.name)
                    match mappings:
                        case dict() as mapping_dict:
                            for old_name, new_name in mapping_dict.items():
                                match (old_name, new_name):
                                    case (str() as old_name_str, str() as new_name_str):
                                        if old_name_str in row:
                                            row[new_name_str] = row.pop(old_name_str)
                                    case _:
                                        continue
                        case _:
                            pass
                case _:
                    pass
            # Remove ignored columns
            ignored_columns: list[t.JsonValue] = self.config.get("ignored_columns", [])
            for column in ignored_columns:
                match column:
                    case str() as column_name:
                        row.pop(column_name, None)
                    case _:
                        continue

        # Add context information if available
        if context:
            row["_context"] = {k: str(v) for k, v in context.items()}

        return row


# Stream discovery is now fully dynamic - no predefined stream classes needed

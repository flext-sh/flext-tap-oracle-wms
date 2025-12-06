"""Streams for FLEXT Tap Oracle WMS.

Implements Singer streams for Oracle WMS entities using flext-oracle-wms client.
Consolidates stream definitions and functionality following PEP8 patterns.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Awaitable, Coroutine, Iterable, Mapping, Sequence
from typing import override

from flext_core import FlextLogger, FlextResult, t

# Use FLEXT Meltano wrappers instead of direct singer_sdk imports (domain separation)
from flext_meltano import FlextMeltanoStream as Stream, FlextMeltanoTap as Tap
from flext_oracle_wms import FlextOracleWmsClient

from flext_tap_oracle_wms.utilities import FlextMeltanoTapOracleWmsUtilities

logger = FlextLogger(__name__)


class FlextMeltanoTapOracleWMSStream(Stream):
    """Dynamic stream for Oracle WMS entities.

    Uses flext-oracle-wms client for all data operations.
    This is a generic stream class that adapts to any Oracle WMS entity dynamically.
    """

    # Dynamic attributes - will be set at runtime as instance variables in __init__

    @override
    def __init__(
        self,
        tap: Tap,
        name: str | None = None,
        schema: dict[str, object] | None = None,
        _path: str | None = None,
    ) -> None:
        """Initialize stream."""
        super().__init__(tap=tap, name=name or self.name, schema=schema)

        # Zero Tolerance FIX: Initialize utilities for ALL stream business logic
        self._utilities = FlextMeltanoTapOracleWmsUtilities()

        # FlextOracleWmsClient - concrete type, dynamic import avoids circular deps
        self._client: FlextOracleWmsClient | None = None

        # Zero Tolerance FIX: Use utilities for stream configuration processing
        page_size_result = (
            self._utilities.ConfigurationProcessing.validate_stream_page_size(
                self.config.get("page_size", 100),
            )
        )
        if page_size_result.is_success:
            self._page_size = page_size_result.unwrap()
        else:
            # Fall back to default if validation fails
            self._page_size = 100

        # Initialize instance variables for dynamic configuration
        self.stream_primary_keys: list[str] = []
        self.stream_replication_key: str | None = None

    @property
    def client(self: object) -> FlextOracleWmsClient:
        """Get WMS client from tap."""
        if self._client is None:
            # Access WMS client from tap (FlextMeltanoTapOracleWMS)
            tap_instance = getattr(self, "tap", None) or getattr(self, "_tap", None)
            if tap_instance and hasattr(tap_instance, "wms_client"):
                self._client = tap_instance.wms_client
            else:
                msg = "WMS client not available - tap must be FlextMeltanoTapOracleWMS"
                raise RuntimeError(msg)

        if self._client is None:
            msg = "Client not available after initialization - this should not happen"
            raise RuntimeError(msg)
        return self._client

    @property
    def primary_keys(self: object) -> Sequence[str]:
        """Get primary keys for this stream."""
        return self.stream_primary_keys or []

    @primary_keys.setter
    def primary_keys(self, value: Sequence[str]) -> None:
        """Set primary keys for this stream."""
        self.stream_primary_keys = list(value)

    @property
    def replication_key(self: object) -> str | None:
        """Get replication key for this stream."""
        return self.stream_replication_key

    @replication_key.setter
    def replication_key(self, value: str | None) -> None:
        """Set replication key for this stream."""
        self.stream_replication_key = value

    def _run(
        self,
        coro: Coroutine[object, object, object] | Awaitable[object],
    ) -> object:
        """Run coroutine in sync context."""
        # Zero Tolerance FIX: Use utilities instead of loose function
        return self._utilities.Utilities.run(coro)

    def get_records(
        self,
        context: Mapping[str, object] | None,
    ) -> Iterable[t.JsonDict]:
        """Get records from Oracle WMS.

        Args:
        context: Stream context
        Yields:
        Stream records

        """
        page = 1
        has_more = True
        while has_more:
            try:
                # Get page data
                page_result: FlextResult[object] = self._fetch_page_data(page, context)
                if page_result is None:
                    break
                records, has_more = page_result
                # Process and yield records
                yield from self._process_page_records(records, context)
                # Move to next page
                page += 1
                # Break if no records found
                if not records:
                    break
            except Exception:
                logger.exception("Error getting records for %s", self.name)
                break

    def _fetch_page_data(
        self,
        page: int,
        context: Mapping[str, object] | None,
    ) -> tuple[list[t.JsonDict], bool] | None:
        """Fetch data for a specific page.

        Args:
        page: Page number to fetch
        context: Stream context
        Returns:
        Tuple of (records, has_more) or None if failed

        """
        # Build operation parameters
        operation_name = f"get_{self.name}"
        kwargs = self._build_operation_kwargs(page, context)
        # Execute operation
        # Execute operation using dynamic method call
        execute_method = getattr(self.client, "execute", None)
        if execute_method:
            result: FlextResult[object] = self._run(
                execute_method(operation_name, **kwargs),
            )
        else:
            # Fallback: try direct method call
            method = getattr(self.client, operation_name, None)
            if method:
                result: FlextResult[object] = self._run(method(**kwargs))
            else:
                logger.error("Method %s not found on WMS client", operation_name)
                return None
        # Check for failure
        if hasattr(result, "is_failure") and result.is_failure:
            error_msg = getattr(result, "error", "Unknown error")
            logger.error("Failed to get records for %s: %s", self.name, error_msg)
            return None
        # Extract and process response data
        data: dict[str, object] = getattr(result, "value", result)
        return self._extract_records_from_response(data)

    def _build_operation_kwargs(
        self,
        page: int,
        context: Mapping[str, object] | None,
    ) -> t.JsonDict:
        """Build kwargs for the operation call.

        Args:
        page: Page number
        context: Stream context
        Returns:
        Operation kwargs dict

        """
        kwargs = {
            "page": page,
            "limit": self._page_size,
        }
        # Add incremental replication filter if configured
        if self._replication_key:
            starting_timestamp = self.get_starting_timestamp(context)
            if starting_timestamp:
                kwargs["filter"] = {
                    self._replication_key: {
                        "$gte": starting_timestamp.isoformat(),
                    },
                }
        return kwargs

    def _extract_records_from_response(
        self,
        data: dict[str, object] | list[object] | object,
    ) -> tuple[list[t.JsonDict], bool]:
        """Extract records and pagination info from API response.

        Args:
        data: Raw response data
        Returns:
        Tuple of (records, has_more)

        """
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
        # Ensure records is always a list of dict[str, object]
        match raw_records:
            case list() as records_list:
                coerced_records: list[t.JsonDict] = []
                for record in records_list:
                    match record:
                        case dict() as record_dict:
                            coerced_records.append(record_dict)
                        case _:
                            # Convert non-dict records to dict[str, object] format
                            coerced_records.append({"value": "record"})
                records = coerced_records
            case _:
                records = []
        return records, has_more

    def _process_page_records(
        self,
        records: list[t.JsonDict],
        context: Mapping[str, object] | None,
    ) -> Iterable[t.JsonDict]:
        """Process and yield records from a page.

        Args:
        records: List of records to process
        context: Stream context
        Yields:
        Processed records

        """
        for record in records:
            # Ensure record is a dict[str, object] for processing
            if isinstance(record, dict):
                processed_record = self.post_process(record, context)
                if processed_record is not None:
                    yield processed_record

    def post_process(
        self,
        row: t.JsonDict,
        context: Mapping[str, object] | None = None,
    ) -> t.JsonDict | None:
        """Post-process a record.

        Args:
        row: Record to process
        context: Stream context
        Returns:
        Processed record or None to skip

        """
        # Apply column mappings if configured
        if self.config:
            column_mappings: dict[str, object] = self.config.get("column_mappings", {})
            if self.name in column_mappings:
                mappings = column_mappings[self.name]
                for old_name, new_name in mappings.items():
                    if old_name in row:
                        row[new_name] = row.pop(old_name)
            # Remove ignored columns
            ignored_columns: list[object] = self.config.get("ignored_columns", [])
            for column in ignored_columns:
                row.pop(column, None)

        # Add context information if available
        if context:
            row["_context"] = {k: str(v) for k, v in context.items()}

        return row


# Stream discovery is now fully dynamic - no predefined stream classes needed

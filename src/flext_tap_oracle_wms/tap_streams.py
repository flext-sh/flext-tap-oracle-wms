"""Streams for FLEXT Tap Oracle WMS.

Implements Singer streams for Oracle WMS entities using flext-oracle-wms client.
Consolidates stream definitions and functionality following PEP8 patterns.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar
from flext_tap_oracle_wms.typings import FlextTypes

from flext_meltano import Stream

from flext_tap_oracle_wms.utils import run_async

if TYPE_CHECKING:
    from collections.abc import Awaitable, Coroutine, Iterable, Mapping

    from flext_meltano import Tap
    from flext_oracle_wms import FlextOracleWmsClient

logger = logging.getLogger(__name__)


class FlextTapOracleWMSStream(Stream):
    """Dynamic stream for Oracle WMS entities.

    Uses flext-oracle-wms client for all data operations.
    This is a generic stream class that adapts to any Oracle WMS entity dynamically.
    """

    # Dynamic attributes - will be set at runtime based on discovery
    primary_keys: ClassVar[list[str]] = []  # Will be set dynamically
    replication_key: str | None = None  # Will be set dynamically

    def __init__(
        self,
        tap: Tap,
        name: str | None = None,
        schema: FlextTypes.Core.AnyDict | None = None,
        _path: str | None = None,
    ) -> None:
        """Initialize stream."""
        super().__init__(tap=tap, name=name or self.name, schema=schema)
        # FlextOracleWmsClient - concrete type, dynamic import avoids circular deps
        self._client: FlextOracleWmsClient | None = None
        self._page_size = self.config.get("page_size", 100)

    @property
    def client(self) -> FlextOracleWmsClient:
        """Get WMS client from tap."""
        if self._client is None:
            # Access WMS client from tap (FlextTapOracleWMS)
            tap_instance = getattr(self, "tap", None) or getattr(self, "_tap", None)
            if tap_instance and hasattr(tap_instance, "wms_client"):
                self._client = tap_instance.wms_client
            else:
                msg = "WMS client not available - tap must be FlextTapOracleWMS"
                raise RuntimeError(msg)
        # Type narrowing: after the RuntimeError check above, self._client is guaranteed to be FlextOracleWmsClient
        if self._client is None:
            msg = "Client not available after initialization - this should not happen"
            raise RuntimeError(msg)
        return self._client

    def _run_async(
        self,
        coro: Coroutine[object, object, object] | Awaitable[object],
    ) -> object:
        """Run async coroutine in sync context."""
        return run_async(coro)

    def get_records(
        self,
        context: Mapping[str, object] | None,
    ) -> Iterable[FlextTypes.Core.AnyDict]:
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
                page_result = self._fetch_page_data(page, context)
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
    ) -> tuple[list[FlextTypes.Core.AnyDict], bool] | None:
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
            result = self._run_async(execute_method(operation_name, **kwargs))
        else:
            # Fallback: try direct method call
            method = getattr(self.client, operation_name, None)
            if method:
                result = self._run_async(method(**kwargs))
            else:
                logger.error("Method %s not found on WMS client", operation_name)
                return None

        # Check for failure
        if hasattr(result, "is_failure") and result.is_failure:
            error_msg = getattr(result, "error", "Unknown error")
            logger.error("Failed to get records for %s: %s", self.name, error_msg)
            return None

        # Extract and process response data
        data = getattr(result, "value", result)
        return self._extract_records_from_response(data)

    def _build_operation_kwargs(
        self,
        page: int,
        context: Mapping[str, object] | None,
    ) -> FlextTypes.Core.AnyDict:
        """Build kwargs for the operation call.

        Args:
            page: Page number
            context: Stream context

        Returns:
            Operation kwargs dict

        """
        kwargs = {
            "limit": self._page_size,
            "page": page,
        }

        # Add incremental replication filter if configured
        if self.replication_key:
            starting_timestamp = self.get_starting_timestamp(context)
            if starting_timestamp:
                kwargs["filter"] = {
                    self.replication_key: {
                        "$gte": starting_timestamp.isoformat(),
                    },
                }

        return kwargs

    def _extract_records_from_response(
        self,
        data: dict[str, object] | list[object] | object,
    ) -> tuple[list[FlextTypes.Core.AnyDict], bool]:
        """Extract records and pagination info from API response.

        Args:
            data: Raw response data

        Returns:
            Tuple of (records, has_more)

        """
        match data:
            case dict() as data_dict:
                raw_records = data_dict.get(
                    "data", data_dict.get("items", data_dict.get("results", [])),
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
                # Type cast each record to AnyDict
                coerced_records: list[FlextTypes.Core.AnyDict] = []
                for record in records_list:
                    match record:
                        case dict() as record_dict:
                            # Type narrowing: record is now dict which is compatible with TAnyDict
                            coerced_records.append(record_dict)
                        case _:
                            # Convert non-dict records to dict format
                            coerced_records.append({"value": record})
                records = coerced_records
            case _:
                records = []

        return records, has_more

    def _process_page_records(
        self,
        records: list[FlextTypes.Core.AnyDict],
        context: Mapping[str, object] | None,
    ) -> Iterable[FlextTypes.Core.AnyDict]:
        """Process and yield records from a page.

        Args:
            records: List of records to process
            context: Stream context

        Yields:
            Processed records

        """
        for record in records:
            # Ensure record is a dict for processing
            if isinstance(record, dict):
                processed_record = self.post_process(record, context)
                if processed_record is not None:
                    yield processed_record

    def post_process(
        self,
        row: FlextTypes.Core.AnyDict,
        _context: Mapping[str, object] | None = None,
    ) -> FlextTypes.Core.AnyDict | None:
        """Post-process a record.

        Args:
            row: Record to process
            context: Stream context

        Returns:
            Processed record or None to skip

        """
        # Apply column mappings if configured
        if self.config:
            column_mappings = self.config.get("column_mappings", {})
            if self.name in column_mappings:
                mappings = column_mappings[self.name]
                for old_name, new_name in mappings.items():
                    if old_name in row:
                        row[new_name] = row.pop(old_name)

            # Remove ignored columns
            ignored_columns = self.config.get("ignored_columns", [])
            for column in ignored_columns:
                row.pop(column, None)

        return row


# Stream discovery is now fully dynamic - no predefined stream classes needed

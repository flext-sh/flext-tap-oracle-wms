"""Streams for FLEXT Tap Oracle WMS.

Implements Singer streams for Oracle WMS entities using flext-oracle-wms client.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any, ClassVar
from urllib.parse import parse_qs, urlparse

from flext_core.flext_types import TService, TValue
from singer_sdk import typing as th
from singer_sdk.streams import Stream

if TYPE_CHECKING:
    from collections.abc import Awaitable, Coroutine, Iterable, Mapping

    from flext_core import FlextResult
    from flext_core.flext_types import TAnyDict
    from flext_oracle_wms import FlextOracleWmsClient
    from singer_sdk import Tap

logger = logging.getLogger(__name__)


class FlextTapOracleWMSStream(Stream):
    """Dynamic stream for Oracle WMS entities.

    Uses flext-oracle-wms client for all data operations.
    This is a generic stream class that adapts to any Oracle WMS entity dynamically.
    """

    # Dynamic attributes - will be set at runtime based on discovery
    primary_keys: ClassVar[list[str]] = []  # Will be set dynamically
    replication_key: str | None = None  # Will be set dynamically

    def __init__(self, tap: Tap, name: str | None = None, schema: dict[str, Any] | None = None, path: str | None = None) -> None:
        """Initialize stream."""
        super().__init__(tap=tap, name=name or self.name, schema=schema)
        # FlextOracleWmsClient - concrete type, dynamic import avoids circular deps
        self._client: object | None = None
        self._page_size = self.config.get("page_size", 100)

    @property
    def client(self) -> Any:  # FlextOracleWmsClient at runtime
        """Get WMS client from tap."""
        if self._client is None:
            # Access WMS client from tap (FlextTapOracleWMS)
            tap_instance = getattr(self, "tap", None) or getattr(self, "_tap", None)
            if tap_instance and hasattr(tap_instance, "wms_client"):
                self._client = tap_instance.wms_client
            else:
                raise RuntimeError("WMS client not available - tap must be FlextTapOracleWMS")
        return self._client

    def _run_async(self, coro: Coroutine[object, object, object] | Awaitable[object]) -> object:
        """Run async coroutine in sync context."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def get_records(self, context: Mapping[str, Any] | None) -> Iterable[dict[str, Any]]:
        """Get records from Oracle WMS.

        Args:
            context: Stream context

        Yields:
            Stream records

        """
        # Get entity data using flext-oracle-wms client
        page = 1
        has_more = True

        while has_more:
            # Execute operation through client
            operation_name = f"get_{self.name}"
            kwargs = {
                "limit": self._page_size,
                "page": page,
            }

            # Add filtering for incremental replication
            if self.replication_key:
                starting_timestamp = self.get_starting_timestamp(context)
                if starting_timestamp:
                    kwargs["filter"] = {
                        self.replication_key: {
                            "$gte": starting_timestamp.isoformat(),
                        },
                    }

            try:
                # Execute operation
                result = self._run_async(
                    self.client.execute(operation_name, **kwargs)
                )

                if hasattr(result, "is_failure") and result.is_failure:
                    error_msg = getattr(result, "error", "Unknown error")
                    logger.error(f"Failed to get records for {self.name}: {error_msg}")
                    break

                # Extract records from response
                data = getattr(result, "value", result)
                if isinstance(data, dict):
                    records = data.get("data", data.get("items", data.get("results", [])))
                    has_more = data.get("has_more", False) or data.get("next_page", False)
                elif isinstance(data, list):
                    records = data
                    has_more = len(records) == self._page_size
                else:
                    records = []
                    has_more = False

                # Ensure records is always a list
                if records is None:
                    records = []

                # Yield records
                for record in records:
                    # Ensure record is a dict for processing
                    if isinstance(record, dict):
                        processed_record = self.post_process(record, context)
                        if processed_record is not None:
                            yield processed_record

                # Move to next page
                page += 1

                # Break if no more records
                if not records:
                    break

            except Exception as e:
                logger.exception(f"Error getting records for {self.name}: {e}")
                break

    def post_process(
        self,
        row: dict[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any] | None:
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

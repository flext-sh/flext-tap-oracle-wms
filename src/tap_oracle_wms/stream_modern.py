"""Modern WMS Stream - Clean Singer SDK implementation without bloat."""

from __future__ import annotations

from datetime import UTC, datetime
import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

from singer_sdk.streams import Stream

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from singer_sdk import Tap

    from .client import WMSClient
    from .models import TapMetrics, WMSEntity

logger = logging.getLogger(__name__)


class WMSStream(Stream):
    """Modern, simplified WMS stream implementation.

    Replaces the 1,184-line streams.py with a clean, focused implementation
    following Singer SDK patterns and SOLID principles.
    """

    def __init__(
        self,
        tap: Tap,
        entity: WMSEntity,
        client: WMSClient,
        metrics: TapMetrics,
        schema: dict[str, Any],
    ) -> None:
        """Initialize WMS stream with entity configuration."""
        self.entity = entity
        self.client = client
        self.metrics = metrics

        super().__init__(
            tap=tap,
            name=entity.name,
            schema=schema,
        )

    @property
    def is_incremental(self) -> bool:
        """Check if this stream supports incremental sync."""
        return self.entity.has_mod_ts

    def get_records(
        self,
        context: Mapping[str, Any] | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Extract records from WMS entity.

        Clean implementation replacing complex pagination and field processing.
        """
        logger.info("Starting extraction for %s", self.entity.name)

        # Get starting point for incremental sync
        start_date = self._get_start_date(dict(context) if context else None)
        page_token = None
        total_records = 0

        while True:
            # Build query parameters
            params = self._build_query_params(start_date, page_token)

            try:
                # Get data from WMS
                response = self.client.get_entity_data(self.entity.name, params)
                records = self._extract_records(response)

                if not records:
                    logger.info("No more records for %s", self.entity.name)
                    break

                # Process and yield records
                for record in records:
                    processed_record = self.transform_record(record)
                    if processed_record:
                        yield processed_record
                        total_records += 1

                self.metrics.add_records(len(records))

                # Check for next page
                page_token = self._get_next_page_token(response)
                if not page_token:
                    break

            except (ValueError, KeyError, TypeError):
                logger.exception("Error extracting %s", self.entity.name)
                break

        logger.info("Extracted %d records from %s", total_records, self.entity.name)

    def _get_start_date(self, context: dict[str, Any] | None) -> datetime | None:
        """Get starting date for incremental sync."""
        if not self.is_incremental or not context:
            return None

        # Get bookmark from state
        bookmarks = context.get("bookmarks", {})
        stream_bookmark = bookmarks.get(self.name, {})

        if "mod_ts" in stream_bookmark:
            try:
                return datetime.fromisoformat(stream_bookmark["mod_ts"])
            except ValueError:
                logger.warning("Invalid bookmark date for %s", self.name)

        # Fallback to tap start_date
        start_date = self.config.get("start_date")
        if start_date:
            try:
                return datetime.fromisoformat(start_date)
            except ValueError:
                logger.warning("Invalid start_date in config")

        return None

    def _build_query_params(
        self,
        start_date: datetime | None,
        page_token: str | None,
    ) -> dict[str, Any]:
        """Build query parameters for WMS API call."""
        params: dict[str, Any] = {
            "page_size": self.client.config.page_size,
        }

        # Add incremental filter
        if self.is_incremental and start_date:
            # WMS uses mod_ts for incremental sync
            params["mod_ts_gt"] = start_date.isoformat()
            params["order_by"] = "mod_ts"

        # Add pagination
        if page_token:
            # Handle different pagination patterns
            if page_token.isdigit():
                params["page"] = page_token  # Keep as string for API
            else:
                params["cursor"] = page_token

        return params

    def _extract_records(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract records from API response."""
        # response is always a dict from our API
        if isinstance(response, dict):
            # Try common response patterns
            for key in ["data", "records", "items", "results"]:
                if key in response and isinstance(response[key], list):
                    return response[key]  # type: ignore[no-any-return]

            # Single record response
            if any(field in response for field in ["id", "name", "mod_ts"]):
                return [response]

        return []

    def transform_record(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """Process individual record.

        Simplified from complex field mapping and transformation logic.
        """
        # Record is always a dict from _extract_records

        # Basic data cleaning
        processed = {}

        for key, value in record.items():
            # Skip null/empty values for cleaner output
            if value is None or value == "":
                continue

            # Clean field names (remove special characters)
            clean_key = key.replace(" ", "_").replace("-", "_").lower()
            processed[clean_key] = value

        # Ensure we have some data
        if not processed:
            return None

        # Add extraction metadata
        processed["_extracted_at"] = datetime.now(UTC).isoformat()

        return processed

    def _get_next_page_token(self, response: dict[str, Any]) -> str | None:
        """Get next page token from response."""
        # response is always a dict from our API

        # Check for next page URL (HATEOAS)
        next_url = response.get("next") or response.get("next_page")
        if next_url:
            parsed = urlparse(next_url)
            query_params = parse_qs(parsed.query)

            # Extract page number or cursor
            if "page" in query_params:
                return str(query_params["page"][0])
            if "cursor" in query_params:
                return str(query_params["cursor"][0])

        # Check for pagination metadata
        pagination = response.get("pagination", {})
        if pagination.get("has_next", False):
            current_page = pagination.get("page", 0)
            return str(current_page + 1)

        return None

    def get_child_context(
        self,
        _record: dict[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get context for child streams (if any)."""
        # Simplified - most WMS extractions don't need child contexts
        return dict(context) if context else {}

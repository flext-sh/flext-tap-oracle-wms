"""Dynamic streams for Oracle WMS entities."""

from collections.abc import Iterable
from typing import Any
from urllib.parse import parse_qs, urlparse
import logging

import backoff
import httpx
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from singer_sdk.pagination import BaseOffsetPaginator
from singer_sdk.streams import RESTStream

from .auth import get_wms_authenticator, get_wms_headers
from .tap import TapOracleWMS


class WMSPaginator(BaseOffsetPaginator):
    """Paginator for Oracle WMS API."""

    def __init__(self, start_value: int, page_size: int, mode: str = "offset") -> None:
        """Initialize paginator.

        Args:
        ----
            start_value: Starting offset/page
            page_size: Number of records per page
            mode: Pagination mode (offset or cursor)

        """
        super().__init__(start_value=start_value, page_size=page_size)
        self.mode = mode
        self._cursor = None

    def has_more(self, response: httpx.Response) -> bool:
        """Check if there are more pages.

        Args:
        ----
            response: API response

        Returns:
        -------
            True if more pages exist

        """
        try:
            data = response.json()

            if self.mode == "cursor":
                # In cursor mode, check for next_page URL
                return bool(data.get("next_page"))
            # In offset mode, check based on WMS API response structure
            current_page = data.get("page_nbr", 1)
            total_pages = data.get("page_count", 1)
            results = data.get("results", [])

            # If we got fewer results than page_size, we're at the end
            if len(results) < self._page_size:
                return False

            # Check if current page is less than total pages
            if current_page < total_pages:
                return True

            # Also check if we have next_page URL as backup
            return bool(data.get("next_page"))
        except (ValueError, KeyError):
            return False

    def get_next(self, response: httpx.Response) -> int | None:
        """Get next page token.

        Args:
        ----
            response: API response

        Returns:
        -------
            Next offset/cursor value

        """
        try:
            data = response.json()

            if self.mode == "cursor":
                # Extract cursor from next_page URL
                next_url = data.get("next_page")
                if next_url:
                    parsed = urlparse(next_url)
                    params = parse_qs(parsed.query)
                    self._cursor = params.get("cursor", [None])[0]
                    return self.current_value + 1  # Increment to avoid loop
                return None
            # Standard offset pagination based on WMS API structure
            if not self.has_more(response):
                return None

            current_page = data.get("page_nbr", 1)
            total_pages = data.get("page_count", 1)

            # Calculate next page
            next_page = current_page + 1

            # Ensure we don't exceed total pages
            if next_page > total_pages:
                return None

            return next_page
        except (ValueError, KeyError):
            return None


class WMSDynamicStream(RESTStream):
    """Dynamic stream for any Oracle WMS entity."""

    # Class attributes that will be set dynamically
    _entity_name: str = None
    _entity_schema: dict[str, Any] = None
    _tap_config: dict[str, Any] = None

    # Enable incremental replication by default
    forced_replication_method = None  # Let the catalog decide based on replication_key

    @classmethod
    def create_for_testing(
        cls, entity_name: str, schema: dict[str, Any]
    ) -> "WMSDynamicStream":
        """Create a stream instance for testing without a tap.

        Args:
        ----
            entity_name: Name of the WMS entity
            schema: JSON schema for the entity

        Returns:
        -------
            Stream instance ready for testing

        """
        return cls(tap=None, entity_name=entity_name, schema=schema)

    def __init__(self, tap, entity_name: str, schema: dict[str, Any]) -> None:
        """Initialize dynamic stream.

        Args:
        ----
            tap: Parent tap instance (can be None for testing)
            entity_name: Name of the WMS entity
            schema: JSON schema for the entity

        """
        # Set instance attributes before calling super().__init__
        self._entity_name = entity_name
        self._entity_schema = schema
        self._tap_config = getattr(tap, "config", {}) if tap else {}

        # Initialize primary keys
        self._primary_keys = self._determine_primary_keys()

        # Initialize replication key
        self._replication_key = self._determine_replication_key()

        # Handle testing scenario where tap might be None
        if tap is None:
            # Create a minimal tap instance with default config for testing
            test_tap = TapOracleWMS(config={})
            test_tap.logger = logging.getLogger("tap_oracle_wms")

            # Call parent constructor with test tap
            super().__init__(tap=test_tap, name=entity_name, schema=schema)
            # Restore the values that were calculated before
            self._primary_keys = self._determine_primary_keys()
            self._replication_key = self._determine_replication_key()
            return

        # Debug logging
        if hasattr(self, "logger"):
            self.logger.info(
                "Initialized %s with replication_key: %s",
                entity_name,
                self._replication_key,
            )

        # Call parent constructor
        super().__init__(tap)

        # Force replication key after parent initialization
        # This ensures it's set even if parent constructor overrides it
        if self._replication_key:
            self._replication_key = self._determine_replication_key()

    @property
    def name(self) -> str:
        """Stream name."""
        # Return the Singer SDK name if set, otherwise use entity name
        return getattr(self, "_name", None) or self._entity_name

    @name.setter
    def name(self, value: str) -> None:
        """Set stream name (for Singer SDK compatibility)."""
        self._name = value

    @property
    def path(self) -> str:
        """API path for entity."""
        return f"/wms/lgfapi/v10/entity/{self._entity_name}"

    @property
    def primary_keys(self) -> list[str]:
        """Primary keys for the entity."""
        return self._primary_keys

    @primary_keys.setter
    def primary_keys(self, value: list[str]) -> None:
        """Set primary keys for the entity."""
        self._primary_keys = value

    def _determine_primary_keys(self) -> list[str]:
        """Determine primary keys for the entity."""
        # Check if schema has required fields that could be PKs
        if "required" in self._entity_schema:
            # Look for 'id' or similar fields
            for field in ["id", f"{self._entity_name}_id", "code"]:
                if field in self._entity_schema.get("properties", {}):
                    return [field]

        # Default to 'id'
        return ["id"]

    @property
    def replication_key(self) -> str | None:
        """Replication key for incremental sync."""
        return self._replication_key

    @replication_key.setter
    def replication_key(self, value: str | None) -> None:
        """Set replication key for the entity."""
        self._replication_key = value

    @property
    def is_timestamp_replicable(self) -> bool:
        """Return True if stream supports timestamp-based incremental replication."""
        return self.replication_key is not None

    def get_metadata(self, *, reload: bool = False) -> Any:
        """Get stream metadata including replication configuration."""
        metadata = super().get_metadata(reload=reload)

        # Set replication method based on whether we have a replication key
        if self.replication_key:
            # Configure for incremental replication
            metadata.get_property_metadata(".", "replication-method").selected = False
            metadata.get_property_metadata(".", "replication-method").value = (
                "INCREMENTAL"
            )
            metadata.get_property_metadata(".", "replication-key").selected = False
            metadata.get_property_metadata(".", "replication-key").value = (
                self.replication_key
            )
        else:
            # Configure for full table replication
            metadata.get_property_metadata(".", "replication-method").selected = False
            metadata.get_property_metadata(".", "replication-method").value = (
                "FULL_TABLE"
            )

        return metadata

    def _determine_replication_key(self) -> str | None:
        """Determine replication key for incremental sync."""
        # Look for timestamp fields
        if not self._entity_schema:
            return None
        properties = self._entity_schema.get("properties", {})

        # Preferred replication keys in order
        for key in [
            "update_ts",
            "modify_ts",
            "mod_ts",
            "create_ts",
            "created_at",
        ]:
            if key in properties:
                prop = properties[key]
                # Check if it's a datetime field
                if isinstance(prop, dict):
                    # Direct format check
                    if prop.get("format") in {"date-time", "date"}:
                        return key
                    # Check anyOf structure for datetime fields
                    if "anyOf" in prop:
                        for any_type in prop["anyOf"]:
                            if isinstance(any_type, dict) and any_type.get(
                                "format"
                            ) in {"date-time", "date"}:
                                return key
                    # Check for string types with time-related names
                    if prop.get("type") == "string" and "time" in key.lower():
                        return key

        return None

    @property
    def schema(self) -> dict[str, Any]:
        """JSON schema for the stream."""
        return self._entity_schema

    @property
    def authenticator(self) -> Any:
        """Get authenticator for the stream."""
        return get_wms_authenticator(self, self.config)

    @property
    def http_headers(self) -> dict[str, str]:
        """HTTP headers for API requests."""
        headers = get_wms_headers(self.config)

        # Add authentication headers
        if self.authenticator:
            headers.update(self.authenticator.auth_headers)

        return headers

    @property
    def url_base(self) -> str:
        """Base URL for API requests."""
        return self.config["base_url"].rstrip("/")

    def get_new_paginator(self) -> WMSPaginator:
        """Get a new paginator instance."""
        mode = self.config.get("pagination_mode", "offset")
        page_size = self.config.get("page_size", 100)

        # Start from page 1 for offset mode
        start_value = 1 if mode == "offset" else 0

        return WMSPaginator(start_value=start_value, page_size=page_size, mode=mode)

    def get_url_params(
        self, context: dict[str, Any] | None, next_page_token: Any | None
    ) -> dict[str, Any] | None:
        """Get URL parameters for the request.

        Args:
        ----
            context: Stream context
            next_page_token: Next page token

        Returns:
        -------
            Dictionary of URL parameters

        """
        params: dict = {}

        # Pagination parameters
        if self.config.get("pagination_mode") == "cursor":
            params["page_mode"] = "sequenced"
            params["page_size"] = self.config.get("page_size", 100)

            # Add cursor if we have one
            paginator = self.get_new_paginator()
            if hasattr(paginator, "_cursor") and paginator._cursor:
                params["cursor"] = paginator._cursor
        else:
            # Standard offset pagination
            params["page_size"] = self.config.get("page_size", 100)
            params["page"] = next_page_token or 1

        # Add field selection if configured
        fields = self._get_selected_fields()
        if fields:
            params["fields"] = ",".join(fields)

        # Add ordering
        ordering = self._get_ordering()
        if ordering:
            params["ordering"] = ordering

        # Add filters
        filters = self._get_filters()
        params.update(filters)

        # Add incremental replication filter
        if self.replication_key:
            replication_key_value = self.get_starting_replication_key_value(context)
            if replication_key_value:
                params[f"{self.replication_key}__gte"] = replication_key_value

        return params

    def _get_selected_fields(self) -> list[str] | None:
        """Get fields to select for this entity."""
        # Check entity-specific field selection
        field_selection = self.config.get("field_selection", {})
        if self._entity_name in field_selection:
            return field_selection[self._entity_name]

        # Use default fields if configured
        return self.config.get("default_fields")

    def _get_ordering(self) -> str | None:
        """Get ordering for this entity."""
        # Check entity-specific ordering
        entity_ordering = self.config.get("entity_ordering", {})
        if self._entity_name in entity_ordering:
            return entity_ordering[self._entity_name]

        # Use default ordering
        return self.config.get("default_ordering", "id")

    def _get_filters(self) -> dict[str, Any]:
        """Get filters for this entity."""
        filters: dict = {}

        # Apply global filters
        global_filters = self.config.get("global_filters", {})
        filters.update(global_filters)

        # Apply entity-specific filters
        entity_filters = self.config.get("entity_filters", {})
        if self._entity_name in entity_filters:
            filters.update(entity_filters[self._entity_name])

        return filters

    def parse_response(self, response: httpx.Response) -> Iterable[dict[str, Any]]:
        """Parse API response and yield records.

        Args:
        ----
            response: API response

        Yields:
        ------
            Parsed records

        """
        data = response.json()

        # Handle paginated response
        if isinstance(data, dict) and "results" in data:
            yield from data["results"]
        # Handle direct array response
        elif isinstance(data, list):
            yield from data
        # Handle single record response
        elif isinstance(data, dict):
            yield data

    def validate_response(self, response: httpx.Response) -> None:
        """Validate HTTP response.

        Args:
        ----
            response: HTTP response object

        Raises:
        ------
            FatalAPIError: For 4xx errors
            RetriableAPIError: For 5xx errors

        """
        if 400 <= response.status_code < 500:
            msg = (
                f"{response.status_code} Client Error: "
                f"{response.reason_phrase} for url: {response.url}"
            )
            raise FatalAPIError(msg)

        if 500 <= response.status_code < 600:
            msg = (
                f"{response.status_code} Server Error: "
                f"{response.reason_phrase} for url: {response.url}"
            )
            raise RetriableAPIError(msg)

    @backoff.on_exception(
        backoff.expo,
        (RetriableAPIError, httpx.ReadTimeout),
        max_tries=5,
        factor=2,
    )
    def _request_with_backoff(
        self,
        prepared_request: httpx.Request,
        context: dict[str, Any] | None,
    ) -> httpx.Response:
        """Make HTTP request with retry logic.

        Args:
        ----
            prepared_request: Prepared HTTP request
            context: Stream context

        Returns:
        -------
            HTTP response

        """
        response = self.requests_session.send(prepared_request)
        self.validate_response(response)
        return response

    def get_starting_replication_key_value(
        self, context: dict | None = None
    ) -> str | None:
        """Get the starting replication key value for incremental sync.

        Args:
        ----
            context: Stream context

        Returns:
        -------
            Starting replication key value or None for full sync

        """
        if not self.replication_key:
            return None

        # Get the starting value from state
        state = self.get_context_state(context or {})

        # Check for bookmark in state
        bookmark_value = (
            state.get("bookmarks", {}).get(self.name, {}).get("replication_key_value")
        )

        if bookmark_value:
            self.logger.info(
                "Using bookmark value for %s: %s", self.name, bookmark_value
            )
            return bookmark_value

        # Check for start_date in config
        start_date = self.config.get("start_date")
        if start_date:
            self.logger.info("Using start_date for %s: %s", self.name, start_date)
            return start_date

        return None

    def get_replication_key_signpost(self, context: dict | None = None) -> str | None:
        """Get the current replication key signpost.

        Args:
        ----
            context: Stream context

        Returns:
        -------
            Current replication key value

        """
        if not self.replication_key:
            return None

        state = self.get_context_state(context or {})
        return (
            state.get("bookmarks", {}).get(self.name, {}).get("replication_key_value")
        )

    def compare_replication_key_value(self, value1: str, value2: str) -> int:
        """Compare two replication key values.

        Args:
        ----
            value1: First value
            value2: Second value

        Returns:
        -------
            -1 if value1 < value2, 0 if equal, 1 if value1 > value2

        """
        if not self.replication_key:
            return 0

        # Handle timestamp comparison
        if self.replication_key.endswith(("_ts", "_at", "_time")):
            from datetime import datetime

            try:
                dt1 = datetime.fromisoformat(value1.replace("Z", "+00:00"))
                dt2 = datetime.fromisoformat(value2.replace("Z", "+00:00"))

                if dt1 < dt2:
                    return -1
                if dt1 > dt2:
                    return 1
                return 0
            except ValueError:
                # Fall back to string comparison
                pass

        # String comparison
        if value1 < value2:
            return -1
        if value1 > value2:
            return 1
        return 0

    def update_sync_progress_markers(
        self,
        latest_record: dict,
        latest_bookmark: str | None,
        context: dict,
    ) -> None:
        """Update sync progress markers.

        Args:
        ----
            latest_record: Latest record processed
            latest_bookmark: Latest bookmark value
            context: Stream context

        """
        if not self.replication_key or not latest_record:
            return

        # Get replication key value from record
        replication_value = latest_record.get(self.replication_key)
        if not replication_value:
            return

        # Convert to string for consistency
        replication_value = str(replication_value)

        # Update the bookmark if this value is newer
        current_bookmark = self.get_replication_key_signpost(context)

        if (
            not current_bookmark
            or self.compare_replication_key_value(replication_value, current_bookmark)
            > 0
        ):
            # Update state
            state = self.get_context_state(context)
            if "bookmarks" not in state:
                state["bookmarks"] = {}
            if self.name not in state["bookmarks"]:
                state["bookmarks"][self.name] = {}

            state["bookmarks"][self.name]["replication_key_value"] = replication_value
            state["bookmarks"][self.name]["replication_key"] = self.replication_key

            # Log progress
            self.logger.info(
                "Updated bookmark for %s: %s=%s",
                self.name,
                self.replication_key,
                replication_value,
            )

    def post_process(
        self, row: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Post-process each record.

        Args:
        ----
            row: Individual record
            context: Stream context

        Returns:
        -------
            Processed record

        """
        # Ensure all schema properties exist (with None for missing)
        if "properties" in self._entity_schema:
            for prop in self._entity_schema["properties"]:
                if prop not in row:
                    row[prop] = None

        # Update sync progress markers for incremental replication
        if context:
            self.update_sync_progress_markers(row, None, context)

        return row


def create_dynamic_stream_class(
    entity_name: str, schema: dict[str, Any]
) -> type[WMSDynamicStream]:
    """Create a dynamic stream class for an entity.

    Args:
    ----
        entity_name: Name of the entity
        schema: JSON schema for the entity

    Returns:
    -------
        Dynamic stream class

    """
    # Create a new class dynamically
    class_name = f"{entity_name.title().replace('_', '')}Stream"

    # Create class with proper attributes
    return type(
        class_name,
        (WMSDynamicStream,),
        {
            "_entity_name": entity_name,
            "_entity_schema": schema,
        },
    )

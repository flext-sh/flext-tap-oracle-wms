"""Advanced WMS streams with full Singer SDK functionality.

This module implements all advanced features for Oracle WMS tap:
- Dynamic schema discovery
- Cursor and offset pagination
- Field selection and filtering
- Retry logic and circuit breaker
- Performance optimization
- Monitoring and metrics
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import parse_qs, urlparse

from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from singer_sdk.pagination import BaseOffsetPaginator
from singer_sdk.streams import RESTStream


# Context type alias for compatibility
Context = dict[str, Any]

from .auth import get_wms_authenticator, get_wms_headers


if TYPE_CHECKING:
    from collections.abc import Iterable

    import httpx


logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for resilient API calls."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60) -> None:
        """Initialize circuit breaker.

        Args:
        ----
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery

        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call_succeeded(self) -> None:
        """Record successful call."""
        self.failure_count = 0
        self.state = "closed"

    def call_failed(self) -> None:
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                "Circuit breaker opened after %d failures", self.failure_count
            )

    def can_attempt_call(self) -> bool:
        """Check if call can be attempted."""
        if self.state == "closed":
            return True

        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                logger.info("Circuit breaker entering half-open state")
                return True
            return False

        # half-open state
        return True


class WMSAdvancedPaginator(BaseOffsetPaginator):
    """Advanced paginator supporting both offset and cursor modes."""

    def __init__(self, start_value: int, page_size: int, mode: str = "offset") -> None:
        """Initialize paginator.

        Args:
        ----
            start_value: Starting offset/page
            page_size: Records per page
            mode: Pagination mode (offset or sequenced)

        """
        super().__init__(start_value=start_value, page_size=page_size)
        self.mode = mode
        self._cursor = None
        self._total_records = None
        self._current_page = start_value

    def has_more(self, response: httpx.Response) -> bool:
        """Check if more pages exist."""
        try:
            data = response.json()

            # Track total records if available
            if "result_count" in data:
                self._total_records = data["result_count"]

            if self.mode == "sequenced":
                # Cursor-based pagination
                return bool(data.get("next_page"))

            # Offset-based pagination
            current_page = data.get("page_nbr", self._current_page)
            total_pages = data.get("page_count", 1)

            # Also check if we got any results
            has_results = bool(data.get("results"))

            return current_page < total_pages and has_results

        except (ValueError, KeyError):
            return False

    def get_next(self, response: httpx.Response) -> Optional[int]:
        """Get next page token."""
        if not self.has_more(response):
            return None

        try:
            data = response.json()

            if self.mode == "sequenced":
                # Extract cursor from next_page URL
                next_url = data.get("next_page")
                if next_url:
                    parsed = urlparse(next_url)
                    query_params = parse_qs(parsed.query)
                    cursor = query_params.get("cursor", [None])[0]
                    self._cursor = cursor
                    return self.current_value + 1
                return None

            # Offset mode
            self._current_page += 1
            return self._current_page

        except (ValueError, KeyError):
            return None


class WMSAdvancedStream(RESTStream):
    """Advanced WMS stream with full functionality."""

    # API configuration
    url_base = "https://ta29.wms.ocs.oraclecloud.com/raizen_test"
    rest_method = "GET"
    records_jsonpath = "$.results[*]"
    next_page_token_jsonpath = "$.next_page"

    # Limits
    MAX_PAGE_SIZE = 1250
    DEFAULT_PAGE_SIZE = 100

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    BACKOFF_FACTOR = 2.0

    # Performance settings
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks for streaming

    def __init__(
        self, tap, entity_name: str, schema: dict | None = None, **kwargs
    ) -> None:
        """Initialize advanced WMS stream.

        Args:
        ----
            tap: Parent tap instance
            entity_name: WMS entity name
            schema: Dynamic schema
            **kwargs: Additional arguments

        """
        self.entity_name = entity_name
        self._dynamic_schema = schema
        self._circuit_breaker = CircuitBreaker()

        # Features state
        self._field_selection = None
        self._values_list = False
        self._distinct_values = False
        self._retry_count = 0

        # Performance optimization
        self._connection_pool = None
        self._http2_enabled = tap.config.get("http2_enabled", False)
        self._compression_enabled = tap.config.get("compression_enabled", True)

        # Monitoring
        self._start_time = None
        self._records_extracted = 0
        self._api_calls = 0
        self._errors = {}

        super().__init__(tap=tap, **kwargs)

    @property
    def name(self) -> str:
        """Stream name."""
        return self.entity_name

    @property
    def path(self) -> str:
        """API path."""
        return f"/wms/lgfapi/v10/entity/{self.entity_name}"

    @property
    def url(self) -> str:
        """Full URL."""
        base = self.config.get("base_url", self.url_base).rstrip("/")
        return f"{base}{self.path}"

    def get_url_params(
        self, context: dict | None, next_page_token: Any | None
    ) -> dict[str, Any]:
        """Build URL parameters with all advanced features."""
        params = {}

        # Always use sequenced pagination for sync efficiency
        params["page_mode"] = "sequenced"
        page_size = min(
            self.config.get("page_size", self.DEFAULT_PAGE_SIZE),
            self.MAX_PAGE_SIZE,
        )
        params["page_size"] = page_size

        # Handle cursor for sequenced mode
        paginator = self.get_new_paginator()
        if next_page_token and hasattr(paginator, "_cursor") and paginator._cursor:
            params["cursor"] = paginator._cursor

        # Date filtering
        if self.config.get("start_date"):
            params["mod_ts__gte"] = self.config["start_date"]
        if self.config.get("end_date"):
            params["mod_ts__lte"] = self.config["end_date"]

        # Entity-specific filters
        entity_filters = self.config.get("entity_filters", {}).get(self.entity_name, {})
        params.update(entity_filters)

        # Field selection
        if self.config.get("field_selection", {}).get(self.entity_name):
            fields = self.config["field_selection"][self.entity_name]
            params["fields"] = ",".join(fields)
            self._field_selection = fields

        # Values list mode
        if self.config.get("values_list_mode", {}).get(self.entity_name):
            fields = self.config["values_list_mode"][self.entity_name]
            params["values_list"] = ",".join(fields)
            self._values_list = True

        # Distinct values
        if self.config.get("distinct_values", {}).get(self.entity_name):
            params["distinct"] = 1
            self._distinct_values = True

        # Ordering
        if self.config.get("ordering", {}).get(self.entity_name):
            params["ordering"] = self.config["ordering"][self.entity_name]

        # Advanced filters with operators
        advanced_filters = self.config.get("advanced_filters", {}).get(
            self.entity_name, {}
        )
        for conditions in advanced_filters.values():
            if isinstance(conditions, dict):
                for value in conditions.values():
                    params[f"{field}{operator}"] = value
            else:
                params[field] = conditions

        return params

    def get_new_paginator(self) -> WMSAdvancedPaginator:
        """Create paginator instance."""
        page_size = min(
            self.config.get("page_size", self.DEFAULT_PAGE_SIZE),
            self.MAX_PAGE_SIZE,
        )
        # Always use sequenced mode for sync efficiency
        return WMSAdvancedPaginator(
            start_value=1, page_size=page_size, mode="sequenced"
        )

    @property
    def authenticator(self) -> Any:
        """Get authenticator."""
        return get_wms_authenticator(self, self.config)

    def get_http_headers(self) -> dict:
        """Get HTTP headers with compression support."""
        headers = get_wms_headers(self.config)

        # Add compression
        if self._compression_enabled:
            headers["Accept-Encoding"] = "gzip, deflate, br"

        # Add Singer SDK headers
        headers.update(super().get_http_headers())

        return headers

    def validate_response(self, response: httpx.Response) -> None:
        """Validate HTTP response with circuit breaker."""
        if 200 <= response.status_code < 300:
            self._circuit_breaker.call_succeeded()
            return

        # Check circuit breaker
        if not self._circuit_breaker.can_attempt_call():
            msg = f"Circuit breaker is open for {self.entity_name}"
            raise FatalAPIError(msg)

        # Handle specific errors
        if response.status_code == 429:
            self._circuit_breaker.call_failed()
            retry_after = response.headers.get("Retry-After", "60")
            msg = f"Rate limited. Retry after {retry_after} seconds"
            raise RetriableAPIError(msg)

        if response.status_code in [500, 502, 503, 504]:
            self._circuit_breaker.call_failed()
            msg = f"Server error {response.status_code} for {self.entity_name}"
            raise RetriableAPIError(msg)

        if response.status_code == 401:
            msg = "Authentication failed. Check credentials"
            raise FatalAPIError(msg)

        if response.status_code == 403:
            msg = f"Access denied to entity {self.entity_name}"
            raise FatalAPIError(msg)

        # Default validation
        super().validate_response(response)

    def parse_response(self, response: httpx.Response) -> Iterable[dict]:
        """Parse response with advanced error handling."""
        self._api_calls += 1

        try:
            data = response.json()

            # Handle values list mode
            if self._values_list:
                if isinstance(data, dict) and "results" in data:
                    for row in data["results"]:
                        if isinstance(row, list) and self._field_selection:
                            yield dict(zip(self._field_selection, row))
                        else:
                            yield {"values": row}
                return

            # Standard response formats
            if isinstance(data, dict):
                if "results" in data:
                    # Paginated response
                    for record in data["results"]:
                        self._records_extracted += 1
                        yield record
                elif "data" in data:
                    # Alternative format
                    for record in data["data"]:
                        self._records_extracted += 1
                        yield record
                else:
                    # Single record
                    self._records_extracted += 1
                    yield data
            elif isinstance(data, list):
                # Direct list
                for record in data:
                    self._records_extracted += 1
                    yield record
            else:
                # Unknown format
                logger.warning("Unexpected response format for %s", self.entity_name)
                yield data

        except json.JSONDecodeError as e:
            self._errors["json_decode"] = self._errors.get("json_decode", 0) + 1
            logger.error("JSON decode error for {self.entity_name}: %s", e)
            msg = f"Invalid JSON response from {self.entity_name}"
            raise FatalAPIError(msg) from e
        except Exception as e:
            self._errors["parse_error"] = self._errors.get("parse_error", 0) + 1
            logger.error("Parse error for {self.entity_name}: %s", e)
            raise

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """Post-process records with validation."""
        # Skip invalid records
        if not isinstance(row, dict):
            logger.warning("Invalid record type in {self.entity_name}: %s", type(row))
            return None

        # Ensure ID exists (most entities have it)
        if not row.get("id") and "id" not in row:
            # Some entities might not have ID field
            logger.debug("Record without ID in %s", self.entity_name)

        # Add metadata
        row["_entity_name"] = self.entity_name
        row["_extracted_at"] = datetime.utcnow().isoformat()

        # Add extraction context if available
        if context:
            row["_extraction_context"] = context

        return row

    @property
    def schema(self) -> dict:
        """Dynamic schema with fallback."""
        if self._dynamic_schema:
            return self._dynamic_schema

        # Minimal fallback schema
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": ["integer", "string", "null"],
                    "description": "Entity identifier",
                },
                "_entity_name": {"type": "string", "description": "WMS entity name"},
                "_extracted_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Extraction timestamp",
                },
            },
            "additionalProperties": True,
        }

    def get_records(self, context: Context | None) -> Iterable[dict]:
        """Get records with monitoring."""
        self._start_time = time.time()

        try:
            yield from super().get_records(context)
        finally:
            # Log extraction metrics
            duration = time.time() - self._start_time
            if duration > 0:
                rate = self._records_extracted / duration
                logger.info(
                    "Extracted %d records from %s in %.2fs (%.2f records/sec)",
                    self._records_extracted,
                    self.entity_name,
                    duration,
                    rate,
                )

            if self._errors:
                logger.warning("Errors during extraction: %s", self._errors)

    def request_decorator(self, func) -> Any:
        """Decorator for retry logic with exponential backoff."""

        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(self.MAX_RETRIES):
                try:
                    return func(*args, **kwargs)
                except RetriableAPIError as e:
                    last_exception = e
                    if attempt < self.MAX_RETRIES - 1:
                        delay = self.RETRY_DELAY * (self.BACKOFF_FACTOR**attempt)
                        logger.warning(
                            "Retrying after %.1fs (attempt %d/%d): %s",
                            delay,
                            attempt + 1,
                            self.MAX_RETRIES,
                            e,
                        )
                        time.sleep(delay)
                    else:
                        logger.error("Max retries reached for %s", self.entity_name)
                        raise
                except Exception:
                    # Don't retry on non-retriable errors
                    raise

            if last_exception:
                raise last_exception
            return None

        return wrapper


# Export the advanced stream
WMSEntityStream = WMSAdvancedStream

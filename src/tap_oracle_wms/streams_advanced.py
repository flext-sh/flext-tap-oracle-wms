"""Advanced WMS streams with full Singer SDK functionality.

This module implements all advanced features for Oracle WMS tap:
- Dynamic schema discovery
- Cursor and offset pagination
- Field selection and filtering
- Retry logic and circuit breaker
- Performance optimization
- Monitoring and metrics

INCREMENTAL SYNC RULES (based on validated implementation):
===========================================================
For incremental sync, the following rules are implemented:

1. Filter Rule: mod_ts > max(mod_ts do banco) - 5 min
   - Get maximum MOD_TS from existing database table
   - Subtract 5 minutes for safety overlap
   - Filter WMS API with: mod_ts__gte = (max_mod_ts - 5min)

2. Ordering Rule: mod_ts (chronological ascending)
   - Always use chronological ordering for incremental sync
   - Ensures proper timestamp-based processing

3. Pagination Configuration:
   - Singer SDK: pagination_mode="cursor" (follows next_page URLs)
   - WMS API: page_mode="sequenced" (cursor-based, no total counts)
   - Optimal page size: 1000 for WMS API performance

4. Operation: UPSERT with TK_DATE support
   - Insert new records or update existing based on ID
   - Handle timestamp fields correctly

FULL SYNC RULES:
================
For full sync, the following rules are implemented:

1. Filter Rule: id < min_id_in_table
   - Get minimum ID from existing database table
   - Filter WMS API with: id__lt = (min_id - 1)

2. Ordering Rule: -id (descending)
   - Process records from highest ID to lowest
   - Allows intelligent resume from interruptions

3. Pagination Configuration:
   - Singer SDK: pagination_mode="cursor" (follows next_page URLs)
   - WMS API: page_mode="sequenced" (cursor-based, no total counts)

WMS PAGINATION MODES EXPLAINED:
==============================

Oracle WMS API supports two page_mode values for different use cases:

• page_mode="paged" (default):
  - Returns: result_count, page_count, page_nbr, next_page, previous_page, results
  - Navigation: Uses ?page=3 parameter for specific pages
  - Behavior: Calculates total counts upfront (slower for large datasets)
  - Use case: Human-readable interfaces, when total counts are needed

• page_mode="sequenced" (recommended for system integrations):
  - Returns: only next_page, previous_page, results (no totals)
  - Navigation: Uses ?cursor=cD0xNDAw parameter (system-generated)
  - Behavior: Generated on-the-fly for better performance
  - Use case: System-to-system integration, when totals are not needed

SINGER SDK PAGINATION MODES:
============================

The Singer SDK pagination_mode setting determines how the tap handles pagination:

• pagination_mode="offset":
  - Works with numeric page numbers
  - Compatible with WMS page_mode="paged"
  - Uses page tokens for navigation

• pagination_mode="cursor":
  - Works with next_page URLs
  - Compatible with WMS page_mode="sequenced"
  - Follows hyperlinks for navigation

OPTIMAL CONFIGURATION FOR INCREMENTAL SYNC:
===========================================

For best performance with incremental sync:
- Singer SDK: pagination_mode="cursor"
- WMS API: page_mode="sequenced"
- Page size: 1000 (optimal balance between API efficiency and memory usage)
- Ordering: mod_ts ASC (chronological for incremental)
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any
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
                "Circuit breaker opened after %d failures",
                self.failure_count,
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

    def get_next(self, response: httpx.Response) -> int | None:
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
    """Advanced WMS stream with full functionality and incremental sync support.

    INCREMENTAL SYNC IMPLEMENTATION:
    ===============================
    This stream implements proper incremental sync based on MOD_TS timestamps:

    1. Replication Method: INCREMENTAL
    2. Replication Key: mod_ts
    3. Bookmark Strategy:
       - Get max(mod_ts) from state/database
       - Apply 5-minute safety overlap
       - Filter: mod_ts__gte = max_mod_ts - 5min
    4. Ordering: mod_ts ASC (chronological)
    5. State Management: Track latest mod_ts for next run

    FULL SYNC IMPLEMENTATION:
    =========================
    For full sync with intelligent resume:

    1. Replication Method: FULL_TABLE
    2. Resume Strategy:
       - Get min(id) from existing data
       - Filter: id__lt = min_id - 1
    3. Ordering: -id DESC (highest to lowest)
    4. State Management: Track minimum ID processed
    """

    # API configuration - Class attribute for Singer SDK compatibility
    url_base = ""  # Will be overridden by url property
    rest_method = "GET"
    records_jsonpath = "$.results[*]"
    next_page_token_jsonpath = "$.next_page"

    # Limits
    MAX_PAGE_SIZE = 1250
    DEFAULT_PAGE_SIZE = 1000  # Optimized for WMS API

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    BACKOFF_FACTOR = 2.0

    # Performance settings
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks for streaming

    # Incremental sync configuration
    replication_method = "INCREMENTAL"  # Default to incremental
    replication_keys = ["mod_ts"]  # MOD_TS is the change tracking field

    def __init__(
        self,
        tap,
        entity_name: str,
        schema: dict | None = None,
        **kwargs,
    ) -> None:
        """Initialize advanced WMS stream with incremental sync support.

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

        # Store config for dynamic URL construction
        self._base_url = tap.config.get("base_url")
        if not self._base_url:
            msg = "base_url MUST be configured - NO hardcode allowed"
            raise ValueError(msg)

        # Incremental sync support
        self._enable_incremental = tap.config.get("enable_incremental", True)
        self._safety_overlap_minutes = tap.config.get("incremental_overlap_minutes", 5)

        # Set replication method based on config
        if self._enable_incremental:
            self.replication_method = "INCREMENTAL"
            self.replication_keys = ["mod_ts"]
        else:
            self.replication_method = "FULL_TABLE"
            self.replication_keys = []

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
        self._start_time: float | None = None
        self._records_extracted = 0
        self._api_calls = 0
        self._errors: dict[str, int] = {}

        super().__init__(tap=tap, **kwargs)

        # CRITICAL: Override url_base after super().__init__ for Singer SDK
        self.url_base = self._base_url.rstrip("/")

    @property
    def name(self) -> str:
        """Stream name."""
        return self.entity_name

    @property
    def requests_session(self):
        """Create requests session with configured timeout.

        Override Singer SDK default to use our configured request_timeout
        instead of the hardcoded 300-second timeout for massive data extractions.
        """
        import requests

        session = requests.Session()
        # Get timeout from config, default to 7200 seconds (2 hours) for massive historical extractions
        timeout = self.config.get("request_timeout", 7200)

        # Apply timeout to all requests made by this session
        session.request = lambda *args, **kwargs: (
            kwargs.setdefault("timeout", timeout),
            super(requests.Session, session).request(*args, **kwargs),
        )[1]

        return session

    @property
    def path(self) -> str:
        """API path."""
        return f"/wms/lgfapi/v10/entity/{self.entity_name}"

    @property
    def url(self) -> str:
        """Full URL using config base_url."""
        return f"{self._base_url.rstrip('/')}{self.path}"

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Build URL parameters with incremental sync rules implemented.

        INCREMENTAL SYNC RULES IMPLEMENTATION:
        =====================================

        For INCREMENTAL sync:
        - Filter: mod_ts__gte = max(mod_ts from state) - 5 minutes
        - Ordering: mod_ts ASC (chronological)
        - WMS API: page_mode="sequenced" (cursor navigation, no totals)

        For FULL_TABLE sync:
        - Filter: id__lt = min(id from state) if resuming
        - Ordering: -id DESC (highest to lowest)
        - WMS API: page_mode="sequenced" (cursor navigation, no totals)

        Note: Singer SDK uses pagination_mode="cursor" to handle next_page URLs,
        while WMS API uses page_mode="sequenced" for efficient navigation.

        This method now uses the tap's generic filtering methods to ensure
        consistent behavior across all entities.
        """
        # Build base parameters
        params: dict[str, Any] = {
            "page_mode": "sequenced",  # WMS API: cursor-based pagination (high performance)
            "page_size": self._get_optimal_page_size(),
        }

        # Apply generic entity filters from configuration
        params = self._tap.apply_entity_filters(self.entity_name, params)

        # Handle incremental vs full sync filtering using generic methods
        replication_method = self.replication_method

        if replication_method == "INCREMENTAL":
            # Get bookmark for incremental sync
            bookmark_value = self.get_starting_replication_key_value(context)
            params = self._tap.apply_incremental_filters(
                self.entity_name,
                params,
                bookmark_value,
            )

            # Ensure chronological ordering for incremental
            if "ordering" not in params:
                replication_config = self._tap.get_entity_replication_config(
                    self.entity_name,
                )
                params["ordering"] = replication_config["ordering"]["incremental"]

        elif replication_method == "FULL_TABLE":
            # Apply full sync filters with resume capability
            resume_context = self._get_resume_context(context)
            params = self._tap.apply_full_sync_filters(
                self.entity_name,
                params,
                resume_context,
            )

        # Handle pagination token (next_page URL from WMS)
        if next_page_token:
            # For cursor-based pagination, the next_page_token contains
            # URL parameters that override our base parameters
            if isinstance(next_page_token, dict):
                params.update(next_page_token)
            elif isinstance(next_page_token, str):
                # Parse cursor token if it's a string
                try:
                    import urllib.parse as urlparse

                    parsed = urlparse.parse_qs(next_page_token)
                    # Convert single-item lists to values
                    cursor_params = {
                        k: v[0] if len(v) == 1 else v for k, v in parsed.items()
                    }
                    params.update(cursor_params)
                except Exception as e:
                    logger.warning(f"Failed to parse next_page_token: {e}")

        # Log final parameters for debugging
        logger.debug(f"🔧 Final URL params for {self.entity_name}: {params}")

        return params

    def _get_resume_context(self, context: dict | None) -> dict[str, Any] | None:
        """Get resume context for full sync intelligent resume.

        RESUME CONTEXT CONSTRUCTION:
        ===========================
        This method provides context about existing data in the target system
        to enable intelligent resume of interrupted full syncs. It's used by
        the generic full sync filtering to determine where to resume.

        Context Information:
        -------------------
        - has_existing_data: Whether target has data for this entity
        - min_id_in_target: Minimum ID already in target (for id < min_id filter)
        - total_records: Estimated total records in target
        - sync_strategy: Preferred strategy for this resume

        This is a placeholder implementation that can be enhanced with actual
        target system queries when integrated with specific targets.

        Args:
            context: Stream context from Singer SDK

        Returns:
            Resume context dictionary or None if no resume needed

        """
        # TODO: This can be enhanced to query the target system (database, warehouse)
        # to get actual statistics about existing data. For now, we provide a
        # basic implementation that checks for configuration hints.

        resume_config = self.config.get("resume_config", {}).get(self.entity_name, {})

        if resume_config.get("enabled", False):
            return {
                "has_existing_data": resume_config.get("has_existing_data", False),
                "min_id_in_target": resume_config.get("min_id_in_target"),
                "total_records": resume_config.get("total_records", 0),
                "sync_strategy": resume_config.get("strategy", "id_based_resume"),
            }

        return None

    def get_new_paginator(self) -> WMSAdvancedPaginator:
        """Create paginator instance."""
        page_size = min(
            self.config.get("page_size", self.DEFAULT_PAGE_SIZE),
            self.MAX_PAGE_SIZE,
        )
        # Always use sequenced mode for sync efficiency
        return WMSAdvancedPaginator(
            start_value=1,
            page_size=page_size,
            mode="sequenced",
        )

    @property
    def authenticator(self) -> Any:
        """Get authenticator."""
        return get_wms_authenticator(self, self.config)

    @property
    def http_headers(self) -> dict:
        """Get HTTP headers with compression and authentication support."""
        headers = get_wms_headers(self.config)

        # Add compression
        if self._compression_enabled:
            headers["Accept-Encoding"] = "gzip, deflate, br"

        # CRITICAL FIX: Add authentication headers (was missing!)
        if self.authenticator:
            headers.update(self.authenticator.auth_headers)

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

        if response.status_code in {500, 502, 503, 504}:
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

    def parse_response(self, response: httpx.Response) -> Iterable[dict[str, Any]]:
        """Parse response with advanced error handling."""
        self._api_calls += 1

        try:
            data = response.json()

            # Handle values list mode
            if self._values_list:
                if isinstance(data, dict) and "results" in data:
                    for row in data["results"]:
                        if isinstance(row, list) and self._field_selection:
                            yield dict(zip(self._field_selection, row, strict=False))
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
                    # Single record
                    self._records_extracted += 1
                    yield data
            elif isinstance(data, list):
                # Direct list
                for record in data:
                    self._records_extracted += 1
                    yield record
                # Unknown format
                logger.warning("Unexpected response format for %s", self.entity_name)
                yield data

        except json.JSONDecodeError as e:
            self._errors["json_decode"] = self._errors.get("json_decode", 0) + 1
            logger.exception("JSON decode error for {self.entity_name}: %s", e)
            msg = f"Invalid JSON response from {self.entity_name}"
            raise FatalAPIError(msg) from e
        except Exception as e:
            self._errors["parse_error"] = self._errors.get("parse_error", 0) + 1
            logger.exception("Parse error for {self.entity_name}: %s", e)
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
                        logger.exception("Max retries reached for %s", self.entity_name)
                        raise
                except Exception:
                    # Don't retry on non-retriable errors
                    raise

            if last_exception:
                raise last_exception
            return None

        return wrapper

    def _get_optimal_page_size(self) -> int:
        """Get optimal page size for this entity.

        DYNAMIC PAGE SIZE OPTIMIZATION:
        ==============================
        This method calculates the optimal page size for each entity based on:
        - Configuration settings (entity-specific or global)
        - Entity characteristics (estimated record size)
        - Performance constraints (memory, network)
        - API limitations (WMS-imposed maximums)

        Page Size Strategy:
        ------------------
        1. Use entity-specific page_size if configured
        2. Use global page_size from configuration
        3. Apply performance optimizations based on entity type
        4. Enforce WMS API maximum limits

        Args:
            None

        Returns:
            Optimal page size for this entity

        """
        # Check entity-specific page size configuration
        entity_pagination_config = self.config.get("pagination_config", {}).get(
            self.entity_name,
            {},
        )
        entity_page_size = entity_pagination_config.get("page_size")

        if entity_page_size:
            return min(entity_page_size, self.MAX_PAGE_SIZE)

        # Check global page size configuration
        global_page_size = self.config.get("page_size", self.DEFAULT_PAGE_SIZE)

        # Apply entity-specific optimizations
        # Large entities with many fields: smaller page sizes
        if self.entity_name in {"allocation_dtl", "inventory_dtl", "order_line"}:
            optimized_size = min(
                global_page_size,
                500,
            )  # Detailed entities: smaller pages
        # Lookup entities with few fields: larger page sizes
        elif self.entity_name in {"facility", "item_master", "location"}:
            optimized_size = min(
                global_page_size * 2,
                2000,
            )  # Simple entities: larger pages
        else:
            optimized_size = global_page_size

        return min(optimized_size, self.MAX_PAGE_SIZE)


# Export the advanced stream
WMSEntityStream = WMSAdvancedStream

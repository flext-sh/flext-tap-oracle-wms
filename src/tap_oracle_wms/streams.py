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

from datetime import datetime, timezone
import json
import logging
import time
from typing import TYPE_CHECKING, Any

from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

from .auth import get_wms_authenticator, get_wms_headers


if TYPE_CHECKING:
    from collections.abc import Iterable

    import httpx


# Context type alias for compatibility
Context = dict[str, Any]


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


class WMSAdvancedPaginator(BaseHATEOASPaginator):
    """Modern WMS paginator using HATEOAS pattern for next_page URLs.

    MODERN SINGER SDK 0.46.4+ PAGINATION PATTERN:
    =============================================
    This paginator follows the modern Singer SDK HATEOAS (Hypermedia as the
    Engine of Application State) pattern by extracting next_page URLs from
    the API response and using them for navigation.

    Oracle WMS API Response Format:
    ------------------------------
    {
        "results": [...],
        "next_page": "https://api.com/entity?cursor=xyz&page_size=1000",
        "page_nbr": 1,
        "page_count": 10,
        "result_count": 9500
    }

    Singer SDK Integration:
    ----------------------
    - BaseHATEOASPaginator automatically handles ParseResult objects
    - current_value property contains parsed URL components
    - get_next_url() extracts the next_page URL from response
    - Singer SDK handles URL parameter extraction via get_url_params()
    """

    def get_next_url(self, response) -> str | None:
        """Extract next_page URL from Oracle WMS API response.

        Modern Singer SDK 0.46.4+ Pattern:
        ----------------------------------
        This method implements the HATEOAS pattern by extracting the next_page
        URL directly from the API response. The Singer SDK will automatically
        parse this URL and provide the components via current_value.

        Oracle WMS API provides cursor-based pagination URLs like:
        https://api.com/entity?cursor=cD0xNDAw&page_size=1000&page_mode=sequenced

        Args:
            response: HTTP response from Oracle WMS API

        Returns:
            Next page URL string or None if no more pages
        """
        try:
            data = response.json()
            return data.get("next_page")
        except (ValueError, KeyError, AttributeError):
            return None

    def has_more(self, response) -> bool:
        """Check if more pages are available.

        Modern Implementation:
        ---------------------
        Uses the next_page URL presence as the definitive indicator of more data.
        This aligns with Oracle WMS page_mode="sequenced" behavior where
        page counts are not provided for performance reasons.

        Args:
            response: HTTP response from Oracle WMS API

        Returns:
            True if more pages available, False otherwise
        """
        try:
            data = response.json()

            # Primary check: next_page URL presence
            has_next_url = bool(data.get("next_page"))

            # Secondary check: ensure we have results in current page
            has_results = bool(data.get("results"))

            # For first page, we need results to continue
            # For subsequent pages, next_page URL is sufficient
            if self.count == 0:
                return has_next_url and has_results

            return has_next_url

        except (ValueError, KeyError, AttributeError):
            return False


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
        tap: Any,
        entity_name: str,
        schema: dict | None = None,
        **kwargs: Any,
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
    def requests_session(self) -> None:
        """Create requests session with configured timeout.

        Override Singer SDK default to use our configured request_timeout
        instead of the hardcoded 300-second timeout for massive data extractions.
        """
        import requests

        session = requests.Session()
        # Get timeout from config, default to 7200 seconds (2 hours) for
        # massive historical extractions
        timeout = self.config.get("request_timeout", 7200)

        # Apply timeout to all requests made by this session
        session.request = lambda *args, **kwargs: (
            kwargs.setdefault("timeout", timeout),
            super(requests.Session, session).request(*args, **kwargs),
        )[1]

        return session

    @property
    def path(self) -> str:
        """Get the API path for this stream's entity endpoint."""
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
        """Build URL parameters using modern Singer SDK 0.46.4+ HATEOAS pattern.

        MODERN SINGER SDK 0.46.4+ PAGINATION PATTERN:
        =============================================

        The modern Singer SDK uses HATEOAS (Hypermedia as the Engine of Application
        State) pagination where:

        1. First Request: Uses base parameters (filters, ordering, page_size)
        2. Subsequent Requests: Uses parameters extracted from next_page URLs
        3. ParseResult Integration: next_page_token is a ParseResult object with
           parsed URL components (scheme, netloc, path, query, etc.)

        Oracle WMS API Integration:
        --------------------------
        - First request: page_mode=sequenced, page_size=1000, filters, ordering
        - Next requests: cursor=xyz, page_size=1000 (from next_page URL)
        - The cursor parameter contains the continuation state

        This method handles both first requests and continuation requests seamlessly.
        """
        # For subsequent pages, extract parameters from next_page URL
        if next_page_token and hasattr(next_page_token, "query"):
            # Modern HATEOAS pattern: Extract URL parameters from ParseResult
            from urllib.parse import parse_qsl

            try:
                # Parse query string from next_page URL
                url_params = dict(parse_qsl(next_page_token.query))

                # Log pagination continuation for debugging
                logger.debug(
                    f"🔄 Continuing pagination for {self.entity_name} with cursor: "
                    f"{url_params.get('cursor', 'unknown')[:20]}..."
                )

                return url_params

            except (AttributeError, ValueError) as e:
                logger.warning(
                    f"Failed to parse HATEOAS next_page_token for {self.entity_name}: {e}"
                )
                # Fall through to base parameters

        # First request: Build base parameters with filters and ordering
        params: dict[str, Any] = {
            "page_mode": "sequenced",  # Oracle WMS: cursor-based pagination
            "page_size": self._get_optimal_page_size(),
        }

        # Apply entity-specific filters from configuration
        if hasattr(self._tap, "apply_entity_filters"):
            params = self._tap.apply_entity_filters(self.entity_name, params)

        # Handle incremental vs full sync filtering
        replication_method = self.replication_method

        if replication_method == "INCREMENTAL":
            # Apply incremental sync filters (mod_ts__gte with safety overlap)
            bookmark_value = self.get_starting_replication_key_value(context)

            if hasattr(self._tap, "apply_incremental_filters"):
                params = self._tap.apply_incremental_filters(
                    self.entity_name,
                    params,
                    bookmark_value,
                )
            elif bookmark_value:
                # Fallback implementation for incremental sync
                from datetime import datetime, timedelta, timezone

                # Apply 5-minute safety overlap for incremental sync
                if isinstance(bookmark_value, (str, datetime)):
                    if isinstance(bookmark_value, str):
                        try:
                            bookmark_dt = datetime.fromisoformat(
                                bookmark_value.replace("Z", "+00:00")
                            )
                        except ValueError:
                            bookmark_dt = datetime.now(timezone.utc)
                    else:
                        bookmark_dt = bookmark_value

                    # Subtract 5 minutes for safety overlap
                    filter_dt = bookmark_dt - timedelta(minutes=5)
                    params["mod_ts__gte"] = filter_dt.isoformat()

                    # Ensure chronological ordering for incremental
                    params["ordering"] = "mod_ts"

        elif replication_method == "FULL_TABLE":
            # Apply full sync filters with intelligent resume
            resume_context = self._get_resume_context(context)

            if hasattr(self._tap, "apply_full_sync_filters"):
                params = self._tap.apply_full_sync_filters(
                    self.entity_name,
                    params,
                    resume_context,
                )
            elif resume_context and resume_context.get("min_id_in_target"):
                # Fallback implementation for full sync resume
                min_id = resume_context["min_id_in_target"]
                params["id__lt"] = min_id
                params["ordering"] = "-id"  # Descending order

        # Log first request parameters for debugging
        logger.debug(f"🔧 Initial URL params for {self.entity_name}: {params}")

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
        """Create modern HATEOAS paginator instance.

        Modern Singer SDK 0.46.4+ Pattern:
        ----------------------------------
        Returns a HATEOAS-based paginator that extracts next_page URLs from
        Oracle WMS API responses. This eliminates the need for manual cursor
        tracking and provides seamless pagination using the API's native links.

        The paginator will:
        1. Use next_page URLs for navigation
        2. Parse URL parameters automatically
        3. Handle cursor-based pagination transparently
        4. Integrate with Singer SDK's HATEOAS framework

        Returns:
            WMSAdvancedPaginator configured for HATEOAS navigation
        """
        return WMSAdvancedPaginator()

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
        row["_extracted_at"] = datetime.now(timezone.utc).isoformat()

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

    def request_decorator(self, func: Any) -> Any:
        """Decorator for retry logic with exponential backoff."""

        def wrapper(*args, **kwargs) -> Any:
            """Function for wrapper operations."""
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

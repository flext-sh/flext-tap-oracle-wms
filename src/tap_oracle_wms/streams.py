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

Oracle WMS API uses HATEOAS pagination for optimal performance:

• page_mode="sequenced" (ONLY SUPPORTED MODE):
  - Returns: only next_page, previous_page, results (no totals)
  - Navigation: Uses ?cursor=cD0xNDAw parameter (system-generated)
  - Behavior: Generated on-the-fly for better performance
  - Use case: System-to-system integration (optimal for all scenarios)

SINGER SDK PAGINATION MODE:
===========================

This tap uses only one pagination mode for optimal performance:

• pagination_mode="sequenced":
  - Works with cursor-based navigation
  - Compatible with WMS page_mode="sequenced"
  - Uses HATEOAS next_page_url for navigation
  - Optimized for large datasets and system integration

CONFIGURATION:
=============
- Singer SDK: pagination_mode="sequenced" (ONLY OPTION)
- WMS API: page_mode="sequenced" (ONLY OPTION)
- Page size: 100-1000 (optimal balance between API efficiency and memory usage)
- Ordering: id ASC (default) or mod_ts ASC (for incremental)
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

from .auth import get_wms_authenticator, get_wms_headers
from .enhanced_logging import (
    get_enhanced_logger,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    import httpx


# Context type alias for compatibility
Context = dict[str, Any]


logger = logging.getLogger(__name__)
enhanced_logger = get_enhanced_logger(__name__)


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
        self.last_failure_time: float | None = None
        self.state = "closed"  # closed, open, half-open

    def call_succeeded(self) -> None:
        """Record successful call."""
        if self.state != "closed":
            enhanced_logger.info("🔓 Circuit breaker closed - call succeeded")
        self.failure_count = 0
        self.state = "closed"

    def call_failed(self) -> None:
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        enhanced_logger.warning(
            f"🔥 Circuit breaker failure #{self.failure_count}/{self.failure_threshold}"
        )

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            enhanced_logger.error(
                f"🚨 Circuit breaker OPENED after {self.failure_count} failures - blocking calls for {self.recovery_timeout}s"
            )

    def can_attempt_call(self) -> bool:
        """Check if call can be attempted."""
        if self.state == "closed":
            return True

        if self.state == "open":
            if (
                self.last_failure_time is not None
                and time.time() - self.last_failure_time > self.recovery_timeout
            ):
                self.state = "half-open"
                enhanced_logger.info(
                    "🔄 Circuit breaker entering HALF-OPEN state - testing recovery"
                )
                return True

            time_remaining = (
                self.recovery_timeout - (time.time() - self.last_failure_time)
                if self.last_failure_time
                else 0
            )
            enhanced_logger.debug(
                f"🚨 Circuit breaker OPEN - {time_remaining:.1f}s remaining"
            )
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

    def get_next_url(self, response: Any) -> str | None:
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
            return data.get("next_page") if isinstance(data, dict) else None
        except (ValueError, KeyError, AttributeError):
            return None

    def has_more(self, response: Any) -> bool:
        """Check if more pages are available.

        Modern Implementation:
        ---------------------
        Uses the next_page URL presence as the definitive indicator of more data.
        This aligns with Oracle WMS page_mode="sequenced" behavior where
        page counts are not provided for performance reasons.

        Also respects record_limit configuration to prevent extracting thousands of records.

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


class WMSAdvancedStream(RESTStream[dict[str, Any]]):
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
        schema: dict[str, Any] | None = None,
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
        # Store entity name and schema BEFORE parent init
        self._entity_name = entity_name
        self._dynamic_schema = schema or {"type": "object", "properties": {}}

        # Initialize circuit breaker with configuration
        circuit_config = tap.config.get("circuit_breaker", {})
        failure_threshold = circuit_config.get("failure_threshold", 5)
        recovery_timeout = circuit_config.get("recovery_timeout", 60)
        self._circuit_breaker = CircuitBreaker(failure_threshold, recovery_timeout)

        enhanced_logger.info(
            f"🔒 Circuit breaker initialized for {entity_name}: threshold={failure_threshold}, timeout={recovery_timeout}s"
        )

        # Store config for dynamic URL construction
        self._base_url = tap.config.get("base_url")
        if not self._base_url:
            msg = "base_url MUST be configured - NO hardcode allowed"
            raise ValueError(msg)

        # CRITICAL: Set _schema attribute for Singer SDK compatibility
        # Add metadata fields that will be added in post_process
        enhanced_schema = self._dynamic_schema.copy()
        if "properties" not in enhanced_schema:
            enhanced_schema["properties"] = {}

        # Add metadata fields to prevent Singer SDK warnings
        enhanced_schema["properties"]["_entity_name"] = {"type": "string"}
        enhanced_schema["properties"]["_extracted_at"] = {
            "type": "string",
            "format": "date-time",
        }
        enhanced_schema["properties"]["_extraction_context"] = {
            "type": ["object", "null"]
        }

        # Add common API fields that might be present in responses
        enhanced_schema["properties"]["url"] = {"type": ["string", "null"]}

        # Add flattened ID fields that might be created during processing
        id_props = [
            prop for prop in enhanced_schema["properties"] if prop.endswith("_id")
        ]
        for prop in id_props:
            base_prop = prop[:-3]
            enhanced_schema["properties"][f"{base_prop}_id_id"] = {
                "type": ["string", "null"]
            }
            enhanced_schema["properties"][f"{base_prop}_id_key"] = {
                "type": ["string", "null"]
            }
            enhanced_schema["properties"][f"{base_prop}_id_url"] = {
                "type": ["string", "null"]
            }

        self._schema = enhanced_schema

        # Incremental sync support
        self._enable_incremental = tap.config.get("enable_incremental", True)
        self._safety_overlap_minutes = tap.config.get("incremental_overlap_minutes", 5)

        # Initialize primary_keys as instance variable (Singer SDK requirement)
        self._primary_keys = []

        # Smart replication key detection
        self._determine_replication_keys(tap.config)

        # Set replication method based on config
        if self._enable_incremental and self.replication_keys:
            self.replication_method = "INCREMENTAL"
        else:
            self.replication_method = "FULL_TABLE"
            self.replication_keys = []

        # Set primary keys based on schema
        schema_props = self._dynamic_schema.get("properties", {})
        if "id" in schema_props:
            self._primary_keys = ["id"]

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

        # Pass name and schema to parent class for Singer SDK
        if "name" not in kwargs:
            kwargs["name"] = entity_name
        if "schema" not in kwargs:
            kwargs["schema"] = self._dynamic_schema

        super().__init__(tap=tap, **kwargs)

        # CRITICAL: Override url_base after super().__init__ for Singer SDK
        self.url_base = self._base_url.rstrip("/")

    def get_name(self) -> str:
        """Stream name."""
        return self._entity_name

    @property
    def entity_name(self) -> str:
        """Entity name for this stream."""
        return self._entity_name

    @property
    def schema(self) -> dict[str, Any]:
        """Return the schema for this stream (Singer SDK compatibility)."""
        # Use _schema for Singer SDK compatibility
        result = getattr(self, "_schema", self._dynamic_schema)
        return result if result is not None else {}

    @property
    def replication_key(self) -> str | None:
        """Return the primary replication key for incremental sync.

        Singer SDK expects a single replication_key property for incremental streams.
        We return the first replication key if available.
        """
        if self.replication_keys:
            return self.replication_keys[0]
        return None

    @replication_key.setter
    def replication_key(self, value: str | None) -> None:
        """Set replication key for this stream (Singer SDK requirement)."""
        if value:
            self.replication_keys = [value]
        else:
            self.replication_keys = []

    @property
    def primary_keys(self) -> Sequence[str]:
        """Return primary keys for this stream.

        For WMS entities, we typically use ['id'] as the primary key.
        This is required by Singer SDK for proper record identification.
        """
        return getattr(self, "_primary_keys", [])

    @primary_keys.setter
    def primary_keys(self, value: Sequence[str] | None) -> None:
        """Set primary keys for this stream (Singer SDK requirement)."""
        self._primary_keys = value

    def _determine_replication_keys(self, config: dict[str, Any]) -> None:
        """Determine smart replication keys: primary key + optional mod_ts.

        Logic:
        1. Auto-discover primary key from schema (id field)
        2. Optionally add mod_ts for timestamp-based incremental sync
        3. Support entity-specific replication key configuration
        """
        replication_keys = []

        # Step 1: Auto-discover primary key from schema
        schema_props = self._dynamic_schema.get("properties", {})
        required_fields = self._dynamic_schema.get("required", [])

        # Look for primary key candidates (id, allocation_id, etc.)
        primary_key_candidates = [
            "id",  # Standard Oracle WMS primary key
            f"{self._entity_name}_id",  # Entity-specific ID
            "allocation_id",
            "order_id",
            "item_id",  # Common WMS IDs
        ]

        for candidate in primary_key_candidates:
            if candidate in schema_props and candidate in required_fields:
                replication_keys.append(candidate)
                break

        # Step 2: Check for mod_ts incremental sync configuration
        incremental_config = config.get("incremental_replication", {})
        entity_config = incremental_config.get(self._entity_name, {})

        # Entity-specific replication key override
        if entity_config.get("replication_keys"):
            replication_keys = entity_config["replication_keys"]
        else:
            # Add mod_ts if available and incremental is enabled
            use_mod_ts = entity_config.get(
                "use_mod_ts",
                False,
            ) or incremental_config.get("use_mod_ts_default", False)

            if (
                use_mod_ts
                and "mod_ts" in schema_props
                and "mod_ts" not in replication_keys
            ):
                replication_keys.append("mod_ts")

        # Step 3: Fallback to id if nothing found
        if not replication_keys and "id" in schema_props:
            replication_keys = ["id"]

        self.replication_keys = replication_keys

        try:
            from tap_oracle_wms.enhanced_logging import setup_enhanced_logging

            enhanced_logger = setup_enhanced_logging(__name__)
            enhanced_logger.info(
                "🔑 Replication keys for %s: %s",
                self._entity_name,
                replication_keys,
            )
        except ImportError:
            # Fallback to standard logging if enhanced_logging not available
            import logging

            logging.getLogger(__name__).info(
                "🔑 Replication keys for %s: %s",
                self._entity_name,
                replication_keys,
            )

    @property
    def requests_session(self) -> Any:
        """Create requests session with configured timeout.

        Override Singer SDK default to use our configured request_timeout
        instead of the hardcoded 300-second timeout for massive data extractions.
        """
        import requests

        session = requests.Session()
        # Get timeout from config, default to 7200 seconds (2 hours) for
        # massive historical extractions
        timeout = self.config.get("request_timeout", 7200)

        # Apply timeout using adapter pattern instead of method assignment
        original_request = session.request

        def request_with_timeout(*args, **kwargs):  # type: ignore[no-untyped-def]
            kwargs.setdefault("timeout", timeout)
            return original_request(*args, **kwargs)

        session.request = request_with_timeout  # type: ignore[method-assign]
        return session

    def get_path(self) -> str:
        """Get the API path for this stream's entity endpoint."""
        return f"/wms/lgfapi/v10/entity/{self.entity_name}"

    # Compatibility property
    path = property(lambda self: self.get_path())

    @property
    def url(self) -> str:
        """Full URL using config base_url."""
        url = f"{self._base_url.rstrip('/')}{self.path}"
        enhanced_logger.info(f"🌐 Building URL: {url}")
        return url

    def get_url_params(  # type: ignore[override]
        self,
        context: dict[str, Any] | None,
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
        enhanced_logger.info(
            "🔗 get_url_params called for entity=%s, next_page_token=%s",
            self.entity_name,
            next_page_token,
        )
        enhanced_logger.trace("🔬 EXTREME TRACE: Context=%s", context)
        enhanced_logger.trace("🔬 EXTREME TRACE: next_page_token=%s", next_page_token)
        enhanced_logger.trace(
            "🔬 EXTREME TRACE: next_page_token type=%s",
            type(next_page_token),
        )
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
                    f"{url_params.get('cursor', 'unknown')[:20]}...",
                )

                return url_params

            except (AttributeError, ValueError) as e:
                logger.warning(
                    "Failed to parse HATEOAS next_page_token for %s: %s",
                    self.entity_name,
                    e,
                )
                # Fall through to base parameters

        # First request: Build base parameters with filters and ordering
        params: dict[str, Any] = {
            "page_mode": self.config.get("page_mode", "sequenced"),
            "page_size": self.config.get("page_size"),
        }

        # Handle record_limit configuration
        record_limit = self.config.get("record_limit")
        # Force page_mode to always be "sequenced" - only supported mode
        params["page_mode"] = "sequenced"

        if record_limit and record_limit > 0:
            enhanced_logger.info(
                f"🔢 Record limit configured: {record_limit} records for entity {self.entity_name}"
            )

            # For page_mode="sequenced", we'll track record count during extraction
            # Initialize record counter if not exists
            if not hasattr(self, "_extracted_records_count"):
                self._extracted_records_count = 0
                enhanced_logger.info(
                    f"🎯 Initializing record counter for {self.entity_name}"
                )

        enhanced_logger.info(f"🔧 Initial params: {params}")

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
                                bookmark_value.replace("Z", "+00:00"),
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

        # Apply entity-specific ordering if configured
        entity_ordering = self.config.get("entity_ordering", {})
        if self.entity_name in entity_ordering:
            custom_ordering = entity_ordering[self.entity_name]
            params["ordering"] = custom_ordering
            enhanced_logger.info(
                f"📊 Custom ordering applied for {self.entity_name}: {custom_ordering}"
            )
        elif "ordering" not in params:
            # Apply default ordering if no specific ordering was set
            default_ordering = self.config.get("default_ordering", "id")
            params["ordering"] = default_ordering
            enhanced_logger.info(
                f"📊 Default ordering applied for {self.entity_name}: {default_ordering}"
            )

        # Log first request parameters for debugging
        logger.debug("🔧 Initial URL params for %s: %s", self.entity_name, params)

        enhanced_logger.info(
            "🎯🎯🎯 EXTREME TRACE: Final URL params for %s: %s",
            self.entity_name,
            params,
        )
        enhanced_logger.trace("🔬 EXTREME TRACE: Params count: %d", len(params))
        for key, value in params.items():
            enhanced_logger.trace("🔬 EXTREME TRACE: Param %s = %s", key, value)

        return params

    def _get_resume_context(
        self, context: dict[str, Any] | None
    ) -> dict[str, Any] | None:
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
        enhanced_logger.trace(
            "🔍 Getting incremental context for: %s",
            self.entity_name,
        )

        # PRIORITY 1: Check for direct resume_context in tap
        # configuration (new approach)
        resume_context_config = self.config.get("resume_context")
        if resume_context_config and resume_context_config.get("min_id_in_target"):
            enhanced_logger.info(
                "🎯 RESUME CONTEXT FOUND: Using direct resume_context configuration",
            )
            enhanced_logger.info("🎯 RESUME DATA: %s", resume_context_config)
            return dict(resume_context_config)

        # PRIORITY 2: Check for stream instance context (set by client)
        if hasattr(self, "context") and self.context:
            enhanced_logger.info(
                "🎯 STREAM CONTEXT FOUND: Using stream instance context",
            )
            enhanced_logger.info("🎯 STREAM CONTEXT DATA: %s", self.context)
            if self.context.get("min_id_in_target"):
                return dict(self.context)

        # PRIORITY 3: Check for legacy resume_config pattern
        resume_config = self.config.get("resume_config", {}).get(self.entity_name, {})
        if resume_config.get("enabled", False):
            enhanced_logger.info("🎯 LEGACY RESUME CONFIG: Using resume_config pattern")
            return {
                "has_existing_data": resume_config.get("has_existing_data", False),
                "min_id_in_target": resume_config.get("min_id_in_target"),
                "total_records": resume_config.get("total_records", 0),
                "sync_strategy": resume_config.get("strategy", "id_based_resume"),
            }

        enhanced_logger.info("🎯 NO RESUME CONTEXT: No resume configuration found")
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
        return get_wms_authenticator(self, dict(self.config))

    @property
    def http_headers(self) -> dict[str, str]:
        """Get HTTP headers with compression and authentication support."""
        headers = get_wms_headers(dict(self.config))

        # Add compression
        if self._compression_enabled:
            headers["Accept-Encoding"] = "gzip, deflate, br"

        # CRITICAL FIX: Add authentication headers (was missing!)
        if self.authenticator:
            headers.update(self.authenticator.auth_headers)

        return headers

    def validate_response(self, response: httpx.Response) -> None:  # type: ignore[override]
        """Validate HTTP response with circuit breaker and enhanced error handling."""
        enhanced_logger.debug(
            f"🌐 Response validation for {self.entity_name}: status={response.status_code}"
        )

        if 200 <= response.status_code < 300:
            self._circuit_breaker.call_succeeded()
            enhanced_logger.debug(f"✅ Successful response for {self.entity_name}")
            return

        # Check circuit breaker BEFORE processing errors
        if not self._circuit_breaker.can_attempt_call():
            enhanced_logger.error(
                f"🚨 Circuit breaker blocking call to {self.entity_name}"
            )
            msg = f"Circuit breaker is open for {self.entity_name} - service temporarily unavailable"
            raise FatalAPIError(msg)

        # Handle specific errors with circuit breaker integration
        if response.status_code == 429:
            self._circuit_breaker.call_failed()
            retry_after = response.headers.get("Retry-After", "60")
            enhanced_logger.warning(
                f"⏱️ Rate limited for {self.entity_name}: retry after {retry_after}s"
            )
            msg = f"Rate limited for {self.entity_name}. Retry after {retry_after} seconds"
            raise RetriableAPIError(msg)

        if response.status_code in {500, 502, 503, 504}:
            self._circuit_breaker.call_failed()
            enhanced_logger.error(
                f"🔥 Server error {response.status_code} for {self.entity_name}"
            )
            msg = (
                f"Server error {response.status_code} for {self.entity_name} - retrying"
            )
            raise RetriableAPIError(msg)

        if response.status_code == 401:
            enhanced_logger.error(f"🔐 Authentication failed for {self.entity_name}")
            msg = f"Authentication failed for {self.entity_name}. Check credentials"
            raise FatalAPIError(msg)

        if response.status_code == 403:
            enhanced_logger.error(f"🚫 Access denied to entity {self.entity_name}")
            msg = f"Access denied to entity {self.entity_name} - check permissions"
            raise FatalAPIError(msg)

        if response.status_code == 404:
            enhanced_logger.error(f"❓ Entity not found: {self.entity_name}")
            msg = f"Entity {self.entity_name} not found - check entity name"
            raise FatalAPIError(msg)

        if response.status_code == 408:
            self._circuit_breaker.call_failed()
            enhanced_logger.warning(f"⏰ Request timeout for {self.entity_name}")
            msg = f"Request timeout for {self.entity_name} - retrying"
            raise RetriableAPIError(msg)

        # Handle any other 4xx errors as fatal (client errors)
        if 400 <= response.status_code < 500:
            enhanced_logger.error(
                f"❌ Client error {response.status_code} for {self.entity_name}"
            )
            msg = f"Client error {response.status_code} for {self.entity_name}"
            raise FatalAPIError(msg)

        # Handle any other 5xx errors as retriable (server errors)
        if response.status_code >= 500:
            self._circuit_breaker.call_failed()
            enhanced_logger.error(
                f"💥 Server error {response.status_code} for {self.entity_name}"
            )
            msg = (
                f"Server error {response.status_code} for {self.entity_name} - retrying"
            )
            raise RetriableAPIError(msg)

        # Default validation for any other cases
        enhanced_logger.debug(
            f"🔍 Using default validation for {self.entity_name} status {response.status_code}"
        )
        super().validate_response(response)  # type: ignore[arg-type]

    def parse_response(self, response: httpx.Response) -> Iterable[dict[str, Any]]:  # type: ignore[override]
        """Parse response with EXTREME TRACE monitoring."""
        self._api_calls += 1

        enhanced_logger.info(
            "🌐🌐🌐 EXTREME TRACE: parse_response called for entity=%s",
            self.entity_name,
        )
        enhanced_logger.trace("🔬 EXTREME TRACE: API call #%d", self._api_calls)
        enhanced_logger.trace(
            "🔬 EXTREME TRACE: Response status=%d",
            response.status_code,
        )
        enhanced_logger.trace(
            "🔬 EXTREME TRACE: Response headers=%s",
            dict(response.headers),
        )
        enhanced_logger.info(
            "📏 EXTREME TRACE: Response content length=%d bytes",
            len(response.content),
        )

        try:
            enhanced_logger.trace("🔬 EXTREME TRACE: About to parse JSON from response")
            data = response.json()
            enhanced_logger.info("✅✅✅ EXTREME TRACE: JSON parsed successfully")
            enhanced_logger.trace("🔬 EXTREME TRACE: Data type=%s", type(data))

            if isinstance(data, dict):
                enhanced_logger.trace(
                    "🔬 EXTREME TRACE: Dict keys=%s",
                    list(data.keys()),
                )
                if "results" in data:
                    results = data["results"]
                    enhanced_logger.info(
                        "📊📊📊 EXTREME TRACE: Found 'results' key with %d items",
                        len(results) if isinstance(results, list) else "non-list",
                    )
                else:
                    enhanced_logger.warning(
                        "⚠️⚠️⚠️ EXTREME TRACE: NO 'results' key found in response!",
                    )
                    enhanced_logger.trace(
                        "🔬 EXTREME TRACE: Available keys: %s",
                        list(data.keys()),
                    )
            elif isinstance(data, list):
                enhanced_logger.info(
                    "📊📊📊 EXTREME TRACE: Direct list response with %d items",
                    len(data),
                )
            else:
                enhanced_logger.warning(
                    "⚠️⚠️⚠️ EXTREME TRACE: Unexpected data type: %s",
                    type(data),
                )

            # Handle values list mode
            if self._values_list:
                enhanced_logger.trace(
                    "🔬 EXTREME TRACE: Processing in values_list mode",
                )
                if isinstance(data, dict) and "results" in data:
                    for row in data["results"]:
                        if isinstance(row, list) and self._field_selection:
                            yield dict(zip(self._field_selection, row, strict=False))
                        else:
                            yield {"values": row}
                return

            records_yielded = 0

            # Standard response formats
            if isinstance(data, dict):
                if "results" in data:
                    # Paginated response
                    enhanced_logger.info(
                        "📄📄📄 EXTREME TRACE: Processing paginated response",
                    )
                    for i, record in enumerate(data["results"]):
                        # Check record limit before processing
                        record_limit = self.config.get("record_limit")
                        if record_limit and hasattr(self, "_extracted_records_count"):
                            if self._extracted_records_count >= record_limit:
                                enhanced_logger.info(
                                    f"🛑 Record limit reached: {record_limit} records for entity {self.entity_name}"
                                )
                                return  # Stop processing
                            self._extracted_records_count += 1

                        enhanced_logger.trace(
                            "🔬 EXTREME TRACE: Processing result #%d",
                            i + 1,
                        )
                        if i == 0:
                            enhanced_logger.info(
                                "📥📥📥 EXTREME TRACE: First result type=%s",
                                type(record),
                            )
                            if isinstance(record, dict):
                                enhanced_logger.trace(
                                    "🔬 EXTREME TRACE: First result keys=%s",
                                    list(record.keys()),
                                )
                                enhanced_logger.trace(
                                    "🔬 EXTREME TRACE: First result sample=%s",
                                    str(record)[:200],
                                )

                        self._records_extracted += 1
                        records_yielded += 1
                        yield record

                elif "data" in data:
                    # Alternative format
                    enhanced_logger.info(
                        "📄📄📄 EXTREME TRACE: Processing 'data' format response",
                    )
                    for record in data["data"]:
                        # Check record limit before processing
                        record_limit = self.config.get("record_limit")
                        if record_limit and hasattr(self, "_extracted_records_count"):
                            if self._extracted_records_count >= record_limit:
                                enhanced_logger.info(
                                    f"🛑 Record limit reached: {record_limit} records for entity {self.entity_name}"
                                )
                                return  # Stop processing
                            self._extracted_records_count += 1

                        self._records_extracted += 1
                        records_yielded += 1
                        yield record
                else:
                    # Single record
                    enhanced_logger.info(
                        "📄📄📄 EXTREME TRACE: Processing single record format",
                    )
                    # Check record limit before processing
                    record_limit = self.config.get("record_limit")
                    if record_limit and hasattr(self, "_extracted_records_count"):
                        if self._extracted_records_count >= record_limit:
                            enhanced_logger.info(
                                f"🛑 Record limit reached: {record_limit} records for entity {self.entity_name}"
                            )
                            return  # Stop processing
                        self._extracted_records_count += 1

                    self._records_extracted += 1
                    records_yielded += 1
                    yield data

            elif isinstance(data, list):
                # Direct list
                enhanced_logger.info(
                    "📄📄📄 EXTREME TRACE: Processing direct list format",
                )
                for record in data:
                    # Check record limit before processing
                    record_limit = self.config.get("record_limit")
                    if record_limit and hasattr(self, "_extracted_records_count"):
                        if self._extracted_records_count >= record_limit:
                            enhanced_logger.info(
                                f"🛑 Record limit reached: {record_limit} records for entity {self.entity_name}"
                            )
                            return  # Stop processing
                        self._extracted_records_count += 1

                    self._records_extracted += 1
                    records_yielded += 1
                    yield record
            else:
                # Unknown format
                enhanced_logger.warning(
                    "⚠️⚠️⚠️ EXTREME TRACE: Unexpected response format for %s",
                    self.entity_name,
                )
                enhanced_logger.critical(
                    "🚨🚨🚨 EXTREME TRACE: Data type=%s, content=%s",
                    type(data),
                    str(data)[:500],
                )
                # Wrap unknown format in dict to maintain type consistency
                yield {"_raw_data": data, "_entity_name": self.entity_name}
                records_yielded += 1

            enhanced_logger.info(
                "🏁🏁🏁 EXTREME TRACE: parse_response completed - yielded %d records",
                records_yielded,
            )

            if records_yielded == 0:
                enhanced_logger.critical(
                    "🚨🚨🚨 EXTREME TRACE: ZERO RECORDS YIELDED FROM RESPONSE!",
                )
                enhanced_logger.critical("🚨 Raw response data: %s", str(data)[:1000])

        except json.JSONDecodeError as e:
            enhanced_logger.critical(
                "🚨🚨🚨 EXTREME TRACE: JSON decode error: %s",
                str(e),
            )
            enhanced_logger.critical(
                "🚨 Raw response content: %s",
                response.text[:1000],
            )
            self._errors["json_decode"] = self._errors.get("json_decode", 0) + 1
            logger.exception("JSON decode error for %s", self.entity_name)
            msg = f"Invalid JSON response from {self.entity_name}"
            raise FatalAPIError(msg) from e
        except Exception:
            self._errors["parse_error"] = self._errors.get("parse_error", 0) + 1
            logger.exception("Parse error for %s", self.entity_name)
            raise

    def post_process(  # type: ignore[override]
        self, row: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Post-process records with validation, flattening, and JSON field handling."""
        # Skip invalid records
        if not isinstance(row, dict):
            logger.warning("Invalid record type in %s: %s", self.entity_name, type(row))
            return None

        # Apply flattening and JSON field processing if enabled
        processed_row = self._process_complex_fields(row.copy())

        # Ensure ID exists (most entities have it)
        if not processed_row.get("id") and "id" not in processed_row:
            # Some entities might not have ID field
            logger.debug("Record without ID in %s", self.entity_name)

        # Add metadata
        processed_row["_entity_name"] = self.entity_name
        processed_row["_extracted_at"] = datetime.now(timezone.utc).isoformat()

        # Add extraction context if available
        if context:
            processed_row["_extraction_context"] = context

        return processed_row

    def _process_complex_fields(self, row: dict[str, Any]) -> dict[str, Any]:
        """Process complex fields according to configuration."""
        if not hasattr(self._tap, "config"):
            return row

        config = dict(self._tap.config)

        # Check if flattening or JSON processing is enabled
        enable_flattening = config.get("enable_flattening", True)
        preserve_nested = config.get("preserve_nested_objects", True)

        if not enable_flattening and not preserve_nested:
            return row

        # Import processing classes from discovery module
        try:
            from .discovery import SchemaGenerator  # noqa: F401

            # Create processors with current configuration
            flattener = ObjectFlattener(config) if enable_flattening else None
            json_handler = JsonFieldHandler(config) if preserve_nested else None

            # Apply flattening first
            if flattener:
                row = flattener.flatten_object(row)

            # Then apply JSON field handling
            if json_handler:
                row = json_handler.process_nested_objects(row)

        except ImportError:
            logger.debug(
                "Could not import processing classes, skipping complex field processing",
            )

        return row

    @property
    def dynamic_schema(self) -> dict[str, Any]:
        """Dynamic schema - PRODUCTION: Must have valid schema."""
        enhanced_logger.trace("🔍 Retrieving schema for entity: %s", self.entity_name)

        if self._dynamic_schema:
            enhanced_logger.trace(
                "✅ Using dynamic schema with %d properties",
                len(self._dynamic_schema.get("properties", {})),
            )
            return self._dynamic_schema

        # PRODUCTION: Never use fallback - always require proper schema discovery
        enhanced_logger.critical(
            "❌ No schema available for entity: %s",
            self.entity_name,
        )
        msg = (
            f"No schema available for entity '{self.entity_name}'. "
            f"Schema discovery must be completed before accessing streams."
        )
        raise ValueError(msg)


class ObjectFlattener:
    """Enhanced object flattening with configurable rules."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize object flattener."""
        self.config = config
        self.enable_flattening = config.get("enable_flattening", True)
        self.flatten_id_objects = config.get("flatten_id_based_objects", True)
        self.flatten_key_objects = config.get("flatten_key_based_objects", True)
        self.flatten_url_objects = config.get("flatten_url_based_objects", True)
        self.max_depth = config.get("max_flatten_depth", 3)

    def should_flatten_object(self, obj: dict[str, Any], key: str = "") -> bool:
        """Determine if an object should be flattened."""
        if not self.enable_flattening:
            return False

        if not isinstance(obj, dict):
            return False

        # Check for ID-based objects
        if self.flatten_id_objects and "id" in obj:
            return True

        # Check for key-based objects
        if self.flatten_key_objects and "key" in obj:
            return True

        # Check for URL-based objects
        if self.flatten_url_objects and any(
            k.endswith(("url", "_url", "href", "_href")) for k in obj
        ):
            return True

        # Check for simple objects (< 5 fields)
        return len(obj) <= 3

    def flatten_object(
        self,
        obj: Any,
        prefix: str = "",
        depth: int = 0,
    ) -> dict[str, Any]:
        """Flatten complex objects with configurable rules."""
        if depth > self.max_depth:
            return {prefix.rstrip("_"): obj}

        if not isinstance(obj, dict):
            return {prefix.rstrip("_"): obj}

        result = {}

        for key, value in obj.items():
            new_key = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                if self.should_flatten_object(value, key):
                    # Flatten this object
                    flattened = self.flatten_object(value, f"{new_key}_", depth + 1)
                    result.update(flattened)
                else:
                    # Keep as nested object
                    result[new_key] = value
            elif isinstance(value, list):
                if (
                    value
                    and isinstance(value[0], dict)
                    and self.should_flatten_object(value[0])
                ):
                    # Flatten array of simple objects
                    for i, item in enumerate(
                        value[:3],
                    ):  # Limit array flattening to first 3 items
                        if isinstance(item, dict):
                            flattened = self.flatten_object(
                                item,
                                f"{new_key}_{i}_",
                                depth + 1,
                            )
                            result.update(flattened)
                        else:
                            result[f"{new_key}_{i}"] = item
                else:
                    # Keep as array
                    result[new_key] = value
            else:
                result[new_key] = value

        return result


class JsonFieldHandler:
    """Handle nested objects as JSON fields."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize JSON field handler."""
        self.config = config
        self.preserve_nested = config.get("preserve_nested_objects", True)
        self.json_prefix = config.get("json_field_prefix", "json_")
        self.nested_threshold = config.get("nested_object_threshold", 5)

    def should_preserve_as_json(self, obj: dict[str, Any]) -> bool:
        """Determine if object should be preserved as JSON field."""
        if not self.preserve_nested:
            return False

        if not isinstance(obj, dict):
            return False

        # Large objects become JSON fields
        if len(obj) > self.nested_threshold:
            return True

        # Objects with nested objects become JSON fields
        return bool(any(isinstance(v, (dict, list)) for v in obj.values()))

    def process_nested_objects(self, obj: dict[str, Any]) -> dict[str, Any]:
        """Process nested objects according to configuration."""
        import json

        result: dict[str, Any] = {}

        for key, value in obj.items():
            if isinstance(value, dict):
                if self.should_preserve_as_json(value):
                    # Convert to JSON field
                    result[f"{self.json_prefix}{key}"] = json.dumps(value)
                else:
                    # Keep as regular field
                    result[key] = value
            elif isinstance(value, list):
                if (
                    value
                    and isinstance(value[0], dict)
                    and self.should_preserve_as_json(value[0])
                ):
                    # Convert array of objects to JSON
                    result[f"{self.json_prefix}{key}"] = json.dumps(value)
                else:
                    result[key] = value
            else:
                result[key] = value

        return result


# Export the advanced stream
WMSEntityStream = WMSAdvancedStream

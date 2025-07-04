"""Oracle WMS Stream - Enterprise implementation using Singer SDK REST capabilities.

This module implements a dynamic REST stream specifically for Oracle WMS API
with full functionality including:

- HATEOAS pagination following Oracle WMS patterns
- Incremental sync with WMS timestamp fields (mod_ts)
- Dynamic URL generation for WMS entities
- Automatic retry with exponential backoff
- Request caching and performance optimization
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs

import requests
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

# Import commonly used modules to avoid PLC0415 violations
if TYPE_CHECKING:
    from .auth import get_wms_authenticator
    from .discovery import SchemaGenerator
else:
    try:
        from .auth import get_wms_authenticator
        from .discovery import SchemaGenerator
    except ImportError:
        # Handle circular import gracefully
        SchemaGenerator = None
        get_wms_authenticator = None

# Type alias for value parameters that can accept various types
ValueType = object | str | int | float | bool | dict[str, object] | list[object] | None

# Error logging functionality integrated inline

# HTTP status code constants
STATUS_OK = 200
STATUS_UNAUTHORIZED = 401
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_TOO_MANY_REQUESTS = 429
STATUS_SERVER_ERROR_START = 500
STATUS_SERVER_ERROR_END = 600
DEFAULT_RETRY_AFTER = 60

# Validation and processing constants
MAX_PARAM_KEY_LENGTH = 50
MAX_OVERLAP_MINUTES = 1440  # 24 hours
MAX_REASONABLE_ID = 999999999999

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    import requests


class WMSPaginator(BaseHATEOASPaginator):
    """Paginator for Oracle WMS HATEOAS-style pagination.

    Oracle WMS uses cursor-based pagination with next_page URLs.
    This paginator extracts and follows these URLs automatically.
    """

    def get_next_url(self, response: requests.Response) -> str | None:
        """Get the next page URL from the response."""
        try:
            data = response.json()
            return data.get("next_page") if isinstance(data, dict) else None
        except (ValueError, json.JSONDecodeError) as e:
            # CRITICAL: JSON parsing failures in pagination must not be silent
            logger = logging.getLogger(__name__)
            error_msg = (
                "Critical pagination failure: Failed to parse JSON response. "
                "This will terminate extraction and may cause incomplete datasets. "
                f"Response status: {response.status_code}, "
                f"Content-Type: {response.headers.get('Content-Type', 'unknown')}"
            )
            logger.exception(error_msg, exc_info=e)
            # Raise exception to ensure pagination failures are not silent
            msg = f"Pagination JSON parsing failed: {e}"
            raise RetriableAPIError(msg) from e

    def has_more(self, response: requests.Response) -> bool:
        """Check if there are more pages to fetch."""
        return self.get_next_url(response) is not None


class WMSStream(RESTStream[dict[str, Any]]):
    """Oracle WMS API stream using Singer SDK capabilities.

    This stream is specifically designed for Oracle WMS REST API with:
    - WMS entity path generation (/wms/lgfapi/v10/entity/{entity})
    - Automatic schema discovery from WMS metadata
    - Incremental sync using mod_ts timestamps
    - WMS-specific filtering and ordering
    - HATEOAS pagination support
    """

    # Use HATEOAS paginator
    pagination_class = WMSPaginator

    # Default replication settings (will be overridden in __init__)
    replication_method = "INCREMENTAL"
    replication_key = None

    def __init__(
        self,
        *args: object,
        **kwargs: dict[str, object],
    ) -> None:
        """Initialize stream with dynamic settings."""
        # Extract custom settings before calling parent
        self._entity_name = str(kwargs.get("name", ""))
        self._schema = dict(kwargs.get("schema", {}))

        super().__init__(*args, **kwargs)

        # Error logging setup removed for simplicity

        # Set primary keys based on schema
        if "id" in self._schema.get("properties", {}):
            self.primary_keys = ["id"]

        # Determine replication method
        schema_props = self._schema.get("properties", {})

        # Get configured replication key
        configured_rep_key = self.config.get("replication_key", "updated_at")

        # Check for forced full sync in config
        force_full_table = self.config.get("force_full_table", False)
        enable_incremental = self.config.get("enable_incremental", True)

        if force_full_table or not enable_incremental:
            # Forced full sync via config
            self.replication_method = "FULL_TABLE"
            # Use primary key for bookmark tracking in full sync
            self.replication_key = self.primary_keys[0] if self.primary_keys else "id"
        elif configured_rep_key in schema_props:
            # Use incremental sync with configured key
            self.replication_method = "INCREMENTAL"
            self.replication_key = configured_rep_key
        else:
            # Fall back to full table sync if replication key not found
            self.replication_method = "FULL_TABLE"
            self.replication_key = self.primary_keys[0] if self.primary_keys else "id"

    @property
    def url_base(self) -> str:
        """Base URL from config."""
        return str(self.config["base_url"]).rstrip("/")

    @property
    def path(self) -> str:  # type: ignore[override]
        """Generate entity-specific path."""
        # Build path from configuration
        prefix = self.config.get("api_endpoint_prefix", "")
        if prefix and not prefix.startswith("/"):
            prefix = f"/{prefix}"

        # Support custom path patterns
        path_pattern = self.config.get("path_pattern", "/{entity}")
        path = path_pattern.replace("{entity}", self._entity_name)

        return f"{prefix}{path}"

    @property
    def http_headers(self) -> dict[str, Any]:
        """Return headers for all requests."""
        headers = super().http_headers

        # Add standard headers
        headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        # Add custom headers from config
        custom_headers = self.config.get("custom_headers", {})
        if custom_headers:
            headers.update(custom_headers)

        return headers

    def get_url_params(
        self,
        context: Mapping[str, Any] | None,
        next_page_token: object | None,
    ) -> dict[str, Any]:
        """Generate URL parameters for requests.

        This method handles:
        - Pagination parameters
        - Incremental sync filtering
        - Custom entity filters
        - Ordering parameters
        """
        self._log_request_params(context, next_page_token)

        # Handle pagination first
        if next_page_token:
            return self._get_pagination_params(next_page_token)

        # Build initial request parameters
        params = self._get_base_params()
        self._add_replication_filters(params, context)
        self._add_ordering_params(params)
        self._add_entity_filters(params)

        self._log_final_params(params)
        return params

    def _log_request_params(
        self,
        context: Mapping[str, Any] | None,
        next_page_token: object | None,
    ) -> None:
        """Log detailed request parameters for debugging."""
        self.logger.info(
            "WMS REQUEST PARAMS - Entity: %s",
            self._entity_name,
            extra={
                "entity": self._entity_name,
                "has_next_page_token": next_page_token is not None,
                "context": context,
                "replication_method": self.replication_method,
                "replication_key": self.replication_key,
            },
        )

    def _get_pagination_params(self, next_page_token: object) -> dict[str, Any]:
        """Extract parameters from pagination token with validation."""
        params: dict[str, Any] = {}
        if hasattr(next_page_token, "query") and next_page_token.query:
            try:
                parsed_params = parse_qs(next_page_token.query)
                # Validate and sanitize query parameters
                for key, value in parsed_params.items():
                    # Prevent parameter injection attacks
                    if not isinstance(key, str) or len(key) > MAX_PARAM_KEY_LENGTH:
                        self.logger.warning("Suspicious query parameter key: %s", key)
                        continue
                    # Basic sanitization - allow only alphanumeric, underscore, dash
                    if not key.replace("_", "").replace("-", "").isalnum():
                        self.logger.warning(
                            "Invalid query parameter key format: %s",
                            key,
                        )
                        continue
                    # Handle value arrays safely
                    if isinstance(value, list) and value:
                        clean_values = [str(v)[:100] for v in value if v is not None]
                        params[key] = (
                            clean_values[0] if len(clean_values) == 1 else clean_values
                        )
            except Exception as e:
                self.logger.exception(
                    "Failed to parse pagination query parameters",
                )
                msg = f"Invalid pagination token query: {e}"
                raise ValueError(msg) from e
        return params

    def _get_base_params(self) -> dict[str, Any]:
        """Get base request parameters."""
        return {
            "page_size": self.config.get("page_size", 100),
            "page_mode": "sequenced",  # Always use cursor-based pagination
        }

    def _add_replication_filters(
        self,
        params: dict[str, Any],
        context: Mapping[str, Any] | None,
    ) -> None:
        """Add replication-specific filters to parameters."""
        if self.replication_method == "INCREMENTAL" and self.replication_key:
            self._add_incremental_filter(params, context)
        elif self.replication_method == "FULL_TABLE":
            self._add_full_table_filter(params, context)

    def _add_incremental_filter(
        self,
        params: dict[str, Any],
        context: Mapping[str, Any] | None,
    ) -> None:
        """Add incremental sync filter with comprehensive timestamp validation.

        REGRA: sync incr --- ordering mod_ts e filter mod_ts>=(last mod_ts -5m)
        SEM ESTADO: filtro inicial usa hora_atual - 5m
        """
        start_date = self.get_starting_timestamp(context)

        # Se não há estado inicial, usar hora_atual - 5m
        if not start_date:
            overlap_minutes = self.config.get("lookback_minutes", 5)
            now = datetime.now(timezone.utc)
            start_date = now - timedelta(minutes=overlap_minutes)
            self.logger.info(
                "No initial state - using current time minus %d minutes: %s",
                overlap_minutes,
                start_date.isoformat(),
            )

        # Validate timestamp has timezone information
        if start_date.tzinfo is None:
            error_msg = (
                f"Critical timestamp error: start_date '{start_date}' for entity "
                f"'{self._entity_name}' lacks timezone information. This can cause "
                f"data consistency issues across time zones."
            )
            self.logger.exception(error_msg)
            # Add UTC timezone as fallback but warn
            start_date = start_date.replace(tzinfo=timezone.utc)
            self.logger.warning("Applied UTC timezone as fallback for start_date")

        # Validate overlap configuration para estado existente
        if self.get_starting_timestamp(context):  # Só se tem estado
            overlap_minutes = self.config.get("incremental_overlap_minutes", 5)
            if not isinstance(overlap_minutes, (int, float)) or overlap_minutes < 0:
                self.logger.warning(
                    "Invalid overlap_minutes: %s, using default 5",
                    overlap_minutes,
                )
                overlap_minutes = 5
            if overlap_minutes > MAX_OVERLAP_MINUTES:  # More than 24 hours
                self.logger.warning(
                    "Large overlap_minutes may cause performance issues: %s",
                    overlap_minutes,
                )

            adjusted_date = start_date - timedelta(minutes=overlap_minutes)
        else:
            # Para estado inicial, já calculamos acima
            adjusted_date = start_date

        # Validate date range reasonableness
        now = datetime.now(timezone.utc)
        if adjusted_date > now:
            self.logger.warning("Start date is in the future: %s", adjusted_date)

        params[f"{self.replication_key}__gte"] = adjusted_date.isoformat()
        self.logger.info(
            "Incremental filter: %s >= %s",
            self.replication_key,
            adjusted_date.isoformat(),
        )

    def _add_full_table_filter(
        self,
        params: dict[str, Any],
        context: Mapping[str, Any] | None,
    ) -> None:
        """Add full table sync filter for recovery by ID.

        Full sync works by:
        1. Starting from highest ID (no filter)
        2. Each batch saves the lowest ID as bookmark
        3. Next request uses id__lt=bookmark to continue
        4. Stops when reaching ID=0 or no more records
        """
        bookmark = self.get_starting_replication_key_value(context)
        if bookmark and "id" in self._schema.get("properties", {}):
            try:
                bookmark_id = int(bookmark)

                # Validate bookmark is reasonable
                if bookmark_id < 0:
                    self.logger.warning(
                        "Bookmark ID is negative (%s), resetting full sync",
                        bookmark_id,
                    )
                    return  # No filter = start from beginning

                if bookmark_id > MAX_REASONABLE_ID:  # Reasonable upper limit
                    self.logger.warning(
                        "Bookmark ID suspiciously large (%s), resetting full sync",
                        bookmark_id,
                    )
                    return  # No filter = start from beginning

                # Use id__lt (less than) to get records with ID lower than bookmark
                # This ensures we continue from where we left off in descending order
                params["id__lt"] = str(bookmark_id)
                self.logger.info("Full sync continuing from ID < %s", bookmark_id)

            except (ValueError, TypeError):
                self.logger.exception(
                    "Invalid bookmark '%s' for full sync, starting from beginning",
                    bookmark,
                )
                # Don't add filter = start from highest ID
        else:
            self.logger.info("Full sync starting from beginning (highest ID)")
            # No bookmark or no ID field = start from beginning

    def _add_ordering_params(self, params: dict[str, Any]) -> None:
        """Add ordering parameters for consistent results."""
        if self.replication_method == "FULL_TABLE":
            self._add_full_table_ordering(params)
        else:
            self._add_incremental_ordering(params)

    def _add_full_table_ordering(self, params: dict[str, Any]) -> None:
        """Add ordering for full table sync.

        Full sync MUST use ordering=-id (descending) to enable proper recovery:
        - Start from highest ID and work down to 0
        - Each batch bookmark is the lowest ID from that batch
        - Next request continues with id__lt=bookmark
        """
        if "id" in self._schema.get("properties", {}):
            params["ordering"] = "-id"  # CRITICAL: Descending for full sync recovery
            self.logger.debug("Full sync using ordering=-id for proper recovery")
        # Fallback if no ID field
        elif self.replication_key:
            params["ordering"] = f"-{self.replication_key}"
            self.logger.warning(
                "No ID field found, using -%s for ordering",
                self.replication_key,
            )

    def _add_incremental_ordering(self, params: dict[str, Any]) -> None:
        """Add ordering for incremental sync.

        Incremental sync MUST use temporal ordering for proper checkpointing:
        - Order by mod_ts ascending to get oldest-to-newest changes
        - Each batch bookmark is the latest mod_ts from that batch
        - Next request continues with mod_ts__gte=bookmark
        """
        if self.replication_key == "mod_ts":
            params["ordering"] = "mod_ts"  # CRITICAL: Ascending temporal order
            self.logger.debug(
                "Incremental sync using ordering=mod_ts for temporal progression",
            )
        elif self.replication_key:
            params["ordering"] = self.replication_key
            self.logger.debug(
                "Incremental sync using ordering=%s",
                self.replication_key,
            )
        elif "id" in self._schema.get("properties", {}):
            params["ordering"] = "id"  # Fallback to ID if no replication key
            self.logger.warning(
                "No temporal replication key, falling back to ordering=id",
            )

    def _add_entity_filters(self, params: dict[str, Any]) -> None:
        """Add custom entity filters from config."""
        entity_filters = self.config.get("entity_filters", {})
        if self._entity_name in entity_filters:
            params.update(entity_filters[self._entity_name])

    def _log_final_params(self, params: dict[str, Any]) -> None:
        """Log final request parameters."""
        self.logger.info(
            "WMS FINAL PARAMS - Entity: %s - URL: %s%s - PARAMS: %s",
            self._entity_name,
            self.url_base,
            self.path,
            params,
            extra={
                "entity": self._entity_name,
                "final_params": params,
                "url_path": self.path,
                "base_url": self.url_base,
            },
        )

    def parse_response(self, response: requests.Response) -> Iterable[dict[str, Any]]:
        """Parse records from API response.

        Oracle WMS returns data in format:
        {
            "results": [...],
            "next_page": "...",
            "page_nbr": 1
        }
        """
        try:
            data = response.json()
            self._log_response_structure(data)

            # Extract records from results array
            if isinstance(data, dict) and "results" in data:
                yield from self._yield_results_array(data)
            elif isinstance(data, list):
                yield from self._yield_direct_array(data)
            else:
                self._log_unexpected_format(data)

        except json.JSONDecodeError as e:
            # JSON decode errors indicate serious API issues
            error_msg = (
                f"Critical JSON error for entity {self._entity_name}: Invalid format. "
                "This indicates API incompatibility or server-side issues."
            )
            self.logger.exception(error_msg, exc_info=e)
            msg = f"Invalid JSON response from API for entity {self._entity_name}: {e}"
            # This is likely a retriable error (server issue)
            raise RetriableAPIError(msg) from e

    def _log_response_structure(self, data: object) -> None:
        """Log response structure for debugging."""
        self.logger.info(
            "WMS RESPONSE STRUCTURE - Entity: %s",
            self._entity_name,
            extra={
                "entity": self._entity_name,
                "response_type": type(data).__name__,
                "response_keys": (
                    list(data.keys()) if isinstance(data, dict) else None
                ),
                "response_length": (
                    len(data) if isinstance(data, (list, dict)) else None
                ),
                "has_results": ("results" in data if isinstance(data, dict) else False),
                "has_next_page": (
                    "next_page" in data if isinstance(data, dict) else False
                ),
                "page_info": self._extract_page_info(data),
            },
        )

    def _extract_page_info(self, data: object) -> dict[str, object] | None:
        """Extract page information from response data."""
        if not isinstance(data, dict):
            return None

        results_count = None
        if "results" in data:
            results = data.get("results", [])
            results_count = len(results) if isinstance(results, list) else None

        return {
            "page_nbr": data.get("page_nbr"),
            "next_page": data.get("next_page") is not None,
            "results_count": results_count,
        }

    def _yield_results_array(self, data: dict[str, object]) -> Iterable[dict[str, Any]]:
        """Yield records from results array format."""
        results = data["results"]
        if isinstance(results, list):
            self.logger.info(
                "WMS YIELDING RECORDS - Entity: %s - Count: %d",
                self._entity_name,
                len(results),
                extra={
                    "entity": self._entity_name,
                    "records_in_page": len(results),
                    "page_number": data.get("page_nbr", "unknown"),
                },
            )
            yield from results
        else:
            # Critical error: results field exists but is not a list
            error_msg = (
                f"Critical API data format error for entity '{self._entity_name}': "
                f"'results' exists but not a list (got {type(results).__name__}). "
                f"This indicates API format change that prevents data extraction."
            )
            self.logger.exception(error_msg)
            raise FatalAPIError(error_msg)

    def _yield_direct_array(self, data: list[Any]) -> Iterable[dict[str, Any]]:
        """Yield records from direct array format."""
        self.logger.info(
            "WMS YIELDING DIRECT ARRAY - Entity: %s - Count: %d",
            self._entity_name,
            len(data),
            extra={
                "entity": self._entity_name,
                "records_in_response": len(data),
            },
        )
        yield from data

    def _log_unexpected_format(self, data: object) -> None:
        """Log error and raise exception for unexpected response format."""
        error_msg = (
            f"Critical API response format error for entity '{self._entity_name}': "
            f"Expected dict with 'results' key or list, but got {type(data).__name__}. "
            f"This indicates an API incompatibility that prevents data extraction."
        )
        self.logger.exception(error_msg)
        raise FatalAPIError(error_msg)

    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response and handle errors."""
        status = response.status_code

        if status == STATUS_UNAUTHORIZED:
            msg = "Authentication failed (401)"
            raise FatalAPIError(msg)
        if status == STATUS_FORBIDDEN:
            msg = f"Access forbidden to {self._entity_name} (403)"
            raise FatalAPIError(msg)
        if status == STATUS_NOT_FOUND:
            msg = f"Entity {self._entity_name} not found (404)"
            raise FatalAPIError(msg)
        if status == STATUS_TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After", DEFAULT_RETRY_AFTER)
            msg = f"Rate limit exceeded. Retry after {retry_after} seconds"
            raise RetriableAPIError(msg)
        if STATUS_SERVER_ERROR_START <= status < STATUS_SERVER_ERROR_END:
            msg = f"Server error {status}: {response.text}"
            raise RetriableAPIError(msg)
        if status != STATUS_OK:
            msg = f"Unexpected status {status}: {response.text}"
            raise FatalAPIError(msg)

    def post_process(
        self,
        row: dict[str, Any],
        _context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Process each record after extraction with metadata-first consistent logic.

        This method:
        - Applies SAME flattening logic used in schema discovery
        - Ensures 100% consistency between schema and data extraction
        - Adds metadata fields
        - Handles data type conversions using metadata-first pattern
        """
        # 🎯 APPLY CONSISTENT FLATTENING (exact same logic as discovery)
        flattening_enabled = self.config.get("flattening_enabled", True)

        if flattening_enabled:
            # Use IDENTICAL flattening logic from discovery for consistency
            # Import moved to top of file for PLC0415 compliance
            schema_gen = SchemaGenerator(dict(self.config))
            row = schema_gen.flatten_complex_objects(row)

        # 🎯 APPLY METADATA-FIRST TYPE PROCESSING
        # Ensure extracted data matches schema types generated in discovery
        processed_row = self._apply_metadata_first_processing(row)

        # Add extraction metadata (prefixed to avoid conflicts)
        processed_row["_sdc_extracted_at"] = datetime.now(timezone.utc).isoformat()
        processed_row["_sdc_entity"] = self._entity_name

        # Ensure replication key is properly formatted (ISO standard)
        if self.replication_key and processed_row.get(self.replication_key):
            processed_row[self.replication_key] = self._normalize_timestamp(
                processed_row[self.replication_key],
            )

        return processed_row

    def _apply_metadata_first_processing(self, row: dict[str, Any]) -> dict[str, Any]:
        """Apply metadata-first type processing to extracted data.

        Ensures data types match exactly what was defined in schema discovery.
        This guarantees consistency between schema generation and data extraction.

        🎯 CRITICAL FIX: Automatically add missing fields found in real data
        but not present in schema discovery to avoid data loss.
        """
        # Get schema properties for type validation
        schema_properties = self._schema.get("properties", {})

        # Handle missing fields auto-discovery
        self._handle_missing_fields(row, schema_properties)

        # Process all fields with proper typing
        return self._process_all_fields(row, schema_properties)

    def _handle_missing_fields(
        self,
        row: dict[str, Any],
        schema_properties: dict[str, Any],
    ) -> None:
        """Handle auto-discovery of missing fields."""
        missing_fields = set(row.keys()) - set(schema_properties.keys())
        if not missing_fields:
            return

        self._log_missing_fields_warning(missing_fields, schema_properties, row)

        # Auto-add missing fields to schema
        for field_name in missing_fields:
            field_value = row.get(field_name)
            inferred_schema = self._infer_field_schema(field_name, field_value)
            schema_properties[field_name] = inferred_schema
            self._log_auto_added_field(field_name, inferred_schema)

        # Update the stream schema to include auto-discovered fields
        self._schema["properties"] = schema_properties

    def _log_missing_fields_warning(
        self,
        missing_fields: set[str],
        schema_properties: dict[str, Any],
        row: dict[str, Any],
    ) -> None:
        """Log warning about missing fields."""
        self.logger.warning(
            "🚨 SCHEMA EXTENSION: Found %d fields not in schema discovery: %s",
            len(missing_fields),
            sorted(missing_fields),
            extra={
                "entity": self._entity_name,
                "missing_fields": sorted(missing_fields),
                "schema_fields_count": len(schema_properties),
                "data_fields_count": len(row.keys()),
            },
        )

    def _infer_field_schema(
        self,
        field_name: str,
        field_value: object,
    ) -> dict[str, Any]:
        """Infer schema for a field based on name and value."""
        # Infer type from field name patterns
        if field_name.endswith("_key"):
            inferred_schema = {"type": ["string", "null"], "maxLength": 255}
        elif field_name.endswith("_id"):
            inferred_schema = self._infer_id_field_schema(field_value)
        elif field_name.endswith(("_ts", "_date", "_time")):
            inferred_schema = {
                "type": ["string", "null"],
                "format": "date-time",
            }
        elif field_name.endswith("_flg"):
            inferred_schema = {"type": ["boolean", "null"]}
        else:
            inferred_schema = self._infer_from_value_type(field_value)

        # Add metadata for traceability
        inferred_schema["x-wms-metadata"] = {
            "original_metadata_type": "auto_discovered",
            "inferred_from": "data_analysis",
            "column_name": field_name,
            "auto_added": True,
        }
        return inferred_schema

    def _infer_id_field_schema(self, field_value: ValueType) -> dict[str, Any]:
        """Infer schema for ID fields."""
        if isinstance(field_value, (int, float)) or (
            isinstance(field_value, str) and field_value.isdigit()
        ):
            return {"type": ["integer", "null"]}
        return {
            "type": ["string", "null"],
            "maxLength": 100,
        }

    def _infer_from_value_type(self, field_value: ValueType) -> dict[str, Any]:
        """Infer schema from value type."""
        if isinstance(field_value, bool):
            return {"type": ["boolean", "null"]}
        if isinstance(field_value, (int, float)):
            return {"type": ["number", "null"]}
        # Default to string with generous length
        return {"type": ["string", "null"], "maxLength": 500}

    def _log_auto_added_field(
        self,
        field_name: str,
        inferred_schema: dict[str, Any],
    ) -> None:
        """Log information about auto-added field."""
        self.logger.info(
            "🔧 AUTO-ADDED field '%s' to schema with type %s",
            field_name,
            inferred_schema.get("type"),
            extra={
                "entity": self._entity_name,
                "field_name": field_name,
                "inferred_type": inferred_schema.get("type"),
                "auto_added": True,
            },
        )

    def _process_all_fields(
        self,
        row: dict[str, Any],
        schema_properties: dict[str, Any],
    ) -> dict[str, Any]:
        """Process all fields with proper typing."""
        processed_row: dict[str, Any] = {}

        for field_name, field_value in row.items():
            # Get schema definition for this field
            field_schema = schema_properties.get(field_name, {})

            # Apply type processing based on schema
            if field_value is None:
                # Preserve nulls (all fields are nullable in our schema)
                processed_row[field_name] = None
            elif "x-wms-metadata" in field_schema:
                # Process field using metadata-first pattern
                processed_row[field_name] = self._process_field_with_metadata(
                    field_name,
                    field_value,
                    field_schema,
                )
            else:
                # Standard processing for fields without metadata
                processed_row[field_name] = self._process_field_standard(
                    field_name,
                    field_value,
                    field_schema,
                )

        return processed_row

    def _process_field_with_metadata(
        self,
        field_name: str,
        field_value: ValueType,
        field_schema: dict[str, Any],
    ) -> ValueType:
        """Process field using metadata-first pattern information."""
        metadata = field_schema.get("x-wms-metadata", {})
        original_type = metadata.get("original_metadata_type")
        schema_type = field_schema.get("type", ["string", "null"])

        # Extract actual type (remove 'null' from Singer schema)
        actual_type = (
            next((t for t in schema_type if t != "null"), "string")
            if isinstance(schema_type, list)
            else schema_type
        )

        try:
            # Apply metadata-first type conversions
            if original_type:
                return self._convert_by_metadata_type(original_type, field_value)
            # Pattern-based fields (inferred_from: "pattern") - use Singer type
            return self._convert_by_schema_type(actual_type, field_value)

        except (ValueError, TypeError) as e:
            # Type conversion failures are serious data quality issues
            error_msg = (
                f"Critical type conversion error for field '{field_name}': "
                f"Cannot convert '{field_value}' (type: {type(field_value).__name__}) "
                f"to expected type '{original_type}'. Data quality issues "
                f"or incorrect schema definition. Error: {e}"
            )
            self.logger.exception(error_msg)
            # Fail fast - don't mask data quality issues
            raise ValueError(error_msg) from e

    def _convert_by_metadata_type(
        self,
        original_type: str,
        field_value: ValueType,
    ) -> ValueType:
        """Convert field value based on WMS metadata type."""
        if original_type in {"pk", "integer"}:
            return int(field_value) if field_value not in {"", None} else None
        if original_type in {"number", "decimal"}:
            return float(field_value) if field_value not in {"", None} else None
        if original_type == "boolean":
            return self._convert_to_boolean(field_value)
        if original_type in {"datetime", "date"}:
            return self._normalize_timestamp(field_value)
        if original_type in {"varchar", "char", "text"}:
            return str(field_value) if field_value is not None else None
        # Fallback for unknown metadata types
        return str(field_value) if field_value is not None else None

    def _convert_by_schema_type(
        self,
        actual_type: str,
        field_value: ValueType,
    ) -> ValueType:
        """Convert field value based on Singer schema type."""
        if actual_type == "integer":
            return int(field_value) if field_value not in {"", None} else None
        if actual_type == "number":
            return float(field_value) if field_value not in {"", None} else None
        if actual_type == "boolean":
            return bool(field_value) if field_value is not None else None
        return str(field_value) if field_value is not None else None

    def _convert_to_boolean(self, field_value: ValueType) -> bool | None:
        """Convert various value types to boolean."""
        if isinstance(field_value, bool):
            return field_value
        if isinstance(field_value, str):
            return field_value.lower() in {"true", "1", "yes", "y"}
        if isinstance(field_value, (int, float)):
            return bool(field_value)
        return None

    def _process_field_standard(
        self,
        field_name: str,
        field_value: ValueType,
        field_schema: dict[str, Any],
    ) -> ValueType:
        """Process field without metadata using standard approach."""
        schema_type = field_schema.get("type", ["string", "null"])

        # Extract actual type (remove 'null' from Singer schema)
        actual_type = (
            next((t for t in schema_type if t != "null"), "string")
            if isinstance(schema_type, list)
            else schema_type
        )

        try:
            if actual_type == "integer":
                return int(field_value) if field_value not in {"", None} else None
            if actual_type == "number":
                return float(field_value) if field_value not in {"", None} else None
            if actual_type == "boolean":
                return bool(field_value) if field_value is not None else None
            return str(field_value) if field_value is not None else None
        except (ValueError, TypeError) as e:
            # Type conversion failures indicate serious data/schema issues
            error_msg = (
                f"Critical type conversion error for field '{field_name}': "
                f"Cannot convert '{field_value}' (type: {type(field_value).__name__}) "
                f"to expected type '{actual_type}'. Data quality issues. Error: {e}"
            )
            self.logger.exception(error_msg)
            # Fail fast - don't mask data quality issues
            raise ValueError(error_msg) from e

    def _normalize_timestamp(self, timestamp_value: ValueType) -> str | None:
        """Normalize timestamp to ISO format with timezone."""
        if timestamp_value is None:
            return None

        if isinstance(timestamp_value, str):
            return self._normalize_string_timestamp(timestamp_value)
        if isinstance(timestamp_value, datetime):
            return self._normalize_datetime_timestamp(timestamp_value)
        # Try to convert to string - timestamp_value is guaranteed non-None here
        return str(timestamp_value)

    def _normalize_string_timestamp(self, timestamp_value: str) -> str | None:
        """Normalize string timestamp values."""
        if not timestamp_value.strip():
            return None
        # Ensure UTC timezone if not present
        if not timestamp_value.endswith("Z") and "+00:00" not in timestamp_value:
            try:
                # Try to parse and add UTC timezone
                dt = datetime.fromisoformat(timestamp_value.replace("Z", ""))
                return dt.replace(tzinfo=timezone.utc).isoformat()
            except (ValueError, TypeError):
                # Timestamp normalization failures - log as error but proceed
                self.logger.exception(
                    "Timestamp normalization failed for value '%s'. "
                    "Using original value - may cause timezone issues downstream.",
                    timestamp_value,
                )
                return timestamp_value
        return timestamp_value

    def _normalize_datetime_timestamp(self, timestamp_value: datetime) -> str:
        """Normalize datetime timestamp objects."""
        if timestamp_value.tzinfo is None:
            timestamp_with_tz = timestamp_value.replace(tzinfo=timezone.utc)
            return timestamp_with_tz.isoformat()
        return timestamp_value.isoformat()

    def request_records(
        self,
        context: Mapping[str, Any] | None,
    ) -> Iterable[dict[str, Any]]:
        """Override request_records to add detailed HTTP logging."""
        request_count = 0

        # Get URL and params
        url = self.get_url(context)
        params = self.get_url_params(context, None)
        headers = self.http_headers

        # 🔍 LOG REQUISIÇÃO HTTP DETALHADA
        self.logger.info(
            "WMS HTTP REQUEST #%d - Entity: %s",
            request_count + 1,
            self._entity_name,
            extra={
                "entity": self._entity_name,
                "request_number": request_count + 1,
                "url": url,
                "params": params,
                "headers": {
                    k: v
                    for k, v in headers.items()
                    if k.lower()
                    not in {"authorization", "cookie", "x-api-key", "x-auth-token"}
                },
                "method": "GET",
                "request_start_time": time.time(),
            },
        )

        try:
            # Use parent implementation but track each request
            yield from super().request_records(context)
        except Exception as e:
            self.logger.exception(
                "WMS HTTP REQUEST FAILED - Entity: %s",
                self._entity_name,
                extra={
                    "entity": self._entity_name,
                    "request_number": request_count + 1,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise

    def _request(
        self,
        prepared_request: requests.PreparedRequest,
        context: Mapping[str, Any] | None,
    ) -> requests.Response:
        """Override _request to log every HTTP call with timing."""
        request_start = time.time()

        # 📡 LOG CADA CHAMADA HTTP INDIVIDUAL
        self.logger.info(
            "WMS INDIVIDUAL HTTP CALL - Entity: %s - URL: %s - HEADERS: %d",
            self._entity_name,
            prepared_request.url,
            len(prepared_request.headers) if prepared_request.headers else 0,
            extra={
                "entity": self._entity_name,
                "method": prepared_request.method,
                "url": prepared_request.url,
                "headers_count": (
                    len(prepared_request.headers) if prepared_request.headers else 0
                ),
                "body_size": len(prepared_request.body) if prepared_request.body else 0,
                "call_start_time": request_start,
            },
        )

        try:
            # Fazer a requisição usando o método pai
            response = super()._request(prepared_request, context)

            request_duration = time.time() - request_start

            # 📈 LOG RESPOSTA HTTP COM TIMING
            self.logger.info(
                "WMS HTTP RESPONSE - Entity: %s",
                self._entity_name,
                extra={
                    "entity": self._entity_name,
                    "status_code": response.status_code,
                    "response_time_seconds": request_duration,
                    "content_length": len(response.content) if response.content else 0,
                    "headers": dict(response.headers),
                    "encoding": response.encoding,
                },
            )
        except Exception as e:
            request_duration = time.time() - request_start

            # ❌ LOG ERRO HTTP COM TIMING
            self.logger.exception(
                "WMS HTTP ERROR - Entity: %s",
                self._entity_name,
                extra={
                    "entity": self._entity_name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "request_duration_seconds": request_duration,
                    "url": prepared_request.url,
                },
            )
            raise
        else:
            return response

    def get_records(
        self,
        context: Mapping[str, Any] | None,
    ) -> Iterable[dict[str, Any]]:
        """Get records from the stream with retry logic."""
        self.logger.info(
            "WMS GET_RECORDS START - Entity: %s",
            self._entity_name,
            extra={
                "entity": self._entity_name,
                "context": context,
                "stream_start_time": time.time(),
            },
        )

        record_count = 0
        start_time = time.time()

        try:
            # Use parent implementation with our customizations
            for record in super().get_records(context):
                record_count += 1
                if record_count % 100 == 0:  # Log progress every 100 records
                    self.logger.info(
                        "WMS PROGRESS - Entity: %s - Records: %d",
                        self._entity_name,
                        record_count,
                        extra={
                            "entity": self._entity_name,
                            "records_processed": record_count,
                            "elapsed_time": time.time() - start_time,
                        },
                    )
                yield record
        except RetriableAPIError as e:
            self.logger.warning("Retryable error for %s: %s", self._entity_name, e)
            raise
        except FatalAPIError:
            self.logger.exception("Fatal error for %s", self._entity_name)
            raise
        except Exception:
            self.logger.exception("Unexpected error for %s", self._entity_name)
            raise
        finally:
            elapsed_time = time.time() - start_time
            self.logger.info(
                "WMS GET_RECORDS END - Entity: %s",
                self._entity_name,
                extra={
                    "entity": self._entity_name,
                    "total_records": record_count,
                    "total_time_seconds": elapsed_time,
                    "records_per_second": (
                        record_count / elapsed_time if elapsed_time > 0 else 0
                    ),
                },
            )

    @property
    def authenticator(self) -> object:
        """Return authenticator for API requests."""
        return get_wms_authenticator(self, dict(self.config))

    # Additional Singer SDK features

    @property
    def schema(self) -> dict[str, Any]:
        """Return the schema for this stream."""
        return self._schema

    def get_starting_timestamp(
        self,
        context: Mapping[str, Any] | None,
    ) -> datetime | None:
        """Get starting timestamp for incremental sync."""
        if self.replication_key:
            # Try to get from state
            state_value = self.get_starting_replication_key_value(context)
            if state_value:
                try:
                    return datetime.fromisoformat(
                        state_value.replace("Z", "+00:00"),
                    )
                except (ValueError, TypeError) as e:
                    self.logger.exception(
                        "State corruption: Failed to parse timestamp '%s'. "
                        "Corrupted state prevents incremental sync.",
                        state_value,
                    )
                    msg = f"Corrupted state timestamp '{state_value}': {e}"
                    raise ValueError(msg) from e

            # Fall back to config start_date
            if self.config.get("start_date"):
                start_date_value = self.config["start_date"]
                if isinstance(start_date_value, str):
                    return datetime.fromisoformat(start_date_value)
                if isinstance(start_date_value, datetime):
                    return start_date_value
                return datetime.fromisoformat(str(start_date_value))

        return None

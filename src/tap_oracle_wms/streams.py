"""WMS Stream - Simplified implementation using Singer SDK 0.47.4+ REST capabilities.

This module implements a dynamic REST stream that can handle any Oracle WMS entity
with full functionality including:

- HATEOAS pagination following next_page URLs
- Incremental sync with MOD_TS timestamps
- Dynamic URL and parameter generation
- Automatic retry with exponential backoff
- Request caching and performance optimization
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs

import requests
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

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
            # JSON parsing errors in pagination indicate API issues
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                "Failed to parse pagination response as JSON - stopping pagination: %s. "
                "This may indicate API version incompatibility.", e
            )
            return None

    def has_more(self, response: requests.Response) -> bool:
        """Check if there are more pages to fetch."""
        return self.get_next_url(response) is not None


class WMSStream(RESTStream[dict[str, Any]]):
    """Dynamic WMS stream using Singer SDK REST capabilities.

    This stream automatically adapts to any WMS entity with:
    - Dynamic path generation
    - Automatic schema discovery
    - Incremental sync support
    - Advanced filtering
    """

    # Use HATEOAS paginator
    pagination_class = WMSPaginator

    # Default replication settings
    replication_method = "INCREMENTAL"
    replication_key = "mod_ts"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize stream with dynamic settings."""
        # Extract custom settings before calling parent
        self._entity_name = str(kwargs.get("name", ""))
        self._schema = dict(kwargs.get("schema", {}))

        super().__init__(*args, **kwargs)

        # Set primary keys based on schema
        if "id" in self._schema.get("properties", {}):
            self.primary_keys = ["id"]

        # Determine replication method
        schema_props = self._schema.get("properties", {})

        # Check for forced full sync in config
        stream_maps = self.config.get("stream_maps", {})
        entity_config = stream_maps.get(self._entity_name, {})
        forced_method = entity_config.get("replication_method")

        if forced_method == "FULL_TABLE":
            # Forced full sync via config
            self.replication_method = "FULL_TABLE"
            # Use id as replication key for full sync bookmark tracking
            self.replication_key = "id" if "id" in schema_props else "record_id"
        elif "mod_ts" not in schema_props:
            # Fall back to full table sync if no mod_ts field
            self.replication_method = "FULL_TABLE"
            # Use id as replication key for full sync bookmark tracking
            self.replication_key = "id" if "id" in schema_props else "record_id"
        else:
            # Use incremental sync with mod_ts
            self.replication_method = "INCREMENTAL"
            self.replication_key = "mod_ts"

    @property
    def url_base(self) -> str:
        """Base URL from config."""
        return str(self.config["base_url"]).rstrip("/")

    @property
    def path(self) -> str:  # type: ignore[override]
        """Generate entity-specific path."""
        # Oracle WMS REST API pattern
        return f"/wms/lgfapi/v10/entity/{self._entity_name}"

    @property
    def http_headers(self) -> dict[str, Any]:
        """Return headers for all requests."""
        headers = super().http_headers

        # Add WMS-specific headers
        headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-WMS-Company": self.config.get("company_code", "*"),
                "X-WMS-Facility": self.config.get("facility_code", "*"),
            },
        )

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
        """Extract parameters from pagination token."""
        params: dict[str, Any] = {}
        if hasattr(next_page_token, "query") and next_page_token.query:
            parsed_params = parse_qs(next_page_token.query)
            for key, value in parsed_params.items():
                params[key] = value[0] if len(value) == 1 else value
        return params

    def _get_base_params(self) -> dict[str, Any]:
        """Get base request parameters."""
        return {
            "page_size": self.config.get("page_size", 1000),
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
        """Add incremental sync filter."""
        start_date = self.get_starting_timestamp(context)
        if start_date:
            overlap_minutes = self.config.get("incremental_overlap_minutes", 5)
            adjusted_date = start_date - timedelta(minutes=overlap_minutes)
            params[f"{self.replication_key}__gte"] = adjusted_date.isoformat()

    def _add_full_table_filter(
        self,
        params: dict[str, Any],
        context: Mapping[str, Any] | None,
    ) -> None:
        """Add full table sync filter."""
        bookmark = self.get_starting_replication_key_value(context)
        if bookmark and "id" in self._schema.get("properties", {}):
            try:
                bookmark_id = int(bookmark)
                params["id__lte"] = str(bookmark_id)
            except (ValueError, TypeError) as e:
                self.logger.warning(
                    "Invalid bookmark format for full sync, "
                    "expected integer ID but got '%s': %s",
                    bookmark,
                    e,
                )

    def _add_ordering_params(self, params: dict[str, Any]) -> None:
        """Add ordering parameters for consistent results."""
        if self.replication_method == "FULL_TABLE":
            self._add_full_table_ordering(params)
        else:
            self._add_incremental_ordering(params)

    def _add_full_table_ordering(self, params: dict[str, Any]) -> None:
        """Add ordering for full table sync."""
        if "id" in self._schema.get("properties", {}):
            params["ordering"] = "-id"  # Descending for full sync
        elif self.replication_key:
            params["ordering"] = f"-{self.replication_key}"

    def _add_incremental_ordering(self, params: dict[str, Any]) -> None:
        """Add ordering for incremental sync."""
        if self.replication_key == "mod_ts":
            params["ordering"] = "mod_ts"  # Ascending for incremental
        elif self.replication_key:
            params["ordering"] = self.replication_key
        elif "id" in self._schema.get("properties", {}):
            params["ordering"] = "id"

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
            self.logger.exception(
                "Critical JSON parsing error for entity %s: Invalid response format. "
                "This indicates API incompatibility or server-side issues.",
                self._entity_name
            )
            msg = f"Invalid JSON response from WMS API for entity {self._entity_name}: {e}"
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
                "has_results": (
                    "results" in data if isinstance(data, dict) else False
                ),
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
        """Log warning for unexpected response format."""
        self.logger.warning(
            "Unexpected response format for %s: %s",
            self._entity_name,
            type(data).__name__,
        )

    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response and handle errors."""
        # HTTP status code constants
        STATUS_OK = 200
        STATUS_UNAUTHORIZED = 401
        STATUS_FORBIDDEN = 403
        STATUS_NOT_FOUND = 404
        STATUS_TOO_MANY_REQUESTS = 429
        STATUS_SERVER_ERROR_START = 500
        STATUS_SERVER_ERROR_END = 600
        DEFAULT_RETRY_AFTER = 60

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
        context: Mapping[str, Any] | None = None,
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
            from .discovery import SchemaGenerator

            schema_gen = SchemaGenerator(dict(self.config))
            row = schema_gen._flatten_complex_objects(row)

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
        """
        processed_row: dict[str, Any] = {}

        # Get schema properties for type validation
        schema_properties = self._schema.get("properties", {})

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
                    field_name, field_value, field_schema,
                )
            else:
                # Standard processing for fields without metadata
                processed_row[field_name] = self._process_field_standard(
                    field_name, field_value, field_schema,
                )

        return processed_row

    def _process_field_with_metadata(
        self, field_name: str, field_value: Any, field_schema: dict[str, Any],
    ) -> Any:
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
            if original_type in ("pk", "integer"):
                return int(field_value) if field_value not in ("", None) else None
            if original_type in ("number", "decimal"):
                return float(field_value) if field_value not in ("", None) else None
            if original_type == "boolean":
                if isinstance(field_value, bool):
                    return field_value
                if isinstance(field_value, str):
                    return field_value.lower() in ("true", "1", "yes", "y")
                if isinstance(field_value, (int, float)):
                    return bool(field_value)
                return None
            if original_type in ("datetime", "date"):
                return self._normalize_timestamp(field_value)
            if original_type in ("varchar", "char", "text"):
                return str(field_value) if field_value is not None else None
            if original_type is None:
                # Pattern-based fields (inferred_from: "pattern") - use Singer schema type
                if actual_type == "integer":
                    return int(field_value) if field_value not in ("", None) else None
                if actual_type == "number":
                    return float(field_value) if field_value not in ("", None) else None
                if actual_type == "boolean":
                    return bool(field_value) if field_value is not None else None
                return str(field_value) if field_value is not None else None
            # Fallback for unknown metadata types
            return str(field_value) if field_value is not None else None

        except (ValueError, TypeError) as e:
            # Type conversion failures are serious data quality issues
            error_msg = (
                f"Critical type conversion error for field '{field_name}': "
                f"Cannot convert value '{field_value}' (type: {type(field_value).__name__}) "
                f"to expected type '{original_type}'. This indicates data quality issues "
                f"or incorrect schema definition. Error: {e}"
            )
            self.logger.error(error_msg)
            # Fail fast - don't mask data quality issues
            raise ValueError(error_msg) from e

    def _process_field_standard(
        self, field_name: str, field_value: Any, field_schema: dict[str, Any],
    ) -> Any:
        """Standard field processing for fields without metadata."""
        schema_type = field_schema.get("type", ["string", "null"])

        # Extract actual type (remove 'null' from Singer schema)
        actual_type = (
            next((t for t in schema_type if t != "null"), "string")
            if isinstance(schema_type, list)
            else schema_type
        )

        try:
            if actual_type == "integer":
                return int(field_value) if field_value not in ("", None) else None
            if actual_type == "number":
                return float(field_value) if field_value not in ("", None) else None
            if actual_type == "boolean":
                return bool(field_value) if field_value is not None else None
            return str(field_value) if field_value is not None else None
        except (ValueError, TypeError) as e:
            # Type conversion failures indicate serious data/schema issues
            error_msg = (
                f"Critical type conversion error for field '{field_name}': "
                f"Cannot convert value '{field_value}' (type: {type(field_value).__name__}) "
                f"to expected type '{actual_type}'. This indicates data quality issues. Error: {e}"
            )
            self.logger.error(error_msg)
            # Fail fast - don't mask data quality issues
            raise ValueError(error_msg) from e

    def _normalize_timestamp(self, timestamp_value: Any) -> str | None:
        """Normalize timestamp to ISO format with timezone."""
        if timestamp_value is None:
            return None

        if isinstance(timestamp_value, str):
            if not timestamp_value.strip():
                return None
            # Ensure UTC timezone if not present
            if not timestamp_value.endswith("Z") and "+00:00" not in timestamp_value:
                try:
                    # Try to parse and add UTC timezone
                    dt = datetime.fromisoformat(timestamp_value.replace("Z", ""))
                    return dt.replace(tzinfo=timezone.utc).isoformat()
                except (ValueError, TypeError) as e:
                    # Timestamp parsing failures can be tolerated for normalization
                    self.logger.warning(
                        "Failed to normalize timestamp timezone for '%s': %s. "
                        "Using original timestamp format.",
                        timestamp_value, e,
                    )
                    return timestamp_value
            return timestamp_value
        if isinstance(timestamp_value, datetime):
            # Convert datetime to ISO string with timezone
            if timestamp_value.tzinfo is None:
                timestamp_with_tz = timestamp_value.replace(tzinfo=timezone.utc)
                return timestamp_with_tz.isoformat()
            return timestamp_value.isoformat()
        # Try to convert to string - timestamp_value is guaranteed non-None here
        return str(timestamp_value)

    def request_records(self, context: Mapping[str, Any] | None) -> Iterable[dict[str, Any]]:
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
                "headers": {k: v for k, v in headers.items() if k.lower() not in ["authorization", "cookie"]},
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

    def _request(self, prepared_request: requests.PreparedRequest, context: Mapping[str, Any] | None) -> requests.Response:
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
                "headers_count": len(prepared_request.headers) if prepared_request.headers else 0,
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

            return response

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

    def get_records(self, context: Mapping[str, Any] | None) -> Iterable[dict[str, Any]]:
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
        except FatalAPIError as e:
            self.logger.exception("Fatal error for %s: %s", self._entity_name, e)
            raise
        except Exception as e:
            self.logger.exception("Unexpected error for %s: %s", self._entity_name, e)
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
                    "records_per_second": record_count / elapsed_time if elapsed_time > 0 else 0,
                },
            )

    @property
    def authenticator(self) -> Any:
        """Return authenticator for API requests."""
        from .auth import get_wms_authenticator

        return get_wms_authenticator(self, dict(self.config))

    # Additional Singer SDK features

    @property
    def schema(self) -> dict[str, Any]:
        """Return the schema for this stream."""
        return self._schema

    def get_starting_timestamp(self, context: Mapping[str, Any] | None) -> datetime | None:
        """Get starting timestamp for incremental sync."""
        if self.replication_key:
            # Try to get from state
            state_value = self.get_starting_replication_key_value(context)
            if state_value:
                try:
                    return datetime.fromisoformat(state_value.replace("Z", "+00:00"))
                except (ValueError, TypeError) as e:
                    self.logger.warning(
                        "Failed to parse state timestamp '%s': %s",
                        state_value,
                        e,
                    )
                    # Continue to fall back to config start_date

            # Fall back to config start_date
            if self.config.get("start_date"):
                start_date_value = self.config["start_date"]
                if isinstance(start_date_value, str):
                    return datetime.fromisoformat(start_date_value)
                if isinstance(start_date_value, datetime):
                    return start_date_value
                return datetime.fromisoformat(str(start_date_value))

        return None

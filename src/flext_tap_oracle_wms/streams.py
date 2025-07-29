"""Oracle WMS Stream - Enterprise implementation using Singer SDK REST capabilities."""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs

# Removed circular dependency - use DI pattern
from flext_core import get_logger

# MIGRATED: Singer SDK imports centralized via flext-meltano
from flext_meltano import BaseHATEOASPaginator
from flext_meltano.singer import FlextMeltanoStream as RESTStream

from flext_tap_oracle_wms.auth import get_wms_authenticator
from flext_tap_oracle_wms.config_mapper import ConfigMapper

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    import requests
# Type alias for value parameters that can accept various types
ValueType = object | str | int | float | bool | dict[str, object] | list[object] | None
# HTTP status code constants
STATUS_OK = 200
STATUS_UNAUTHORIZED = 401
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_TOO_MANY_REQUESTS = 429
STATUS_SERVER_ERROR_START = 500
STATUS_SERVER_ERROR_END = 600
DEFAULT_RETRY_AFTER = 60
# Logging constants
MAX_LOG_DATA_LENGTH = 200


class WMSPaginator(BaseHATEOASPaginator):
    """Paginator for Oracle WMS HATEOAS-style pagination."""

    @staticmethod
    def get_next_url(response: requests.Response) -> str | None:
        """Extract next page URL from Oracle WMS HATEOAS response.

        Args:
            response: HTTP response from Oracle WMS API.

        Returns:
            URL string for next page or None if no more pages.

        Raises:
            RetriableAPIError: If response cannot be parsed as JSON.

        """
        try:
            data = response.json()
            return data.get("next_page") if isinstance(data, dict) else None
        except (ValueError, json.JSONDecodeError) as e:
            logger = get_logger(__name__)
            error_msg = (
                "Critical pagination failure: Failed to parse JSON response. "
                "This will terminate extraction and may cause incomplete datasets. "
                f"Response status: {response.status_code}, "
                f"Content-Type: {response.headers.get('Content-Type', 'unknown')}"
            )
            logger.exception(error_msg, exc_info=e)
            msg = "Critical pagination failure: Failed to parse JSON response"
            raise ValueError(msg) from e

    def has_more(self, response: requests.Response) -> bool:
        """Check if more pages are available.

        Args:
            response: HTTP response from Oracle WMS API.

        Returns:
            True if more pages exist, False otherwise.

        """
        return self.get_next_url(response) is not None


class WMSStream(RESTStream[dict[str, Any]]):
    """Oracle WMS API stream using Singer SDK capabilities."""

    # Use HATEOAS paginator
    pagination_class = WMSPaginator
    # Default replication settings (will be overridden in __init__)
    replication_method = "INCREMENTAL"
    replication_key = None

    def __init__(self, tap: object, name: str, schema: dict[str, Any]) -> None:
        """Initialize WMS stream with tap, name and schema.

        Args:
            tap: Parent tap instance.
            name: Stream name.
            schema: JSON schema for the stream.

        Raises:
            ValueError: If replication key configuration is invalid.

        """
        # Store entity-specific information
        self._entity_name = name
        self._schema = schema
        # Call parent with correct Singer SDK types
        super().__init__(
            tap=tap,
            name=name,
            schema=schema,
        )
        # Initialize configuration mapper for flexible configuration
        self.config_mapper = ConfigMapper(dict(self.config))
        # Set primary keys using configurable logic
        entity_primary_keys = self.config_mapper.get_entity_primary_keys(
            self._entity_name,
        )
        if entity_primary_keys:
            self.primary_keys = entity_primary_keys
        elif "id" in self._schema.get("properties", {}):
            self.primary_keys = ["id"]
        # Determine replication method
        schema_props = self._schema.get("properties", {})
        # Get configured replication key from mapper
        configured_rep_key = self.config_mapper.get_replication_key()
        # Check for forced full sync in config
        force_full_table = self.config.get("force_full_table", False)
        enable_incremental = self.config.get("enable_incremental", True)
        if force_full_table or not enable_incremental:
            # Forced full sync via config - no state management
            self.replication_method = "FULL_TABLE"
            self.replication_key = None  # No replication key for full table
        elif configured_rep_key in schema_props:
            # Use incremental sync with configured key
            self.replication_method = "INCREMENTAL"
            self.replication_key = configured_rep_key
        else:
            # No fallback - fail explicitly if configuration is invalid
            msg = (
                f"Incremental sync enabled but replication key '{configured_rep_key}' "
                f"not found in schema properties: {list(schema_props.keys())}"
            )
            raise ValueError(msg)

    @property
    def url_base(self) -> str:
        """Get base URL for Oracle WMS API requests.

        Returns:
            Base URL with trailing slash removed.

        """
        return str(self.config["base_url"]).rstrip("/")

    @property
    def path(self) -> str:
        """Generate entity-specific path for REST endpoint."""
        # Build path from configuration using ConfigMapper
        pattern = self.config_mapper.get_entity_endpoint_pattern()
        prefix = self.config_mapper.get_endpoint_prefix()
        version = self.config_mapper.get_api_version()
        # Replace placeholders in pattern and fix double slashes
        path = pattern.format(
            prefix=prefix,
            version=version,
            entity=self._entity_name,
        )
        # Remove leading slash if present to avoid double slashes with url_base
        return path.removeprefix("/")

    @property
    def http_headers(self) -> dict[str, Any]:
        """Get HTTP headers for WMS API requests.

        Returns:
            Dictionary of headers including authentication and custom headers.

        """
        headers = super().http_headers
        # Get headers from configuration mapper (no longer hardcoded)
        configured_headers = self.config_mapper.get_custom_headers()
        headers.update(configured_headers)
        return headers

    @property
    def is_timestamp_replication_key(self) -> bool:
        """Check if replication key is a timestamp field.

        Returns:
            True if replication key is a timestamp/datetime field, False otherwise.

        """
        if not self.replication_key:
            return False
        # Check if this is a known timestamp field
        timestamp_fields = {"mod_ts", "created_at", "updated_at", "last_modified"}
        if self.replication_key in timestamp_fields:
            return True
        # Check schema for timestamp types
        schema_props = self._schema.get("properties", {})
        if self.replication_key in schema_props:
            field_schema = schema_props[self.replication_key]
            if isinstance(field_schema, dict):
                field_type = field_schema.get("type", "")
                field_format = field_schema.get("format", "")
                # Check for timestamp/datetime types
                if field_type == "string" and field_format in {"date-time", "date"}:
                    return True
                # Handle type arrays like ["string", "null"]
                if isinstance(field_type, list):
                    for t in field_type:
                        if t in {"timestamp", "datetime"}:
                            return True
                elif field_type in {"timestamp", "datetime"}:
                    return True
        return False

    def get_url_params(
        self,
        context: Mapping[str, Any] | None,
        next_page_token: object | None,
    ) -> dict[str, Any]:
        """Build URL parameters for WMS API requests.

        Args:
            context: Stream context containing partition information.
            next_page_token: Token for pagination (if continuing from previous page).

        Returns:
            Dictionary of URL parameters for the API request.

        """
        # Handle pagination first
        if next_page_token:
            return self._get_pagination_params(next_page_token)
        # Build initial request parameters
        params = self._get_base_params()
        self._add_replication_filters(params, context)
        self._add_ordering_params(params)
        self._add_entity_filters(params)
        return params

    @staticmethod
    def _get_pagination_params(next_page_token: object) -> dict[str, Any]:
        """Build URL parameters for WMS API requests.

        Args:
            next_page_token: Token for pagination (if continuing from previous page).

        Returns:
            Dictionary of URL parameters for the API request.

        """
        params: dict[str, Any] = {}
        try:
            if hasattr(next_page_token, "query"):
                parsed_params = parse_qs(next_page_token.query)
            else:
                parsed_params = {}
            # Validate and sanitize query parameters
            for key, value in parsed_params.items():
                # Basic sanitization - allow only alphanumeric, underscore, dash
                if not key.replace("_", "").replace("-", "").isalnum():
                    continue
                # Handle value arrays safely
                if isinstance(value, list) and value:
                    clean_values = [str(v)[:100] for v in value if v is not None]
                    params[key] = (
                        clean_values[0] if len(clean_values) == 1 else clean_values
                    )
        except (ValueError, KeyError, TypeError, RuntimeError) as e:
            msg = "Failed to parse pagination parameters"
            raise ValueError(msg) from e
        return params

    def _get_base_params(self) -> dict[str, Any]:
        return {
            "page_size": self.config_mapper.get_page_size(),
            "page_mode": self.config_mapper.get_pagination_mode(),
        }

    def _add_replication_filters(
        self,
        params: dict[str, Any],
        context: Mapping[str, Any] | None,
    ) -> None:
        if self.replication_method == "INCREMENTAL" and self.replication_key:
            self._add_incremental_filter(params, context)
        elif self.replication_method == "FULL_TABLE":
            self._add_full_table_filter(params, context)

    def _add_incremental_filter(
        self,
        params: dict[str, Any],
        context: Mapping[str, Any] | None,
    ) -> None:
        start_date = self.get_starting_timestamp(context)
        # Se não há estado inicial, usar hora_atual - 5m
        if not start_date:
            overlap_minutes = self.config_mapper.get_lookback_minutes()
            now = datetime.now(UTC)
            start_date = now - timedelta(minutes=overlap_minutes)
        # Validate timestamp has timezone information
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=UTC)
        # Validate overlap configuration para estado existente
        if self.get_starting_timestamp(context):
            # Só se tem estado
            overlap_minutes = self.config_mapper.get_incremental_overlap_minutes()
            if not isinstance(overlap_minutes, int | float) or overlap_minutes < 0:
                overlap_minutes = 5
            adjusted_date = start_date - timedelta(minutes=overlap_minutes)
        else:
            # Para estado inicial, já calculamos acima
            adjusted_date = start_date
        params[f"{self.replication_key}__gte"] = adjusted_date.isoformat()

    def _add_full_table_filter(
        self,
        params: dict[str, Any],
        context: Mapping[str, Any] | None,
    ) -> None:
        bookmark = self.get_starting_replication_key_value(context)
        try:
            if bookmark is not None:
                bookmark_id = int(bookmark)
            else:
                return  # No bookmark to use
            # Validate bookmark is reasonable
            if bookmark_id < 0:
                return  # No filter = start from beginning
            # Use id__lt (less than) to get records with ID lower than bookmark
            params["id__lt"] = str(bookmark_id)
        except (ValueError, TypeError):
            # Don't add filter = start from highest ID
            pass

    def _add_ordering_params(self, params: dict[str, Any]) -> None:
        if self.replication_method == "FULL_TABLE":
            self._add_full_table_ordering(params)
        else:
            self._add_incremental_ordering(params)

    def _add_full_table_ordering(self, params: dict[str, Any]) -> None:
        if "id" in self._schema.get("properties", {}):
            params["ordering"] = "-id"  # CRITICAL: Descending for full sync recovery
        # Fallback if no ID field
        elif self.replication_key:
            params["ordering"] = f"-{self.replication_key}"

    def _add_incremental_ordering(self, params: dict[str, Any]) -> None:
        if self.replication_key == "mod_ts":
            params["ordering"] = "mod_ts"  # CRITICAL: Ascending temporal order
        elif self.replication_key:
            params["ordering"] = self.replication_key
        elif "id" in self._schema.get("properties", {}):
            params["ordering"] = "id"  # Fallback to ID if no replication key

    def _add_entity_filters(self, params: dict[str, Any]) -> None:
        entity_filters = self.config.get("entity_filters", {})
        if self._entity_name in entity_filters:
            params.update(entity_filters[self._entity_name])

    def parse_response(self, response: requests.Response) -> Iterable[dict[str, Any]]:
        """Parse records from API response.

        Args:
            response: HTTP response from WMS API
        Yields:
            Dictionary records from the response data
        Raises:
            RetriableAPIError: If response parsing fails.

        """
        try:
            data = response.json()
            # Extract records from results array
            if isinstance(data, dict) and "results" in data:
                yield from self._yield_results_array(data)
            elif isinstance(data, list):
                yield from self._yield_direct_array(data)
            elif isinstance(data, dict) and not data:
                # Handle empty dict response - this is valid (no data available)
                # Must yield nothing to maintain generator contract
                return
            else:
                self._log_unexpected_format(data)
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON response from API for entity {self._entity_name}: {e}"
            raise ValueError(msg) from e

    def _yield_results_array(self, data: dict[str, object]) -> Iterable[dict[str, Any]]:
        results = data["results"]
        if isinstance(results, list):
            yield from results
        else:
            # Critical error: results field exists but is not a list
            error_msg = (
                f"Critical API data format error for entity '{self._entity_name}': "
                f"'results' exists but not a list (got {type(results).__name__}). "
                "This indicates API format change that prevents data extraction."
            )
            raise TypeError(error_msg)

    @staticmethod
    def _yield_direct_array(data: list[Any]) -> Iterable[dict[str, Any]]:
        yield from data

    def _log_unexpected_format(self, data: object) -> None:
        error_msg = (
            f"Critical API response format error for entity '{self._entity_name}': "
            f"Expected dict with 'results' key or list, but got {type(data).__name__}. "
            f"Response data: {str(data)[:200]}... "
            "This indicates an API incompatibility that prevents data extraction."
        )
        raise ValueError(error_msg)

    def validate_response(self, response: requests.Response) -> None:
        """Validate Oracle WMS API response and handle errors.

        Args:
            response: HTTP response from Oracle WMS API.

        Raises:
            FatalAPIError: For authentication, authorization, or entity errors.
            RetriableAPIError: For temporary server errors that can be retried.

        """
        status = response.status_code
        if status == STATUS_UNAUTHORIZED:
            msg = "Unauthorized access to Oracle WMS API"
            raise ValueError(msg)
        if status == STATUS_FORBIDDEN:
            msg = "Forbidden access to Oracle WMS API"
            raise ValueError(msg)
        if status == STATUS_NOT_FOUND:
            msg = "Resource not found in Oracle WMS API"
            raise ValueError(msg)
        if status == STATUS_TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After", DEFAULT_RETRY_AFTER)
            msg = (
                f"Too many requests to Oracle WMS API "
                f"(retry after {retry_after} seconds)"
            )
            raise ValueError(msg)
        if STATUS_SERVER_ERROR_START <= status < STATUS_SERVER_ERROR_END:
            msg = "Server error in Oracle WMS API"
            raise ValueError(msg)
        if status != STATUS_OK:
            msg = "Unexpected status code from Oracle WMS API"
            raise ValueError(msg)

    def post_process(
        self,
        row: dict[str, Any],
        _context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Post-process WMS data records with extraction metadata.

        Args:
            row: Data record from Oracle WMS API.
            _context: Stream context (unused in this implementation).

        Returns:
            Processed record with Singer metadata fields added.

        """
        # Singer SDK will add the required metadata automatically
        # No need to manually add _sdc_ fields - this prevents schema warnings
        return row

    @property
    def authenticator(self) -> object:
        """Return authenticator for API requests."""
        return get_wms_authenticator(self, dict(self.config))

    @property
    def schema(self) -> dict[str, Any]:
        """Get JSON schema for this WMS entity stream.

        Returns:
            JSON schema dictionary defining the structure of records.

        """
        return self._schema

    def get_starting_timestamp(
        self,
        context: Mapping[str, Any] | None,
    ) -> datetime | None:
        """Get starting timestamp for incremental data extraction.

        Args:
            context: Stream context containing partition information.

        Returns:
            Starting timestamp for incremental sync or None for full sync.

        Raises:
            ValueError: If state contains corrupted timestamp value.

        """
        if self.replication_key:
            # Try to get from state
            state_value = self.get_starting_replication_key_value(context)
            try:
                if state_value is not None:
                    return datetime.fromisoformat(str(state_value))
            except (ValueError, TypeError) as e:
                msg = "Failed to parse starting timestamp from state"
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

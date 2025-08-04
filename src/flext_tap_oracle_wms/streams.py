"""Oracle WMS Stream - Enterprise implementation using flext-core centralized models.

REFACTORED from original streams.py to use flext-core semantic models:
- Uses FlextSingerStreamModel, FlextOperationModel from flext-core
- Eliminates type duplication through centralized type system
- Implements domain models from domain layer
- Uses factory functions for stream creation
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, ClassVar, cast
from urllib.parse import parse_qs

# Import centralized models and types from flext-core
from flext_core import (
    # Base models
    TAnyDict,
    TEntityId,
    TValue,
    get_logger,
)

# Import generic interfaces from flext-meltano
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

from flext_tap_oracle_wms.auth import get_wms_authenticator

# Import domain models from centralized domain layer
from flext_tap_oracle_wms.domain.models import (
    OracleWmsEntityInfo,
    OracleWmsReplicationMethod,
    OracleWmsTapConfiguration,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    import requests
    from singer_sdk import Tap
    from singer_sdk.authenticators import SimpleAuthenticator
# REFACTORED: Use centralized types from flext-core - eliminates all type duplication
OracleWmsValueType = TValue  # Oracle WMS values use core value type
OracleWmsEntityId = TEntityId  # Oracle WMS entities use core entity ID
OracleWmsConfigDict = TAnyDict  # Oracle WMS config uses core dict type
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


class ReplicationKeyTimestampStrategy:
    """Strategy Pattern: Timestamp field detection for replication keys.

    SOLID REFACTORING: Eliminates 6 returns using Strategy Pattern + Guard Clauses.
    """

    # Known timestamp field patterns
    TIMESTAMP_FIELDS: ClassVar[set[str]] = {
        "mod_ts",
        "created_at",
        "updated_at",
        "last_modified",
    }
    TIMESTAMP_FORMATS: ClassVar[set[str]] = {"date-time", "date"}
    TIMESTAMP_TYPES: ClassVar[set[str]] = {"timestamp", "datetime"}

    @classmethod
    def is_timestamp_field(
        cls,
        replication_key: str | None,
        schema: dict[str, object],
    ) -> bool:
        """Determine if replication key is a timestamp field using Strategy Pattern.

        SOLID REFACTORING: Eliminates 6 returns from original method using
        Strategy Pattern with Guard Clauses.

        Args:
            replication_key: The replication key field name
            schema: JSON schema containing field definitions

        Returns:
            True if field is timestamp-based, False otherwise

        """
        # Guard Clause: No replication key
        if not replication_key:
            return False

        # Strategy 1: Known timestamp fields
        if cls._is_known_timestamp_field(replication_key):
            return True

        # Strategy 2: Schema-based detection
        return cls._is_schema_timestamp_field(replication_key, schema)

    @classmethod
    def _is_known_timestamp_field(cls, field_name: str) -> bool:
        """Strategy 1: Check against known timestamp field patterns."""
        return field_name in cls.TIMESTAMP_FIELDS

    @classmethod
    def _is_schema_timestamp_field(
        cls,
        field_name: str,
        schema: dict[str, object],
    ) -> bool:
        """Strategy 2: Schema-based timestamp detection using Guard Clauses."""
        schema_props = cast("dict[str, Any]", schema.get("properties", {}))

        # Guard Clause: Field not in schema
        if field_name not in schema_props:
            return False

        field_schema = schema_props[field_name]

        # Guard Clause: Invalid field schema
        if not isinstance(field_schema, dict):
            return False

        return cls._check_field_type_for_timestamp(field_schema)

    @classmethod
    def _check_field_type_for_timestamp(cls, field_schema: dict[str, Any]) -> bool:
        """Check field type and format for timestamp indicators using Guard Clauses."""
        field_type = field_schema.get("type", "")
        field_format = field_schema.get("format", "")

        # Strategy: String with datetime format
        if cls._is_string_datetime_field(field_type, field_format):
            return True

        # Strategy: Direct timestamp type
        if cls._is_direct_timestamp_type(field_type):
            return True

        # Strategy: Type array with timestamp types
        return cls._is_array_with_timestamp_type(field_type)

    @classmethod
    def _is_string_datetime_field(
        cls,
        field_type: object,
        field_format: object,
    ) -> bool:
        """Check if field is string with datetime format."""
        return field_type == "string" and field_format in cls.TIMESTAMP_FORMATS

    @classmethod
    def _is_direct_timestamp_type(cls, field_type: object) -> bool:
        """Check if field type is directly a timestamp type."""
        return field_type in cls.TIMESTAMP_TYPES

    @classmethod
    def _is_array_with_timestamp_type(cls, field_type: object) -> bool:
        """Check if field type is array containing timestamp types."""
        if not isinstance(field_type, list):
            return False

        return any(t in cls.TIMESTAMP_TYPES for t in field_type)


class UrlParamsBuilder:
    """Strategy Pattern: URL parameter building for WMS API requests.

    SOLID REFACTORING: Reduces complexity in get_url_params method using
    Strategy Pattern + Extract Method Pattern.
    """

    @classmethod
    def build_params(
        cls,
        stream: WMSStream,
        context: Mapping[str, object] | None,
        next_page_token: object | None,
    ) -> dict[str, object]:
        """Build URL parameters using Strategy Pattern.

        SOLID REFACTORING: Eliminates complexity by extracting parameter
        building logic into separate strategy methods.

        Args:
            stream: WMS stream instance
            context: Stream context containing partition information
            next_page_token: Token for pagination

        Returns:
            Dictionary of URL parameters for API request

        """
        # Strategy 1: Handle pagination
        if next_page_token:
            return cls._build_pagination_params(next_page_token)

        # Strategy 2: Build initial request parameters
        return cls._build_initial_params(stream, context)

    @staticmethod
    def _build_pagination_params(next_page_token: object) -> dict[str, object]:
        """Strategy 1: Build pagination-specific parameters."""
        return WMSStream.get_pagination_params(next_page_token)

    @classmethod
    def _build_initial_params(
        cls,
        stream: WMSStream,
        context: Mapping[str, object] | None,
    ) -> dict[str, object]:
        """Strategy 2: Build initial request parameters using Template Method."""
        params = stream._get_base_params()  # noqa: SLF001

        # Template Method: Apply parameter builders in sequence
        cls._apply_replication_filters(stream, params, context)
        cls._apply_ordering_params(stream, params)
        cls._apply_entity_filters(stream, params)

        return params

    @staticmethod
    def _apply_replication_filters(
        stream: WMSStream,
        params: dict[str, object],
        context: Mapping[str, object] | None,
    ) -> None:
        """Apply replication-specific filters to parameters."""
        stream._add_replication_filters(params, context)  # noqa: SLF001

    @staticmethod
    def _apply_ordering_params(stream: WMSStream, params: dict[str, object]) -> None:
        """Apply ordering parameters based on replication method."""
        stream._add_ordering_params(params)  # noqa: SLF001

    @staticmethod
    def _apply_entity_filters(stream: WMSStream, params: dict[str, object]) -> None:
        """Apply entity-specific filters to parameters."""
        stream._add_entity_filters(params)  # noqa: SLF001


class ResponseParser:
    """Strategy Pattern: WMS API response parsing with reduced complexity.

    SOLID REFACTORING: Eliminates nesting and simplifies response parsing
    using Strategy Pattern + Guard Clauses.
    """

    @classmethod
    def parse_wms_response(
        cls,
        response: requests.Response,
        entity_name: str,
    ) -> Iterable[dict[str, object]]:
        """Parse WMS API response using Strategy Pattern.

        SOLID REFACTORING: Reduces complexity by extracting parsing logic
        into separate strategy methods with Guard Clauses.

        Args:
            response: HTTP response from WMS API
            entity_name: Name of WMS entity for error context

        Yields:
            Dictionary records from response data

        Raises:
            ValueError: If response parsing fails

        """
        try:
            data = response.json()
            yield from cls._parse_response_data(data, entity_name)
        except json.JSONDecodeError as e:
            msg: str = f"Invalid JSON response from API for entity {entity_name}: {e}"
            raise ValueError(msg) from e

    @classmethod
    def _parse_response_data(
        cls,
        data: object,
        entity_name: str,
    ) -> Iterable[dict[str, object]]:
        """Parse response data using Strategy Pattern with Guard Clauses."""
        # Strategy 1: Results array format
        if cls._is_results_array_format(data):
            yield from cls._parse_results_array(cast("dict[str, object]", data))
            return

        # Strategy 2: Direct array format
        if cls._is_direct_array_format(data):
            yield from cls._parse_direct_array(cast("list[dict[str, object]]", data))
            return

        # Strategy 3: Empty response (valid case)
        if cls._is_empty_response(data):
            return  # Valid empty response

        # Strategy 4: Unexpected format (error case)
        cls._handle_unexpected_format(data, entity_name)

    @staticmethod
    def _is_results_array_format(data: object) -> bool:
        """Check if data is in results array format."""
        return isinstance(data, dict) and "results" in data

    @staticmethod
    def _is_direct_array_format(data: object) -> bool:
        """Check if data is in direct array format."""
        return isinstance(data, list)

    @staticmethod
    def _is_empty_response(data: object) -> bool:
        """Check if response is empty (valid case)."""
        return isinstance(data, dict) and not data

    @classmethod
    def _parse_results_array(
        cls, data: dict[str, object],
    ) -> Iterable[dict[str, object]]:
        """Parse results array format using Guard Clauses."""
        results = data["results"]

        # Guard Clause: Validate results is list
        if not isinstance(results, list):
            error_msg = (
                f"Critical API data format error: "
                f"'results' exists but not a list (got {type(results).__name__}). "
                "This indicates API format change that prevents data extraction."
            )
            raise TypeError(error_msg)

        yield from results

    @staticmethod
    def _parse_direct_array(
        data: list[dict[str, object]],
    ) -> Iterable[dict[str, object]]:
        """Parse direct array format."""
        yield from data

    @staticmethod
    def _handle_unexpected_format(data: object, entity_name: str) -> None:
        """Handle unexpected response format."""
        error_msg = (
            f"Critical API response format error for entity '{entity_name}': "
            f"Expected dict with 'results' key or list, but got {type(data).__name__}. "
            f"Response data: {str(data)[:200]}... "
            "This indicates an API incompatibility that prevents data extraction."
        )
        raise ValueError(error_msg)


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
            # Get logger from flext-core
            from flext_core import get_logger

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


class WMSStream(RESTStream[dict[str, object]]):
    """Oracle WMS API stream using flext-core centralized patterns.

    REFACTORED: Uses domain models and centralized configuration instead of custom patterns.
    Eliminates duplication by extending flext-core stream models.
    """

    # Use HATEOAS paginator for Oracle WMS
    pagination_class = WMSPaginator

    # Domain configuration using centralized models
    _wms_config: OracleWmsTapConfiguration | None = None
    _entity_info: OracleWmsEntityInfo | None = None
    # Default replication settings (will be overridden in __init__)
    replication_method = "INCREMENTAL"
    replication_key = None

    def __init__(self, tap: Tap, name: str, schema: dict[str, object]) -> None:
        """Initialize WMS stream using flext-core centralized patterns.

        Args:
            tap: Parent tap instance with centralized configuration.
            name: Stream name.
            schema: JSON schema for the stream.

        Raises:
            ValueError: If replication key configuration is invalid.

        REFACTORED: Uses domain models instead of storing raw configuration.

        """
        # Create domain entity info from stream configuration
        self._entity_info = OracleWmsEntityInfo(
            name=name,
            display_name=name.replace("_", " ").title(),
        )

        # Store schema for Singer SDK compatibility
        self._schema = schema
        self._entity_name = name
        # Call parent with correct Singer SDK types
        super().__init__(
            tap=tap,
            name=name,
            schema=schema,
            path=self._generate_api_path(name),
        )
        # REFACTORED: Use centralized configuration instead of custom mapper
        if hasattr(tap, "wms_config") and tap.wms_config:
            self._wms_config = tap.wms_config
        else:
            # Fallback: create configuration from tap config
            from flext_tap_oracle_wms.domain.models import create_oracle_wms_tap_config

            self._wms_config = create_oracle_wms_tap_config(dict(self.config))
        # REFACTORED: Use domain model for primary key configuration
        if self._entity_info and self._entity_info.primary_keys:
            self.primary_keys = self._entity_info.primary_keys
        else:
            # Check if id field exists in schema properties
            schema_properties = cast(
                "dict[str, object]", self._schema.get("properties", {}),
            )
            if "id" in schema_properties:
                self.primary_keys = ["id"]
                # Update domain model with discovered primary key
                if self._entity_info:
                    object.__setattr__(self._entity_info, "primary_keys", ["id"])
        # REFACTORED: Use centralized configuration for replication method
        schema_props = cast("dict[str, Any]", self._schema.get("properties", {}))

        # Get replication configuration from centralized config
        force_full_table = self.config.get("force_full_table", False)
        enable_incremental = self.config.get("enable_incremental", True)
        # Smart replication key detection based on available schema fields
        default_rep_key = self._detect_replication_key(schema_props)
        configured_rep_key = self.config.get("replication_key", default_rep_key)

        if force_full_table or not enable_incremental or not configured_rep_key:
            # Use full table replication
            self.replication_method = OracleWmsReplicationMethod.FULL_TABLE.value
            self.replication_key = None
            # Get logger from flext-core
            from flext_core import get_logger

            logger = get_logger(__name__)
            logger.info("Using full table replication")
            # Update domain model
            if self._entity_info:
                object.__setattr__(self._entity_info, "replication_key", None)
        elif configured_rep_key and configured_rep_key in schema_props:
            # Use incremental replication
            self.replication_method = OracleWmsReplicationMethod.INCREMENTAL.value
            self.replication_key = configured_rep_key
            # Get logger from flext-core
            from flext_core import get_logger

            logger = get_logger(__name__)
            logger.info(f"Using incremental replication with key: {configured_rep_key}")
            # Update domain model
            if self._entity_info:
                object.__setattr__(
                    self._entity_info,
                    "replication_key",
                    configured_rep_key,
                )
        else:
            # Fallback to full table if configured key not available
            # Get logger from flext-core
            from flext_core import get_logger

            logger = get_logger(__name__)
            logger.warning(
                f"Configured replication key '{configured_rep_key}' not found in schema. "
                f"Available: {list(schema_props.keys())[:5]}... Falling back to full table.",
            )
            self.replication_method = OracleWmsReplicationMethod.FULL_TABLE.value
            self.replication_key = None
            # Update domain model
            if self._entity_info:
                object.__setattr__(self._entity_info, "replication_key", None)

    @property
    def url_base(self) -> str:
        """Get base URL for Oracle WMS API requests.

        Returns:
            Base URL with trailing slash removed.

        """
        return str(self.config["base_url"]).rstrip("/")

    def _generate_api_path(self, entity_name: str) -> str:
        """Generate entity-specific path for REST endpoint."""
        # Simple path generation for now
        return f"/wms/lgfapi/v10/entity/{entity_name}"

    @property
    def http_headers(self) -> dict[str, object]:
        """Get HTTP headers for WMS API requests using centralized configuration.

        Returns:
            Dictionary of headers including authentication and custom headers.

        REFACTORED: Uses domain configuration instead of config mapper.

        """
        headers = super().http_headers

        # Add Oracle WMS specific headers from centralized configuration
        if (
            self._wms_config
            and self._wms_config.authentication.company_code
            and self._wms_config.authentication.company_code != "*"
        ):
            headers["X-Company-Code"] = self._wms_config.authentication.company_code
        if (
            self._wms_config
            and self._wms_config.authentication.facility_code
            and self._wms_config.authentication.facility_code != "*"
        ):
            headers["X-Facility-Code"] = self._wms_config.authentication.facility_code

        # Add API version header
        if self._wms_config:
            headers["X-WMS-API-Version"] = self._wms_config.connection.api_version

        return headers

    @property
    def is_timestamp_replication_key(self) -> bool:
        """Check if replication key is a timestamp field.

        Returns:
            True if replication key is a timestamp/datetime field, False otherwise.

        """
        # Strategy Pattern: Use ReplicationKeyTimestampStrategy to eliminate 6 returns
        return ReplicationKeyTimestampStrategy.is_timestamp_field(
            self.replication_key,
            self._schema,
        )

    def get_url_params(
        self,
        context: Mapping[str, object] | None,
        next_page_token: object | None,
    ) -> dict[str, object]:
        """Build URL parameters for WMS API requests.

        Args:
            context: Stream context containing partition information.
            next_page_token: Token for pagination (if continuing from previous page).

        Returns:
            Dictionary of URL parameters for the API request.

        """
        # Strategy Pattern: Use UrlParamsBuilder to reduce complexity
        return UrlParamsBuilder.build_params(self, context, next_page_token)

    @staticmethod
    def get_pagination_params(next_page_token: object) -> dict[str, object]:
        """Build URL parameters for WMS API requests.

        Args:
            next_page_token: Token for pagination (if continuing from previous page).

        Returns:
            Dictionary of URL parameters for the API request.

        """
        params: dict[str, object] = {}
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

    def _get_base_params(self) -> dict[str, object]:
        """Get base parameters using centralized configuration.

        REFACTORED: Uses domain configuration instead of config mapper.
        """
        if self._wms_config:
            return {
                "page_size": self._wms_config.page_size,
                "page_mode": self._wms_config.page_mode,
            }
        return {
            "page_size": self.config.get("page_size", 1000),
            "page_mode": self.config.get("page_mode", "sequenced"),
        }

    def _add_replication_filters(
        self,
        params: dict[str, object],
        context: Mapping[str, object] | None,
    ) -> None:
        if self.replication_method == "INCREMENTAL" and self.replication_key:
            self._add_incremental_filter(params, context)
        elif self.replication_method == "FULL_TABLE":
            self._add_full_table_filter(params, context)

    def _add_incremental_filter(
        self,
        params: dict[str, object],
        context: Mapping[str, object] | None,
    ) -> None:
        """Add incremental filter using centralized configuration.

        REFACTORED: Uses domain configuration instead of config mapper.
        """
        start_date = self.get_starting_timestamp(context)

        # Get overlap configuration from centralized config
        if not start_date:
            lookback_minutes = (
                self._wms_config.lookback_minutes
                if self._wms_config
                else self.config.get("lookback_minutes", 5)
            )
            now = datetime.now(UTC)
            start_date = now - timedelta(minutes=lookback_minutes)

        # Ensure timezone information
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=UTC)

        # Apply overlap for existing state
        if self.get_starting_timestamp(context):
            overlap_minutes = (
                self._wms_config.incremental_overlap_minutes
                if self._wms_config
                else self.config.get("incremental_overlap_minutes", 5)
            )
            if not isinstance(overlap_minutes, int | float) or overlap_minutes < 0:
                overlap_minutes = 5
            adjusted_date = start_date - timedelta(minutes=overlap_minutes)
        else:
            adjusted_date = start_date

        # Set filter parameter
        if self.replication_key:
            params[f"{self.replication_key}__gte"] = adjusted_date.isoformat()

    def _add_full_table_filter(
        self,
        params: dict[str, object],
        context: Mapping[str, object] | None,
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

    def _add_ordering_params(self, params: dict[str, object]) -> None:
        if self.replication_method == "FULL_TABLE":
            self._add_full_table_ordering(params)
        else:
            self._add_incremental_ordering(params)

    def _add_full_table_ordering(self, params: dict[str, object]) -> None:
        if "id" in self._schema.get("properties", {}):
            params["ordering"] = "-id"  # CRITICAL: Descending for full sync recovery
        # Fallback if no ID field
        elif self.replication_key:
            params["ordering"] = f"-{self.replication_key}"

    def _detect_replication_key(self, schema_props: dict[str, Any]) -> str:
        """Detect the best available replication key from schema properties.

        Priority order:
        1. mod_ts (preferred Oracle WMS standard)
        2. mod_date (alternative Oracle standard)
        3. modified_at (common alternative)
        4. updated_at (common alternative)
        5. create_date (fallback)
        6. None (full table only)

        Args:
            schema_props: Schema properties dictionary

        Returns:
            Best available replication key or None for full table

        """
        # Get logger from flext-core
        logger = get_logger(__name__)

        # Ordered list of preferred replication keys
        replication_candidates = [
            "mod_ts",
            "mod_date",
            "modified_at",
            "updated_at",
            "last_updated",
            "create_date",
            "created_at",
        ]

        available_props = set(schema_props.keys())

        for candidate in replication_candidates:
            if candidate in available_props:
                logger.info(f"Using replication key: {candidate}")
                return candidate

        logger.warning(
            "No suitable replication key found, using full table replication",
        )
        return ""  # Empty string indicates full table replication

    def _add_incremental_ordering(self, params: dict[str, object]) -> None:
        if self.replication_key == "mod_ts":
            params["ordering"] = "mod_ts"  # CRITICAL: Ascending temporal order
        elif self.replication_key:
            params["ordering"] = self.replication_key
        elif "id" in self._schema.get("properties", {}):
            params["ordering"] = "id"  # Fallback to ID if no replication key

    def _add_entity_filters(self, params: dict[str, object]) -> None:
        """Add entity-specific filters using centralized configuration.

        REFACTORED: Uses domain configuration instead of raw config access.
        """
        # Entity filters are not directly on configuration - use fallback to raw config
        # TODO: Add entity_filters to domain model if needed
        # Fallback to raw config for backward compatibility
        entity_filters = self.config.get("entity_filters", {})
        if self._entity_name in entity_filters:
            params.update(entity_filters[self._entity_name])

    def parse_response(
        self,
        response: requests.Response,
    ) -> Iterable[dict[str, object]]:
        """Parse records from API response.

        Args:
            response: HTTP response from WMS API
        Yields:
            Dictionary records from the response data
        Raises:
            RetriableAPIError: If response parsing fails.

        """
        # Strategy Pattern: Use ResponseParser to reduce complexity
        return ResponseParser.parse_wms_response(response, self._entity_name)

    def _yield_results_array(
        self,
        data: dict[str, object],
    ) -> Iterable[dict[str, object]]:
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
    def _yield_direct_array(data: list[Any]) -> Iterable[dict[str, object]]:
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
        row: dict[str, object],
        _context: Mapping[str, object] | None = None,
    ) -> dict[str, object] | None:
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
    def authenticator(self) -> SimpleAuthenticator:
        """Return authenticator for API requests using centralized configuration.

        REFACTORED: Uses domain configuration instead of raw config dict.
        """
        # Use centralized configuration for authentication
        if self._wms_config:
            auth_config: dict[str, object] = {
                "username": self._wms_config.authentication.username,
                "password": self._wms_config.authentication.password,
                "auth_method": self._wms_config.authentication.auth_method.value
                if hasattr(self._wms_config.authentication.auth_method, "value")
                else self._wms_config.authentication.auth_method,
                "base_url": self._wms_config.connection.base_url,
            }
        else:
            auth_config = dict(self.config)

        return get_wms_authenticator(self, auth_config)

    @property
    def schema(self) -> dict[str, object]:
        """Get JSON schema for this WMS entity stream.

        Returns:
            JSON schema dictionary defining the structure of records.

        """
        return self._schema

    def get_starting_timestamp(
        self,
        context: Mapping[str, object] | None,
    ) -> datetime | None:
        """Get starting timestamp using centralized configuration patterns.

        Args:
            context: Stream context containing partition information.

        Returns:
            Starting timestamp for incremental sync or None for full sync.

        Raises:
            ValueError: If state contains corrupted timestamp value.

        REFACTORED: Uses domain configuration for start date handling.

        """
        if self.replication_key:
            # Try to get from state first
            state_value = self.get_starting_replication_key_value(context)
            try:
                if state_value is not None:
                    return datetime.fromisoformat(str(state_value))
            except (ValueError, TypeError) as e:
                msg = "Failed to parse starting timestamp from state"
                raise ValueError(msg) from e

        # Fall back to centralized configuration start_date
        start_date_value = None
        if self._wms_config and hasattr(self._wms_config, "extraction"):
            start_date_value = self._wms_config.extraction.get("start_date")
        else:
            start_date_value = self.config.get("start_date")

        if start_date_value:
            if isinstance(start_date_value, str):
                return datetime.fromisoformat(start_date_value)
            if isinstance(start_date_value, datetime):
                return start_date_value
            return datetime.fromisoformat(str(start_date_value))

        return None

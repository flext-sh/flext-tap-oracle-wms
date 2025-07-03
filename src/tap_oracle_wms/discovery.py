"""Dynamic entity discovery for Oracle WMS."""

from __future__ import annotations

import json
import logging
import ssl
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from .auth import get_wms_authenticator, get_wms_headers

logger = logging.getLogger(__name__)


# Custom exception classes for proper error handling
class WMSDiscoveryError(Exception):
    """Base exception for WMS discovery errors."""


class EntityDiscoveryError(WMSDiscoveryError):
    """Exception raised when entity discovery fails."""


class EntityDescriptionError(WMSDiscoveryError):
    """Exception raised when entity description fails."""


class SchemaGenerationError(WMSDiscoveryError):
    """Exception raised when schema generation fails."""


class DataTypeConversionError(WMSDiscoveryError):
    """Exception raised when data type conversion fails."""


class NetworkError(WMSDiscoveryError):
    """Exception raised for network-related errors."""


class AuthenticationError(WMSDiscoveryError):
    """Exception raised for authentication errors."""


class EntityDiscovery:
    """Handle dynamic entity discovery from Oracle WMS API."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize entity discovery.

        Args:
        ----
            config: Configuration dictionary

        """
        logger.debug("Initializing entity discovery system")
        logger.debug("Config keys: %s", list(config.keys()))
        self.config = config
        self.base_url = config["base_url"].rstrip("/")
        self.api_version = "v10"  # Current stable version
        self.headers = get_wms_headers(config)

        # Add authentication
        self._authenticator = None
        self._setup_authentication()

        # Enhanced cache for discovered entities with comprehensive caching
        self._entity_cache: dict[str, str] | None = None
        self._schema_cache: dict[str, dict[str, Any]] = {}
        self._access_cache: dict[str, bool] = {}
        self._sample_cache: dict[str, list[dict[str, Any]]] = {}
        self._metadata_cache: dict[str, dict[str, Any]] = {}

        # Cache configuration
        self._cache_ttl = config.get("schema_cache_ttl", 3600)
        self._entity_cache_ttl = config.get(
            "entity_cache_ttl",
            7200,
        )  # 2 hours for entity discovery
        self._access_cache_ttl = config.get(
            "access_cache_ttl",
            1800,
        )  # 30 minutes for access checks

        # Cache timestamps
        self._last_cache_time: datetime | None = None
        self._last_entity_cache_time: datetime | None = None
        self._access_cache_times: dict[str, datetime] = {}
        self._sample_cache_times: dict[str, datetime] = {}
        self._metadata_cache_times: dict[str, datetime] = {}

    def _setup_authentication(self) -> None:
        """Set up authentication headers."""
        try:
            # Create a minimal stream context for authenticator
            stream_context = type(
                "StreamContext",
                (),
                {
                    "config": self.config,
                    "tap_name": "tap-oracle-wms",
                    "logger": logger,
                },
            )()

            auth = get_wms_authenticator(stream_context, self.config)
            if auth:
                auth_headers = getattr(auth, "auth_headers", {})
                if auth_headers:
                    self.headers.update(auth_headers)
                else:
                    logger.debug("No auth headers returned from authenticator")
            else:
                logger.debug("No authenticator configured")
        except ImportError as e:
            logger.exception("Authentication module import failed: %s", e)
            msg = f"Could not import authentication module: {e}"
            raise AuthenticationError(msg) from e
        except (AttributeError, ValueError, TypeError) as e:
            logger.exception("Authentication setup failed: %s", e)
            msg = f"Authentication configuration error: {e}"
            raise AuthenticationError(msg) from e

    @property
    def entity_endpoint(self) -> str:
        """Get the entity discovery endpoint.

        Returns
        -------
            Full URL for entity endpoint

        """
        return f"{self.base_url}/wms/lgfapi/{self.api_version}/entity/"

    async def discover_entities(self) -> dict[str, str]:
        """Discover all available entities from WMS API.

        Returns
        -------
            Dictionary mapping entity names to their URLs

        Raises
        ------
            HTTPError: If API request fails

        """
        # Check enhanced entity cache
        if (
            self._entity_cache
            and self._last_entity_cache_time
            and datetime.now(timezone.utc) - self._last_entity_cache_time
            < timedelta(seconds=self._entity_cache_ttl)
        ):
            logger.debug("Using cached entity list")
            return self._entity_cache

        logger.info("Discovering entities from Oracle WMS API")

        # Setup timeouts
        timeout = httpx.Timeout(
            connect=self.config.get("connect_timeout", 30),
            read=self.config.get("read_timeout", 120),
            write=self.config.get("write_timeout", 30),
            pool=self.config.get("pool_timeout", 10),
        )

        # SSL configuration
        verify_ssl = self.config.get("verify_ssl", True)
        if not verify_ssl:
            verify_ssl = False
        elif self.config.get("ssl_ca_file"):
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(self.config["ssl_ca_file"])
            verify_ssl = ssl_context

        async with httpx.AsyncClient(
            timeout=timeout,
            verify=verify_ssl,
            headers={"User-Agent": self.config.get("user_agent", "tap-oracle-wms/1.0")},
        ) as client:
            try:
                response = await client.get(
                    self.entity_endpoint,
                    headers=self.headers,
                )
                response.raise_for_status()

                entity_list = response.json()

                # Convert list of entity names to dictionary mapping names to URLs
                entities: dict[str, str] = {}
                if isinstance(entity_list, list):
                    base_url = f"{self.base_url}/wms/lgfapi/{self.api_version}/entity"
                    for entity_name in entity_list:
                        if isinstance(entity_name, str):
                            entities[entity_name] = f"{base_url}/{entity_name}"
                elif isinstance(entity_list, dict):
                    # If API returns dict directly, use it
                    entities = entity_list

                # Cache the results with enhanced caching
                self._entity_cache = entities
                self._last_entity_cache_time = datetime.now(timezone.utc)

                logger.info("Discovered %s entities", len(entities))
            except httpx.HTTPStatusError as e:
                logger.exception("Failed to discover entities")
                logger.exception("Response: %s", e.response.text)
                raise
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.RequestError,
            ):
                logger.exception("Network error discovering entities")
                raise
            except (ValueError, KeyError, TypeError):
                logger.exception("Data parsing error discovering entities")
                raise
        return entities

    async def describe_entity(self, entity_name: str) -> dict[str, Any] | None:
        """Get entity metadata from describe endpoint.

        Args:
        ----
            entity_name: Name of the entity

        Returns:
        -------
            Entity metadata including field definitions

        """
        # Check enhanced metadata cache
        if entity_name in self._metadata_cache:
            cache_time = self._metadata_cache_times.get(entity_name)
            if cache_time and datetime.now(timezone.utc) - cache_time < timedelta(
                seconds=self._cache_ttl,
            ):
                logger.debug("Using cached metadata for entity: %s", entity_name)
                return self._metadata_cache[entity_name]

        url = f"{self.entity_endpoint}/{entity_name}/describe/"

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                metadata: dict[str, Any] = response.json()

                # Cache the result with enhanced caching
                self._metadata_cache[entity_name] = metadata
                self._metadata_cache_times[entity_name] = datetime.now(timezone.utc)

                return metadata

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # 404 is a legitimate failure - entity doesn't exist
                    logger.exception(
                        "Entity %s does not exist (404) - check name or permissions",
                        entity_name,
                    )
                    msg = (
                        f"Entity '{entity_name}' not found. "
                        f"Verify entity name and access permissions."
                    )
                    raise EntityDescriptionError(msg) from e
                logger.exception("HTTP error describing entity %s: %s", entity_name, e)
                msg = (
                    f"Failed to describe entity {entity_name}: "
                    f"HTTP {e.response.status_code}"
                )
                raise EntityDescriptionError(msg) from e
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.RequestError,
            ) as e:
                logger.exception(
                    "Network error describing entity %s: %s", entity_name, e
                )
                msg = f"Network error describing entity {entity_name}: {e}"
                raise httpx.RequestError(msg) from e
            except (ValueError, KeyError, TypeError) as e:
                # Data parsing errors during optional size estimation
                logger.warning(
                    "Data parsing error during size estimation for entity %s: %s. "
                    "Response format may not include size information. "
                    "Size estimation failed but extraction will continue normally.",
                    entity_name,
                    e,
                )
                return None

    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear cached data.

        Args:
        ----
            cache_type: Type of cache to clear
                ("all", "entities", "metadata", "samples", "access")

        """
        if cache_type in {"all", "entities"}:
            self._entity_cache = None
            self._last_entity_cache_time = None
            logger.info("Cleared entity cache")

        if cache_type in {"all", "metadata"}:
            self._metadata_cache.clear()
            self._metadata_cache_times.clear()
            logger.info("Cleared metadata cache")

        if cache_type in {"all", "samples"}:
            self._sample_cache.clear()
            self._sample_cache_times.clear()
            logger.info("Cleared sample cache")

        if cache_type in {"all", "access"}:
            self._access_cache.clear()
            self._access_cache_times.clear()
            logger.info("Cleared access cache")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns
        -------
            Dictionary with cache statistics

        """
        current_time = datetime.now(timezone.utc)

        # Calculate cache hit ratios and sizes
        return {
            "entity_cache": {
                "cached": self._entity_cache is not None,
                "last_updated": (
                    self._last_entity_cache_time.isoformat()
                    if self._last_entity_cache_time
                    else None
                ),
                "ttl_seconds": self._entity_cache_ttl,
                "valid": bool(
                    self._entity_cache
                    and self._last_entity_cache_time
                    and current_time - self._last_entity_cache_time
                    < timedelta(seconds=self._entity_cache_ttl),
                ),
            },
            "metadata_cache": {
                "entries": len(self._metadata_cache),
                "ttl_seconds": self._cache_ttl,
                "valid_entries": sum(
                    1
                    for entity_name, cache_time in self._metadata_cache_times.items()
                    if current_time - cache_time < timedelta(seconds=self._cache_ttl)
                ),
            },
            "sample_cache": {
                "entries": len(self._sample_cache),
                "ttl_seconds": self._cache_ttl,
                "valid_entries": sum(
                    1
                    for cache_key, cache_time in self._sample_cache_times.items()
                    if current_time - cache_time < timedelta(seconds=self._cache_ttl)
                ),
            },
            "access_cache": {
                "entries": len(self._access_cache),
                "ttl_seconds": self._access_cache_ttl,
                "valid_entries": sum(
                    1
                    for entity_name, cache_time in self._access_cache_times.items()
                    if current_time - cache_time
                    < timedelta(seconds=self._access_cache_ttl)
                ),
            },
        }

    def cleanup_expired_cache(self) -> None:
        """Clean up expired cache entries to prevent memory bloat."""
        current_time = datetime.now(timezone.utc)

        # Clean expired metadata cache
        expired_metadata = [
            entity_name
            for entity_name, cache_time in self._metadata_cache_times.items()
            if current_time - cache_time >= timedelta(seconds=self._cache_ttl)
        ]
        for entity_name in expired_metadata:
            self._metadata_cache.pop(entity_name, None)
            self._metadata_cache_times.pop(entity_name, None)

        # Clean expired sample cache
        expired_samples = [
            cache_key
            for cache_key, cache_time in self._sample_cache_times.items()
            if current_time - cache_time >= timedelta(seconds=self._cache_ttl)
        ]
        for cache_key in expired_samples:
            self._sample_cache.pop(cache_key, None)
            self._sample_cache_times.pop(cache_key, None)

        # Clean expired access cache
        expired_access = [
            entity_name
            for entity_name, cache_time in self._access_cache_times.items()
            if current_time - cache_time >= timedelta(seconds=self._access_cache_ttl)
        ]
        for entity_name in expired_access:
            self._access_cache.pop(entity_name, None)
            self._access_cache_times.pop(entity_name, None)

        if expired_metadata or expired_samples or expired_access:
            logger.debug(
                "Cleaned up %d metadata, %d sample, %d access entries",
                len(expired_metadata),
                len(expired_samples),
                len(expired_access),
            )

    def filter_entities(self, entities: dict[str, str]) -> dict[str, str]:
        """Filter entities based on configuration patterns."""
        # Check for entity filters in config
        entity_filters = self.config.get("entity_filters", {})
        entity_includes = self.config.get("entity_includes", [])
        entity_excludes = self.config.get("entity_excludes", [])

        if not entity_includes and not entity_excludes and not entity_filters:
            return entities

        filtered: dict[str, str] = {}

        for entity_name, entity_url in entities.items():
            # Apply include filter
            if entity_includes:
                if not any(pattern in entity_name for pattern in entity_includes):
                    continue

            # Apply exclude filter
            if entity_excludes:
                if any(pattern in entity_name for pattern in entity_excludes):
                    continue

            filtered[entity_name] = entity_url

        return filtered

    async def get_entity_sample(
        self, entity_name: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Get sample records from an entity for schema inference."""
        url = f"{self.entity_endpoint}/{entity_name}"
        params = {"page_size": limit, "page_mode": "sequenced"}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,  # type: ignore[arg-type]
                )
                response.raise_for_status()

                data = response.json()

                # Extract records from response
                if isinstance(data, dict) and "results" in data:
                    results = data["results"]
                    if isinstance(results, list):
                        return results[:limit]
                elif isinstance(data, list):
                    return data[:limit]

                return []

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.exception("Entity %s not found for sampling", entity_name)
                    msg = f"Entity '{entity_name}' not found for sampling"
                    raise EntityDiscoveryError(msg) from e
                logger.exception(
                    "HTTP error getting samples for entity %s", entity_name
                )
                msg = f"HTTP error getting samples for entity {entity_name}: {e}"
                raise EntityDiscoveryError(msg) from e
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.RequestError,
            ) as e:
                logger.exception(
                    "Network error getting samples for entity %s: %s", entity_name, e
                )
                msg = f"Network error getting samples for entity {entity_name}: {e}"
                raise NetworkError(msg) from e
            except (ValueError, KeyError, TypeError) as e:
                logger.exception(
                    "Data parsing error getting samples for entity %s: %s",
                    entity_name,
                    e,
                )
                msg = (
                    f"Data parsing error getting samples for entity {entity_name}: {e}"
                )
                raise DataTypeConversionError(msg) from e


class SchemaGenerator:
    """Generate Singer schemas from WMS entity metadata."""

    # Map WMS types to Singer/JSON Schema types
    TYPE_MAPPING = {  # noqa: RUF012
        "integer": "integer",
        "string": "string",
        "number": "number",
        "decimal": "number",
        "float": "number",
        "boolean": "boolean",
        "datetime": "string",  # with format
        "date": "string",  # with format
        "time": "string",  # with format
        "array": "array",
        "object": "object",
        "text": "string",
        "char": "string",
        "varchar": "string",
    }

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize schema generator with flattening configuration."""
        self.config = config or {}

        # Flattening configuration
        self.enable_flattening = self.config.get("enable_flattening", True)
        self.flatten_id_objects = self.config.get("flatten_id_based_objects", True)
        self.flatten_key_objects = self.config.get("flatten_key_based_objects", True)
        self.flatten_url_objects = self.config.get("flatten_url_based_objects", True)
        self.max_flatten_depth = self.config.get("max_flatten_depth", 3)

        # JSON field configuration
        self.preserve_nested = self.config.get("preserve_nested_objects", True)
        self.json_prefix = self.config.get("json_field_prefix", "json_")
        self.nested_threshold = self.config.get("nested_object_threshold", 5)

    def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Generate schema from entity describe metadata.

        Args:
        ----
            metadata: Entity metadata from describe endpoint

        Returns:
        -------
            Singer-compatible schema

        """
        properties: dict[str, Any] = {}
        required_fields: list[str] = []

        # The describe endpoint returns field names in "parameters"
        # and definitions in "fields"
        field_names = metadata.get("parameters", [])
        field_definitions = metadata.get("fields", {})

        for field_name in field_names:
            if field_name in field_definitions:
                field_def = field_definitions[field_name]
                # Create property definition
                prop = self._create_property_from_field(field_name, field_def)
                properties[field_name] = prop

                # Track required fields
                if field_def.get("required", False):
                    required_fields.append(field_name)
            else:
                # Default property for fields without definition
                properties[field_name] = {"type": ["string", "null"]}

        # Build schema
        schema = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }

        if required_fields:
            schema["required"] = required_fields

        return schema

    def generate_from_sample(self, samples: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate schema by inferring from sample data with enhanced flattening.

        Args:
        ----
            samples: List of sample records

        Returns:
        -------
            Singer-compatible schema with flattened complex objects

        """
        if not samples:
            return {"type": "object", "properties": {}}

        # Process samples with flattening if enabled
        processed_samples = []
        for sample in samples:
            if self.enable_flattening:
                processed_sample = self._flatten_complex_objects(sample)
            else:
                processed_sample = sample
            processed_samples.append(processed_sample)

        # Analyze all samples to build complete schema
        properties: dict[str, Any] = {}

        for sample in processed_samples:
            for field_name, value in sample.items():
                if field_name not in properties:
                    properties[field_name] = self._infer_type_enhanced(
                        value,
                        field_name,
                        metadata_type=None,
                    )
                else:
                    # Update type if needed (handle nulls, mixed types)
                    current_type = properties[field_name]
                    new_type = self._infer_type_enhanced(
                        value,
                        field_name,
                        metadata_type=None,
                    )
                    properties[field_name] = self._merge_types(current_type, new_type)

        return {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }

    def generate_hybrid_schema(
        self,
        metadata: dict[str, Any],
        samples: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate schema using metadata for base types and samples for FK objects.

        Args:
        ----
            metadata: Entity metadata from describe endpoint
            samples: Sample records for complex object detection

        Returns:
        -------
            Optimized schema with correct base types and flattened FK objects

        """
        if not samples:
            return self.generate_from_metadata(metadata)

        # Start with metadata-based schema for accurate base types
        base_schema = self.generate_from_metadata(metadata)
        base_properties = base_schema.get("properties", {})

        # Process samples to detect additional flattened fields from complex objects
        processed_samples = []
        for sample in samples:
            if self.enable_flattening:
                processed_sample = self._flatten_complex_objects(sample)
            else:
                processed_sample = sample
            processed_samples.append(processed_sample)

        # Find fields that exist in samples but not in metadata (flattened FK fields)
        sample_fields: set[str] = set()
        for sample in processed_samples:
            sample_fields.update(sample.keys())

        metadata_fields = set(base_properties.keys())
        additional_fields = sample_fields - metadata_fields

        # Add flattened FK fields with metadata-first type inference
        for field_name in additional_fields:
            # Find representative value from samples
            field_value = None
            for sample in processed_samples:
                if field_name in sample and sample[field_name] is not None:
                    field_value = sample[field_name]
                    break

            if field_value is not None:
                # No metadata for flattened fields, use pattern-based inference
                base_properties[field_name] = self._infer_type_enhanced(
                    field_value,
                    field_name,
                    metadata_type=None,
                )
            else:
                # Default nullable type based on field name pattern
                base_properties[field_name] = self._infer_type_from_name(field_name)

        return {
            "type": "object",
            "properties": base_properties,
            "additionalProperties": False,
        }

    def _flatten_complex_objects(
        self,
        record: dict[str, Any],
        parent_key: str = "",
        separator: str = "_",
    ) -> dict[str, Any]:
        """Flatten complex nested objects with enhanced FK and SET handling.

        Args:
        ----
            record: Dictionary to flatten
            parent_key: Parent key for nested objects
            separator: Separator for nested keys

        Returns:
        -------
            Flattened dictionary with enhanced FK handling

        """
        flattened = {}

        for key, value in record.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key

            if isinstance(value, dict):
                # Handle SET objects (relationship collections)
                if key.endswith("_set") and "result_count" in value:
                    # Extract only useful data from set, ignore URL
                    set_data = {
                        "count": value.get("result_count", 0),
                        "total": value.get("total_count", value.get("result_count", 0)),
                    }

                    # Add query parameters if available (useful for filtering)
                    if "url" in value:
                        url_str = value["url"]
                        if "?" in url_str:
                            # Extract query parameters as metadata
                            query_part = url_str.split("?")[1]
                            params = {}
                            for param in query_part.split("&"):
                                if "=" in param:
                                    param_key, param_value = param.split("=", 1)
                                    params[param_key] = param_value
                            if params:
                                set_data["filter_params"] = json.dumps(params)

                    # Flatten the set data
                    for set_key, set_value in set_data.items():
                        flattened[f"{new_key}_{set_key}"] = set_value

                # Handle FK objects (id/key/url triplets)
                elif self._is_fk_object(value):
                    base_name = self._get_fk_base_name(key)

                    # Add ID field (primary for joins)
                    if "id" in value:
                        flattened[f"{base_name}_id"] = value["id"]

                    # Add key field (human readable identifier)
                    if "key" in value:
                        flattened[f"{base_name}_key"] = value["key"]

                    # Skip URL field as requested by user
                    # if "url" in value:
                    #     flattened[f"{base_name}_url"] = value["url"]

                # Handle other complex objects
                else:
                    nested_flattened = self._flatten_complex_objects(
                        value,
                        new_key,
                        separator,
                    )
                    flattened.update(nested_flattened)

            elif isinstance(value, list):
                # Handle list/array fields
                if (
                    key.endswith("_set")
                    or "instructions" in key.lower()
                    or "serial" in key.lower()
                ):
                    # For sets, store as JSON string with count
                    flattened[f"{new_key}_count"] = len(value)
                    if value:  # Only store non-empty lists
                        # Store as JSON for complex analysis later
                        flattened[f"{new_key}_data"] = json.dumps(value, default=str)

                        # Extract summary info
                        if isinstance(value[0], dict):
                            # If list of objects, extract key fields
                            keys_found: set[str] = set()
                            for item in value:
                                if isinstance(item, dict):
                                    keys_found.update(item.keys())
                            flattened[f"{new_key}_schema"] = json.dumps(
                                sorted(keys_found),
                            )
                        elif isinstance(value[0], str):
                            # If list of strings, store unique values count
                            unique_values = len(set(value))
                            flattened[f"{new_key}_unique_count"] = unique_values
                else:
                    # For regular arrays, store with index
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            nested_flattened = self._flatten_complex_objects(
                                item,
                                f"{new_key}_{i}",
                                separator,
                            )
                            flattened.update(nested_flattened)
                        else:
                            flattened[f"{new_key}_{i}"] = item

            else:
                # Simple value
                flattened[new_key] = value

        return flattened

    def _is_fk_object(self, obj: Any) -> bool:
        """Check if object is a foreign key object with id/key/url structure.

        Args:
        ----
            obj: Object to check

        Returns:
        -------
            True if object looks like a FK object

        """
        if not isinstance(obj, dict):
            return False

        # FK objects typically have id, key, and/or url fields
        fk_indicators = {"id", "key", "url", "href"}
        obj_keys = set(obj.keys())

        # Must have at least id OR key
        has_id_or_key = bool(obj_keys & {"id", "key"})

        # Most keys should be FK indicators
        indicator_ratio = (
            len(obj_keys & fk_indicators) / len(obj_keys) if obj_keys else 0
        )

        return has_id_or_key and indicator_ratio >= 0.5

    def _get_fk_base_name(self, field_name: str) -> str:
        """Extract base name from FK field name.

        Args:
        ----
            field_name: Original field name (e.g., 'item_id', 'order_id')

        Returns:
        -------
            Base name for FK fields (e.g., 'item', 'order')

        """
        # Remove '_id' suffix if present
        if field_name.endswith("_id"):
            return field_name[:-3]
        return field_name

    def _should_flatten_object(self, obj: dict[str, Any], key: str = "") -> bool:
        """Determine if an object should be flattened."""
        if not self.enable_flattening or not isinstance(obj, dict):
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

        # Check for simple objects (≤ 3 fields)
        return len(obj) <= 3

    def _should_preserve_as_json(self, obj: Any) -> bool:
        """Determine if object should be preserved as JSON field."""
        if not self.preserve_nested:
            return False

        if isinstance(obj, dict):
            # Large objects become JSON fields
            if len(obj) > self.nested_threshold:
                return True

            # Objects with nested objects become JSON fields
            if any(isinstance(v, (dict, list)) for v in obj.values()):
                return True

        elif isinstance(obj, list):
            # Arrays of complex objects become JSON fields
            if obj and isinstance(obj[0], dict) and len(obj[0]) > 3:
                return True

        return False

    def _infer_type_enhanced(
        self,
        value: Any,
        field_name: str = "",
        metadata_type: str | None = None,
    ) -> dict[str, Any]:
        """Enhanced type inference using metadata FIRST, then patterns as fallback.

        Args:
        ----
            value: Sample value
            field_name: Field name for context
            metadata_type: Type from WMS metadata (preferred)

        Returns:
        -------
            Type definition prioritizing metadata over patterns

        """
        # Check if this is a JSON field
        if field_name.startswith(self.json_prefix):
            return {"type": "string", "description": "JSON-encoded complex object"}

        # 🎯 PRIORITY 1: Use metadata type if available
        if metadata_type:
            return self._convert_metadata_type_to_singer(metadata_type, field_name)

        # 🎯 PRIORITY 2: Smart inference based on field name patterns (fallback)
        field_lower = field_name.lower()

        # FK ID fields (flattened)
        if field_lower.endswith("_id") and not field_lower.endswith("_id_id"):
            return {"anyOf": [{"type": "integer"}, {"type": "null"}]}

        # FK Key fields (flattened)
        if field_lower.endswith(("_key", "_id_key")):
            return {"anyOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]}

        # SET count fields (flattened from complex objects)
        if field_lower.endswith("_count") and "_set_" in field_lower:
            return {"anyOf": [{"type": "integer"}, {"type": "null"}]}

        # SET data fields (JSON storage)
        if field_lower.endswith("_data") and "_set_" in field_lower:
            return {"anyOf": [{"type": "string"}, {"type": "null"}]}

        # SET filter params (JSON storage)
        if field_lower.endswith(("_filter_params", "_params")):
            return {"anyOf": [{"type": "string", "maxLength": 1000}, {"type": "null"}]}

        # Quantity fields
        if any(
            suffix in field_lower
            for suffix in ["_qty", "_quantity", "alloc_qty", "ord_qty"]
        ):
            return {"anyOf": [{"type": "number"}, {"type": "null"}]}

        # Price/Cost/Amount fields
        if any(
            suffix in field_lower
            for suffix in [
                "_price",
                "_cost",
                "_amount",
                "_value",
            ]
        ):
            return {"anyOf": [{"type": "number", "multipleOf": 0.01}, {"type": "null"}]}

        # Percentage fields
        if "percentage" in field_lower or field_lower.endswith("_pct"):
            return {
                "anyOf": [
                    {"type": "number", "minimum": 0, "maximum": 100},
                    {"type": "null"},
                ],
            }

        # Decimal fields (custom fields)
        if "decimal" in field_lower:
            return {"anyOf": [{"type": "number"}, {"type": "null"}]}

        # Date fields
        if any(suffix in field_lower for suffix in ["_date", "_exp_date", "cust_date"]):
            return {"anyOf": [{"type": "string", "format": "date"}, {"type": "null"}]}

        # Timestamp fields
        if any(
            suffix in field_lower
            for suffix in ["_ts", "_timestamp", "create_ts", "mod_ts"]
        ):
            return {
                "anyOf": [{"type": "string", "format": "date-time"}, {"type": "null"}],
            }

        # Boolean flags
        if field_lower.endswith(("_flg", "_flag")):
            return {"anyOf": [{"type": "boolean"}, {"type": "null"}]}

        # Number fields
        if any(
            suffix in field_lower
            for suffix in ["_nbr", "_number", "_seq_nbr", "_count"]
        ):
            return {"anyOf": [{"type": "integer"}, {"type": "null"}]}

        # Code fields (usually short strings)
        if field_lower.endswith("_code"):
            return {"anyOf": [{"type": "string", "maxLength": 50}, {"type": "null"}]}

        # Reference fields
        if field_lower.endswith("_ref"):
            return {"anyOf": [{"type": "string", "maxLength": 100}, {"type": "null"}]}

        # 🎯 PRIORITY 3: Use standard type inference for everything else
        base_type = self._infer_type(value)

        # Make non-required fields nullable
        if base_type.get("type") != "null":
            return {"anyOf": [base_type, {"type": "null"}]}

        return base_type

    def _convert_metadata_type_to_singer(
        self,
        metadata_type: str,
        field_name: str,
    ) -> dict[str, Any]:
        """Convert WMS metadata type to Singer type using centralized mapping."""
        from .type_mapping import convert_metadata_type_to_singer

        return convert_metadata_type_to_singer(
            metadata_type=metadata_type,
            column_name=field_name,
        )

    def _infer_type_from_name(self, field_name: str) -> dict[str, Any]:
        """Infer type purely from field name patterns when no sample value available.

        Args:
        ----
            field_name: Field name to analyze

        Returns:
        -------
            Type definition based on naming patterns

        """
        field_lower = field_name.lower()

        # FK ID fields
        if field_lower.endswith("_id"):
            return {"anyOf": [{"type": "integer"}, {"type": "null"}]}

        # FK Key fields
        if field_lower.endswith("_key"):
            return {"anyOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]}

        # FK URL fields
        if field_lower.endswith("_url"):
            return {"anyOf": [{"type": "string", "maxLength": 1000}, {"type": "null"}]}

        # Quantity fields
        if any(suffix in field_lower for suffix in ["_qty", "_quantity"]):
            return {"anyOf": [{"type": "number"}, {"type": "null"}]}

        # Price/Cost fields
        if any(suffix in field_lower for suffix in ["_price", "_cost", "_amount"]):
            return {"anyOf": [{"type": "number", "multipleOf": 0.01}, {"type": "null"}]}

        # Date fields
        if "_date" in field_lower:
            return {"anyOf": [{"type": "string", "format": "date"}, {"type": "null"}]}

        # Timestamp fields
        if field_lower.endswith("_ts"):
            return {
                "anyOf": [{"type": "string", "format": "date-time"}, {"type": "null"}],
            }

        # Boolean flags
        if field_lower.endswith("_flg"):
            return {"anyOf": [{"type": "boolean"}, {"type": "null"}]}

        # Default to nullable string
        return {"anyOf": [{"type": "string"}, {"type": "null"}]}

    def _create_property_from_field(
        self,
        field_name: str,
        field_def: dict[str, Any],
    ) -> dict[str, Any]:
        """Create property definition using metadata-first approach.

        Args:
        ----
            field_name: Field name
            field_def: Field definition from describe endpoint

        Returns:
        -------
            Property definition with enhanced metadata mapping

        """
        # 🎯 Use metadata type directly via enhanced converter
        metadata_type = field_def.get("type", "string").lower()

        # Use the new metadata converter for consistent type mapping
        return self._convert_metadata_type_to_singer(metadata_type, field_name)

    def _create_property(self, param: dict[str, Any]) -> dict[str, Any]:
        """Create a property definition from parameter metadata.

        Args:
        ----
            param: Parameter metadata

        Returns:
        -------
            Property definition

        """
        field_type = param.get("type", "string").lower()
        base_type = self.TYPE_MAPPING.get(field_type, "string")

        base_prop = {"type": base_type}

        # Add description if available
        if param.get("help_text"):
            base_prop["description"] = param["help_text"]
        elif param.get("description"):
            base_prop["description"] = param["description"]

        # Add constraints
        if base_type == "string":
            if param.get("max_length"):
                base_prop["maxLength"] = param["max_length"]

            # Add format for date/time types
            if field_type in {"datetime", "timestamp"}:
                base_prop["format"] = "date-time"
            elif field_type == "date":
                base_prop["format"] = "date"
            elif field_type == "time":
                base_prop["format"] = "time"

        elif base_type in {"number", "integer"}:
            if param.get("min_value") is not None:
                base_prop["minimum"] = param["min_value"]
            if param.get("max_value") is not None:
                base_prop["maximum"] = param["max_value"]

        # Handle enums
        if param.get("choices"):
            base_prop["enum"] = param["choices"]

        # Handle default values
        if param.get("default") is not None:
            base_prop["default"] = param["default"]

        # Handle nullable fields by wrapping in anyOf
        if param.get("allow_blank") or param.get("required") == "N":
            return {"anyOf": [base_prop, {"type": "null"}]}

        return base_prop

    def _infer_type(self, value: Any) -> dict[str, Any]:
        """Infer JSON schema type from a value.

        Args:
        ----
            value: Sample value

        Returns:
        -------
            Type definition

        """
        if value is None:
            return {"type": "null"}

        if isinstance(value, bool):
            return {"type": "boolean"}

        if isinstance(value, int):
            return {"type": "integer"}

        if isinstance(value, float):
            return {"type": "number"}

        if isinstance(value, str):
            # Try to detect date/time formats
            if self._is_datetime(value):
                return {"type": "string", "format": "date-time"}
            if self._is_date(value):
                return {"type": "string", "format": "date"}
            return {"type": "string"}

        if isinstance(value, list):
            if value:
                # Infer array item type from first element
                item_type = self._infer_type(value[0])
                return {"type": "array", "items": item_type}
            return {"type": "array"}

        if isinstance(value, dict):
            return {"type": "object"}

        # Default to string for unknown types
        return {"type": "string"}

    def _merge_types(
        self,
        type1: dict[str, Any],
        type2: dict[str, Any],
    ) -> dict[str, Any]:
        """Merge two type definitions.

        Args:
        ----
            type1: First type definition
            type2: Second type definition

        Returns:
        -------
            Merged type definition

        """
        # If types are identical, return as-is
        if type1 == type2:
            return type1

        # Handle null types
        if type1.get("type") == "null":
            return {"anyOf": [type2, {"type": "null"}]}
        if type2.get("type") == "null":
            return {"anyOf": [type1, {"type": "null"}]}

        # If types differ, create a union
        return {"anyOf": [type1, type2]}

    def _is_datetime(self, value: str) -> bool:
        """Check if string value is a datetime."""
        if not isinstance(value, str) or not value.strip():
            return False

        # Common datetime formats
        for fmt in [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
        ]:
            try:
                dt = datetime.strptime(value, fmt)
                if dt.tzinfo is None:
                    # If no timezone info, assume UTC
                    dt = dt.replace(tzinfo=timezone.utc)
                return True
            except ValueError:
                continue  # Try next format
        # Not masking - this is legitimate format checking
        return False

    def _is_date(self, value: str) -> bool:
        """Check if string value is a date."""
        if not isinstance(value, str) or not value.strip():
            return False

        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            # Not masking - this is legitimate format checking
            return False

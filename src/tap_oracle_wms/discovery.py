"""Dynamic entity discovery for Oracle WMS."""

import fnmatch
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from .auth import get_wms_authenticator, get_wms_headers
from .config import HTTP_FORBIDDEN, HTTP_NOT_FOUND, HTTP_OK

logger = logging.getLogger(__name__)


class EntityDiscovery:
    """Handle dynamic entity discovery from Oracle WMS API."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize entity discovery.

        Args:
        ----
            config: Configuration dictionary

        """
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
            "entity_cache_ttl", 7200
        )  # 2 hours for entity discovery
        self._access_cache_ttl = config.get(
            "access_cache_ttl", 1800
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
        except (ImportError, AttributeError, ValueError, TypeError) as e:
            logger.warning("Failed to setup authentication: %s", e)
            # Continue without auth - basic auth will be used via headers

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
            and datetime.now(UTC) - self._last_entity_cache_time
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
            import ssl

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

                entities = response.json()

                # Cache the results with enhanced caching
                self._entity_cache = entities
                self._last_entity_cache_time = datetime.now(UTC)

                logger.info("Discovered %s entities", len(entities))
                return entities

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

    async def describe_entity(self, entity_name: str) -> dict[str, Any]:
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
            if cache_time and datetime.now(UTC) - cache_time < timedelta(
                seconds=self._cache_ttl
            ):
                logger.debug("Using cached metadata for entity: %s", entity_name)
                return self._metadata_cache[entity_name]

        url = f"{self.entity_endpoint}/{entity_name}/describe/"

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                metadata = response.json()

                # Cache the result with enhanced caching
                self._metadata_cache[entity_name] = metadata
                self._metadata_cache_times[entity_name] = datetime.now(UTC)

                return metadata

            except httpx.HTTPStatusError as e:
                logger.warning("Failed to describe entity %s: %s", entity_name, e)
                return None
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.RequestError,
            ):
                logger.exception("Network error describing entity")
                return None
            except (ValueError, KeyError, TypeError):
                logger.exception("Data parsing error describing entity")
                return None

    async def get_entity_sample(
        self, entity_name: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Get sample records from entity for schema inference with caching.

        Args:
        ----
            entity_name: Name of the entity
            limit: Number of sample records to fetch

        Returns:
        -------
            List of sample records

        """
        # Check enhanced sample cache
        cache_key = f"{entity_name}_{limit}"
        if cache_key in self._sample_cache:
            cache_time = self._sample_cache_times.get(cache_key)
            if cache_time and datetime.now(UTC) - cache_time < timedelta(
                seconds=self._cache_ttl
            ):
                logger.debug("Using cached sample data for entity: %s", entity_name)
                return self._sample_cache[cache_key]
        url = f"{self.entity_endpoint}/{entity_name}"
        params = {"page_size": limit, "page": 1}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                )
                response.raise_for_status()

                data = response.json()

                # Handle different response formats
                if isinstance(data, dict) and "results" in data:
                    sample_data = data["results"]
                elif isinstance(data, list):
                    sample_data = data[:limit]
                else:
                    sample_data: list = []

                # Cache the sample data
                self._sample_cache[cache_key] = sample_data
                self._sample_cache_times[cache_key] = datetime.now(UTC)

                return sample_data

            except httpx.HTTPStatusError as e:
                if e.response.status_code == HTTP_NOT_FOUND:
                    logger.debug("Entity %s not found for sampling", entity_name)
                else:
                    logger.warning(
                        "HTTP error getting sample for %s: %s", entity_name, e
                    )
                return []
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.RequestError,
            ) as e:
                logger.warning(
                    "Network error getting sample for entity %s: %s", entity_name, e
                )
                return []
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(
                    "Data parsing error getting sample for entity %s: %s",
                    entity_name,
                    e,
                )
                return []

    def filter_entities(self, entities: dict[str, str]) -> dict[str, str]:
        """Filter entities based on configuration.

        Args:
        ----
            entities: Dictionary of discovered entities

        Returns:
        -------
            Filtered dictionary of entities

        """
        # If specific entities are configured, use only those
        if self.config.get("entities"):
            configured_entities = self.config["entities"]
            return {
                name: url
                for name, url in entities.items()
                if name in configured_entities
            }

        # Apply pattern-based filtering
        filtered = dict(entities)

        patterns = self.config.get("entity_patterns", {})

        # Apply include patterns
        if patterns.get("include"):
            filtered = {
                name: url
                for name, url in filtered.items()
                if any(
                    fnmatch.fnmatch(name, pattern) for pattern in patterns["include"]
                )
            }

        # Apply exclude patterns
        if patterns.get("exclude"):
            filtered = {
                name: url
                for name, url in filtered.items()
                if not any(
                    fnmatch.fnmatch(name, pattern) for pattern in patterns["exclude"]
                )
            }

        # Always exclude system/internal entities
        system_prefixes = ["_", "sys_", "internal_"]
        return {
            name: url
            for name, url in filtered.items()
            if not any(name.startswith(prefix) for prefix in system_prefixes)
        }

    async def check_entity_access(self, entity_name: str) -> bool:
        """Check if user has access to entity with caching.

        Args:
        ----
            entity_name: Name of the entity

        Returns:
        -------
            True if entity is accessible

        """
        # Check enhanced access cache
        if entity_name in self._access_cache:
            cache_time = self._access_cache_times.get(entity_name)
            if cache_time and datetime.now(UTC) - cache_time < timedelta(
                seconds=self._access_cache_ttl
            ):
                logger.debug("Using cached access result for entity: %s", entity_name)
                return self._access_cache[entity_name]
        url = f"{self.entity_endpoint}/{entity_name}"
        params = {"page_size": 1, "page": 1}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                )
                access_result = response.status_code == HTTP_OK

                # Cache the access result
                self._access_cache[entity_name] = access_result
                self._access_cache_times[entity_name] = datetime.now(UTC)

                return access_result

            except httpx.HTTPStatusError as e:
                if e.response.status_code == HTTP_FORBIDDEN:
                    logger.warning("No access to entity %s", entity_name)
                    access_result = False
                else:
                    access_result = False

                # Cache negative results too
                self._access_cache[entity_name] = access_result
                self._access_cache_times[entity_name] = datetime.now(UTC)

                return access_result
            except Exception:
                # Don't cache exceptions, allow retry
                return False

    async def estimate_entity_size(self, entity_name: str) -> int | None:
        """Estimate the number of records in an entity.

        Args:
        ----
            entity_name: Name of the entity

        Returns:
        -------
            Estimated record count or None

        """
        url = f"{self.entity_endpoint}/{entity_name}"
        params = {"page_size": 1, "page": 1}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                )
                response.raise_for_status()

                data = response.json()

                # Look for count in response
                if isinstance(data, dict):
                    return (
                        data.get("result_count")
                        or data.get("count")
                        or data.get("total")
                    )

                return None

            except httpx.HTTPStatusError as e:
                if e.response.status_code == HTTP_NOT_FOUND:
                    logger.debug("Entity %s size estimation not supported", entity_name)
                else:
                    logger.warning(
                        "HTTP error estimating size for entity %s: %s", entity_name, e
                    )
                return None
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.RequestError,
            ) as e:
                logger.warning(
                    "Network error estimating size for entity %s: %s", entity_name, e
                )
                return None
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(
                    "Data parsing error estimating size for entity %s: %s",
                    entity_name,
                    e,
                )
                return None

    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear cached data.

        Args:
        ----
            cache_type: Type of cache to clear ("all", "entities", "metadata", "samples", "access")

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
        current_time = datetime.now(UTC)

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
                    < timedelta(seconds=self._entity_cache_ttl)
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
        current_time = datetime.now(UTC)

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


class SchemaGenerator:
    """Generate Singer schemas from WMS entity metadata."""

    # Map WMS types to Singer/JSON Schema types
    TYPE_MAPPING = {
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

    def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Generate schema from entity describe metadata.

        Args:
        ----
            metadata: Entity metadata from describe endpoint

        Returns:
        -------
            Singer-compatible schema

        """
        properties: dict = {}
        required_fields: list = []

        # The describe endpoint returns field names in "parameters" and definitions in "fields"
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
        """Generate schema by inferring from sample data.

        Args:
        ----
            samples: List of sample records

        Returns:
        -------
            Singer-compatible schema

        """
        if not samples:
            return {"type": "object", "properties": {}}

        # Analyze all samples to build complete schema
        properties: dict = {}

        for sample in samples:
            for field_name, value in sample.items():
                if field_name not in properties:
                    properties[field_name] = self._infer_type(value)
                else:
                    # Update type if needed (handle nulls, mixed types)
                    current_type = properties[field_name]
                    new_type = self._infer_type(value)
                    properties[field_name] = self._merge_types(current_type, new_type)

        return {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }

    def _create_property_from_field(
        self, field_name: str, field_def: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a property definition from field definition.

        Args:
        ----
            field_name: Field name
            field_def: Field definition from describe endpoint

        Returns:
        -------
            Property definition

        """
        field_type = field_def.get("type", "string").lower()
        base_type = self.TYPE_MAPPING.get(field_type, "string")

        prop = {"type": base_type}

        # Add description if available
        if field_def.get("description"):
            prop["description"] = field_def["description"]

        # Handle nullable fields
        if not field_def.get("required"):
            prop = {"anyOf": [prop, {"type": "null"}]}

        # Add constraints
        if base_type == "string":
            if field_def.get("max_length"):
                prop.setdefault("type", {})
                if (
                    isinstance(prop, dict)
                    and "type" in prop
                    and prop["type"] == "string"
                ):
                    prop["maxLength"] = field_def["max_length"]

            # Add format for date/time types
            if field_type in {"datetime", "timestamp"}:
                prop["format"] = "date-time"
            elif field_type == "date":
                prop["format"] = "date"
            elif field_type == "time":
                prop["format"] = "time"

        elif base_type in {"number", "integer"}:
            if field_def.get("min_value") is not None:
                prop["minimum"] = field_def["min_value"]
            if field_def.get("max_value") is not None:
                prop["maximum"] = field_def["max_value"]

        # Handle enums
        if field_def.get("choices"):
            prop["enum"] = field_def["choices"]

        # Handle default values
        if field_def.get("default") is not None:
            prop["default"] = field_def["default"]

        return prop

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

        prop = {"type": base_type}

        # Add description if available
        if param.get("help_text"):
            prop["description"] = param["help_text"]
        elif param.get("description"):
            prop["description"] = param["description"]

        # Handle nullable fields
        if param.get("allow_blank") or param.get("required") == "N":
            prop = {"anyOf": [prop, {"type": "null"}]}

        # Add constraints
        if base_type == "string":
            if param.get("max_length"):
                prop.setdefault("type", {})
                if isinstance(prop, dict) and "type" in prop:
                    prop["maxLength"] = param["max_length"]

            # Add format for date/time types
            if field_type in {"datetime", "timestamp"}:
                prop["format"] = "date-time"
            elif field_type == "date":
                prop["format"] = "date"
            elif field_type == "time":
                prop["format"] = "time"

        elif base_type in {"number", "integer"}:
            if param.get("min_value") is not None:
                prop["minimum"] = param["min_value"]
            if param.get("max_value") is not None:
                prop["maximum"] = param["max_value"]

        # Handle enums
        if param.get("choices"):
            prop["enum"] = param["choices"]

        # Handle default values
        if param.get("default") is not None:
            prop["default"] = param["default"]

        return prop

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
        self, type1: dict[str, Any], type2: dict[str, Any]
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
        try:
            # Common datetime formats
            for fmt in [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
            ]:
                dt = datetime.strptime(value, fmt)
                if dt.tzinfo is None:
                    # If no timezone info, assume UTC
                    dt = dt.replace(tzinfo=UTC)
                return True
        except ValueError:
            pass
        return False

    def _is_date(self, value: str) -> bool:
        """Check if string value is a date."""
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

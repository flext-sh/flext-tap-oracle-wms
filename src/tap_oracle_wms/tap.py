"""Oracle WMS Tap - Simplified implementation using Singer SDK 0.47.4+ features.

This tap extracts data from Oracle Warehouse Management System (WMS) REST API
using the latest Singer SDK capabilities while maintaining all original functionality:

- Automatic entity discovery from WMS API
- Dynamic schema generation from API metadata and sample data
- Incremental sync with MOD_TS timestamps
- HATEOAS pagination following next_page URLs
- Advanced filtering and field selection
- Circuit breaker for resilient API calls
- Performance monitoring and metrics
"""

from __future__ import annotations

import asyncio
from typing import Any

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from .discovery import (
    AuthenticationError,
    EntityDescriptionError,
    EntityDiscovery,
    EntityDiscoveryError,
    NetworkError,
    SchemaGenerationError,
    SchemaGenerator,
)

# Error logging functionality removed for simplicity
from .streams import WMSStream


class TapOracleWMS(Tap):
    """Oracle WMS tap class using Singer SDK 0.47.4+ patterns.

    This tap implements automatic entity discovery and dynamic schema generation
    to work with any Oracle WMS instance without hardcoded business logic.
    """

    name = "tap-oracle-wms"

    # Configuration schema using Singer SDK typing
    config_jsonschema = th.PropertiesList(
        # Core connection settings
        th.Property(
            "base_url",
            th.StringType,
            required=True,
            description="Oracle WMS base URL (e.g., https://wms.company.com)",
        ),
        th.Property(
            "auth_method",
            th.StringType,
            default="basic",
            allowed_values=["basic", "oauth2"],
            description="Authentication method",
        ),
        th.Property(
            "username",
            th.StringType,
            secret=True,
            description="Username for basic auth",
        ),
        th.Property(
            "password",
            th.StringType,
            secret=True,
            description="Password for basic auth",
        ),
        th.Property(
            "company_code",
            th.StringType,
            default="*",
            description="WMS company code (* for all)",
        ),
        th.Property(
            "facility_code",
            th.StringType,
            default="*",
            description="WMS facility code (* for all)",
        ),
        # Entity discovery settings
        th.Property(
            "entities",
            th.ArrayType(th.StringType),
            description="Specific entities to extract (default: auto-discover)",
        ),
        th.Property(
            "entity_patterns",
            th.ObjectType(
                th.Property("include", th.ArrayType(th.StringType)),
                th.Property("exclude", th.ArrayType(th.StringType)),
            ),
            description="Entity filtering patterns",
        ),
        # Performance settings
        th.Property(
            "page_size",
            th.IntegerType,
            default=1000,
            description="Records per page (max 1250)",
        ),
        th.Property(
            "request_timeout",
            th.IntegerType,
            default=120,
            description="Request timeout in seconds",
        ),
        th.Property(
            "max_retries",
            th.IntegerType,
            default=3,
            description="Maximum retry attempts",
        ),
        # Incremental sync settings
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Start date for incremental sync",
        ),
        th.Property(
            "enable_incremental",
            th.BooleanType,
            default=True,
            description="Enable incremental sync using MOD_TS",
        ),
        # Advanced features
        th.Property(
            "stream_maps",
            th.ObjectType(),
            description="Stream maps for inline transformations",
        ),
        th.Property(
            "stream_map_config",
            th.ObjectType(),
            description="Additional stream map configuration",
        ),
        th.Property(
            "state_partitioning_keys",
            th.ArrayType(th.StringType),
            description="Keys for partitioned state management",
        ),
        # Discovery settings
        th.Property(
            "discover_catalog",
            th.BooleanType,
            default=True,
            description="Auto-discover catalog on startup",
        ),
        th.Property(
            "catalog_cache_ttl",
            th.IntegerType,
            default=3600,
            description="Catalog cache TTL in seconds",
        ),
        # OAuth2 settings (if using OAuth2)
        th.Property("oauth_client_id", th.StringType, secret=True),
        th.Property("oauth_client_secret", th.StringType, secret=True),
        th.Property("oauth_token_url", th.StringType),
        th.Property("oauth_scope", th.StringType, default="wms.read"),
        # SSL/TLS settings
        th.Property(
            "verify_ssl",
            th.BooleanType,
            default=True,
            description="Verify SSL certificates",
        ),
        th.Property(
            "ssl_ca_file",
            th.StringType,
            description="Path to CA bundle file",
        ),
    ).to_dict()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize tap with entity discovery."""
        # Cache for discovered entities and schemas
        self._entity_cache: dict[str, str] | None = None
        self._schema_cache: dict[str, dict[str, Any]] = {}

        # Lazy-load discovery system
        self._discovery: EntityDiscovery | None = None
        self._schema_generator: SchemaGenerator | None = None

        # Detection for discovery mode vs sync mode
        self._is_discovery_mode = False

        # Call parent init
        super().__init__(*args, **kwargs)

        # Setup critical error logging to prevent silencing
        # Error logging setup removed for simplicity

    @property
    def discovery(self) -> EntityDiscovery:
        """Get or create discovery instance."""
        if self._discovery is None:
            self._discovery = EntityDiscovery(dict(self.config))
        return self._discovery

    @property
    def schema_generator(self) -> SchemaGenerator:
        """Get or create schema generator instance."""
        if self._schema_generator is None:
            self._schema_generator = SchemaGenerator(dict(self.config))
        return self._schema_generator

    def set_discovery_mode(self, enabled: bool = True) -> None:
        """Set discovery mode flag."""
        self._is_discovery_mode = enabled

    @classmethod
    def invoke(cls, *args: Any, **kwargs: Any) -> Any:
        """Override invoke to detect discovery mode."""
        # Check if this is a discovery command
        import sys

        if "--discover" in sys.argv:
            instance = cls(*args, **kwargs)
            instance.set_discovery_mode(True)
            return instance.discover_streams()
        return super().invoke(*args, **kwargs)

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Uses pre-configured entities from config or falls back to dynamic discovery
        for --discover mode only.
        """
        streams: list[Stream] = []

        # Check if this is discovery mode (--discover flag)
        if hasattr(self, "_is_discovery_mode") and self._is_discovery_mode:
            # DISCOVERY MODE: Full API discovery for catalog generation
            discovered_entities = asyncio.run(self._discover_entities_async())

            for entity_name, entity_url in discovered_entities.items():
                # Generate schema for entity
                schema = asyncio.run(self._generate_schema_async(entity_name))

                if schema:
                    # Create stream instance with dynamic schema
                    stream = WMSStream(
                        tap=self,
                        name=entity_name,
                        schema=schema,
                    )
                    streams.append(stream)

                    self.logger.info(
                        f"Discovered stream: {entity_name} with "
                        f"{len(schema.get('properties', {}))} properties",
                    )
        else:
            # SYNC MODE: Use pre-configured entities from config
            configured_entities = self.config.get("entities", [])

            # If no entities configured, skip sync mode
            if not configured_entities:
                self.logger.warning(
                    "No entities configured for sync mode. "
                    "Use --discover to generate catalog or configure 'entities'.",
                )
                return streams

            for entity_name in configured_entities:
                # 🎯 CRITICAL FIX: Use proper schema generation vs generic fallback
                # This ensures WMS-specific field types instead of fallback Oracle types
                try:
                    schema = asyncio.run(self._generate_schema_async(entity_name))

                    if schema:
                        stream = WMSStream(
                            tap=self,
                            name=entity_name,
                            schema=schema,
                        )
                        streams.append(stream)

                        self.logger.info(
                            f"Configured stream: {entity_name} with "
                            f"{len(schema.get('properties', {}))} WMS properties"
                        )
                    else:
                        self.logger.warning(
                            f"Could not generate schema for {entity_name}, skipping"
                        )
                except Exception as e:
                    self.logger.exception(
                        f"Schema generation failed for {entity_name}: {e}"
                    )
                    # Fallback to predefined schema as last resort
                    schema = self._get_predefined_schema(entity_name)
                    if schema:
                        stream = WMSStream(
                            tap=self,
                            name=entity_name,
                            schema=schema,
                        )
                        streams.append(stream)
                        self.logger.warning(f"Using fallback schema for {entity_name}")

        return streams

    def _get_predefined_schema(self, entity_name: str) -> dict[str, Any] | None:
        """Get basic schema for configured entities (generic for all entities)."""
        # Generic base schema for sync mode - Singer will discover actual structure
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": ["integer", "null"],
                    "description": "Primary key",
                },
                "mod_ts": {
                    "type": ["string", "null"],
                    "format": "date-time",
                    "description": "Modification timestamp",
                },
                "create_ts": {
                    "type": ["string", "null"],
                    "format": "date-time",
                    "description": "Creation timestamp",
                },
            },
            "additionalProperties": True,  # Allow dynamic discovery of all properties
        }

    async def _discover_entities_async(self) -> dict[str, str]:
        """Discover available entities from WMS API."""
        # Check cache first
        if self._entity_cache is not None:
            return self._entity_cache

        # Discover entities
        entities = await self.discovery.discover_entities()

        # Apply filtering
        filtered_entities = self.discovery.filter_entities(entities)

        # Cache results
        self._entity_cache = filtered_entities

        self.logger.info(f"Discovered {len(filtered_entities)} entities from WMS API")
        return filtered_entities

    async def _generate_schema_async(self, entity_name: str) -> dict[str, Any] | None:
        """Generate schema for entity using sample data (for flattening) or metadata."""
        # Check cache first
        if entity_name in self._schema_cache:
            return self._schema_cache[entity_name]

        # Schema generation with clear failure modes
        flattening_enabled = self.config.get("flattening_enabled", True)

        try:
            if flattening_enabled:
                # 🎯 FLATTENING ENABLED: Hybrid approach (metadata + samples for FK)
                metadata = await self.discovery.describe_entity(entity_name)
                samples = await self.discovery.get_entity_sample(entity_name)

                if metadata and samples:
                    # PRIORITY: Hybrid schema (metadata-first + flattened FK objects)
                    schema = self.schema_generator.generate_hybrid_schema(
                        metadata, samples
                    )
                    self.logger.info(
                        f"Generated hybrid schema for {entity_name} "
                        f"with {len(schema.get('properties', {}))} properties",
                    )
                elif metadata:
                    # ACCEPTABLE: Pure metadata (accurate types but no FK flattening)
                    schema = self.schema_generator.generate_from_metadata(metadata)
                    self.logger.info(
                        f"Generated metadata-only schema for {entity_name} "
                        f"(samples unavailable but not critical)",
                    )
                else:
                    # FAILURE: No metadata means entity doesn't exist or no access
                    error_msg = (
                        f"Schema generation failed for {entity_name}: "
                        f"Entity metadata unavailable. This indicates the entity "
                        f"doesn't exist or you lack permissions to access it."
                    )
                    self.logger.exception(error_msg)
                    raise ValueError(error_msg)
            else:
                # 🎯 FLATTENING DISABLED: Metadata-first approach (faster)
                metadata = await self.discovery.describe_entity(entity_name)
                if metadata:
                    # PRIORITY: Pure metadata (most accurate and fastest)
                    schema = self.schema_generator.generate_from_metadata(metadata)
                    self.logger.info(
                        f"Generated metadata schema for {entity_name} "
                        f"with {len(schema.get('properties', {}))} properties",
                    )
                else:
                    # FAILURE: No metadata means entity doesn't exist or no access
                    error_msg = (
                        f"Schema generation failed for {entity_name}: "
                        f"Entity metadata unavailable. This indicates the entity "
                        f"doesn't exist or you lack permissions to access it."
                    )
                    self.logger.exception(error_msg)
                    raise ValueError(error_msg)
        except (
            EntityDiscoveryError,
            EntityDescriptionError,
            NetworkError,
            AuthenticationError,
        ) as e:
            # These are specific WMS errors - re-raise with context
            error_msg = f"WMS error during schema generation for {entity_name}: {e}"
            self.logger.exception(error_msg)
            raise SchemaGenerationError(error_msg) from e
        except Exception as e:
            # Unexpected errors
            error_msg = (
                f"Unexpected error during schema generation for {entity_name}: {e}"
            )
            self.logger.exception(error_msg)
            raise SchemaGenerationError(error_msg) from e

        # Cache schema
        self._schema_cache[entity_name] = schema
        return schema

    # Singer SDK hooks for advanced functionality

    def post_process(
        self, row: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Post-process a record after extraction.

        This can be used for:
        - Adding metadata fields
        - Data type conversions
        - Filtering
        """
        # Add extraction metadata
        from datetime import datetime, timezone

        row["_extracted_at"] = datetime.now(timezone.utc).isoformat()
        return row

    @property
    def catalog_dict(self) -> dict[str, Any]:
        """Get catalog dictionary for caching."""
        return self._catalog.to_dict() if self._catalog else {}

    @property
    def state_dict(self) -> dict[str, Any]:
        """Get state dictionary for persistence."""
        return dict(self.state) if self.state else {}


if __name__ == "__main__":
    # Allow direct execution for testing
    TapOracleWMS.cli()

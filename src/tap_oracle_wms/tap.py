"""Oracle WMS Tap - Enterprise-grade implementation using Singer SDK.

This tap extracts data from Oracle Warehouse Management System REST API
with advanced features:

- Automatic entity discovery from WMS API
- Dynamic schema generation from API metadata and sample data
- Incremental sync with timestamp-based replication
- HATEOAS pagination following Oracle WMS patterns
- Advanced filtering and field selection
- Resilient API calls with retry logic
- Performance monitoring and metrics

Designed specifically for Oracle WMS REST API integration.
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone
from typing import Any

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from .config_mapper import ConfigMapper
from .config_profiles import ConfigProfileManager
from .config_validator import ConfigValidationError, validate_config_with_mapper
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
    """Oracle WMS tap using modern Singer SDK patterns.

    This tap implements automatic entity discovery and dynamic schema generation
    specifically designed for Oracle Warehouse Management System REST API.

    Built with professional standards: SOLID principles, clean architecture,
    and enterprise-grade error handling.
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
        # WMS-specific settings
        th.Property(
            "company_code",
            th.StringType,
            default="*",
            description="WMS company code (* for all companies)",
        ),
        th.Property(
            "facility_code",
            th.StringType,
            default="*",
            description="WMS facility code (* for all facilities)",
        ),
        th.Property(
            "custom_headers",
            th.ObjectType(),
            description="Additional headers to send with WMS API requests",
        ),
        # Entity configuration
        th.Property(
            "wms_api_version",
            th.StringType,
            default="v10",
            description="WMS API version (e.g., v10, v11)",
        ),
        th.Property(
            "entities",
            th.ArrayType(th.StringType),
            description="Specific WMS entities to extract (e.g., allocation, order_hdr)",
        ),
        th.Property(
            "entity_patterns",
            th.ObjectType(
                th.Property("include", th.ArrayType(th.StringType)),
                th.Property("exclude", th.ArrayType(th.StringType)),
            ),
            description="Entity filtering patterns",
        ),
        # WMS API behavior configuration
        th.Property(
            "page_mode",
            th.StringType,
            default="sequenced",
            allowed_values=["sequenced", "paged"],
            description="WMS pagination mode",
        ),
        th.Property(
            "max_page_size",
            th.IntegerType,
            default=1250,
            description="Maximum page size supported by WMS API",
        ),
        # Performance settings
        th.Property(
            "page_size",
            th.IntegerType,
            default=100,
            description="Records per page",
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
            description="Enable incremental sync using replication key",
        ),
        th.Property(
            "replication_key",
            th.StringType,
            default="mod_ts",
            description="Field to use for incremental replication (WMS typically uses mod_ts)",
        ),
        th.Property(
            "replication_key_format",
            th.StringType,
            default="datetime",
            allowed_values=["datetime", "timestamp", "unix"],
            description="Format of the replication key field",
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
        th.Property(
            "discovery_timeout",
            th.IntegerType,
            default=30,
            description="HTTP timeout for discovery operations in seconds",
        ),
        th.Property(
            "auth_timeout",
            th.IntegerType,
            default=30,
            description="HTTP timeout for authentication operations in seconds",
        ),
        # 🚨 SCHEMA DISCOVERY: HARD-CODED to use ONLY API metadata describe
        # This functionality is not configurable - no environment variables exist for this
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

    def __init__(self, *args: object, **kwargs: dict[str, object]) -> None:
        """Initialize tap with entity discovery and configuration profiles."""
        # Check for configuration profile override
        self._profile_config = self._load_profile_config()

        # Merge profile config with provided config
        if self._profile_config and "config" in kwargs:
            merged_config = {**self._profile_config}
            merged_config.update(kwargs["config"])
            kwargs["config"] = merged_config
        elif self._profile_config and not kwargs.get("config"):
            kwargs["config"] = self._profile_config

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

        # Validate configuration using ConfigMapper
        self._validate_configuration()

        # Setup critical error logging to prevent silencing
        # Error logging setup removed for simplicity

    def _load_profile_config(self) -> dict[str, Any] | None:
        """Load configuration from profile if specified.

        Returns:
            Configuration dictionary from profile, or None if no profile specified

        """
        profile_name = os.getenv("WMS_PROFILE_NAME")
        if not profile_name:
            return None

        try:
            manager = ConfigProfileManager()
            profile = manager.load_profile(profile_name)
            config = profile.to_singer_config()

            self.logger.info(f"Loaded configuration from profile: {profile_name}")
            self.logger.debug(
                f"Profile config: company={profile.company_name}, "
                f"environment={profile.environment}, "
                f"entities={len(profile.get_enabled_entities())}"
            )

            return config
        except Exception as e:
            self.logger.warning(f"Failed to load profile '{profile_name}': {e}")
            return None

    def _validate_configuration(self) -> None:
        """Validate configuration using ConfigMapper and profiles."""
        # 🚨 SCHEMA DISCOVERY: HARD-CODED to use ONLY API metadata describe
        # This tap uses EXCLUSIVELY API metadata - this is not configurable and not optional
        # NO environment variables or configuration options exist for schema discovery method

        self.logger.info(
            "✅ SCHEMA DISCOVERY: Hard-coded to use ONLY API metadata describe (no configuration options)"
        )

        try:
            # Create ConfigMapper with merged configuration
            config_mapper = ConfigMapper(dict(self.config))

            # Validate configuration
            validate_config_with_mapper(config_mapper)

            self.logger.info("✅ Configuration validation passed")

        except ConfigValidationError as e:
            self.logger.error(f"❌ Configuration validation failed: {e}")
            raise
        except Exception as e:
            self.logger.warning(f"Configuration validation encountered an error: {e}")
            # Don't fail the entire tap for validation errors, just warn

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

    def set_discovery_mode(self, *, enabled: bool = True) -> None:
        """Set discovery mode flag."""
        self._is_discovery_mode = enabled

    @classmethod
    def invoke(cls, *args: str, **kwargs: dict[str, Any]) -> int:
        """Override invoke to detect discovery mode."""
        # Check if this is a discovery command
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

            for entity_name in discovered_entities:
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
                        "Discovered stream: %s with %s properties",
                        entity_name,
                        len(schema.get("properties", {})),
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

            # Process entities individually to avoid performance issues
            for entity_name in configured_entities:
                stream = self._create_stream_safe(entity_name)
                if stream:
                    streams.append(stream)

        return streams

    def _create_stream_safe(self, entity_name: str) -> WMSStream | None:
        """Create stream with proper error handling to avoid try-except in loop."""
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

                self.logger.info(
                    "Configured stream: %s with %s WMS properties",
                    entity_name,
                    len(schema.get("properties", {})),
                )
                return stream
        except Exception:
            # 🚨 CRITICAL: NO FALLBACK HARDCODED SCHEMAS ALLOWED - ABORT INSTEAD
            error_msg = f"❌ CRITICAL FAILURE: Schema generation failed for {entity_name} - ABORTING! NO fallback schemas allowed!"
            self.logger.error(error_msg)
            self.logger.exception("Schema generation failed - this is FATAL:")
            raise ValueError(error_msg)

    # 🚨 CRITICAL: _get_predefined_schema METHOD PERMANENTLY DELETED
    # NEVER, NEVER, NEVER use fallback hardcoded schemas - THIS IS FORBIDDEN
    # Schema MUST ALWAYS come from API metadata describe - NO EXCEPTIONS!

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

        self.logger.info("Discovered %s entities from WMS API", len(filtered_entities))
        return filtered_entities

    async def _generate_schema_async(self, entity_name: str) -> dict[str, Any] | None:
        """Generate schema for entity using ONLY API metadata - NEVER samples."""
        # Check cache first
        if entity_name in self._schema_cache:
            return self._schema_cache[entity_name]

        # 🚨 CRITICAL: Schema generation uses ONLY API metadata describe

        flattening_enabled = self.config.get("flattening_enabled", True)

        try:
            # 🎯 ALWAYS GET METADATA FIRST - This is fundamental and never optional
            metadata = await self.discovery.describe_entity(entity_name)

            if not metadata:
                error_msg = f"❌ CRITICAL FAILURE: Cannot get metadata for entity: {entity_name}. This is a fatal error - aborting!"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            # 🚀 METADATA-ONLY MODE: HARD-CODED BEHAVIOR
            self.logger.info(
                "🚀 METADATA-ONLY MODE (HARD-CODED): Using ONLY API metadata for entity: %s",
                entity_name,
            )

            # Generate schema from metadata ONLY - flattening support if enabled
            if flattening_enabled:
                schema = self.schema_generator.generate_metadata_schema_with_flattening(
                    metadata
                )
                self.logger.info(
                    "✅ Generated metadata schema with flattening for %s with %d total fields",
                    entity_name,
                    len(schema.get("properties", {})),
                )
            else:
                schema = self.schema_generator.generate_from_metadata(metadata)
                self.logger.info(
                    "✅ Generated basic metadata schema for %s with %d fields",
                    entity_name,
                    len(schema.get("properties", {})),
                )

            # Log schema field names for verification
            field_names = list(schema.get("properties", {}).keys())
            self.logger.info(
                "📋 Schema fields for %s: %s",
                entity_name,
                field_names[:10] + ["..."] if len(field_names) > 10 else field_names,
            )
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
        self,
        row: dict[str, Any],
        _context: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Post-process a record after extraction.

        This can be used for:
        - Adding metadata fields
        - Data type conversions
        - Filtering
        """
        # Add extraction metadata
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

    def _raise_schema_error(self, error_msg: str) -> None:
        """Raise schema generation errors."""
        raise ValueError(error_msg)


if __name__ == "__main__":
    # Allow direct execution for testing
    TapOracleWMS.cli()

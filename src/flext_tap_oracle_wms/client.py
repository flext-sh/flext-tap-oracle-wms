"""Tap and plugin implementations for Oracle WMS extraction."""

from __future__ import annotations

import importlib.metadata
from collections.abc import Mapping, Sequence
from typing import ClassVar

from flext_core import FlextLogger, FlextResult, t
from flext_meltano import FlextMeltanoTap as Tap
from flext_oracle_wms import FlextOracleWmsClient, FlextOracleWmsSettings

from .exceptions import FlextTapOracleWmsSettingsurationError
from .models import m
from .settings import FlextTapOracleWmsSettings
from .streams import FlextTapOracleWmsStream

logger = FlextLogger(__name__)


class FlextTapOracleWms(Tap):
    """Singer-compatible tap implementation backed by flext_oracle_wms."""

    name = "flext-tap-oracle-wms"
    config_jsonschema: ClassVar[dict[str, t.GeneralValueType]] = {
        "type": "object",
        "properties": {
            "base_url": {"type": "string"},
            "username": {"type": "string"},
            "password": {"type": "string", "secret": True},
            "api_version": {"type": "string", "default": "v1"},
            "page_size": {"type": "integer", "default": 100},
            "verify_ssl": {"type": "boolean", "default": True},
        },
        "required": ["base_url", "username", "password"],
    }

    def __init__(
        self,
        config: Mapping[str, t.GeneralValueType]
        | FlextTapOracleWmsSettings
        | None = None,
        catalog: Mapping[str, t.GeneralValueType] | None = None,
        state: Mapping[str, t.GeneralValueType] | None = None,
        *,
        parse_env_config: bool = True,
        validate_config: bool = True,
    ) -> None:
        """Initialize the tap with validated FLEXT settings."""
        match config:
            case FlextTapOracleWmsSettings() as settings_model:
                settings = settings_model
            case Mapping() as config_mapping:
                settings = FlextTapOracleWmsSettings.model_validate(
                    dict(config_mapping),
                )
            case _:
                settings = FlextTapOracleWmsSettings.model_validate({})

        self._flext_config = settings
        self._wms_client: FlextOracleWmsClient | None = None

        super().__init__(
            config=settings.model_dump(exclude_unset=True),
            catalog=catalog,
            state=state,
            parse_env_config=parse_env_config,
            validate_config=validate_config,
        )

    @property
    def flext_config(self) -> FlextTapOracleWmsSettings:
        """Return validated tap settings."""
        return self._flext_config

    @property
    def wms_client(self) -> FlextOracleWmsClient:
        """Return a started WMS client instance."""
        if self._wms_client is None:
            wms_settings = FlextOracleWmsSettings(
                base_url=str(self.flext_config.base_url),
                username=self.flext_config.username,
                password=self.flext_config.password.get_secret_value(),
                api_version=self.flext_config.api_version,
                timeout=self.flext_config.timeout,
                retry_attempts=self.flext_config.max_retries,
                enable_ssl_verification=self.flext_config.verify_ssl,
            )
            client = FlextOracleWmsClient(config=wms_settings)
            start_result = client.start()
            if start_result.is_failure:
                msg = start_result.error or "Failed to start Oracle WMS client"
                raise FlextTapOracleWmsSettingsurationError(msg)
            self._wms_client = client
        return self._wms_client

    def discover_catalog(self) -> FlextResult[m.Meltano.SingerCatalog]:
        """Discover source entities and convert them into Singer catalog streams."""
        discovery_result = self.wms_client.discover_entities()
        if discovery_result.is_failure:
            return FlextResult[m.Meltano.SingerCatalog].fail(
                discovery_result.error or "Discovery failed",
            )

        entities: list[str] = []
        for entity in discovery_result.value:
            match entity:
                case str() | int() | float() | bool():
                    entities.append(str(entity))
                case _:
                    continue
        streams = [
            m.Meltano.SingerCatalogEntry(
                tap_stream_id=entity,
                stream=entity,
                schema=self._schema_for_entity(),
                metadata=[
                    m.Meltano.SingerCatalogMetadata(
                        breadcrumb=[],
                        metadata={
                            "inclusion": "available",
                            "forced-replication-method": "FULL_TABLE",
                            "table-key-properties": ["id"],
                        },
                    ),
                ],
            )
            for entity in entities
        ]
        return FlextResult[m.Meltano.SingerCatalog].ok(
            m.Meltano.SingerCatalog(streams=streams),
        )

    def discover_streams(self) -> Sequence[FlextTapOracleWmsStream]:
        """Build stream objects from the discovered catalog."""
        catalog_result = self.discover_catalog()
        if catalog_result.is_failure:
            logger.warning("Catalog discovery failed: %s", catalog_result.error)
            return []

        streams_raw = catalog_result.value.streams
        if not streams_raw:
            return []

        streams: list[FlextTapOracleWmsStream] = []
        for stream_raw in streams_raw:
            stream_name = stream_raw.stream
            stream_schema = stream_raw.schema_definition
            stream = FlextTapOracleWmsStream(
                tap=self,
                name=stream_name,
                schema=stream_schema,
            )
            streams.append(stream)
        return streams

    def execute(self, message: str | None = None) -> FlextResult[bool]:
        """Run a full tap sync when no custom message is provided."""
        if message:
            return FlextResult[bool].fail("Tap does not support message execution")
        self.sync_all()
        return FlextResult[bool].ok(True)

    def validate_configuration(self) -> FlextResult[Mapping[str, t.GeneralValueType]]:
        """Expose non-secret validated configuration fields."""
        return FlextResult[Mapping[str, t.GeneralValueType]].ok(
            {
                "base_url": str(self.flext_config.base_url),
                "api_version": self.flext_config.api_version,
                "page_size": self.flext_config.page_size,
            },
        )

    def get_implementation_name(self) -> str:
        """Return the human-readable implementation name."""
        return "FLEXT Oracle WMS Tap"

    def get_implementation_version(self) -> str:
        """Return installed package version or project fallback."""
        try:
            return importlib.metadata.version("flext-tap-oracle-wms")
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ):
            return "0.9.0"

    def get_implementation_metrics(
        self,
    ) -> FlextResult[Mapping[str, t.GeneralValueType]]:
        """Return basic runtime metrics for observability."""
        return FlextResult[Mapping[str, t.GeneralValueType]].ok(
            {
                "tap_name": self.name,
                "version": self.get_implementation_version(),
                "streams_available": len(self.discover_streams()),
            },
        )

    def __del__(self) -> None:
        """Attempt graceful WMS client shutdown during object cleanup."""
        if self._wms_client is not None:
            stop_result = self._wms_client.stop()
            if stop_result.is_failure:
                logger.debug("Failed to stop WMS client: %s", stop_result.error)

    @staticmethod
    def _schema_for_entity() -> Mapping[str, t.JsonValue]:
        """Return a default Singer JSON schema for discovered entities."""
        return {
            "type": "object",
            "properties": {
                "id": {"type": ["string", "null"]},
                "name": {"type": ["string", "null"]},
                "created_at": {"type": ["string", "null"], "format": "date-time"},
                "updated_at": {"type": ["string", "null"], "format": "date-time"},
            },
        }


class FlextTapOracleWmsPlugin:
    """Plugin wrapper exposing tap operations to the host runtime."""

    def __init__(self, config: Mapping[str, t.GeneralValueType]) -> None:
        """Initialize plugin state and hold tap configuration."""
        self._config = config
        self._tap: FlextTapOracleWms | None = None
        self._name = "flext-tap-oracle-wms"
        self._version = "0.9.0"

    @property
    def name(self) -> str:
        """Return plugin identifier."""
        return self._name

    @property
    def version(self) -> str:
        """Return plugin version."""
        return self._version

    def get_info(self) -> Mapping[str, t.GeneralValueType]:
        """Return plugin metadata for discovery and capabilities."""
        return {
            "name": self.name,
            "version": self.version,
            "description": "Oracle WMS Singer Tap Plugin",
            "capabilities": ["discover", "sync"],
        }

    def initialize(self, _context: t.GeneralValueType) -> FlextResult[bool]:
        """Instantiate the tap for subsequent operations."""
        self._tap = FlextTapOracleWms(config=self._config)
        return FlextResult[bool].ok(True)

    def shutdown(self) -> FlextResult[bool]:
        """Release tap resources held by this plugin."""
        self._tap = None
        return FlextResult[bool].ok(True)

    def execute(
        self,
        operation: str,
        _parameters: Mapping[str, t.GeneralValueType] | None = None,
    ) -> FlextResult[Mapping[str, t.GeneralValueType]]:
        """Execute supported plugin operations against the tap."""
        if self._tap is None:
            init_result = self.initialize(None)
            if init_result.is_failure:
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    init_result.error or "Tap initialization failed",
                )
        tap = self._tap
        if tap is None:
            return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                "Tap not initialized"
            )

        if operation == "discover":
            catalog_result = tap.discover_catalog()
            if catalog_result.is_failure:
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    catalog_result.error or "Discovery failed",
                )
            return FlextResult[Mapping[str, t.GeneralValueType]].ok(
                catalog_result.value.model_dump(mode="json"),
            )
        if operation == "sync":
            execute_result = tap.execute()
            if execute_result.is_failure:
                return FlextResult[Mapping[str, t.GeneralValueType]].fail(
                    execute_result.error or "Sync failed",
                )
            return FlextResult[Mapping[str, t.GeneralValueType]].ok({"success": True})

        return FlextResult[Mapping[str, t.GeneralValueType]].fail(
            f"Unsupported operation: {operation}",
        )

"""Tap and plugin implementations for Oracle WMS extraction."""

from __future__ import annotations

import importlib.metadata
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import ClassVar, TypedDict, override

from flext_core import FlextLogger, r
from flext_oracle_wms import (
    FlextOracleWmsClient,
    FlextOracleWmsSettings,
)
from singer_sdk.tap_base import Tap

from flext_tap_oracle_wms import c, m, t
from flext_tap_oracle_wms.exceptions import FlextTapOracleWmsConfigurationError
from flext_tap_oracle_wms.settings import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream

logger = FlextLogger(__name__)


class SingerMetadataEntry(TypedDict):
    """Singer catalog metadata entry."""

    breadcrumb: list[str]
    metadata: dict[str, t.ContainerValue]


class SingerStreamEntry(TypedDict):
    """Singer catalog stream entry."""

    tap_stream_id: str
    stream: str
    schema: dict[str, t.ContainerValue]
    metadata: list[SingerMetadataEntry]


class SingerCatalogDict(TypedDict):
    """Singer catalog dict with typed streams."""

    streams: list[SingerStreamEntry]


class FlextTapOracleWms(Tap):
    """Singer-compatible tap implementation backed by flext_oracle_wms."""

    name = "flext-tap-oracle-wms"
    config_jsonschema: ClassVar[dict[str, t.NormalizedValue]] = {
        "type": c.TapOracleWms.SCHEMA_TYPE_OBJECT,
        "properties": {
            "base_url": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING},
            "username": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING},
            "password": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING, "secret": True},
            "api_version": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING, "default": "v1"},
            "page_size": {"type": c.TapOracleWms.SCHEMA_TYPE_INTEGER, "default": 100},
            "verify_ssl": {"type": c.TapOracleWms.SCHEMA_TYPE_BOOLEAN, "default": True},
        },
        "required": list(c.TapOracleWms.REQUIRED_CONFIG_FIELDS),
    }

    _wms_client: FlextOracleWmsClient | None = None
    _discovery: t.ContainerValue | None = None
    _schema_generator: t.ContainerValue | None = None
    _discovery_mode: bool = False

    @override
    def __init__(
        self,
        config: t.ContainerMapping
        | Mapping[str, t.ContainerValue]
        | FlextTapOracleWmsSettings
        | None = None,
        catalog: t.ContainerMapping | None = None,
        state: t.ContainerMapping | None = None,
        parse_env_config: bool = False,
        validate_config: bool = True,
    ) -> None:
        """Initialize tap, accepting settings object or raw dict."""
        if isinstance(config, FlextTapOracleWmsSettings):
            raw_config: dict[str, t.ContainerValue] = dict(
                config.model_dump(mode="json").items()
            )
        else:
            raw_config = dict(config) if config else {}
        tap_init: t.ContainerValue = Tap.__init__
        tap_init(
            self,
            config=raw_config,
            catalog=catalog,
            state=state,
            parse_env_config=parse_env_config,
            validate_config=validate_config,
        )

    @property
    def catalog_dict(self) -> SingerCatalogDict:
        """Return typed Singer catalog as dict."""
        raw_untyped: Mapping[str, t.ContainerValue] = dict(super().catalog_dict)
        raw_streams_raw: Sequence[t.ContainerValue] = (
            raw_untyped.get("streams")
            if isinstance(raw_untyped.get("streams"), Sequence)
            and not isinstance(raw_untyped.get("streams"), (str, bytes))
            else []
        )
        streams: list[SingerStreamEntry] = [
            SingerStreamEntry(
                tap_stream_id=str(s.get("tap_stream_id", "")),
                stream=str(s.get("stream", "")),
                schema=(
                    s_schema
                    if isinstance(s_schema := s.get("schema", {}), dict)
                    else {}
                ),
                metadata=(
                    [e for e in s_meta if isinstance(e, dict)]
                    if isinstance(s_meta := s.get("metadata", []), list)
                    and not isinstance(s_meta, (str, bytes))
                    else []
                ),
            )
            for s in raw_streams_raw
            if isinstance(s, Mapping)
        ]
        return SingerCatalogDict(streams=streams)

    @property
    def flext_config(self) -> FlextTapOracleWmsSettings:
        """Return validated tap settings."""
        config_map = dict(self.config)
        try:
            return FlextTapOracleWmsSettings.model_validate(config_map)
        except (ValueError, TypeError, KeyError) as exc:
            msg = f"Invalid configuration: {exc}"
            raise FlextTapOracleWmsConfigurationError(msg) from exc

    @property
    def wms_client(self) -> FlextOracleWmsClient:
        """Return a started WMS client instance."""
        if self._wms_client is None:
            wms_settings = FlextOracleWmsSettings.testing_config().model_copy(
                update={
                    "base_url": str(self.flext_config.base_url),
                    "timeout": self.flext_config.timeout,
                },
            )
            client = FlextOracleWmsClient(config=wms_settings)
            start_result = client.start()
            if start_result.is_failure:
                msg = start_result.error or "Failed to start Oracle WMS client"
                raise FlextTapOracleWmsConfigurationError(msg)
            self._wms_client = client
        return self._wms_client

    @staticmethod
    def _schema_for_entity() -> t.FlatContainerMapping:
        """Return a default Singer JSON schema for discovered entities."""
        return {"type": c.TapOracleWms.SCHEMA_TYPE_OBJECT}

    def discover_catalog(self) -> r[m.Meltano.SingerCatalog]:
        """Discover source entities and convert them into Singer catalog streams."""
        discovery_result = self.wms_client.discover_entities()
        if discovery_result.is_failure:
            return r[m.Meltano.SingerCatalog].fail(
                discovery_result.error or "Discovery failed",
            )
        entities: t.StrSequence = list(discovery_result.value)
        streams = [
            m.Meltano.SingerCatalogEntry.model_validate({
                "tap_stream_id": entity,
                "stream": entity,
                "schema": dict(self._schema_for_entity()),
                "metadata": [
                    m.Meltano.SingerCatalogMetadata(
                        breadcrumb=[],
                        metadata={
                            "inclusion": "available",
                            "forced-replication-method": "FULL_TABLE",
                            "table-key-properties": ["id"],
                        },
                    ),
                ],
                "key_properties": ["id"],
                "replication_key": None,
                "replication_method": "FULL_TABLE",
                "is_view": None,
                "table_name": None,
                "database_name": None,
                "row_count": None,
            })
            for entity in entities
        ]
        return r[m.Meltano.SingerCatalog].ok(
            m.Meltano.SingerCatalog(type="CATALOG", streams=streams),
        )

    @override
    def discover_streams(self) -> Sequence[FlextTapOracleWmsStream]:
        """Build stream objects from the discovered catalog."""
        catalog_result = self.discover_catalog()
        if catalog_result.is_failure:
            logger.warning("Catalog discovery failed: %s", catalog_result.error or "")
            return []
        streams_raw = catalog_result.value.streams
        if not streams_raw:
            return []
        streams: Sequence[FlextTapOracleWmsStream] = [
            FlextTapOracleWmsStream(
                tap=self,
                name=stream_raw.stream,
                schema={
                    k: v
                    for k, v in stream_raw.schema_definition.items()
                    if not isinstance(v, Path)
                },
            )
            for stream_raw in streams_raw
        ]
        return streams

    def execute(self, message: str | None = None) -> r[bool]:
        """Run a full tap sync when no custom message is provided."""
        if message:
            return r[bool].fail("Tap does not support message execution")
        self.sync_all()
        return r[bool].ok(True)

    def get_implementation_metrics(self) -> r[t.ContainerValue]:
        """Return basic runtime metrics for observability."""
        return r[t.ContainerValue].ok({
            "tap_name": self.name,
            "version": self.get_implementation_version(),
            "streams_available": len(self.discover_streams()),
        })

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

    def validate_configuration(self) -> r[t.ContainerValue]:
        """Expose non-secret validated configuration fields."""
        return r[t.ContainerValue].ok({
            "base_url": str(self.flext_config.base_url),
            "api_version": self.flext_config.api_version,
            "page_size": self.flext_config.page_size,
        })

    def initialize(self) -> r[bool]:
        """Initialize the tap and validate connectivity."""
        try:
            _ = self.flext_config
            return r[bool].ok(True)
        except (
            ValueError,
            TypeError,
            KeyError,
            FlextTapOracleWmsConfigurationError,
        ) as exc:
            return r[bool].fail(str(exc))


class FlextTapOracleWmsPlugin:
    """Plugin wrapper exposing tap operations to the host runtime."""

    def __init__(self, config: Mapping[str, t.ContainerValue]) -> None:
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

    def execute(
        self,
        operation: str,
        _parameters: Mapping[str, t.ContainerValue] | None = None,
    ) -> r[t.ContainerValue]:
        """Execute supported plugin operations against the tap."""
        if self._tap is None:
            init_result = self.initialize(None)
            if init_result.is_failure:
                return r[t.ContainerValue].fail(
                    init_result.error or "Tap initialization failed",
                )
        tap = self._tap
        if tap is None:
            return r[t.ContainerValue].fail("Tap not initialized")
        if operation == "discover":
            catalog_result = tap.discover_catalog()
            if catalog_result.is_failure:
                return r[t.ContainerValue].fail(
                    catalog_result.error or "Discovery failed",
                )
            return r[t.ContainerValue].ok(catalog_result.value.model_dump(mode="json"))
        if operation == "sync":
            execute_result = tap.execute()
            if execute_result.is_failure:
                return r[t.ContainerValue].fail(execute_result.error or "Sync failed")
            return r[t.ContainerValue].ok({"success": True})
        return r[t.ContainerValue].fail(f"Unsupported operation: {operation}")

    def get_info(self) -> Mapping[str, t.ContainerValue]:
        """Return plugin metadata for discovery and capabilities."""
        return {
            "name": self.name,
            "version": self.version,
            "description": "Oracle WMS Singer Tap Plugin",
            "capabilities": ["discover", "sync"],
        }

    def initialize(self, _context: t.ContainerValue | None) -> r[bool]:
        """Instantiate the tap for subsequent operations."""
        self._tap = FlextTapOracleWms(config=dict(self._config))
        return r[bool].ok(True)

    def shutdown(self) -> r[bool]:
        """Release tap resources held by this plugin."""
        self._tap = None
        return r[bool].ok(True)

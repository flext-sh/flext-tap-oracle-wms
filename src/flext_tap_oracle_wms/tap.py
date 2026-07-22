"""Tap and plugin implementations for Oracle WMS extraction."""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence, Sequence
from pathlib import Path
from typing import ClassVar, override

from flext_oracle_wms import FlextOracleWmsSettings, FlextOracleWmsUtilities
from flext_tap_oracle_wms import FlextTapOracleWmsSettings, c, m, p, r, t, u
from flext_tap_oracle_wms.__version__ import __version__
from flext_tap_oracle_wms.errors import FlextTapOracleWmsConfigurationError
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream


class FlextTapOracleWms(m.Meltano.SingerTapBase):
    """Singer-compatible tap implementation backed by flext_oracle_wms."""

    name = "flext-tap-oracle-wms"
    config_jsonschema: ClassVar[t.JsonDict] = {
        "type": c.TapOracleWms.SCHEMA_TYPE_OBJECT,
        "properties": u.normalize_to_json_value({
            "base_url": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING},
            "username": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING},
            "password": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING, "secret": True},
            "api_version": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING, "default": "v1"},
            "page_size": {"type": c.TapOracleWms.SCHEMA_TYPE_INTEGER, "default": 100},
            "verify_ssl": {"type": c.TapOracleWms.SCHEMA_TYPE_BOOLEAN, "default": True},
        }),
        "required": u.normalize_to_json_value(
            list(c.TapOracleWms.REQUIRED_CONFIG_FIELDS)
        ),
    }

    _wms_client: FlextOracleWmsUtilities.OracleWms.Client | None = None
    _discovery: t.JsonValue | None = None
    _schema_generator: t.JsonValue | None = None
    _discovery_mode: bool = False

    @property
    def settings(self) -> t.JsonMapping:
        """Expose tap configuration through legacy settings contract."""
        # NOTE (multi-agent): mro-rn88 — read the Singer tap config (self.config), not an
        # undefined bare `config` (settings-fallout left a self-referential assignment).
        return t.json_dict_adapter().validate_python(self.config)

    @property
    def catalog_dict_typed(self) -> t.MutableJsonMapping:
        """A validated Singer catalog mapping with recursive contracts."""
        raw_catalog_dict: t.JsonMapping = getattr(super(), "catalog_dict", {})
        try:
            validated_catalog = t.CONTAINER_VALUE_MAP_ADAPTER.validate_python(
                raw_catalog_dict
            )
        except c.ValidationError as exc:
            msg = f"Invalid catalog_dict format: {exc}"
            raise FlextTapOracleWmsConfigurationError(msg) from exc
        return self._to_typed_catalog(
            u.TapOracleWms.MappingConversion.safe_str_dict(validated_catalog)
        )

    @staticmethod
    def _to_typed_catalog(raw: t.JsonMapping) -> t.MutableJsonMapping:
        """Convert a raw catalog mapping into a validated Singer catalog dict."""
        raw_streams = raw.get("streams")
        raw_streams_seq: t.JsonList = (
            raw_streams
            if isinstance(raw_streams, Sequence)
            and not isinstance(raw_streams, t.STR_BYTES_TYPES)
            else []
        )
        stream_entries: MutableSequence[m.Meltano.SingerCatalogEntry] = []
        for raw_stream in raw_streams_seq:
            if not isinstance(raw_stream, Mapping):
                continue
            s_dict: t.JsonMapping = u.TapOracleWms.MappingConversion.safe_str_mapping(
                raw_stream
            )
            metadata_raw: t.JsonValue = s_dict.get("metadata", [])
            metadata_entries: MutableSequence[m.Meltano.SingerCatalogMetadata] = []
            if isinstance(metadata_raw, Sequence) and not isinstance(
                metadata_raw, t.STR_BYTES_TYPES
            ):
                for raw_entry in metadata_raw:
                    if not isinstance(raw_entry, Mapping):
                        continue
                    entry_dict = u.TapOracleWms.MappingConversion.safe_str_mapping(
                        raw_entry
                    )
                    breadcrumb_raw: t.JsonValue = entry_dict.get("breadcrumb", [])
                    metadata_map_raw: t.JsonValue = entry_dict.get("metadata", {})
                    metadata_entries.append(
                        m.Meltano.SingerCatalogMetadata(
                            breadcrumb=[str(item) for item in breadcrumb_raw]
                            if isinstance(breadcrumb_raw, Sequence)
                            and not isinstance(breadcrumb_raw, t.STR_BYTES_TYPES)
                            else [],
                            metadata=u.TapOracleWms.MappingConversion.safe_str_dict(
                                metadata_map_raw
                            )
                            if isinstance(metadata_map_raw, Mapping)
                            else {},
                        )
                    )
            schema_raw: t.JsonValue = s_dict.get("schema", {})
            stream_name = str(s_dict.get("stream", ""))
            entry_result = u.Meltano.build_catalog_entry(
                stream_name=stream_name,
                schema=(
                    u.TapOracleWms.MappingConversion.safe_str_dict(schema_raw)
                    if isinstance(schema_raw, Mapping)
                    else {}
                ),
                key_properties=(),
            )
            if entry_result.failure:
                msg = (
                    entry_result.error
                    or f"Failed to build catalog entry for {stream_name}"
                )
                raise FlextTapOracleWmsConfigurationError(msg)
            stream_entries.append(
                entry_result.value.model_copy(
                    update={
                        "tap_stream_id": str(s_dict.get("tap_stream_id", "")),
                        "stream": stream_name,
                        "metadata": metadata_entries,
                    }
                )
            )
        catalog = m.Meltano.SingerCatalog(streams=stream_entries)
        dumped_catalog = catalog.model_dump(
            by_alias=True, exclude_none=True, mode="json"
        )
        return t.json_dict_adapter().validate_python(dumped_catalog)

    @property
    def flext_config(self) -> FlextTapOracleWmsSettings:
        """The validated tap settings."""
        # NOTE (multi-agent): mro-rn88 — the Singer config is FLAT (config_jsonschema
        # properties); the FLEXT settings model namespaces project fields under
        # TapOracleWms.*, so wrap the flat config before validating.
        config_map = dict(self.config)
        try:
            return FlextTapOracleWmsSettings.model_validate({
                "TapOracleWms": config_map
            })
        except c.Meltano.SINGER_SAFE_EXCEPTIONS as exc:
            msg = f"Invalid configuration: {exc}"
            raise FlextTapOracleWmsConfigurationError(msg) from exc

    @property
    def wms_client(self) -> FlextOracleWmsUtilities.OracleWms.Client:
        """A started WMS client instance."""
        if self._wms_client is None:
            password = self.flext_config.TapOracleWms.password
            # NOTE (multi-agent): mro-rn88 — both settings models namespace project fields;
            # read via TapOracleWms.* and build the upstream config under OracleWms.*.
            wms_settings = FlextOracleWmsSettings.model_validate({
                "OracleWms": {
                    "base_url": self.flext_config.TapOracleWms.base_url,
                    "username": self.flext_config.TapOracleWms.username,
                    "password": (
                        password.get_secret_value()
                        if isinstance(password, t.SecretStr)
                        else password
                    ),
                    "timeout": float(self.flext_config.TapOracleWms.timeout),
                    "retry_attempts": self.flext_config.TapOracleWms.max_retries,
                }
            })
            client = FlextOracleWmsUtilities.OracleWms.Client(settings=wms_settings)
            start_result = client.start()
            if start_result.failure:
                msg = start_result.error or "Failed to start Oracle WMS client"
                raise FlextTapOracleWmsConfigurationError(msg)
            self._wms_client = client
        return self._wms_client

    @staticmethod
    def _schema_for_entity() -> t.JsonMapping:
        """Return a default Singer JSON schema for discovered entities."""
        return {"type": c.TapOracleWms.SCHEMA_TYPE_OBJECT}

    def discovercatalog_typed(self) -> p.Result[m.Meltano.SingerCatalog]:
        """Discover source entities and convert them into Singer catalog streams."""
        discovery_result = self.wms_client.discover_entities()
        if discovery_result.failure:
            return r[m.Meltano.SingerCatalog].fail(
                discovery_result.error or "Discovery failed"
            )
        entities: t.StrSequence = list(discovery_result.value)
        streams: list[m.Meltano.SingerCatalogEntry] = []
        for entity in entities:
            entry_result = u.Meltano.build_catalog_entry(
                stream_name=entity,
                schema=dict(self._schema_for_entity()),
                key_properties=("id",),
            )
            if entry_result.failure:
                return r[m.Meltano.SingerCatalog].fail(
                    entry_result.error
                    or f"Failed to build Singer catalog entry for {entity}"
                )
            streams.append(
                entry_result.value.model_copy(
                    update={
                        "metadata": [
                            m.Meltano.SingerCatalogMetadata(
                                breadcrumb=[],
                                metadata={
                                    "inclusion": "available",
                                    "forced-replication-method": "FULL_TABLE",
                                    "table-key-properties": ["id"],
                                },
                            )
                        ]
                    }
                )
            )
        return r[m.Meltano.SingerCatalog].ok(
            m.Meltano.SingerCatalog(type="CATALOG", streams=streams)
        )

    @override
    def discover_streams(self) -> t.SequenceOf[FlextTapOracleWmsStream]:
        """Build stream objects from the discovered catalog."""
        catalog_result = self.discovercatalog_typed()
        if catalog_result.failure:
            msg = f"Catalog discovery failed: {catalog_result.error or 'unknown error'}"
            raise FlextTapOracleWmsConfigurationError(msg)
        streams_raw = catalog_result.value.streams
        if not streams_raw:
            return []
        return [
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

    def execute(self, message: str | None = None) -> p.Result[bool]:
        """Run a full tap sync when no custom message is provided."""
        if message:
            return r[bool].fail("Tap does not support message execution")
        self.sync_all()
        return r[bool].ok(True)

    def get_implementation_metrics(self) -> p.Result[t.JsonValue]:
        """Return the basic runtime metrics for observability."""
        return r[t.JsonValue].ok({
            "tap_name": self.name,
            "version": self.get_implementation_version(),
            "streams_available": len(self.discover_streams()),
        })

    def get_implementation_name(self) -> str:
        """Return the human-readable implementation name."""
        return "FLEXT Oracle WMS Tap"

    def get_implementation_version(self) -> str:
        """Return the installed package version."""
        return __version__

    def validate_configuration(self) -> p.Result[t.JsonValue]:
        """Expose non-secret validated configuration fields."""
        return r[t.JsonValue].ok({
            "base_url": self.flext_config.TapOracleWms.base_url,
            "api_version": self.flext_config.TapOracleWms.api_version,
            "page_size": self.flext_config.TapOracleWms.page_size,
        })

    def initialize(self) -> p.Result[bool]:
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

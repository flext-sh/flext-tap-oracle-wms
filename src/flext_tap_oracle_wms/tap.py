"""Tap and plugin implementations for Oracle WMS extraction.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_tap_oracle_wms/tap
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence, Sequence
from pathlib import Path
from typing import ClassVar, override

from flext_oracle_wms import FlextOracleWmsSettings, FlextOracleWmsUtilities

from flext_tap_oracle_wms import FlextTapOracleWmsSettings, c, e, m, p, r, t, u
from flext_tap_oracle_wms.__version__ import __version__
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStreams


class FlextTapOracleWms(m.Meltano.SingerTapBase):
    """Singer-compatible tap implementation backed by flext_oracle_wms."""

    name = "flext-tap-oracle-wms"
    config_jsonschema: ClassVar[t.JsonDict] = {
        "type": c.TapOracleWms.SCHEMA_TYPE_OBJECT,
        "properties": u.normalize_to_json_value({
            "base_url": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING},
            "username": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING},
            "password": {
                "type": c.TapOracleWms.SCHEMA_TYPE_STRING,
                "secret": c.TapOracleWms.SCHEMA_FIELD_IS_SECRET,
            },
            "api_version": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING, "default": "v1"},
            "page_size": {"type": c.TapOracleWms.SCHEMA_TYPE_INTEGER, "default": 100},
            "verify_ssl": {"type": c.TapOracleWms.SCHEMA_TYPE_BOOLEAN, "default": True},
        }),
        "required": u.normalize_to_json_value(
            list(c.TapOracleWms.REQUIRED_CONFIG_FIELDS),
        ),
    }

    _wms_client: FlextOracleWmsUtilities.OracleWms.Client | None = None
    _discovery: t.JsonValue | None = None
    _schema_generator: t.JsonValue | None = None
    _discovery_mode: bool = False

    @classmethod
    def from_settings(
        cls,
        settings: FlextTapOracleWmsSettings,
        *,
        catalog: m.Meltano.SingerCatalog | None = None,
    ) -> FlextTapOracleWms:
        """Build a tap from typed settings (and an optional typed catalog).

        This is the single boundary where the typed FLEXT models are lowered
        into the flat mapping the Singer SDK constructor requires; callers pass
        ``m.`` models only and never round-trip through raw dictionaries. When a
        catalog is supplied the SDK uses it instead of performing live
        discovery at construction.

        Returns:
            The resulting ``FlextTapOracleWms``.
        """
        catalog_arg = None if catalog is None else catalog.model_dump(mode="json")
        return cls(
            config=settings.TapOracleWms.model_dump(mode="json"),
            catalog=catalog_arg,
        )

    @property
    def settings(self) -> t.JsonMapping:
        """Expose tap configuration through legacy settings contract."""
        # NOTE (multi-agent): mro-rn88 — read the Singer tap config (self.config),
        # not an
        # undefined bare `config` (settings-fallout left a self-referential assignment).
        return t.json_dict_adapter().validate_python(self.config)

    @property
    def catalog_dict_typed(self) -> t.MutableJsonMapping:
        """A validated Singer catalog mapping with recursive contracts.

        Raises:
            e.ConfigurationError: If Invalid catalog_dict format.
        """
        raw_catalog_dict: t.JsonMapping = getattr(super(), "catalog_dict", {})
        try:
            validated_catalog = t.CONTAINER_VALUE_MAP_ADAPTER.validate_python(
                raw_catalog_dict,
            )
        except c.ValidationError as exc:
            msg = f"Invalid catalog_dict format: {exc}"
            raise e.ConfigurationError(msg) from exc
        return self._to_typed_catalog(
            t.json_dict_adapter().validate_python(validated_catalog),
        )

    @staticmethod
    def _streams_sequence(raw: t.JsonMapping) -> t.JsonList:
        """Normalize the raw ``streams`` value into a sequence of stream mappings.

        Returns:
            The resulting ``t.JsonList``.
        """
        raw_streams = raw.get("streams")
        return (
            raw_streams
            if isinstance(raw_streams, Sequence)
            and not isinstance(raw_streams, c.STR_BYTES_TYPES)
            else []
        )

    @staticmethod
    def _metadata_entries(
        s_dict: t.JsonMapping,
    ) -> MutableSequence[m.Meltano.SingerCatalogMetadata]:
        """Build the typed metadata entries declared by one raw stream mapping.

        Returns:
            The resulting ``MutableSequence[m.Meltano.SingerCatalogMetadata]``.
        """
        metadata_raw: t.JsonValue = s_dict.get("metadata", [])
        metadata_entries: MutableSequence[m.Meltano.SingerCatalogMetadata] = []
        if not (
            isinstance(metadata_raw, Sequence)
            and not isinstance(metadata_raw, c.STR_BYTES_TYPES)
        ):
            return metadata_entries
        for raw_entry in metadata_raw:
            if not isinstance(raw_entry, Mapping):
                continue
            metadata_entries.append(FlextTapOracleWms._metadata_entry(raw_entry))
        return metadata_entries

    @staticmethod
    def _metadata_entry(raw_entry: t.JsonMapping) -> m.Meltano.SingerCatalogMetadata:
        """Convert one raw metadata entry into its typed model.

        Returns:
            The resulting ``m.Meltano.SingerCatalogMetadata``.
        """
        entry_dict = t.json_mapping_adapter().validate_python(raw_entry)
        breadcrumb_raw: t.JsonValue = entry_dict.get("breadcrumb", [])
        metadata_map_raw: t.JsonValue = entry_dict.get("metadata", {})
        return m.Meltano.SingerCatalogMetadata(
            breadcrumb=(
                [str(item) for item in breadcrumb_raw]
                if isinstance(breadcrumb_raw, Sequence)
                and not isinstance(breadcrumb_raw, c.STR_BYTES_TYPES)
                else []
            ),
            metadata=(
                t.json_dict_adapter().validate_python(metadata_map_raw)
                if isinstance(metadata_map_raw, Mapping)
                else {}
            ),
        )

    @staticmethod
    def _catalog_entry(
        s_dict: t.JsonMapping,
        metadata_entries: MutableSequence[m.Meltano.SingerCatalogMetadata],
    ) -> m.Meltano.SingerCatalogEntry:
        """Build one typed catalog entry from a raw stream mapping.

        Returns:
            The resulting ``m.Meltano.SingerCatalogEntry``.

        Raises:
            e.ConfigurationError: If ``entry_result.failure``.
        """
        schema_raw: t.JsonValue = s_dict.get("schema", {})
        stream_name = str(s_dict.get("stream", ""))
        entry_result = u.Meltano.build_catalog_entry(
            stream_name=stream_name,
            schema=(
                t.json_dict_adapter().validate_python(schema_raw)
                if isinstance(schema_raw, Mapping)
                else {}
            ),
            key_properties=(),
        )
        if entry_result.failure:
            msg = (
                entry_result.error or f"Failed to build catalog entry for {stream_name}"
            )
            raise e.ConfigurationError(msg)
        entry_value: m.Meltano.SingerCatalogEntry = entry_result.value
        updated: m.Meltano.SingerCatalogEntry = entry_value.model_copy(
            update={
                "tap_stream_id": str(s_dict.get("tap_stream_id", "")),
                "stream": stream_name,
                "metadata": metadata_entries,
            },
        )
        return updated

    @staticmethod
    def _to_typed_catalog(raw: t.JsonMapping) -> t.MutableJsonMapping:
        """Convert a raw catalog mapping into a validated Singer catalog dict.

        Returns:
            The resulting ``t.MutableJsonMapping``.
        """
        stream_entries: list[m.Meltano.SingerCatalogEntry] = []
        for raw_stream in FlextTapOracleWms._streams_sequence(raw):
            if not isinstance(raw_stream, Mapping):
                continue
            s_dict: t.JsonMapping = t.json_mapping_adapter().validate_python(raw_stream)
            stream_entries.append(
                FlextTapOracleWms._catalog_entry(
                    s_dict=s_dict,
                    metadata_entries=FlextTapOracleWms._metadata_entries(s_dict),
                ),
            )
        catalog = m.Meltano.SingerCatalog(streams=stream_entries)
        dumped_catalog = catalog.model_dump(
            by_alias=True,
            exclude_none=True,
            mode="json",
        )
        return t.json_dict_adapter().validate_python(dumped_catalog)

    @property
    def flext_config(self) -> FlextTapOracleWmsSettings:
        """The validated tap settings.

        Raises:
            e.ConfigurationError: If Invalid configuration.
        """
        # NOTE (multi-agent): mro-rn88 — the Singer config is FLAT (config_jsonschema
        # properties); the FLEXT settings model namespaces project fields under
        # TapOracleWms.*, so wrap the flat config before validating.
        config_map = dict(self.config)
        try:
            return FlextTapOracleWmsSettings.model_validate({
                "TapOracleWms": config_map,
            })
        except c.Meltano.SINGER_SAFE_EXCEPTIONS as exc:
            msg = f"Invalid configuration: {exc}"
            raise e.ConfigurationError(msg) from exc

    @property
    def wms_client(self) -> FlextOracleWmsUtilities.OracleWms.Client:
        """A started WMS client instance.

        Raises:
            e.ConfigurationError: If ``start_result.failure``.
        """
        if self._wms_client is None:
            password: str | t.SecretStr = self.flext_config.TapOracleWms.password
            # NOTE (multi-agent): mro-rn88 — both settings models namespace project
            # fields;
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
                },
            })
            client = FlextOracleWmsUtilities.OracleWms.Client(settings=wms_settings)
            start_result = client.start()
            if start_result.failure:
                msg = start_result.error or "Failed to start Oracle WMS client"
                raise e.ConfigurationError(msg)
            self._wms_client = client
        return self._wms_client

    @staticmethod
    def _schema_for_entity() -> t.JsonMapping:
        """Return a default Singer JSON schema for discovered entities."""
        return {"type": c.TapOracleWms.SCHEMA_TYPE_OBJECT}

    def discovercatalog_typed(self) -> p.Result[m.Meltano.SingerCatalog]:
        """Discover source entities and convert them into Singer catalog streams.

        Returns:
            The resulting ``p.Result[m.Meltano.SingerCatalog]``.
        """
        discovery_result = self.wms_client.discover_entities()
        if discovery_result.failure:
            return r[m.Meltano.SingerCatalog].from_failure(discovery_result)
        entities: t.StrSequence = list(discovery_result.value)
        streams: list[m.Meltano.SingerCatalogEntry] = []
        for entity in entities:
            entry_result = u.Meltano.build_catalog_entry(
                stream_name=entity,
                schema=dict(self._schema_for_entity()),
                key_properties=("id",),
            )
            if entry_result.failure:
                return r[m.Meltano.SingerCatalog].from_failure(entry_result)
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
                            ),
                        ],
                    },
                ),
            )
        return r[m.Meltano.SingerCatalog].ok(
            m.Meltano.SingerCatalog(type="CATALOG", streams=streams),
        )

    @override
    def discover_streams(self) -> t.SequenceOf[FlextTapOracleWmsStreams.WmsStream]:
        """Build stream objects from the discovered catalog.

        Returns:
            The resulting ``t.SequenceOf[FlextTapOracleWmsStreams.WmsStream]``.

        Raises:
            e.ConfigurationError: If Catalog discovery failed.
        """
        catalog_result = self.discovercatalog_typed()
        if catalog_result.failure:
            msg = f"Catalog discovery failed: {catalog_result.error or 'unknown error'}"
            raise e.ConfigurationError(msg)
        streams_raw = catalog_result.value.streams
        streams: list[FlextTapOracleWmsStreams.WmsStream] = [
            FlextTapOracleWmsStreams.WmsStream(
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

    def execute(self, message: str | None = None) -> p.Result[bool]:
        """Run a full tap sync when no custom message is provided.

        Returns:
            The resulting ``p.Result[bool]``.
        """
        if message:
            return r[bool].fail("Tap does not support message execution")
        self.sync_all()
        return r[bool].ok(value=True)

    def compute_implementation_metrics(self) -> p.Result[t.JsonValue]:
        """Return the basic runtime metrics for observability."""
        return r[t.JsonValue].ok({
            "tap_name": self.name,
            "version": self.resolve_implementation_version(),
            "streams_available": len(self.discover_streams()),
        })

    @staticmethod
    def resolve_implementation_name() -> str:
        """Return the human-readable implementation name."""
        return "FLEXT Oracle WMS Tap"

    @staticmethod
    def resolve_implementation_version() -> str:
        """Return the installed package version."""
        return __version__

    def validate_configuration(self) -> p.Result[t.JsonValue]:
        """Expose non-secret validated configuration fields.

        Returns:
            The resulting ``p.Result[t.JsonValue]``.
        """
        return r[t.JsonValue].ok({
            "base_url": self.flext_config.TapOracleWms.base_url,
            "api_version": self.flext_config.TapOracleWms.api_version,
            "page_size": self.flext_config.TapOracleWms.page_size,
        })

    def initialize(self) -> p.Result[bool]:
        """Initialize the tap and validate connectivity.

        Returns:
            The resulting ``p.Result[bool]``.
        """
        try:
            _ = self.flext_config
            return r[bool].ok(value=True)
        except (
            ValueError,
            TypeError,
            KeyError,
            e.ConfigurationError,
        ) as exc:
            return r[bool].fail(str(exc), exception=exc)

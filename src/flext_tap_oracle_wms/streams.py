"""Oracle WMS Stream implementations for Singer protocol.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import ClassVar, override

from pydantic import BaseModel

from flext_core import r
from flext_meltano import (
    Stream as FlextMeltanoSingerStreamBase,
    Tap as FlextMeltanoSingerTapBase,
)
from flext_oracle_wms import FlextOracleWmsUtilitiesClient
from flext_tap_oracle_wms import FlextTapOracleWmsError, c, p, t, u

logger = u.fetch_logger(__name__)


class FlextTapOracleWmsStream(FlextMeltanoSingerStreamBase):
    """Dynamic stream for Oracle WMS entities.

    Uses flext-oracle-wms client for all data operations.
    This is a generic stream class that adapts to any Oracle WMS entity dynamically.
    """

    stream_primary_keys: ClassVar[t.StrSequence] = []
    stream_replication_key: str | None = None
    url_base: str = ""
    # Singer SDK attributes exposed for type narrowing in tests/consumers
    tap: FlextMeltanoSingerTapBase
    http_headers: t.MutableStrMapping
    authenticator: None = None

    @override
    def __init__(
        self,
        tap: FlextMeltanoSingerTapBase,
        name: str | None = None,
        schema: t.ContainerValueMapping | None = None,
        _path: str | None = None,
    ) -> None:
        """Initialize stream."""
        schema_dict: dict[str, t.ContainerValue] | None = (
            dict(schema) if schema is not None else None
        )
        FlextMeltanoSingerStreamBase.__init__(
            self,
            tap=tap,
            name=name or self.name,
            schema=schema_dict,
        )
        self._typed_schema: dict[str, t.ContainerValue] | None = schema_dict
        self._client: FlextOracleWmsUtilitiesClient.Client | None = None
        page_size = int(self.config.get("page_size", 100))
        self._page_size = (
            page_size
            if u.TapOracleWms.ConfigurationProcessing.validate_stream_page_size(
                page_size,
            )
            else 100
        )

    @property
    @override
    def schema(self) -> dict[str, t.ContainerValue]:
        """Get schema with proper type narrowing over Singer SDK's bare ``dict``."""
        if self._typed_schema is None:
            msg = f"The schema for stream '{self.name}' was not provided"
            raise ValueError(msg)
        return self._typed_schema

    @property
    def client(self) -> FlextOracleWmsUtilitiesClient.Client:
        """Get WMS client from tap."""
        if self._client is not None:
            return self._client
        tap_instance = self._tap
        if not isinstance(
            tap_instance,
            p.TapOracleWms.OracleWms.TapWithWmsClient,
        ):
            msg = "WMS client not available - tap must be FlextTapOracleWms"
            raise TypeError(msg)
        client = tap_instance.wms_client
        self._client = client
        return client

    @staticmethod
    def normalize_json_value(value: t.NormalizedValue) -> t.Scalar:
        """Normalize arbitrary values into Singer-compatible JSON values."""
        if isinstance(value, t.SCALAR_TYPES):
            return value
        if value is None:
            return ""
        conv = u.TapOracleWms.MappingConversion
        list_value = conv.as_list(
            value,
            normalizer=FlextTapOracleWmsStream.normalize_json_value,
            list_adapter=t.CONTAINER_VALUE_LIST_ADAPTER,
            error_cls=FlextTapOracleWmsError,
        )
        if list_value is not None:
            return str(list(list_value))
        map_value = conv.as_map(
            value,
            normalizer=FlextTapOracleWmsStream.normalize_json_value,
            map_adapter=t.CONTAINER_VALUE_MAP_ADAPTER,
            error_cls=FlextTapOracleWmsError,
        )
        if map_value is not None:
            return str(dict(map_value))
        if isinstance(value, BaseModel | Path):
            return str(value)
        return str(value)

    def get_primary_keys(self) -> t.StrSequence:
        """Get primary keys for this stream."""
        return list(self.stream_primary_keys)

    @override
    def get_records(
        self,
        context: t.ScalarMapping | None,
    ) -> Iterable[dict[str, t.Scalar]]:
        """Get records from Oracle WMS."""
        page = 1
        has_more = True
        while has_more:
            try:
                page_result = self._fetch_page_data(page, context)
                if page_result.failure:
                    logger.error(
                        "Failed to fetch page %s for %s: %s",
                        page,
                        self.name,
                        page_result.error or "",
                    )
                    break
                records, has_more = page_result.value
                yield from self._process_page_records(records, context)
                page += 1
                if not records:
                    break
            except c.Meltano.SINGER_SAFE_EXCEPTIONS as exc:
                msg = f"Error getting records for {self.name}: {exc}"
                logger.exception(msg)
                raise FlextTapOracleWmsError(msg) from exc

    def get_replication_key(self) -> str | None:
        """Get replication key for this stream."""
        return self.stream_replication_key

    @override
    def post_process(
        self,
        row: dict[str, t.Scalar],
        context: t.ScalarMapping | None = None,
    ) -> dict[str, t.Scalar]:
        """Post-process a record."""
        conv = u.TapOracleWms.MappingConversion
        config_map: t.ContainerMapping = self.config
        column_mappings_raw = config_map.get("column_mappings")
        column_mappings = (
            conv.as_map(
                column_mappings_raw,
                map_adapter=t.CONTAINER_VALUE_MAP_ADAPTER,
                error_cls=FlextTapOracleWmsError,
            )
            if column_mappings_raw
            else None
        )
        if column_mappings is not None:
            mapping_raw = column_mappings.get(self.name)
            mapping = (
                conv.as_map(
                    mapping_raw,
                    map_adapter=t.CONTAINER_VALUE_MAP_ADAPTER,
                    error_cls=FlextTapOracleWmsError,
                )
                if mapping_raw is not None
                else None
            )
            if mapping is not None:
                for old_name, new_name in mapping.items():
                    new_name_str = str(new_name)
                    if old_name in row:
                        row[new_name_str] = row.pop(old_name)
        ignored_columns_raw = config_map.get("ignored_columns")
        ignored_columns = (
            conv.as_list(
                ignored_columns_raw,
                list_adapter=t.CONTAINER_VALUE_LIST_ADAPTER,
                error_cls=FlextTapOracleWmsError,
            )
            if ignored_columns_raw
            else None
        )
        if ignored_columns is not None:
            for column_name in ignored_columns:
                if isinstance(column_name, str):
                    row.pop(column_name, None)
        if context:
            row["_context"] = str({k: str(v) for k, v in context.items()})
        return row

    def _build_operation_kwargs(
        self,
        page: int,
        context: t.ScalarMapping | None,
    ) -> t.MutableScalarMapping:
        """Build kwargs for the operation call."""
        result_kwargs: t.MutableScalarMapping = {}
        result_kwargs["page"] = page
        result_kwargs["limit"] = self._page_size
        if self.stream_replication_key:
            starting_timestamp = self.get_starting_timestamp(context)
            if starting_timestamp:
                kwargs_filter = (
                    f"{self.stream_replication_key}>={starting_timestamp.isoformat()}"
                )
                result_kwargs["filter"] = kwargs_filter
        return result_kwargs

    def _fetch_page_data(
        self,
        page: int,
        context: t.ScalarMapping | None,
    ) -> r[tuple[Sequence[t.ScalarMapping], bool]]:
        """Fetch data for a specific page."""
        kwargs = self._build_operation_kwargs(page, context)
        limit_raw = kwargs.get("limit")
        limit = u.to_int(limit_raw, default=self._page_size)
        filters: t.MutableScalarMapping = {}
        filter_raw = kwargs.get("filter")
        if isinstance(filter_raw, str) and self.stream_replication_key:
            filters[self.stream_replication_key] = filter_raw
        result = self.client.get_entity_data(
            entity_name=self.name,
            limit=limit,
            filters=filters or None,
        )
        if result.failure:
            return r[tuple[Sequence[t.ScalarMapping], bool]].fail(
                f"Failed to get records for {self.name}: {result.error}",
            )
        normalized: Sequence[t.ScalarMapping] = [
            {
                str(key): self.normalize_json_value(value)
                for key, value in record.items()
            }
            for record in result.value
        ]
        has_more = len(normalized) == self._page_size
        return r[tuple[Sequence[t.ScalarMapping], bool]].ok((
            normalized,
            has_more,
        ))

    def _process_page_records(
        self,
        records: Sequence[t.ScalarMapping],
        context: t.ScalarMapping | None,
    ) -> Iterable[dict[str, t.Scalar]]:
        """Process and yield records from a page."""
        conv = u.TapOracleWms.MappingConversion
        for record in records:
            record_dict: t.ContainerValueMapping = dict(record)
            processed_record: t.ContainerValueMapping = (
                u.TapOracleWms.DataProcessing.process_wms_record(
                    record=record_dict,
                )
            )
            processed_map = conv.as_map(
                processed_record,
                normalizer=self.normalize_json_value,
                map_adapter=t.CONTAINER_VALUE_MAP_ADAPTER,
                error_cls=FlextTapOracleWmsError,
            )
            if processed_map is None:
                continue
            json_row: dict[str, t.Scalar] = {
                str(k): self.normalize_json_value(v) for k, v in processed_map.items()
            }
            yield self.post_process(json_row, context)

    def _run(self, value: t.Scalar) -> t.Scalar:
        return value

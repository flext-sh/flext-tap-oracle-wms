"""Shared tap-oracle-wms test helpers extracted from e2e/integration tests.

Provides the ``TestsFlextTapOracleWmsHelpers`` that centralises the
catalog-discovery and error-recovery patterns previously duplicated across
``test_e2e.py``, ``test_functional.py``, ``test_streams_functional.py``,
and ``test_wms.py``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import islice
from typing import ClassVar

import pytest

from flext_tap_oracle_wms import (
    FlextTapOracleWms,
    FlextTapOracleWmsSettings,
    FlextTapOracleWmsStreams,
)
from tests import c, p, t, tm, u


class TestsFlextTapOracleWmsHelpers:
    """Shared helpers for Oracle WMS tap integration/e2e tests.

    Centralises the ``_catalog`` / ``_schema`` discovery helpers, the
    recoverable-exception tuple, and connection-error validation so that
    sibling test classes stay thin.
    """

    _TAP_RECOVERABLE_EXCEPTIONS: ClassVar[tuple[type[Exception], ...]] = (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        OSError,
        RuntimeError,
        ImportError,
    )

    _TAP_CONNECTION_ERROR_KEYWORDS: ClassVar[tuple[str, ...]] = (
        "authentication",
        "authorization",
        "credentials",
        "unauthorized",
        "forbidden",
    )

    _TAP_BASE_SETTINGS: ClassVar[t.JsonMapping] = {
        "base_url": "https://wms.example.com",
        "username": "user",
        "password": c.TapOracleWms.Tests.CREDENTIAL,
    }

    @staticmethod
    def _catalog(tap: FlextTapOracleWms) -> p.Meltano.SingerCatalog:
        """Return the typed discovered catalog used by runtime code."""
        result = tap.discovercatalog_typed()
        tm.ok(result)
        catalog: p.Meltano.SingerCatalog = result.unwrap()
        return catalog

    @staticmethod
    def _schema(stream: p.Meltano.SingerCatalogEntry) -> t.JsonMapping:
        """Normalize model schema payload to the runtime stream contract.

        Returns:
            The resulting ``t.JsonMapping``.

        """
        schema: t.JsonMapping = u.json_mapping_adapter().validate_python(
            stream.schema_definition,
        )
        return schema

    def _assert_connection_error(self, error: Exception) -> None:
        """Fail when *error* lacks a meaningful keyword from the class set."""
        error_msg = str(error).lower()
        if not any(kw in error_msg for kw in self._TAP_CONNECTION_ERROR_KEYWORDS):
            pytest.fail(f"Unexpected error: {error}")

    def _stream(
        self,
        tap: FlextTapOracleWms,
        entry: p.Meltano.SingerCatalogEntry,
    ) -> FlextTapOracleWmsStreams.WmsStream:
        """Build the runtime stream for one discovered catalog entry.

        Returns:
            The resulting ``FlextTapOracleWmsStreams.WmsStream``.

        """
        return FlextTapOracleWmsStreams.WmsStream(
            tap=tap,
            name=entry.tap_stream_id,
            schema=self._schema(entry),
        )

    def _first_stream(
        self, tap: FlextTapOracleWms
    ) -> FlextTapOracleWmsStreams.WmsStream:
        """Return the first discovered stream, skipping when none exist."""
        streams = self._catalog(tap).streams
        if not streams:
            u.Tests.skip("No streams discovered")
        return self._stream(tap, streams[0])

    @staticmethod
    def _table_metadata(entry: p.Meltano.SingerCatalogEntry) -> t.JsonMapping:
        """Return the stream-level metadata of *entry* (empty when undeclared)."""
        return next(
            (meta.metadata for meta in entry.metadata if meta.breadcrumb == ()),
            {},
        )

    def _incremental_filter(self, tap: FlextTapOracleWms, start: str) -> str:
        """Return the filter the first incremental stream builds from *start*."""
        streams = (self._stream(tap, entry) for entry in self._catalog(tap).streams)
        stream = next(
            (
                candidate
                for candidate in streams
                if candidate.replication_method == "INCREMENTAL"
                and candidate.replication_key
            ),
            None,
        )
        if stream is None:
            u.Tests.skip("No incremental streams found")
        params = stream.build_operation_kwargs(
            page=1,
            context={"replication_key_value": start},
        )
        filter_text = str(params.get("filter") or "")
        tm.that(
            ">=" in filter_text or ">" in filter_text,
            msg=f"No timestamp filter in incremental params: {list(params)}",
        )
        return filter_text

    @staticmethod
    def _named_stream(
        tap: FlextTapOracleWms,
        name: str,
    ) -> FlextTapOracleWmsStreams.WmsStream:
        """Return the discovered stream called *name*, skipping when absent."""
        stream = next(
            (item for item in tap.discover_streams() if item.name == name),
            None,
        )
        if stream is None:
            u.Tests.skip(f"Stream {name} not available")
        return stream

    @staticmethod
    def _sample_records(
        stream: FlextTapOracleWmsStreams.WmsStream,
        count: int,
    ) -> Sequence[t.JsonMapping]:
        """Extract at most *count* records from *stream*.

        Returns:
            The resulting ``Sequence[t.JsonMapping]``.

        """
        return list(islice(stream.get_records(context=None), count))

    def _assert_invalid_tap_recovery(
        self,
        real_config: FlextTapOracleWmsSettings,
        overrides: t.JsonDict,
    ) -> None:
        """Attempt catalog discovery with invalid settings; assert error."""
        invalid_settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {**real_config.TapOracleWms.model_dump(), **overrides},
        })
        tap = FlextTapOracleWms.from_settings(invalid_settings)
        try:
            catalog = self._catalog(tap)
            tm.that(catalog.streams, none=False)
        except self._TAP_RECOVERABLE_EXCEPTIONS as e:
            self._assert_connection_error(e)

    @classmethod
    def _tap_settings(
        cls,
        overrides: t.JsonDict | None = None,
    ) -> FlextTapOracleWmsSettings:
        """Build validated settings from common defaults plus *overrides*.

        Returns:
            The resulting ``FlextTapOracleWmsSettings``.

        """
        fields: t.JsonDict = dict(cls._TAP_BASE_SETTINGS)
        if overrides:
            fields.update(overrides)
        return FlextTapOracleWmsSettings.model_validate({"TapOracleWms": fields})

    @staticmethod
    def _password_value(settings: FlextTapOracleWmsSettings) -> str:
        """Extract the plaintext password from settings (handles SecretStr).

        Returns:
            The resulting ``str``.

        """
        password: str | t.SecretStr = settings.TapOracleWms.password
        return (
            password.get_secret_value()
            if isinstance(password, t.SecretStr)
            else password
        )


__all__ = ["TestsFlextTapOracleWmsHelpers"]

"""Shared tap-oracle-wms test helpers extracted from e2e/integration tests.

Provides the ``OracleWmsTapTestHelpersMixin`` that centralises the
catalog-discovery and error-recovery patterns previously duplicated across
``test_e2e.py``, ``test_functional.py``, ``test_streams_functional.py``,
and ``test_wms.py``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import pytest
from flext_tests import tm

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from tests import t

if TYPE_CHECKING:
    from tests import m


class OracleWmsTapTestHelpersMixin:
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
        "password": "pass",
    }

    @staticmethod
    def _catalog(tap: FlextTapOracleWms) -> m.Meltano.SingerCatalog:
        """Return the typed discovered catalog used by runtime code."""
        result = tap.discovercatalog_typed()
        tm.ok(result)
        catalog: m.Meltano.SingerCatalog = result.unwrap()
        return catalog

    @staticmethod
    def _schema(stream: m.Meltano.SingerCatalogEntry) -> t.JsonMapping:
        """Normalize model schema payload to the runtime stream contract."""
        schema: t.JsonMapping = t.CONTAINER_VALUE_MAP_ADAPTER.validate_python(
            stream.schema_definition
        )
        return schema

    def _assert_connection_error(self, error: Exception) -> None:
        """Fail when *error* lacks a meaningful keyword from the class set."""
        error_msg = str(error).lower()
        if not any(kw in error_msg for kw in self._TAP_CONNECTION_ERROR_KEYWORDS):
            pytest.fail(f"Unexpected error: {error}")

    def _first_stream(
        self, tap: FlextTapOracleWms
    ) -> FlextTapOracleWmsStream:
        """Return the first discovered stream, skipping when none exist."""
        catalog = self._catalog(tap)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams discovered")
        stream_config = streams[0]
        return FlextTapOracleWmsStream(
            tap=tap,
            name=stream_config.tap_stream_id,
            schema=self._schema(stream_config),
        )

    def _assert_invalid_tap_recovery(
        self, real_config: FlextTapOracleWmsSettings, overrides: t.JsonDict
    ) -> None:
        """Attempt catalog discovery with invalid settings; assert error."""
        invalid_settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                **real_config.TapOracleWms.model_dump(),
                **overrides,
            }
        })
        tap = FlextTapOracleWms.from_settings(invalid_settings)
        try:
            catalog = self._catalog(tap)
            tm.that(catalog.streams, none=False)
        except self._TAP_RECOVERABLE_EXCEPTIONS as e:
            self._assert_connection_error(e)

    @classmethod
    def _tap_settings(
        cls, overrides: t.JsonDict | None = None
    ) -> FlextTapOracleWmsSettings:
        """Build validated settings from common defaults plus *overrides*."""
        fields: dict[str, t.JsonValue] = dict(cls._TAP_BASE_SETTINGS)
        if overrides:
            fields.update(overrides)
        return FlextTapOracleWmsSettings.model_validate({"TapOracleWms": fields})

    @staticmethod
    def _password_value(settings: FlextTapOracleWmsSettings) -> str:
        """Extract the plaintext password from settings (handles SecretStr)."""
        password = settings.TapOracleWms.password
        return password.get_secret_value() if isinstance(password, t.SecretStr) else password

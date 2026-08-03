"""Unit tests for the Oracle WMS tap implementation.

The tap's stream discovery, catalog discovery and sync reach a live Oracle
WMS Cloud endpoint (the Singer SDK calls ``discover_streams`` during
construction). There is no local container or self-contained service, so per
the no-mock law those service-dependent paths are covered by real end-to-end
runs against a provisioned WMS environment rather than by substituting the WMS
client. The tests here construct the tap from a real ``catalog`` input — the
canonical Singer way to build a tap without discovery — and assert only the
genuinely local contract (settings normalization, unsupported-message
handling, redacted validation output, and implementation metadata).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from flext_tests import tm

if TYPE_CHECKING:
    from flext_tap_oracle_wms import m


class TestsFlextTapOracleWmsTap:
    """Validate tap behavior against current implementation contract."""

    def test_tap_initialization_with_config(
        self,
        sample_config: FlextTapOracleWmsSettings,
        sample_catalog: m.Meltano.SingerCatalog,
    ) -> None:
        """Tap stores validated settings and builds from a typed catalog."""
        tap = FlextTapOracleWms.from_settings(sample_config, catalog=sample_catalog)
        tm.that(tap.name, eq="flext-tap-oracle-wms")

    def test_tap_initialization_normalizes_settings(
        self, sample_catalog: m.Meltano.SingerCatalog
    ) -> None:
        """Tap normalizes settings values from a typed settings model."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                "base_url": "https://test.wms.example.com",
                "username": "test_user",
                "password": "test_password",
            }
        })
        tap = FlextTapOracleWms.from_settings(settings, catalog=sample_catalog)
        tm.that(tap.flext_config.TapOracleWms.base_url, has="test.wms.example.com")
        tm.that(tap.flext_config.TapOracleWms.username, eq="test_user")

    def test_execute_with_message_unsupported(
        self, tap_instance: FlextTapOracleWms
    ) -> None:
        """Custom message execution is not supported by the tap."""
        result = tap_instance.execute("some message")
        tm.fail(result)
        tm.that(str(result.error), has="Tap does not support message execution")

    def test_validate_configuration(self, tap_instance: FlextTapOracleWms) -> None:
        """Validation method exposes non-secret effective settings values."""
        result = tap_instance.validate_configuration()
        tm.ok(result)
        value = result.value
        assert isinstance(value, dict)
        tm.that(value["base_url"], eq=tap_instance.flext_config.TapOracleWms.base_url)
        tm.that(value, lacks="password")

    def test_get_implementation_name_and_version(
        self, tap_instance: FlextTapOracleWms
    ) -> None:
        """Implementation metadata methods return stable, non-empty values."""
        tm.that(tap_instance.get_implementation_name(), eq="FLEXT Oracle WMS Tap")
        tm.that(tap_instance.get_implementation_version(), ne="")

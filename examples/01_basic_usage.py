"""Basic usage example for FLEXT Tap Oracle WMS.

Shows how to use the tap with flext-oracle-wms integration.
"""

from __future__ import annotations

import os

from flext_tap_oracle_wms import FlextTapOracleWmsError, FlextTapOracleWmsSettings
from flext_tap_oracle_wms.tap import FlextTapOracleWms


def main() -> int:
    """Run basic example.

    Returns:
      int: Description.

    """
    settings = FlextTapOracleWmsSettings(
        TapOracleWms={
            "base_url": os.getenv(
                "ORACLE_WMS_BASE_URL",
                "https://invalid.wms.ocs.oraclecloud.com/company_unknow",
            ),
            "username": os.getenv("ORACLE_WMS_USERNAME", "user"),
            "password": os.getenv("ORACLE_WMS_PASSWORD", "your_password"),
            "api_version": "v10",
            "page_size": 100,
            "verify_ssl": True,
            "include_entities": ["inventory", "locations", "orders"],
            "enable_request_logging": True,
        }
    )
    # NOTE (multi-agent): mro-u3eu — singer_sdk.Tap.__init__ takes the FLAT
    # Singer config via `config=`; pass the namespaced settings payload.
    tap = FlextTapOracleWms(config=settings.TapOracleWms.model_dump(mode="json"))
    validation_result = tap.validate_configuration()
    if validation_result.failure:
        raise FlextTapOracleWmsError(
            validation_result.error or "configuration validation failed"
        )
    catalog_result = tap.discovercatalog_typed()
    if catalog_result.failure:
        raise FlextTapOracleWmsError(catalog_result.error or "catalog discovery failed")
    catalog = catalog_result.value
    for stream_entry in catalog.streams:
        _ = stream_entry.schema_definition
    tap.get_implementation_metrics()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

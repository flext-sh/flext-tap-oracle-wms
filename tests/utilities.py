"""Utilities for flext-tap-oracle-wms tests - uses composition with FlextTestsUtilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextTypes as t
from flext_tests import FlextTestsUtilities


class TestsFlextMeltanoTapOracleWmsUtilities(FlextTestsUtilities):
    """Utilities for flext-tap-oracle-wms tests - uses composition with FlextTestsUtilities.

    Architecture: Uses composition (not inheritance) with FlextTestsUtilities and FlextMeltanoTapOracleWmsUtilities
    for flext-tap-oracle-wms-specific utility definitions.

    Access patterns:
    - TestsFlextMeltanoTapOracleWmsUtilities.Tests.* = flext_tests test utilities (via composition)
    - TestsFlextMeltanoTapOracleWmsUtilities.TapOracleWms.* = flext-tap-oracle-wms-specific test utilities
    - TestsFlextMeltanoTapOracleWmsUtilities.* = FlextTestsUtilities methods (via composition)

    Rules:
    - Use composition, not inheritance (FlextTestsUtilities deprecates subclassing)
    - flext-tap-oracle-wms-specific utilities go in TapOracleWms namespace
    - Generic utilities accessed via Tests namespace
    """

    # Composition: expose FlextTestsUtilities namespaces
    Tests = FlextTestsUtilities.Tests

    # TapOracleWms-specific test utilities namespace
    class TapOracleWms:
        """Tap Oracle WMS test utilities - domain-specific for Oracle WMS tap testing.

        Contains test utilities specific to Oracle WMS tap functionality including:
        - Oracle WMS connection test helpers
        - Oracle WMS API test helpers
        - Oracle WMS data generation helpers
        """

        @staticmethod
        def create_test_oracle_wms_config(
            base_url: str = "https://test-wms.oraclecloud.com",
            username: str = "test_user",
            password: str = "test_pass",
            facility_ids: list[str] | None = None,
            **kwargs: t.GeneralValueType,
        ) -> dict[str, t.GeneralValueType]:
            """Create test Oracle WMS configuration."""
            config = {
                "base_url": base_url,
                "username": username,
                "password": password,
            }
            if facility_ids:
                config["facility_ids"] = facility_ids
            config.update(kwargs)
            return config

        @staticmethod
        def create_test_oracle_wms_api_response(
            data: list[dict[str, t.GeneralValueType]],
            *,
            has_more: bool = False,
            next_page_url: str | None = None,
            facility_id: str | None = None,
            **kwargs: t.GeneralValueType,
        ) -> dict[str, t.GeneralValueType]:
            """Create test Oracle WMS API response."""
            response = {
                "items": data,
                "hasMore": has_more,
            }
            if next_page_url:
                response["nextPageUrl"] = next_page_url
            if facility_id:
                response["facilityId"] = facility_id
            response.update(kwargs)
            return response

        @staticmethod
        def generate_mock_oracle_wms_records(
            count: int = 5,
            base_id: int = 1000,
            facility_id: str = "FAC001",
            **kwargs: t.GeneralValueType,
        ) -> list[dict[str, t.GeneralValueType]]:
            """Generate mock Oracle WMS records for testing."""
            records = []
            for i in range(count):
                record = {
                    "id": base_id + i,
                    "facilityId": facility_id,
                    "itemNumber": f"ITEM{i + 1:04d}",
                    "description": f"Test Item {i + 1}",
                    "createdDate": "2023-01-01T00:00:00Z",
                    "modifiedDate": "2023-01-01T00:00:00Z",
                }
                # Add custom fields
                record.update(dict(kwargs.items()))
                records.append(record)
            return records

        @staticmethod
        def validate_oracle_wms_config(config: dict[str, t.GeneralValueType]) -> bool:
            """Validate Oracle WMS configuration for testing."""
            required_fields = ["base_url", "username"]
            return all(field in config and config[field] for field in required_fields)


# Alias for simplified usage
tu = TestsFlextMeltanoTapOracleWmsUtilities

__all__ = [
    "TestsFlextMeltanoTapOracleWmsUtilities",
    "tu",
]

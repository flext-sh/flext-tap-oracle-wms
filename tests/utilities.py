"""Utilities for flext-tap-oracle-wms tests - uses composition with TestsFlextUtilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence, Sequence

from flext_tests import FlextTestsUtilities

from flext_tap_oracle_wms import FlextTapOracleWmsUtilities
from tests import t


class TestsFlextTapOracleWmsUtilities(FlextTestsUtilities, FlextTapOracleWmsUtilities):
    """Utilities for flext-tap-oracle-wms tests - uses composition with TestsFlextUtilities.

    Architecture: Uses composition (not inheritance) with TestsFlextUtilities and FlextTapOracleWmsUtilities
    for flext-tap-oracle-wms-specific utility definitions.

    Access patterns:
    - TestsFlextTapOracleWmsUtilities.Tests.* = flext_tests test utilities (via composition)
    - TestsFlextTapOracleWmsUtilities.TapOracleWms.* = flext-tap-oracle-wms-specific test utilities
    - TestsFlextTapOracleWmsUtilities.* = TestsFlextUtilities methods (via composition)

    Rules:
    - Use composition, not inheritance (TestsFlextUtilities deprecates subclassing)
    - flext-tap-oracle-wms-specific utilities go in TapOracleWms namespace
    - Generic utilities accessed via Tests namespace
    """

    class TapOracleWms(FlextTapOracleWmsUtilities.TapOracleWms):
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
            facility_ids: t.StrSequence | None = None,
            **kwargs: t.Scalar,
        ) -> t.MutableRecursiveContainerMapping:
            """Create test Oracle WMS configuration."""
            settings: t.MutableRecursiveContainerMapping = {
                "base_url": base_url,
                "username": username,
                "password": password,
            }
            if facility_ids:
                settings["facility_ids"] = facility_ids
            settings.update(kwargs)
            return settings

        @staticmethod
        def create_test_oracle_wms_api_response(
            data: Sequence[Mapping[str, t.Container]],
            *,
            has_more: bool = False,
            next_page_url: str | None = None,
            facility_id: str | None = None,
            **kwargs: t.Scalar,
        ) -> t.MutableRecursiveContainerMapping:
            """Create test Oracle WMS API response."""
            response: t.MutableRecursiveContainerMapping = {
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
            **kwargs: t.Scalar,
        ) -> MutableSequence[t.MutableRecursiveContainerMapping]:
            """Generate mock Oracle WMS records for testing."""
            records: MutableSequence[t.MutableRecursiveContainerMapping] = []
            for i in range(count):
                record: t.MutableRecursiveContainerMapping = {
                    "id": base_id + i,
                    "facilityId": facility_id,
                    "itemNumber": f"ITEM{i + 1:04d}",
                    "description": f"Test Item {i + 1}",
                    "createdDate": "2023-01-01T00:00:00Z",
                    "modifiedDate": "2023-01-01T00:00:00Z",
                }
                record.update(kwargs)
                records.append(record)
            return records

        @staticmethod
        def validate_oracle_wms_config(
            settings: t.MutableRecursiveContainerMapping,
        ) -> bool:
            """Validate Oracle WMS configuration for testing."""
            required_fields = ["base_url", "username"]
            return all(
                field in settings and settings[field] for field in required_fields
            )


u = TestsFlextTapOracleWmsUtilities
__all__: list[str] = ["TestsFlextTapOracleWmsUtilities", "u"]

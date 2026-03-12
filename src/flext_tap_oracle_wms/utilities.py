"""FLEXT Tap Oracle WMS Utilities - Domain-specific utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import t
from flext_meltano import FlextMeltanoUtilities


class FlextTapOracleWmsUtilities(FlextMeltanoUtilities):
    """Domain-specific Oracle WMS tap utilities.

    Inherits from FlextMeltanoUtilities to avoid duplication.
    """

    class ConfigurationProcessing:
        """Configuration processing utilities for Oracle WMS."""

        @staticmethod
        def validate_stream_page_size(page_size: int) -> bool:
            """Validate stream page size.

            Args:
                page_size: Page size to validate.

            Returns:
                True if valid, False otherwise.

            """
            return page_size > 0

    class DataProcessing:
        """Data processing utilities for Oracle WMS records."""

        @staticmethod
        def process_wms_record(
            record: object,
        ) -> object:
            """Process WMS record for output.

            Args:
                record: Raw WMS record.

            Returns:
                Processed record.

            """
            return record

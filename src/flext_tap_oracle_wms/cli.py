"""FLEXT Tap Oracle WMS - Singer SDK CLI Integration.

This module provides the command-line interface for the Oracle WMS Singer tap,
leveraging the Singer SDK's built-in CLI functionality with flext-meltano
integration for orchestration compatibility.

The tap supports standard Singer protocol operations:
- Discovery: Generate catalog with `--discover`
- Extraction: Run data extraction with `--config`, `--catalog`, `--state`

Integration with flext-meltano's SingerCliTranslator enables automated
command generation and pipeline orchestration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_oracle_wms.client import FlextTapOracleWMS


def main() -> None:
    """Execute Oracle WMS tap using Singer SDK CLI.

    This function serves as the primary entry point for the tap when
    executed as a command-line tool or Python module. It delegates to
    the Singer SDK's built-in CLI functionality for full protocol compliance.

    The CLI supports standard Singer operations:
    - `--discover`: Generate schema catalog
    - `--config FILE`: Specify tap configuration
    - `--catalog FILE`: Specify stream catalog
    - `--state FILE`: Specify state for incremental extraction

    Example:
        # Discovery
        tap-oracle-wms --config config.json --discover > catalog.json

        # Extraction
        tap-oracle-wms --config config.json --catalog catalog.json

        # Incremental sync
        tap-oracle-wms --config config.json --catalog catalog.json --state state.json

    Integration:
        Compatible with flext-meltano SingerCliTranslator for orchestration:

        >>> from flext_meltano import SingerCliTranslator, FlextMeltanoModels
        >>> params = FlextMeltanoModels.TapRunParams(
        ...     tap_name="tap-oracle-wms", config_file="config.json", discover=True
        ... )
        >>> command = SingerCliTranslator.translate_tap_run(params)
        >>> # Executes: ["tap-oracle-wms", "--config", "config.json", "--discover"]

    Raises:
        SystemExit: On configuration errors or execution failures

    """
    FlextTapOracleWMS.cli()


if __name__ == "__main__":
    main()

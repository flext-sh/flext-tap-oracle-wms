"""FLEXT Tap Oracle WMS - Command Line Interface.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_oracle_wms.client import FlextTapOracleWMS


def main() -> None:
    """Provide CLI entry point for FLEXT Tap Oracle WMS.

    Initializes and runs the Oracle WMS Singer tap using the Singer SDK
    CLI framework. Handles command-line argument parsing, configuration
    validation, and delegates to appropriate tap operations (discover, sync).

    This function serves as the primary entry point for the tap when
    executed as a command-line tool or Python module.

    Raises:
      SystemExit: On configuration errors or tap execution failures

    Example:
      # Called automatically when running:
      # python -m flext_tap_oracle_wms --config config.json --discover

    Returns:
            object: Description of return value.

    """
    FlextTapOracleWMS.cli()


def run_as_module() -> None:
    """Entry point for running as python -m flext_tap_oracle_wms.

    This function is called when the module is executed directly with:
    python -m flext_tap_oracle_wms

    It delegates to the main CLI function for consistency.

    Returns:
            object: Description of return value.

    """
    main()


if __name__ == "__main__":
    main()

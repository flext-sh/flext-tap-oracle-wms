"""FLEXT Tap Oracle WMS - Command Line Interface.

Provides the command-line entry point for the Oracle WMS Singer tap,
enabling data extraction from Oracle Warehouse Management Systems
following Singer specification standards.

Consolidates CLI functionality from cli.py and __main__.py following PEP8 patterns.
"""

from __future__ import annotations

from flext_tap_oracle_wms.tap_client import FlextTapOracleWMS


def main() -> None:
    """Main CLI entry point for FLEXT Tap Oracle WMS.

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

    """
    FlextTapOracleWMS.cli()


def run_as_module() -> None:
    """Entry point for running as python -m flext_tap_oracle_wms.

    This function is called when the module is executed directly with:
    python -m flext_tap_oracle_wms

    It delegates to the main CLI function for consistency.
    """
    main()


if __name__ == "__main__":
    main()

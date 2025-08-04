"""FLEXT Tap Oracle WMS - Command Line Interface.

Provides the command-line entry point for the Oracle WMS Singer tap,
enabling data extraction from Oracle Warehouse Management Systems
following Singer specification standards.

This module serves as the CLI gateway to the TapOracleWMS implementation,
supporting standard Singer tap operations including discovery, extraction,
and configuration validation.

Usage:
    tap-oracle-wms --config config.json --discover
    tap-oracle-wms --config config.json --catalog catalog.json

Example:
    # Discover available streams
    python -m flext_tap_oracle_wms --config examples/configs/basic.json --discover
    
    # Extract data
    python -m flext_tap_oracle_wms --config config.json --catalog catalog.json

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from flext_tap_oracle_wms.tap import TapOracleWMS


def main() -> None:
    """
    Main CLI entry point for FLEXT Tap Oracle WMS.
    
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
    TapOracleWMS.cli()


if __name__ == "__main__":
    main()

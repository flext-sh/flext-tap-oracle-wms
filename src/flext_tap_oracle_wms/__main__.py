"""Python module execution entry point for FLEXT Tap Oracle WMS.

Enables execution via `python -m flext_tap_oracle_wms` with full Singer SDK
CLI support and flext-meltano FlextMeltanoSingerCliTranslator compatibility.

Usage:
    python -m flext_tap_oracle_wms --config config.json --discover
    python -m flext_tap_oracle_wms --config config.json --catalog catalog.json

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_oracle_wms.cli import main

if __name__ == "__main__":
    main()

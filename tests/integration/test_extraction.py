#!/usr/bin/env python3
"""Test extraction with debugging."""

import subprocess
import sys

# Test extraction with first stream only
cmd = [
    sys.executable,
    "-m",
    "tap_oracle_wms",
    "--config",
    "config.json",
    "--catalog",
    "catalog_selected.json",
]


# Run with timeout
try:
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,  # 30 second timeout
    )

    # Show stdout
    if result.stdout:
        lines = result.stdout.splitlines()
        for _i, _line in enumerate(lines[:50]):  # First 50 lines
            pass

    # Show stderr
    if result.stderr:
        lines = result.stderr.splitlines()
        for _line in lines[-50:]:  # Last 50 lines
            pass

except subprocess.TimeoutExpired:
    pass

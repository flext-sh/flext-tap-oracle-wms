"""Allow running as python -m flext_tap_oracle_wms.

Following PEP8 reorganization using tap_cli module.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from flext_tap_oracle_wms.tap_cli import run_as_module

if __name__ == "__main__":
    run_as_module()

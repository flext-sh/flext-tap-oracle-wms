"""CLI entry point for Oracle WMS tap."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from flext_tap_oracle_wms.tap import TapOracleWMS


def main() -> None:
    """CLI entry point for Oracle WMS tap."""
    TapOracleWMS().cli()


if __name__ == "__main__":
    main()

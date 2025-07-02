"""CLI entry point for Oracle WMS tap."""

from __future__ import annotations

from .tap import TapOracleWMS


def main() -> None:
    """Run tap using Singer SDK CLI."""
    TapOracleWMS.cli()


if __name__ == "__main__":
    main()

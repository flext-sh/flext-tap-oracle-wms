"""FLEXT Tap Oracle WMS - Singer SDK CLI Integration.

Module entrypoint that dispatches into ``FlextTapOracleWmsService.cli_main``.
The Singer SDK CLI verbs are documented on the service itself; this module
exists solely to provide ``main`` as the ``[project.scripts]`` target.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_oracle_wms.api import FlextTapOracleWmsService

__all__: list[str] = ["main"]


def main() -> int:
    """Execute Oracle WMS tap through the FLEXT service CLI bridge."""
    return FlextTapOracleWmsService().cli_main()


if __name__ == "__main__":
    raise SystemExit(main())

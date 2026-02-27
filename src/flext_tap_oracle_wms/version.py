"""Version and package metadata using importlib.metadata.

Single source of truth pattern following flext-core standards.
All metadata comes from pyproject.toml via importlib.metadata.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from typing import override

from importlib.metadata import metadata

_metadata = metadata("flext_tap_oracle_wms")

__version__ = _metadata["Version"]
__version_info__ = tuple(
    int(part) if part.isdigit() else part for part in __version__.split(".")
)
__title__ = _metadata["Name"]
__description__ = _metadata["Summary"]
__author__ = _metadata["Author"]
__author_email__ = _metadata["Author-Email"]
__license__ = _metadata["License"]
__url__ = _metadata["Home-Page"]


# Version class for typed version information
class FlextTapOracleWmsVersion:
    """Typed version information for flext-tap-oracle-wms."""

    def __init__(self, version: str, version_info: tuple[int | str, ...]) -> None:
        """Initialize version information."""
        self.version = version
        self.version_info = version_info

    @override

    def __str__(self) -> str:
        """Return string representation."""
        return self.version

    @override

    def __repr__(self) -> str:
        """Return repr representation."""
        return f"FlextTapOracleWmsVersion({self.version!r}, {self.version_info!r})"


# Create version instance
VERSION = FlextTapOracleWmsVersion(__version__, __version_info__)

__all__ = [
    "VERSION",
    "FlextTapOracleWmsVersion",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
]

"""Version information for flext-tap-oracle-wms."""

from __future__ import annotations

from typing import Final

# Version components
MAJOR: Final[int] = 0
MINOR: Final[int] = 9
PATCH: Final[int] = 0

# Version string
__version__: Final[str] = f"{MAJOR}.{MINOR}.{PATCH}"
__version_info__: Final[tuple[int, int, int]] = (MAJOR, MINOR, PATCH)


class FlextMeltanoTapOracleWmsVersion:
    """Version information container for flext-tap-oracle-wms."""

    def __init__(self) -> None:
        self.major = MAJOR
        self.minor = MINOR
        self.patch = PATCH
        self.version = __version__
        self.version_info = __version_info__

    @classmethod
    def current(cls) -> FlextMeltanoTapOracleWmsVersion:
        """Return current version information."""
        return cls()


VERSION: Final[FlextMeltanoTapOracleWmsVersion] = (
    FlextMeltanoTapOracleWmsVersion.current()
)

__all__ = [
    "VERSION",
    "FlextMeltanoTapOracleWmsVersion",
    "__version__",
    "__version_info__",
]

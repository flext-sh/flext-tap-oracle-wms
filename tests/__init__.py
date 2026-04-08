# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.constants import (
        TestsFlextTapOracleWmsConstants,
        TestsFlextTapOracleWmsConstants as c,
    )
    from tests.models import (
        TestsFlextTapOracleWmsModels,
        TestsFlextTapOracleWmsModels as m,
    )
    from tests.protocols import (
        TestsFlextTapOracleWmsProtocols,
        TestsFlextTapOracleWmsProtocols as p,
    )
    from tests.typings import (
        TestsFlextTapOracleWmsTypes,
        TestsFlextTapOracleWmsTypes as t,
    )
    from tests.utilities import (
        TestsFlextTapOracleWmsUtilities,
        TestsFlextTapOracleWmsUtilities as u,
    )
_LAZY_IMPORTS = {
    "TestsFlextTapOracleWmsConstants": (
        "tests.constants",
        "TestsFlextTapOracleWmsConstants",
    ),
    "TestsFlextTapOracleWmsModels": ("tests.models", "TestsFlextTapOracleWmsModels"),
    "TestsFlextTapOracleWmsProtocols": (
        "tests.protocols",
        "TestsFlextTapOracleWmsProtocols",
    ),
    "TestsFlextTapOracleWmsTypes": ("tests.typings", "TestsFlextTapOracleWmsTypes"),
    "TestsFlextTapOracleWmsUtilities": (
        "tests.utilities",
        "TestsFlextTapOracleWmsUtilities",
    ),
    "c": ("tests.constants", "TestsFlextTapOracleWmsConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("tests.models", "TestsFlextTapOracleWmsModels"),
    "p": ("tests.protocols", "TestsFlextTapOracleWmsProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("tests.typings", "TestsFlextTapOracleWmsTypes"),
    "u": ("tests.utilities", "TestsFlextTapOracleWmsUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

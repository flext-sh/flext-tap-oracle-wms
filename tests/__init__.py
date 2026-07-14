# AUTO-GENERATED FILE — canonical lazy tests facade. Regenerate with: make gen
"""Test package facade exposing the project test aliases lazily."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from tests.base import (
        TestsFlextTapOracleWmsServiceBase as TestsFlextTapOracleWmsServiceBase,
        s as s,
    )
    from tests.constants import (
        TestsFlextTapOracleWmsConstants as TestsFlextTapOracleWmsConstants,
        c as c,
    )
    from tests.models import (
        TestsFlextTapOracleWmsModels as TestsFlextTapOracleWmsModels,
        m as m,
    )
    from tests.protocols import (
        TestsFlextTapOracleWmsProtocols as TestsFlextTapOracleWmsProtocols,
        p,
    )
    from tests.typings import (
        TestsFlextTapOracleWmsTypes as TestsFlextTapOracleWmsTypes,
        t as t,
    )
    from tests.utilities import (
        TestsFlextTapOracleWmsUtilities as TestsFlextTapOracleWmsUtilities,
        u,
    )

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".constants": ("TestsFlextTapOracleWmsConstants", "c"),
        ".typings": ("TestsFlextTapOracleWmsTypes", "t"),
        ".protocols": ("TestsFlextTapOracleWmsProtocols", "p"),
        ".models": ("TestsFlextTapOracleWmsModels", "m"),
        ".utilities": ("TestsFlextTapOracleWmsUtilities", "u"),
        ".base": ("TestsFlextTapOracleWmsServiceBase", "s"),
    },
)

install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

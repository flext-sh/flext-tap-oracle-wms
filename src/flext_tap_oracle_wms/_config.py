"""FlextTapOracleWmsConfig — frozen config singleton for flext-tap-oracle-wms.

See ADR-005 §7.

Model-less: business rules live in ``config/*.yaml`` under the ``TapOracleWms:`` key and
are exposed through the open ``config.TapOracleWms`` namespace (``extra="allow"``), with
no per-domain model. Access is ``config.TapOracleWms.<domain>[<key>...]``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, Self

from flext_meltano import FlextMeltanoConfig

from flext_tap_oracle_wms import m, t


class FlextTapOracleWmsConfig(FlextMeltanoConfig):
    """TapOracleWms config auto-loaded model-less from ``config/*.yaml``.

    MRO carries ``FlextSettings`` FIRST (ENFORCE-042); the class stays a frozen,
    YAML-validated config singleton.
    """

    # ENFORCE-042 namespace-holder contract: ``FlextSettings`` contributes
    # namespacing only — instance machinery stays plain object semantics so the
    # settings singleton ``__new__`` cannot leak into the config singleton.
    # The inherited pydantic ``__init__`` still runs the frozen, YAML-validated
    # construction, and the inherited pydantic ``__setattr__`` keeps the frozen
    # guard.
    def __new__(cls, *args: t.JsonValue, **kwargs: t.JsonValue) -> Self:
        _ = args, kwargs
        return object.__new__(cls)

    # Identity equality/hash per the frozen-config singleton contract: plain
    # object semantics, never the inherited pydantic field comparison.
    __eq__ = object.__eq__

    __hash__ = object.__hash__

    TapOracleWms: Annotated[
        m.TapOracleWms.TapOracleWmsNamespace,
        m.Field(
            description=(
                "Open namespace exposing ``config/*.yaml`` under ``TapOracleWms``."
            ),
        ),
    ] = m.TapOracleWms.TapOracleWmsNamespace()


config: FlextTapOracleWmsConfig = FlextTapOracleWmsConfig.fetch_global()
"""Pre-instantiated frozen config singleton.

Exposed as ``from flext_tap_oracle_wms import config``.
"""

__all__: list[str] = ["FlextTapOracleWmsConfig", "config"]

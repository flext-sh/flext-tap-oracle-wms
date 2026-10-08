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

from flext_tap_oracle_wms import m


class _TapOracleWmsNamespace(m.BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = m.ConfigDict(extra="allow", frozen=True)


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
    def __new__(cls, *args: object, **kwargs: object) -> Self:
        _ = args, kwargs
        return object.__new__(cls)

    def __eq__(self, other: object) -> bool:
        """Identity equality per the frozen-config singleton contract.

        Returns:
            The resulting ``bool``.
        """
        return object.__eq__(self, other)

    def __hash__(self) -> int:
        """Identity hash per the frozen-config singleton contract.

        Returns:
            The resulting ``int``.
        """
        return object.__hash__(self)

    TapOracleWms: Annotated[
        _TapOracleWmsNamespace,
        m.Field(
            description=(
                "Open namespace exposing ``config/*.yaml`` under ``TapOracleWms``."
            ),
        ),
    ] = _TapOracleWmsNamespace()


config: FlextTapOracleWmsConfig = FlextTapOracleWmsConfig.fetch_global()
"""Pre-instantiated frozen config singleton.

Exposed as ``from flext_tap_oracle_wms import config``.
"""

__all__: list[str] = ["FlextTapOracleWmsConfig", "config"]

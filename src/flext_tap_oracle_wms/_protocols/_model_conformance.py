# AUTO-GENERATED FILE — Regenerate with: make gen
"""Static instance-to-protocol evidence required by candidate admission.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_tap_oracle_wms/_protocols/_model_conformance
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_tap_oracle_wms import m, p

    def model_protocol_1(value: object) -> p.TapOracleWms.TapOracleWmsNamespace:
        if not isinstance(value, m.TapOracleWms.TapOracleWmsNamespace):
            msg = "model protocol witness received another declaring owner"
            raise TypeError(msg)
        return value

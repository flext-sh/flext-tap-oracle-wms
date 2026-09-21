"""Pydantic models used by Oracle WMS tap compatibility layers."""

from __future__ import annotations

from flext_meltano import m
from flext_oracle_wms import m as _oracle_wms_m


class FlextTapOracleWmsModels(m, _oracle_wms_m):
    """Container for stream schema and metadata payload models."""

    class TapOracleWms:
        """TapOracleWms domain namespace.

        Local Singer catalog compatibility types were removed in favor of the
        canonical ``m.Meltano.SingerCatalog*`` Pydantic models plus explicit
        serialization at the Singer dict boundary.
        """


m = FlextTapOracleWmsModels

__all__: list[str] = ["FlextTapOracleWmsModels", "m"]

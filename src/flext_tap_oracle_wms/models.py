"""Pydantic models used by Oracle WMS tap compatibility layers."""

from __future__ import annotations

from flext_meltano import m as meltano_m
from flext_oracle_wms import FlextOracleWmsModels


class FlextTapOracleWmsModels(meltano_m, FlextOracleWmsModels):
    """Container for stream schema and metadata payload models."""

    class TapOracleWms:
        """TapOracleWms domain namespace.

        Local Singer catalog compatibility types were removed in favor of the
        canonical ``m.Meltano.SingerCatalog*`` Pydantic models plus explicit
        serialization at the Singer dict boundary.
        """

        pass


m = FlextTapOracleWmsModels

__all__: list[str] = ["FlextTapOracleWmsModels", "m"]

# AGENTS.md — flext-tap-oracle-wms

> **Parent workspace law** lives in [`../AGENTS.md`](../AGENTS.md) — read it first.
> Universal engineering core: `~/.agents/UNIVERSAL_CORE.md`. Composition: global skills + parent/root `AGENTS.md` + this scope delta. Do not re-embed universal law.
>
> **Standalone / independent mode:** when `../AGENTS.md` does not resolve, pin the parent raw `AGENTS.md` URL to the same branch/release as this package (never `main`).

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
**Package:** `flext_tap_oracle_wms` · deps: `flext-cli`, `flext-core`, `flext-meltano`, `flext-oracle-wms`

## Overview

Singer **tap** (extractor) for Oracle WMS. Thin driver over `flext-meltano` (ADR-006), delegating WMS access to `flext-oracle-wms`.

## Structure

```text
src/flext_tap_oracle_wms/
├── api.py            # FlextTapOracleWmsService(FlextMeltanoTapServiceBase)
├── tap.py            # FlextTapOracleWms(m.Meltano.SingerTapBase), backed by FlextOracleWmsUtilities
├── streams.py        # FlextTapOracleWmsStream
├── errors.py __main__.py
├── constants.py typings.py protocols.py models.py utilities.py   # AUTO-GENERATED facets
```

## Code Map

| Symbol | Kind | Location | Role |
|--------|------|----------|------|
| `FlextTapOracleWmsService` | class | `api.py` | `FlextMeltanoTapServiceBase` |
| `FlextTapOracleWms` | class | `tap.py` | `m.Meltano.SingerTapBase` |
| `FlextTapOracleWmsStream` | class | `streams.py` | stream impl |

## Conventions (specific to this package)

- Config is exposed through the Singer `self.config` contract; WMS settings remain namespaced.
- Config/settings canonical pattern: ADR-012.
- Codemod governance (ast-grep + make mod): ADR-014.

## Commands

```bash
make check PROJECT=flext-tap-oracle-wms
make test  PROJECT=flext-tap-oracle-wms       # tests/{unit,integration,e2e,performance}
```
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->

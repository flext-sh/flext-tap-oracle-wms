# Python Module Organization

<!-- TOC START -->

- [Authority](#authority)
- [This Package](#this-package)

<!-- TOC END -->

## Authority

Module organization is workspace law, not a per-project standard. The binding rules
(facade layering `c -> t -> p -> m -> u`, one public `api.py`, generated lazy
exports, declaration layers as pure data) are stated once in the workspace
[`AGENTS.md`](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md) and its
accepted ADRs. `make check` enforces them through the shared rule catalog.

## This Package

The modules of `flext_tap_oracle_wms` and their responsibilities are listed in
[the architecture document](../architecture.md#package-structure).

# FLEXT Ecosystem Integration

<!-- TOC START -->

- [Overview](#overview)
- [Integration Points](#integration-points)
- [Runnable Example](#runnable-example)

<!-- TOC END -->

## Overview

FLEXT Tap Oracle WMS is a thin Singer driver. It owns no HTTP client, no Singer
runtime and no configuration loader of its own; each of those belongs to a FLEXT
library, and this package only composes them. The source modules below are the
authority: this page points at them instead of repeating their code.

## Integration Points

| Concern                                                   | Owner                       | Where this package composes it                                                                                                |
| --------------------------------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Result, exceptions, settings base, facades                | `flext-core`                | `src/flext_tap_oracle_wms/_settings.py`, `constants.py`, `typings.py`, `protocols.py`, `models.py`, `utilities.py`            |
| Oracle WMS REST client                                    | `flext-oracle-wms`          | `FlextTapOracleWms.wms_client` in `src/flext_tap_oracle_wms/tap.py`                                                           |
| Singer tap and stream bases, catalog models, service base | `flext-meltano`             | `FlextTapOracleWms` in `tap.py`, `FlextTapOracleWmsStreams.WmsStream` in `streams.py`, `FlextTapOracleWmsService` in `api.py` |
| Business rules from `config/*.yaml`                       | `flext-meltano` config base | `src/flext_tap_oracle_wms/_config.py`                                                                                         |

- Settings are namespaced: every tap field lives under `settings.TapOracleWms.*`
  and is read from the `FLEXT_TAP_ORACLE_WMS_` environment prefix.
- `FlextTapOracleWms.from_settings` is the single boundary that lowers the typed
  settings model into the flat mapping the Singer SDK constructor requires.
- Discovery, validation and extraction return `p.Result` values; failures of the
  WMS client surface as `e.ConfigurationError` or `e.OperationError`.

## Runnable Example

`examples/example_01_basic_usage.py` builds the settings, validates the
configuration and discovers the catalog against a reachable Oracle WMS
environment.

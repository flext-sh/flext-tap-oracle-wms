# Architecture Documentation

<!-- TOC START -->

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Discovery Flow](#discovery-flow)
- [Extraction Flow](#extraction-flow)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Related Documentation](#related-documentation)

<!-- TOC END -->

## Overview

FLEXT Tap Oracle WMS is a Singer tap for Oracle Warehouse Management Cloud. It is a
thin driver over `flext-meltano` (Singer runtime) and `flext-oracle-wms` (REST
client); it owns only the tap class, the dynamic stream class and the tap settings.
The source is the authority for every signature named here.

## Package Structure

| Module                                                                    | Responsibility                                                                                                                          |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `tap.py`                                                                  | `FlextTapOracleWms`: Singer tap, catalog discovery, WMS client lifecycle                                                                |
| `streams.py`                                                              | `FlextTapOracleWmsStreams.WmsStream`: one dynamic stream per WMS entity                                                                 |
| `api.py`                                                                  | `FlextTapOracleWmsService`: service facade over the `flext-meltano` tap service base                                                    |
| `cli.py`, `__main__.py`                                                   | `main` entry point                                                                                                                      |
| `_settings.py`                                                            | `FlextTapOracleWmsSettings`: environment-tunable fields under `settings.TapOracleWms`                                                   |
| `_config.py`                                                              | `FlextTapOracleWmsConfig`: business rules loaded from `config/*.yaml`                                                                   |
| `constants.py`, `typings.py`, `protocols.py`, `models.py`, `utilities.py` | Generated `c`, `t`, `p`, `m`, `u` facades composed from the `_constants`, `_typings`, `_protocols`, `_models` and `_utilities` families |

## Discovery Flow

1. `FlextTapOracleWms.from_settings` lowers the typed settings into the flat Singer
   configuration.
1. `FlextTapOracleWms.wms_client` starts the `flext-oracle-wms` client on first use.
1. `FlextTapOracleWms.discovercatalog_typed` asks the client for its entities and
   returns a typed Singer catalog as a `p.Result`.
1. `FlextTapOracleWms.discover_streams` builds one `WmsStream` per catalog entry.

## Extraction Flow

1. `WmsStream.get_records` requests one page at a time through the tap's WMS client.
1. `WmsStream.build_operation_kwargs` derives the page, the limit and, for a stream
   with a replication key, the start filter.
1. Every record value is normalized to a Singer-compatible JSON value.
1. `WmsStream.post_process` applies the configured column mappings and removes the
   ignored columns.

## Configuration

Tap fields are declared once in `FlextTapOracleWmsSettings.TapOracleWmsSettings` and
read from the `FLEXT_TAP_ORACLE_WMS_` environment prefix. The Singer configuration
schema of the tap is `FlextTapOracleWms.config_jsonschema`.

## Error Handling

Fallible operations return `p.Result`. A failed client start or an invalid
configuration raises `e.ConfigurationError`; a failed page request during extraction
raises `e.OperationError`.

## Testing

Tests live under `tests/` and exercise the public tap through real settings and a
real Singer catalog, without mocks. Tests that need a reachable Oracle WMS
environment depend on the `real_config` or `real_tap_instance` fixtures and are
skipped when that environment is not configured.

## Related Documentation

- [Getting Started](getting-started.md)
- [FLEXT Ecosystem Integration](architecture/flext-integration.md)
- [Examples](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-tap-oracle-wms/examples/)

# FLEXT Tap Oracle WMS - Core Module

<!-- TOC START -->

- [Overview](#overview)
- [Module Structure](#module-structure)
- [Usage](#usage)
- [Testing](#testing)

<!-- TOC END -->

## Overview

This package is the Singer tap for Oracle Warehouse Management Cloud. It is a thin
driver over `flext-meltano` and `flext-oracle-wms`; see
[the architecture document](../../docs/architecture.md) for the flows.

## Module Structure

- `tap.py`: `FlextTapOracleWms`, the Singer tap.
- `streams.py`: `FlextTapOracleWmsStreams.WmsStream`, the dynamic entity stream.
- `api.py`: `FlextTapOracleWmsService`, the service facade.
- `cli.py` and `__main__.py`: the `main` entry point.
- `_settings.py`: `FlextTapOracleWmsSettings`.
- `_config.py`: `FlextTapOracleWmsConfig`.
- `constants.py`, `typings.py`, `protocols.py`, `models.py`, `utilities.py`: the
  generated `c`, `t`, `p`, `m`, `u` facades.

## Usage

`examples/example_01_basic_usage.py` is the maintained usage example: it builds the
settings, validates the configuration and discovers the catalog.

## Testing

Run `make tests` from the repository root. See
[tests/README.md](../../tests/README.md) for the test layout.

# FLEXT Tap Oracle WMS Examples

This directory currently ships one runnable Python example for `flext-tap-oracle-wms`.

## Available Example

### `01_basic_usage.py`

This example builds `FlextTapOracleWmsSettings`, validates the configuration, runs catalog discovery, and inspects the discovered streams.

## Required Environment Variables

Set these variables before running the example against a real Oracle WMS environment:

```bash
export ORACLE_WMS_BASE_URL="https://your-wms-instance.example.com"
export ORACLE_WMS_USERNAME="your_username"
export ORACLE_WMS_PASSWORD="your_password"
```

If they are not set, the script falls back to placeholder values that are useful only for local inspection of the setup flow.

## Run The Example

```bash
cd examples
python 01_basic_usage.py
```

This directory does not currently include JSON config fixtures or dedicated `make` targets for discovery and execution. Keep any additional operator commands in project-level docs once those assets exist in the repository.

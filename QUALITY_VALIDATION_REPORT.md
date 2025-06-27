# Project Quality Validation Report

**Date**: 1750990877.6317563
**Validation Script**: validate_project_quality.py

## Summary

| Check             | Status  | Details                |
| ----------------- | ------- | ---------------------- |
| Python Syntax     | ✅ PASS | 0 errors               |
| Import Validation | ❌ FAIL | 1 failures             |
| Ruff Lint         | ❌ FAIL | Comprehensive rule set |
| MyPy Type Check   | ❌ FAIL | Strict mode            |

## Overall Status

**❌ QUALITY ISSUES DETECTED**

## Detailed Results

### Syntax Validation

✅ All Python files have valid syntax

### Import Validation

❌ Import errors found:

- Import failed: from tap_oracle_wms.config import TapOracleWMSConfig -> cannot import name 'TapOracleWMSConfig' from 'tap_oracle_wms.config' (/home/marlonsc/pyauto/tap-oracle-wms/src/tap_oracle_wms/config.py)

### Ruff Lint Analysis

Ruff violations found:

/usr/bin/python: No module named ruff

### MyPy Type Checking

MyPy errors found:
src/tap_oracle_wms/monitoring.py:20: error: Library stubs not installed for "psutil" [import-untyped]
src/tap_oracle_wms/monitoring.py:20: note: Hint: "python3 -m pip install types-psutil"
src/tap_oracle_wms/monitoring.py:20: note: (or run "mypy --install-types" to install all missing stub packages)
src/tap_oracle_wms/monitoring.py:20: note: See <https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports>
src/tap_oracle_wms/monitoring.py:364: error: Name "TimerContext" already defined on line 68 [no-redef]
src/tap_oracle_wms/monitoring.py:556: error: Incompatible types in assignment (expression has type "datetime", variable has type "None") [assignment]
src/tap_oracle_wms/monitoring.py:606: error: Returning Any from function declared to return "bool" [no-any-return]
src/tap_oracle_wms/config.py:960: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/config.py:993: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/auth.py:19: error: Missing type parameters for generic type "RESTStream" [type-arg]
src/tap_oracle_wms/auth.py:73: error: Missing type parameters for generic type "RESTStream" [type-arg]
src/tap_oracle_wms/auth.py:222: error: Missing type parameters for generic type "RESTStream" [type-arg]
src/tap_oracle_wms/streams.py:144: error: Incompatible types in assignment (expression has type "float", variable has type "None") [assignment]
src/tap_oracle_wms/streams.py:159: error: Unsupported operand types for - ("float" and "None") [operator]
src/tap_oracle_wms/streams.py:228: error: Incompatible types in assignment (expression has type "Optional[str]", variable has type "None") [assignment]
src/tap_oracle_wms/streams.py:240: error: Missing type parameters for generic type "RESTStream" [type-arg]
src/tap_oracle_wms/streams.py:290: error: Function is missing a type annotation for one or more arguments [no-untyped-def]
src/tap_oracle_wms/streams.py:294: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/streams.py:352: error: Cannot override writeable attribute with read-only property [override]
src/tap_oracle_wms/streams.py:357: error: Function is missing a return type annotation [no-untyped-def]
src/tap_oracle_wms/streams.py:363: error: Library stubs not installed for "requests" [import-untyped]
src/tap_oracle_wms/streams.py:363: note: Hint: "python3 -m pip install types-requests"
src/tap_oracle_wms/streams.py:372: error: "request" undefined in superclass [misc]
src/tap_oracle_wms/streams.py:378: error: Cannot override writeable attribute with read-only property [override]
src/tap_oracle_wms/streams.py:389: error: Argument 1 of "get_url_params" is incompatible with supertype "\_HTTPStream"; supertype defines the argument type as "Optional[Mapping[str, Any]]" [override]
src/tap_oracle_wms/streams.py:389: note: This violates the Liskov substitution principle
src/tap_oracle_wms/streams.py:389: note: See <https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides>
src/tap_oracle_wms/streams.py:389: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/streams.py:420: error: "Tap" has no attribute "apply_entity_filters" [attr-defined]
src/tap_oracle_wms/streams.py:428: error: "Tap" has no attribute "apply_incremental_filters" [attr-defined]
src/tap_oracle_wms/streams.py:436: error: "Tap" has no attribute "get_entity_replication_config" [attr-defined]
src/tap_oracle_wms/streams.py:444: error: "Tap" has no attribute "apply_full_sync_filters" [attr-defined]
src/tap_oracle_wms/streams.py:475: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/streams.py:533: error: Argument 2 to "get_wms_authenticator" has incompatible type "Mapping[str, Any]"; expected "dict[str, Any]" [arg-type]
src/tap_oracle_wms/streams.py:536: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/streams.py:538: error: Argument 1 to "get_wms_headers" has incompatible type "Mapping[str, Any]"; expected "dict[str, Any]" [arg-type]
src/tap_oracle_wms/streams.py:596: error: Statement is unreachable [unreachable]
src/tap_oracle_wms/streams.py:622: error: Incompatible types in "yield" (actual type "list[Any]", expected type "dict[str, Any]") [misc]
src/tap_oracle_wms/streams.py:634: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/streams.py:634: error: Argument 2 of "post_process" is incompatible with supertype "Stream"; supertype defines the argument type as "Optional[Mapping[str, Any]]" [override]
src/tap_oracle_wms/streams.py:634: note: This violates the Liskov substitution principle
src/tap_oracle_wms/streams.py:634: note: See <https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides>
src/tap_oracle_wms/streams.py:638: error: Statement is unreachable [unreachable]
src/tap_oracle_wms/streams.py:657: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/streams.py:680: error: Argument 1 of "get_records" is incompatible with supertype "\_HTTPStream"; supertype defines the argument type as "Optional[Mapping[str, Any]]" [override]
src/tap_oracle_wms/streams.py:680: note: This violates the Liskov substitution principle
src/tap_oracle_wms/streams.py:680: note: See <https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides>
src/tap_oracle_wms/streams.py:680: error: Argument 1 of "get_records" is incompatible with supertype "Stream"; supertype defines the argument type as "Optional[Mapping[str, Any]]" [override]
src/tap_oracle_wms/streams.py:680: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/streams.py:702: error: Function is missing a type annotation for one or more arguments [no-untyped-def]
src/tap_oracle_wms/streams.py:705: error: Function is missing a type annotation for one or more arguments [no-untyped-def]
src/tap_oracle_wms/streams.py:768: error: Returning Any from function declared to return "int" [no-any-return]
src/tap_oracle_wms/streams.py:789: error: Returning Any from function declared to return "int" [no-any-return]
src/tap_oracle_wms/tap.py:787: error: Statement is unreachable [unreachable]
src/tap_oracle_wms/cli.py:254: error: Argument 1 to "load" has incompatible type "File"; expected "SupportsRead[Union[str, bytes]]" [arg-type]
src/tap_oracle_wms/cli.py:261: error: Call to untyped function "\_run_entity_discovery" in typed context [no-untyped-call]
src/tap_oracle_wms/cli.py:304: error: Argument 1 to "load" has incompatible type "File"; expected "SupportsRead[Union[str, bytes]]" [arg-type]
src/tap_oracle_wms/cli.py:310: error: Function is missing a return type annotation [no-untyped-def]
src/tap_oracle_wms/cli.py:320: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/cli.py:369: error: Call to untyped function "\_generate_schemas" in typed context [no-untyped-call]
src/tap_oracle_wms/cli.py:373: error: Argument 1 to "Path" has incompatible type "Path"; expected "Union[str, PathLike[str]]" [arg-type]
src/tap_oracle_wms/cli.py:421: error: Argument 1 to "load" has incompatible type "File"; expected "SupportsRead[Union[str, bytes]]" [arg-type]
src/tap_oracle_wms/cli.py:433: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/cli.py:498: error: Function is missing a type annotation for one or more arguments [no-untyped-def]
src/tap_oracle_wms/cli.py:519: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/cli.py:563: error: Function is missing a type annotation for one or more arguments [no-untyped-def]
src/tap_oracle_wms/cli.py:668: error: Argument 1 to "load" has incompatible type "File"; expected "SupportsRead[Union[str, bytes]]" [arg-type]
src/tap_oracle_wms/cli.py:672: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/cli.py:807: error: Argument 1 to "load" has incompatible type "File"; expected "SupportsRead[Union[str, bytes]]" [arg-type]
src/tap_oracle_wms/cli.py:832: error: Argument 1 to "load" has incompatible type "File"; expected "SupportsRead[Union[str, bytes]]" [arg-type]
src/tap_oracle_wms/cli.py:1109: error: Argument 2 to "dump" has incompatible type "File"; expected "SupportsWrite[str]" [arg-type]
src/tap_oracle_wms/cli.py:1162: error: Argument 1 to "load" has incompatible type "File"; expected "SupportsRead[Union[str, bytes]]" [arg-type]
src/tap_oracle_wms/cli.py:1297: error: Function is missing a type annotation [no-untyped-def]
src/tap_oracle_wms/cli.py:1299: error: Call to untyped function "\_run_discovery_with_progress" in typed context [no-untyped-call]
src/tap_oracle_wms/cli.py:1302: error: Function is missing a type annotation [no-untyped-def]
src/tap_oracle_wms/cli.py:1321: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/cli.py:1335: error: Function is missing a type annotation [no-untyped-def]
src/tap_oracle_wms/cli.py:1346: error: Missing type parameters for generic type "dict" [type-arg]
src/tap_oracle_wms/cli.py:1360: error: Function is missing a type annotation for one or more arguments [no-untyped-def]
src/tap_oracle_wms/cli.py:1383: error: Need type annotation for "categories" [var-annotated]
src/tap_oracle_wms/cli.py:1493: error: Function is missing a type annotation for one or more arguments [no-untyped-def]
src/tap_oracle_wms/cli.py:1577: error: Argument 1 to "load" has incompatible type "File"; expected "SupportsRead[Union[str, bytes]]" [arg-type]
src/tap_oracle_wms/cli.py:1582: error: Function is missing a return type annotation [no-untyped-def]
src/tap_oracle_wms/cli.py:1589: error: Call to untyped function "\_get_status" in typed context [no-untyped-call]
Found 74 errors in 6 files (checked 10 source files)

## Maintenance Notes

- Run this script regularly to maintain quality standards
- Address any failures immediately to prevent quality degradation
- Update validation criteria as project evolves

**Quality Commitment**: Zero tolerance for violations in production code.

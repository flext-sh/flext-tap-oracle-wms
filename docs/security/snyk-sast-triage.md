# Triagem Snyk Code (SAST) — flext-sh/flext-tap-oracle-wms

<!-- TOC START -->
- [Resumo](#resumo)
- [Como usar este documento](#como-usar-este-documento)
- [Achados](#achados)
  - [1 · ⚪ LOW · Use of Hardcoded Passwords](#1-low-use-of-hardcoded-passwords)
  - [2 · ⚪ LOW · Use of Hardcoded Passwords](#2-low-use-of-hardcoded-passwords)
  - [3 · ⚪ LOW · Use of Hardcoded Passwords](#3-low-use-of-hardcoded-passwords)
  - [4 · ⚪ LOW · Use of Hardcoded Passwords](#4-low-use-of-hardcoded-passwords)
  - [5 · ⚪ LOW · Use of Hardcoded Passwords](#5-low-use-of-hardcoded-passwords)
  - [6 · ⚪ LOW · Use of Hardcoded Passwords](#6-low-use-of-hardcoded-passwords)
  - [7 · ⚪ LOW · Use of Hardcoded Passwords](#7-low-use-of-hardcoded-passwords)
  - [8 · ⚪ LOW · Use of Hardcoded Passwords](#8-low-use-of-hardcoded-passwords)
<!-- TOC END -->

Gerado do scan Snyk (dump 2026-08-06). Bead: `mro-8i5s`

## Resumo

**8 achados** — critical 0, high 0, medium 0, low 8

| categoria | achados |
|---|---|
| Use of Hardcoded Passwords | 8 |

## Como usar este documento

Cada achado traz o **código real** extraído da worktree (linha `>>>` = sink reportado), a regra completa e o CWE.
Preencha **Decisão**: `corrigir` / `falso-positivo` (registrar em `.snyk`) / `risco-aceito` (com prazo).

## Achados

### 1 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/conftest.py:66` · **CWE**: -

```text
return FlextTapOracleWmsSettings.model_validate({
"TapOracleWms": {
"base_url": "https://test.wms.example.com",
"username": "test_user",
>>>    "password": "test_password",
"api_version": "v10",
"page_size": 100,
"timeout": 30,
"max_retries": 3,
```

**Decisão**:

### 2 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/integration/test_wms_connection.py:183` · **CWE**: -

```text
bad_settings = FlextTapOracleWmsSettings.model_validate({
"TapOracleWms": {
"base_url": "https://invalid.example.com",
"username": "invalid",
>>>   "password": "invalid",
}
})
tap = FlextTapOracleWms.from_settings(bad_settings)
result = tap.validate_configuration()
```

**Decisão**:

### 3 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config.py:32` · **CWE**: -

```text
settings = FlextTapOracleWmsSettings.model_validate({
"TapOracleWms": {
"base_url": "https://wms.example.com",
"username": "test_user",
>>>    "password": "test_pass",
}
})
namespace = settings.TapOracleWms
tm.that(namespace.base_url.rstrip("/"), eq="https://wms.example.com")
```

**Decisão**:

### 4 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config.py:57` · **CWE**: -

```text
settings = FlextTapOracleWmsSettings.model_validate({
"TapOracleWms": {
"base_url": "https://prod.wms.example.com",
"username": "prod_user",
>>>    "password": "prod_pass",
"api_version": "v11",
"timeout": 60,
"max_retries": 5,
"retry_delay": 2,
```

**Decisão**:

### 5 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config.py:239` · **CWE**: -

```text
settings = FlextTapOracleWmsSettings.model_validate({
"TapOracleWms": {
"base_url": "https://wms.example.com",
"username": "user",
>>>   "password": "super_secret_password",
}
})
password = settings.TapOracleWms.password
password_value = (
```

**Decisão**:

### 6 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config_validation.py:31` · **CWE**: -

```text
settings = FlextTapOracleWmsSettings.model_validate({
"TapOracleWms": {
"base_url": "https://wms.example.com",
"username": "test_user",
>>>    "password": "test_password",
}
})
namespace = settings.TapOracleWms
tm.that(namespace.base_url.rstrip("/"), eq="https://wms.example.com")
```

**Decisão**:

### 7 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config_validation.py:202` · **CWE**: -

```text
settings = FlextTapOracleWmsSettings.model_validate({
"TapOracleWms": {
"base_url": "https://wms.example.com",
"username": "user",
>>>   "password": "super_secret",
}
})
password = settings.TapOracleWms.password
password_value = (
```

**Decisão**:

### 8 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_tap.py:46` · **CWE**: -

```text
settings = FlextTapOracleWmsSettings.model_validate({
"TapOracleWms": {
"base_url": "https://test.wms.example.com",
"username": "test_user",
>>>    "password": "test_password",
}
})
tap = FlextTapOracleWms.from_settings(settings, catalog=sample_catalog)
tm.that(tap.flext_config.TapOracleWms.base_url, has="test.wms.example.com")
```

**Decisão**:

# Triagem Snyk Code (SAST) — flext-sh/flext-tap-oracle-wms

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

```python
       62      return FlextTapOracleWmsSettings.model_validate({
       63          "TapOracleWms": {
       64              "base_url": "https://test.wms.example.com",
       65              "username": "test_user",
>>>    66              "password": "test_password",
       67              "api_version": "v10",
       68              "page_size": 100,
       69              "timeout": 30,
       70              "max_retries": 3,
```

**Decisão**:

### 2 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/integration/test_wms_connection.py:183` · **CWE**: -

```python
      179          bad_settings = FlextTapOracleWmsSettings.model_validate({
      180              "TapOracleWms": {
      181                  "base_url": "https://invalid.example.com",
      182                  "username": "invalid",
>>>   183                  "password": "invalid",
      184              }
      185          })
      186          tap = FlextTapOracleWms.from_settings(bad_settings)
      187          result = tap.validate_configuration()
```

**Decisão**:

### 3 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config.py:32` · **CWE**: -

```python
       28          settings = FlextTapOracleWmsSettings.model_validate({
       29              "TapOracleWms": {
       30                  "base_url": "https://wms.example.com",
       31                  "username": "test_user",
>>>    32                  "password": "test_pass",
       33              }
       34          })
       35          namespace = settings.TapOracleWms
       36          tm.that(namespace.base_url.rstrip("/"), eq="https://wms.example.com")
```

**Decisão**:

### 4 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config.py:57` · **CWE**: -

```python
       53          settings = FlextTapOracleWmsSettings.model_validate({
       54              "TapOracleWms": {
       55                  "base_url": "https://prod.wms.example.com",
       56                  "username": "prod_user",
>>>    57                  "password": "prod_pass",
       58                  "api_version": "v11",
       59                  "timeout": 60,
       60                  "max_retries": 5,
       61                  "retry_delay": 2,
```

**Decisão**:

### 5 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config.py:239` · **CWE**: -

```python
      235          settings = FlextTapOracleWmsSettings.model_validate({
      236              "TapOracleWms": {
      237                  "base_url": "https://wms.example.com",
      238                  "username": "user",
>>>   239                  "password": "super_secret_password",
      240              }
      241          })
      242          password = settings.TapOracleWms.password
      243          password_value = (
```

**Decisão**:

### 6 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config_validation.py:31` · **CWE**: -

```python
       27          settings = FlextTapOracleWmsSettings.model_validate({
       28              "TapOracleWms": {
       29                  "base_url": "https://wms.example.com",
       30                  "username": "test_user",
>>>    31                  "password": "test_password",
       32              }
       33          })
       34          namespace = settings.TapOracleWms
       35          tm.that(namespace.base_url.rstrip("/"), eq="https://wms.example.com")
```

**Decisão**:

### 7 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config_validation.py:202` · **CWE**: -

```python
      198          settings = FlextTapOracleWmsSettings.model_validate({
      199              "TapOracleWms": {
      200                  "base_url": "https://wms.example.com",
      201                  "username": "user",
>>>   202                  "password": "super_secret",
      203              }
      204          })
      205          password = settings.TapOracleWms.password
      206          password_value = (
```

**Decisão**:

### 8 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_tap.py:46` · **CWE**: -

```python
       42          settings = FlextTapOracleWmsSettings.model_validate({
       43              "TapOracleWms": {
       44                  "base_url": "https://test.wms.example.com",
       45                  "username": "test_user",
>>>    46                  "password": "test_password",
       47              }
       48          })
       49          tap = FlextTapOracleWms.from_settings(settings, catalog=sample_catalog)
       50          tm.that(tap.flext_config.TapOracleWms.base_url, has="test.wms.example.com")
```

**Decisão**:

# Triagem Snyk Code (SAST) — flext-sh/flext-tap-oracle-wms

Gerado do scan Snyk da org Datacosmos (dump 2026-08-06).

**8 achados** — critical 0, high 0, medium 0, low 8

| categoria | achados |
|---|---|
| Use of Hardcoded Passwords | 8 |

## Achados

Coluna **Decisão**: `corrigir` / `falso-positivo` / `risco-aceito`.

| # | sev | categoria | arquivo | linha | CWE | Decisão |
|---|---|---|---|---|---|---|
| 1 | low | Use of Hardcoded Passwords | `tests/conftest.py` | 66 | - | |
| 2 | low | Use of Hardcoded Passwords | `tests/integration/test_wms_connection.py` | 183 | - | |
| 3 | low | Use of Hardcoded Passwords | `tests/unit/test_config.py` | 32 | - | |
| 4 | low | Use of Hardcoded Passwords | `tests/unit/test_config.py` | 57 | - | |
| 5 | low | Use of Hardcoded Passwords | `tests/unit/test_config.py` | 239 | - | |
| 6 | low | Use of Hardcoded Passwords | `tests/unit/test_config_validation.py` | 31 | - | |
| 7 | low | Use of Hardcoded Passwords | `tests/unit/test_config_validation.py` | 202 | - | |
| 8 | low | Use of Hardcoded Passwords | `tests/unit/test_tap.py` | 46 | - | |

## Como triar

1. Abrir `arquivo:linha` e seguir o fluxo de dados até o sink.
2. Classificar: **corrigir** (entrada externa alcança o sink sem sanitização), **falso-positivo** (credencial de fixture, path de constante — registrar em `.snyk` com justificativa), **risco-aceito** (com prazo de revisão).

Dados brutos: `~/snyk-violations/sast/flext-sh__flext-tap-oracle-wms.sast.json`


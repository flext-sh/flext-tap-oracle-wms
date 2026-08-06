# Triagem SonarCloud — flext-sh/flext-tap-oracle-wms

Gerado do dump da plataforma SonarCloud (2026-08-06).

Bead de rastreio: `mro-2wjm.19`

## Resumo

**10 issues** — BLOCKER 0, CRITICAL 2, MAJOR 6, MINOR 2
Tipos: VULNERABILITY 4, BUG 0, CODE_SMELL 6

| regra | issues |
|---|---|
| `python:S3776` | 2 |
| `githubactions:S8233` | 2 |
| `githubactions:S8264` | 1 |
| `python:S108` | 1 |
| `text:S8565` | 1 |
| `python:S3358` | 1 |
| `python:S7504` | 1 |
| `python:S8714` | 1 |

## Issues

Coluna **Decisão**: `corrigir` / `falso-positivo` / `risco-aceito`.

| # | sev | tipo | regra | componente | linha | Decisão |
|---|---|---|---|---|---|---|
| 1 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_tap_oracle_wms/streams.py` | 182 | |
| 2 | CRITICAL | CODE_SMELL | `python:S3776` | `src/flext_tap_oracle_wms/tap.py` | 83 | |
| 3 | MAJOR | VULNERABILITY | `githubactions:S8264` | `.github/workflows/docs.yml` | 18 | |
| 4 | MAJOR | VULNERABILITY | `githubactions:S8233` | `.github/workflows/docs.yml` | 19 | |
| 5 | MAJOR | VULNERABILITY | `githubactions:S8233` | `.github/workflows/docs.yml` | 20 | |
| 6 | MAJOR | CODE_SMELL | `python:S108` | `examples/01_basic_usage.py` | 50 | |
| 7 | MAJOR | VULNERABILITY | `text:S8565` | `pyproject.toml` | - | |
| 8 | MAJOR | CODE_SMELL | `python:S3358` | `src/flext_tap_oracle_wms/api.py` | 42 | |
| 9 | MINOR | CODE_SMELL | `python:S7504` | `conftest.py` | 20 | |
| 10 | MINOR | CODE_SMELL | `python:S8714` | `tests/integration/test_wms_connection.py` | 92 | |

## Como triar

1. **BLOCKER e CRITICAL primeiro**, e todo VULNERABILITY independente de severidade.
2. Classificar: **corrigir**, **falso-positivo** (marcar na plataforma SonarCloud com justificativa), **risco-aceito** (com prazo).
3. CODE_SMELL em volume alto sugere padrão — corrigir a causa raiz, não issue a issue.

Dados brutos: `~/sonarqube-violations/by-repo/flext-sh__flext-tap-oracle-wms.json`


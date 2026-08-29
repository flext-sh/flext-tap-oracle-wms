# Triagem SonarCloud — flext-sh/flext-tap-oracle-wms

Gerado do dump da plataforma SonarCloud (2026-08-06).

Bead: `mro-2wjm.19`

## Resumo

**10 issues** — BLOCKER 0, CRITICAL 2, MAJOR 6, MINOR 2
Tipos: VULNERABILITY 4, BUG 0, CODE_SMELL 6 · **Debt total: 71min**

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

## Como usar

Cada issue traz a **mensagem do SonarQube** (descreve o problema e o impacto), o **código real** (linha `>>>`), o tipo e o effort estimado.
**Decisão**: `corrigir` / `falso-positivo` (marcar na plataforma com justificativa) / `risco-aceito`. Ordem: BLOCKER → CRITICAL → VULNERABILITY → MAJOR. CODE_SMELL em volume pede correção de padrão.

## Issues

### 1 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_tap_oracle_wms/streams.py:182` · **Effort**: 12min

> Refactor this function to reduce its Cognitive Complexity from 22 to the 15 allowed.

```python
      178          """Return the replication key for this stream."""
      179          return self.stream_replication_key
      180  
      181      @override
>>>   182      def post_process(
      183          self, row: t.JsonDict, context: t.ScalarMapping | None = None
      184      ) -> t.JsonDict:
      185          """Post-process a record."""
      186          conv = u.TapOracleWms.MappingConversion
```

**Decisão**: pendente

### 2 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_tap_oracle_wms/tap.py:83` · **Effort**: 19min

> Refactor this function to reduce its Cognitive Complexity from 29 to the 15 allowed.

```python
       79              u.TapOracleWms.MappingConversion.safe_str_dict(validated_catalog)
       80          )
       81  
       82      @staticmethod
>>>    83      def _to_typed_catalog(raw: t.JsonMapping) -> t.MutableJsonMapping:
       84          """Convert a raw catalog mapping into a validated Singer catalog dict."""
       85          raw_streams = raw.get("streams")
       86          raw_streams_seq: t.JsonList = (
       87              raw_streams
```

**Decisão**: pendente

### 3 · 🟡 MAJOR · VULNERABILITY · `githubactions:S8264`
**Local**: `.github/workflows/docs.yml:18` · **Effort**: 5min

> Move this read permission from workflow level to job level.

```yaml
       14        - ".github/workflows/docs.yml"
       15    workflow_dispatch:
       16  
       17  permissions:
>>>    18    contents: read
       19    pages: write
       20    id-token: write
       21  
       22  concurrency:
```

**Decisão**: pendente

### 4 · 🟡 MAJOR · VULNERABILITY · `githubactions:S8233`
**Local**: `.github/workflows/docs.yml:19` · **Effort**: 5min

> Move this write permission from workflow level to job level.

```yaml
       15    workflow_dispatch:
       16  
       17  permissions:
       18    contents: read
>>>    19    pages: write
       20    id-token: write
       21  
       22  concurrency:
       23    group: pages
```

**Decisão**: pendente

### 5 · 🟡 MAJOR · VULNERABILITY · `githubactions:S8233`
**Local**: `.github/workflows/docs.yml:20` · **Effort**: 5min

> Move this write permission from workflow level to job level.

```yaml
       16  
       17  permissions:
       18    contents: read
       19    pages: write
>>>    20    id-token: write
       21  
       22  concurrency:
       23    group: pages
       24    cancel-in-progress: false
```

**Decisão**: pendente

### 6 · 🟡 MAJOR · CODE_SMELL · `python:S108`
**Local**: `examples/01_basic_usage.py:50` · **Effort**: 5min

> Either remove or fill this block of code.

```python
       46      for stream_entry in catalog.streams:
       47          _ = stream_entry.schema_definition
       48      streams = tap.discover_streams()
       49      for _stream in streams:
>>>    50          pass
       51      tap.get_implementation_metrics()
       52      return 0
       53  
       54  
```

**Decisão**: pendente

### 7 · 🟡 MAJOR · VULNERABILITY · `text:S8565`
**Local**: `pyproject.toml:-` · **Effort**: 5min

> Dependency versions are not predictable if the lock file (uv.lock, poetry.lock, pdm.lock or pylock.toml) is missing.

**Decisão**: pendente

### 8 · 🟡 MAJOR · CODE_SMELL · `python:S3358`
**Local**: `src/flext_tap_oracle_wms/api.py:42` · **Effort**: 5min

> Extract this nested conditional expression into an independent statement.

```python
       38          of crashing at construction when no config is pre-supplied.
       39          """
       40          raw_config = (
       41              t.json_dict_adapter().validate_python(
>>>    42                  settings.model_dump() if hasattr(settings, "model_dump") else settings
       43              )
       44              if settings is not None
       45              else None
       46          )
```

**Decisão**: pendente

### 9 · ⚪ MINOR · CODE_SMELL · `python:S7504`
**Local**: `conftest.py:20` · **Effort**: 5min

> Remove this unnecessary `list()` call on an already iterable object.

```python
       16      if (
       17          existing_package is None
       18          or Path(getattr(existing_package, "__file__", "")).resolve() != init_file
       19      ):
>>>    20          for module_name in list(sys.modules):
       21              if module_name == package_name or module_name.startswith(
       22                  f"{package_name}."
       23              ):
       24                  sys.modules.pop(module_name, None)
```

**Decisão**: pendente

### 10 · ⚪ MINOR · CODE_SMELL · `python:S8714`
**Local**: `tests/integration/test_wms_connection.py:92` · **Effort**: 5min

> Remove this try/except block and let the test fail naturally if an exception is raised.

```python
       88              pytest.skip(f"Stream {stream_name} not available")
       89          records: list[t.JsonMapping] = []
       90          record_count = 0
       91          max_records = 5
>>>    92          try:
       93              for record in stream.get_records(context=None):
       94                  records.append(record)
       95                  record_count += 1
       96                  if record_count >= max_records:
```

**Decisão**: pendente

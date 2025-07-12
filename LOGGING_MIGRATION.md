# Logging Migration Report for flext-tap-oracle-wms

## Summary

Total files with logging imports: 11

## Files to Migrate

- `src/tap_oracle_wms/critical_validation.py:10` - `import logging`
- `src/tap_oracle_wms/discovery.py:10` - `import logging`
- `src/tap_oracle_wms/entity_discovery.py:9` - `import logging`
- `src/tap_oracle_wms/schema_generator.py:10` - `import logging`
- `src/tap_oracle_wms/config_mapper.py:12` - `import logging`
- `src/tap_oracle_wms/config_validator.py:10` - `import logging`
- `src/tap_oracle_wms/cache_manager.py:9` - `import logging`
- `src/tap_oracle_wms/cli_enhanced.py:7` - `import logging`
- `src/tap_oracle_wms/client.py:5` - `import logging`
- `src/tap_oracle_wms/auth.py:35` - `import logging`
- `src/tap_oracle_wms/streams.py:16` - `import logging`

## Migration Steps

1. Replace logging imports:

   ```python
   # Old
   import logging
   logger = logging.getLogger(__name__)

   # New
   from flext_observability.logging import get_logger
   logger = get_logger(__name__)
   ```

2. Add setup_logging to your main entry point:

   ```python
   from flext_observability import setup_logging

   setup_logging(
       service_name="flext-tap-oracle-wms",
       log_level="INFO",
       json_logs=True
   )
   ```

3. Update logging calls to use structured format:

   ```python
   # Old
   logger.info("Processing %s items", count)

   # New
   logger.info("Processing items", count=count)
   ```

See `examples/logging_migration.py` for a complete example.

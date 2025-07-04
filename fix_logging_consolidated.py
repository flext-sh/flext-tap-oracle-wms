#!/usr/bin/env python3
"""Corrigir logging para usar logger.error() consolidado ao invés de múltiplas mensagens.
Manter apenas cases legítimos de logger.exception() para erros verdadeiramente inesperados.
"""

import os
import re


def fix_streams_logging() -> None:
    """Corrigir logging em streams.py."""
    file_path = "src/tap_oracle_wms/streams.py"

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Corrigir pagination error logging - consolidar em uma mensagem
    content = re.sub(
        r'logger\.exception\(\s*"Critical pagination failure:.*?".*?\)\s*#.*?msg = f"Pagination JSON parsing failed: \{e\}"\s*raise RetriableAPIError\(msg\) from e',
        """error_msg = (
                f"❌ CRITICAL PAGINATION ERROR - JSON parsing failed - "
                f"Status: {response.status_code}, "
                f"Content-Type: {response.headers.get('Content-Type', 'unknown')}, "
                f"Error: {e}"
            )
            logger.error(error_msg)
            raise RetriableAPIError(error_msg) from e""",
        content,
        flags=re.DOTALL,
    )

    # Corrigir pagination check error - consolidar
    content = re.sub(
        r'logger\.exception\(\s*"Pagination check failed.*?"\s*\)',
        """error_msg = f"❌ PAGINATION CHECK FAILED - terminating data extraction to prevent incomplete results: {e}"
            logger.error(error_msg)""",
        content,
        flags=re.DOTALL,
    )

    # Corrigir bookmark validation error - consolidar
    content = re.sub(
        r'error_msg = \(\s*f"Critical bookmark validation failure.*?\)\s*self\.logger\.exception\(error_msg\)',
        """error_msg = (
                    f"❌ CRITICAL BOOKMARK ERROR - Entity: {self._entity_name} - "
                    f"Invalid bookmark '{bookmark}' (expected integer ID) - "
                    f"This will cause data sync issues - Error: {e}"
                )
                self.logger.error(error_msg)""",
        content,
        flags=re.DOTALL,
    )

    # Corrigir timezone error - consolidar
    content = re.sub(
        r'error_msg = \(\s*f"Critical timestamp error:.*?\)\s*self\.logger\.exception\(error_msg\)',
        """error_msg = (
                    f"❌ CRITICAL TIMEZONE ERROR - Entity: {self._entity_name} - "
                    f"Missing timezone for start_date '{start_date}' - "
                    f"This can cause data consistency issues"
                )
                self.logger.error(error_msg)""",
        content,
        flags=re.DOTALL,
    )

    # Corrigir JSON parsing error - consolidar
    content = re.sub(
        r'self\.logger\.exception\(\s*"Critical JSON parsing error.*?\)\s*msg = f"Invalid JSON response.*?"\s*raise RetriableAPIError\(msg\) from e',
        """error_msg = (
                f"❌ CRITICAL JSON ERROR - Entity: {self._entity_name} - "
                f"Invalid JSON response (Status: {response.status_code}, "
                f"Content-Type: {response.headers.get('Content-Type', 'unknown')}, "
                f"Size: {len(response.content)} bytes) - Error: {e}"
            )
            self.logger.error(error_msg)
            raise RetriableAPIError(error_msg) from e""",
        content,
        flags=re.DOTALL,
    )

    # Corrigir type conversion errors - consolidar
    content = re.sub(
        r'error_msg = \(\s*f"Critical type conversion error.*?\)\s*self\.logger\.exception\(error_msg\)',
        """error_msg = (
                f"❌ TYPE CONVERSION ERROR - Field: '{field_name}' - "
                f"Cannot convert '{field_value}' ({type(field_value).__name__}) "
                f"to {original_type if 'original_type' in locals() else actual_type} - Error: {e}"
            )
            self.logger.error(error_msg)""",
        content,
        flags=re.DOTALL,
    )

    # Corrigir timestamp normalization error - consolidar
    content = re.sub(
        r'error_msg = \(\s*f"Critical timestamp format error:.*?\)\s*self\.logger\.exception\(error_msg\)',
        """error_msg = (
                f"❌ TIMESTAMP FORMAT ERROR - Cannot normalize '{timestamp_value}' - "
                f"Invalid timestamp data may cause downstream issues - Error: {e}"
            )
            self.logger.error(error_msg)""",
        content,
        flags=re.DOTALL,
    )

    # Corrigir pagination query parameter error - consolidar
    content = re.sub(
        r'self\.logger\.exception\("Failed to parse pagination query parameters: %s", e\)\s*msg = f"Invalid pagination token query: \{e\}"\s*raise ValueError\(msg\) from e',
        """error_msg = f"❌ PAGINATION PARAMS ERROR - Failed to parse query parameters: {e}"
            self.logger.error(error_msg)
            raise ValueError(error_msg) from e""",
        content,
        flags=re.DOTALL,
    )

    # Manter apenas os logger.exception() legítimos:
    # 1. HTTP request errors (truly unexpected)
    # 2. Unexpected stream errors (catch-all)
    # 3. Fatal API errors (unexpected)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_discovery_logging() -> None:
    """Corrigir logging em discovery.py."""
    file_path = "src/tap_oracle_wms/discovery.py"

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Corrigir authentication setup error - consolidar
    content = re.sub(
        r'logger\.exception\("Authentication setup failed: %s", e\)',
        """error_msg = f"❌ AUTHENTICATION SETUP FAILED - Configuration error: {e}"
            logger.error(error_msg)""",
        content,
    )

    # Corrigir authentication import error - consolidar
    content = re.sub(
        r'logger\.exception\("Authentication module import failed: %s", e\)',
        """error_msg = f"❌ AUTH MODULE IMPORT FAILED - Could not import authentication: {e}"
            logger.error(error_msg)""",
        content,
    )

    # Corrigir entity discovery HTTP errors - consolidar
    content = re.sub(
        r'logger\.exception\(\s*"❌ HTTP ERROR.*?\)\s*logger\.exception\(f"📄 ERROR RESPONSE:.*?\)',
        """error_msg = (
                f"❌ DISCOVERY HTTP ERROR - Failed with HTTP {e.response.status_code} - "
                f"URL: {e.request.url} - Response: {e.response.text[:200]}"
            )
            logger.error(error_msg)""",
        content,
        flags=re.DOTALL,
    )

    # Corrigir network errors - consolidar
    content = re.sub(
        r'logger\.exception\(\s*"❌ NETWORK ERROR.*?\)',
        """error_msg = f"❌ NETWORK ERROR - Connection/timeout during entity discovery: {str(e)}"
            logger.error(error_msg)""",
        content,
    )

    # Corrigir parsing errors - consolidar
    content = re.sub(
        r'logger\.exception\(\s*"❌ PARSING ERROR.*?\)',
        """error_msg = f"❌ PARSING ERROR - Data parsing during entity discovery: {str(e)}"
            logger.error(error_msg)""",
        content,
    )

    # Corrigir entity description errors - consolidar
    content = re.sub(
        r'logger\.exception\("Entity %s does not exist.*?" % entity_name.*?\)',
        """error_msg = f"❌ ENTITY NOT FOUND - Entity '{entity_name}' does not exist (404) - check name or permissions"
            logger.error(error_msg)""",
        content,
    )

    # Outros erros similares em discovery.py
    content = re.sub(
        r'logger\.exception\("HTTP error describing entity.*?\)',
        """error_msg = f"❌ HTTP ERROR - Failed to describe entity {entity_name}: HTTP {e.response.status_code}"
            logger.error(error_msg)""",
        content,
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_auth_logging() -> None:
    """Corrigir logging em auth.py."""
    file_path = "src/tap_oracle_wms/auth.py"

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Corrigir auth credential error - consolidar
    content = re.sub(
        r'logger\.exception\(\s*"Critical authentication error:.*?\)',
        """error_msg = (
                f"❌ CRITICAL AUTH ERROR - Invalid credentials format for user '{self.username}' - "
                f"Username and password must be non-empty strings - Error: {e}"
            )
            logger.error(error_msg)""",
        content,
        flags=re.DOTALL,
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_tap_logging() -> None:
    """Corrigir logging em tap.py."""
    file_path = "src/tap_oracle_wms/tap.py"

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Corrigir schema generation errors - consolidar
    content = re.sub(
        r'self\.logger\.exception\(f"❌ SCHEMA ERROR.*?\)',
        """error_msg = f"❌ SCHEMA ERROR - {entity_name} - Schema generation returned None - entity may not exist or lack permissions"
            self.logger.error(error_msg)""",
        content,
    )

    content = re.sub(
        r'self\.logger\.exception\(f"❌ ENTITY FAILED.*?\)',
        """error_msg = f"❌ ENTITY FAILED - {entity_name} - {error_msg}"
            self.logger.error(error_msg)""",
        content,
    )

    # Manter logger.exception apenas para erros verdadeiramente inesperados em schema generation

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> None:
    """Executar todas as correções de logging."""
    os.chdir("/home/marlonsc/flext/flext-tap-oracle-wms")

    try:
        fix_streams_logging()
        fix_discovery_logging()
        fix_auth_logging()
        fix_tap_logging()

    except Exception:
        raise


if __name__ == "__main__":
    main()

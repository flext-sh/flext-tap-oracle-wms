#!/usr/bin/env python3
"""Final precision PEP 8 fixer for tap-oracle-wms project."""

from pathlib import Path


class FinalPEP8PrecisionFixer:
    """Precision fixer for remaining PEP 8 violations."""

    def __init__(self) -> None:
        """Initialize the fixer."""
        self.fixes_applied = 0

    def fix_import_order_issues(self) -> None:
        """Fix import order issues with precision."""
        # Specific fixes for known files
        fixes = {
            "src/tap_oracle_wms/cli.py": self._fix_cli_imports,
            "src/tap_oracle_wms/monitoring.py": self._fix_monitoring_imports,
            "src/tap_oracle_wms/discovery.py": self._fix_discovery_imports,
            "src/tap_oracle_wms/tap.py": self._fix_tap_imports,
            "src/tap_oracle_wms/streams.py": self._fix_streams_imports,
            "src/tap_oracle_wms/config.py": self._fix_config_spacing,
        }

        for file_path, fix_func in fixes.items():
            if Path(file_path).exists() and fix_func(file_path):
                self.fixes_applied += 1

    def _fix_cli_imports(self, file_path: str) -> bool:
        """Fix CLI imports specifically."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix the import order issues
        import_section = """from pathlib import Path
from typing import TYPE_CHECKING, Any
import asyncio
import contextlib
import json
import logging
import sys

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import click

from .discovery import EntityDiscovery, SchemaGenerator
from .monitoring import TAPMonitor
from .tap import TapOracleWMS"""

        correct_import_section = """import asyncio
import contextlib
import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .discovery import EntityDiscovery, SchemaGenerator
from .monitoring import TAPMonitor
from .tap import TapOracleWMS"""

        content = content.replace(import_section, correct_import_section)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    def _fix_monitoring_imports(self, file_path: str) -> bool:
        """Fix monitoring imports specifically."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix the mixed imports
        wrong_section = """from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any
from typing_extensions import Self
import asyncio
import contextlib
import json
import logging
import time

from dataclasses import dataclass, field
import psutil"""

        correct_section = """import asyncio
import contextlib
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

import psutil
from typing_extensions import Self"""

        content = content.replace(wrong_section, correct_section)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    def _fix_discovery_imports(self, file_path: str) -> bool:
        """Fix discovery imports specifically."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix the mixed imports
        wrong_section = """from datetime import datetime, timedelta, timezone
from typing import Any
import fnmatch
import httpx
import logging"""

        correct_section = """import fnmatch
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx"""

        content = content.replace(wrong_section, correct_section)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    def _fix_tap_imports(self, file_path: str) -> bool:
        """Fix tap imports specifically."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix the mixed imports
        wrong_section = """from itertools import starmap
from typing import Any
import asyncio
import logging

from singer_sdk import Stream, Tap

from .config import config_schema, validate_auth_config, validate_pagination_config
from .discovery import EntityDiscovery, SchemaGenerator
from .monitoring import TAPMonitor
from .streams import WMSAdvancedStream"""

        correct_section = """import asyncio
import logging
from itertools import starmap
from typing import Any

from singer_sdk import Stream, Tap

from .config import config_schema, validate_auth_config, validate_pagination_config
from .discovery import EntityDiscovery, SchemaGenerator
from .monitoring import TAPMonitor
from .streams import WMSAdvancedStream"""

        content = content.replace(wrong_section, correct_section)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    def _fix_streams_imports(self, file_path: str) -> bool:
        """Fix streams imports specifically."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix the mixed imports
        wrong_section = """from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse
import json
import logging
import time"""

        correct_section = """import json
import logging
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse"""

        content = content.replace(wrong_section, correct_section)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    def _fix_config_spacing(self, file_path: str) -> bool:
        """Fix config spacing issues."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix the missing newlines after imports
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            fixed_lines.append(line)

            # Add proper spacing after imports
            if (
                line.strip() == "from typing import Any"
                and i + 1 < len(lines)
                and lines[i + 1].strip() == ""
                and i + 2 < len(lines)
                and lines[i + 2].strip() == "# Constants"
            ):
                # Need one more blank line
                fixed_lines.append("")

        content = "\n".join(fixed_lines)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    def fix_line_length_issues(self) -> None:
        """Fix specific line length violations."""
        line_fixes = {
            "src/tap_oracle_wms/tap.py": [
                # Fix the specific long line
                (
                    '            f"(bookmark: {bookmark_value}, overlap: {overlap_minutes}min)",',
                    '            f"(bookmark: {bookmark_value}, "\n            f"overlap: {overlap_minutes}min)",',
                ),
            ]
        }

        for file_path, fixes in line_fixes.items():
            if Path(file_path).exists():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()

                    original_content = content

                    for old_text, new_text in fixes:
                        content = content.replace(old_text, new_text)

                    if content != original_content:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        self.fixes_applied += 1

                except Exception:
                    pass

    def fix_missing_newlines(self) -> None:
        """Fix missing newlines at end of files."""
        for file_path in Path("src").rglob("*.py"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                if not content.endswith("\n"):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content + "\n")
                    self.fixes_applied += 1

            except Exception:
                pass

    def run_all_fixes(self) -> None:
        """Run all precision fixes."""
        self.fix_import_order_issues()

        self.fix_line_length_issues()

        self.fix_missing_newlines()

        # Run validation
        import subprocess

        try:
            result = subprocess.run(
                ["python", "strict_pep_validator.py"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if result.stdout:
                lines = result.stdout.split("\n")
                for line in lines[:15]:  # Show first 15 lines
                    if line.strip():
                        pass
        except Exception:
            pass


def main() -> None:
    """Run final precision PEP 8 fixes."""
    fixer = FinalPEP8PrecisionFixer()
    fixer.run_all_fixes()


if __name__ == "__main__":
    main()

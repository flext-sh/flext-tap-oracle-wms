#!/usr/bin/env python3
"""Comprehensive PEP 8 fixer for tap-oracle-wms project."""

import contextlib
from pathlib import Path
import re


class ComprehensivePEP8Fixer:
    """Advanced PEP 8 compliance fixer."""

    def __init__(self) -> None:
        """Initialize the fixer."""
        self.fixes_applied = 0
        self.files_processed = 0

    def fix_import_order(self, content: str) -> str:
        """Fix import order according to PEP 8."""
        lines = content.split("\n")

        # Find import block
        import_start = None
        import_end = None

        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")):
                if import_start is None:
                    import_start = i
                import_end = i
            elif import_start is not None and line.strip() and not line.strip().startswith("#"):
                break

        if import_start is None:
            return content

        # Extract imports
        before_imports = lines[:import_start]
        imports = lines[import_start:import_end + 1]
        after_imports = lines[import_end + 1:]

        # Categorize imports
        future_imports = []
        standard_imports = []
        third_party_imports = []
        local_imports = []

        standard_modules = {
            "abc", "argparse", "array", "ast", "asyncio", "base64", "collections",
            "contextlib", "copy", "csv", "datetime", "decimal", "enum", "fnmatch",
            "functools", "getpass", "glob", "hashlib", "heapq", "html", "http",
            "importlib", "inspect", "io", "itertools", "json", "logging", "math",
            "multiprocessing", "operator", "os", "pathlib", "pickle", "platform",
            "queue", "random", "re", "shutil", "socket", "sqlite3", "statistics",
            "string", "subprocess", "sys", "tempfile", "threading", "time",
            "traceback", "typing", "urllib", "uuid", "warnings", "weakref", "xml"
        }

        for import_line in imports:
            line = import_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("from __future__"):
                future_imports.append(import_line)
            elif any(f"from {mod}" in line or f"import {mod}" in line
                    for mod in standard_modules):
                standard_imports.append(import_line)
            elif "tap_oracle_wms" in line or line.startswith("from ."):
                local_imports.append(import_line)
            else:
                third_party_imports.append(import_line)

        # Sort each category
        future_imports.sort()
        standard_imports.sort()
        third_party_imports.sort()
        local_imports.sort()

        # Reassemble
        new_imports = []
        if future_imports:
            new_imports.extend(future_imports)
            new_imports.append("")
        if standard_imports:
            new_imports.extend(standard_imports)
            new_imports.append("")
        if third_party_imports:
            new_imports.extend(third_party_imports)
            new_imports.append("")
        if local_imports:
            new_imports.extend(local_imports)

        # Remove trailing empty line if it's the last section
        if new_imports and new_imports[-1] == "":
            new_imports.pop()

        # Combine all parts
        result = before_imports + new_imports + after_imports
        return "\n".join(result)

    def fix_line_length(self, content: str) -> str:
        """Fix lines that are too long."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            if len(line) <= 88:
                fixed_lines.append(line)
                continue

            # Handle different types of long lines
            if "description=" in line and '"' in line:
                # Break long description strings
                fixed_lines.append(self._break_description_line(line))
            elif line.strip().startswith("#"):
                # Break long comments
                fixed_lines.append(self._break_comment_line(line))
            elif " and " in line and len(line) > 88:
                # Break logical expressions
                fixed_lines.append(self._break_logical_line(line))
            elif "(" in line and ")" in line:
                # Break function calls/definitions
                fixed_lines.append(self._break_function_line(line))
            else:
                # Default: try to break at logical points
                fixed_lines.append(self._break_generic_line(line))

        return "\n".join(fixed_lines)

    def _break_description_line(self, line: str) -> str:
        """Break long description lines."""
        indent = len(line) - len(line.lstrip())
        indent_str = " " * indent

        desc_match = re.search(r'description="([^"]+)"', line)
        if desc_match:
            desc_text = desc_match.group(1)
            if len(desc_text) > 50:
                # Find good break points
                for break_word in [" and ", " for ", " with ", " in ", " of ", " to "]:
                    if break_word in desc_text:
                        parts = desc_text.split(break_word, 1)
                        return line.replace(
                            f'description="{desc_text}"',
                            f'description="{parts[0]} "\n{indent_str}    "{break_word.strip()} {parts[1]}"'
                        )

        return line

    def _break_comment_line(self, line: str) -> str:
        """Break long comment lines."""
        indent = len(line) - len(line.lstrip())
        indent_str = " " * indent

        if len(line) > 88 and line.strip().startswith("#"):
            comment_text = line.strip()[1:].strip()
            # Break at 80 characters to leave room for # and indent
            break_point = 80 - indent - 2
            if len(comment_text) > break_point:
                # Find last space before break point
                space_pos = comment_text.rfind(" ", 0, break_point)
                if space_pos > 0:
                    first_part = comment_text[:space_pos]
                    second_part = comment_text[space_pos + 1:]
                    return f"{indent_str}# {first_part}\n{indent_str}# {second_part}"

        return line

    def _break_logical_line(self, line: str) -> str:
        """Break logical expressions."""
        if " and " in line:
            indent = len(line) - len(line.lstrip())
            indent_str = " " * (indent + 4)
            parts = line.split(" and ", 1)
            return f"{parts[0]} and \\\n{indent_str}{parts[1]}"
        return line

    def _break_function_line(self, line: str) -> str:
        """Break function definition/call lines."""
        if "(" in line and ")" in line and len(line) > 88:
            # Simple function parameter breaking
            if line.count(",") > 0:
                indent = len(line) - len(line.lstrip())
                indent_str = " " * (indent + 4)

                # Find function start
                func_start = line.find("(")
                if func_start > 0:
                    before_params = line[:func_start + 1]
                    params_part = line[func_start + 1:line.rfind(")")]
                    after_params = line[line.rfind(")"):]

                    # Break parameters
                    params = [p.strip() for p in params_part.split(",")]
                    if len(params) > 1:
                        param_lines = [before_params]
                        for i, param in enumerate(params):
                            if param:
                                if i == len(params) - 1:
                                    param_lines.append(f"{indent_str}{param},")
                                else:
                                    param_lines.append(f"{indent_str}{param},")
                        param_lines.append(f"{' ' * indent}{after_params}")
                        return "\n".join(param_lines)

        return line

    def _break_generic_line(self, line: str) -> str:
        """Break generic long lines."""
        if len(line) > 88:
            # Try to break at logical operators
            for op in [" + ", " - ", " * ", " / ", " == ", " != ", " and ", " or "]:
                if op in line:
                    pos = line.find(op)
                    if 40 < pos < 80:  # Good break position
                        indent = len(line) - len(line.lstrip())
                        indent_str = " " * (indent + 4)
                        first_part = line[:pos + len(op.split()[0]) + 1]
                        second_part = line[pos + len(op.split()[0]) + 1:]
                        return f"{first_part} \\\n{indent_str}{second_part.lstrip()}"

        return line

    def fix_whitespace_issues(self, content: str) -> str:
        """Fix trailing whitespace and other whitespace issues."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()

            # Fix multiple consecutive blank lines (max 2)
            if not line.strip():
                fixed_lines.append("")
            else:
                fixed_lines.append(line)

        # Remove excessive blank lines at end
        while fixed_lines and not fixed_lines[-1].strip():
            fixed_lines.pop()

        # Ensure file ends with single newline
        if fixed_lines:
            fixed_lines.append("")

        return "\n".join(fixed_lines)

    def fix_blank_line_issues(self, content: str) -> str:
        """Fix blank line issues around imports and functions."""
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            fixed_lines.append(line)

            # Add blank lines after imports if missing
            if (line.strip().startswith(("import ", "from ")) and
                i + 1 < len(lines) and
                lines[i + 1].strip() and
                not lines[i + 1].strip().startswith(("import ", "from ", "#"))):
                # Check if we need to add blank lines
                if i + 1 < len(lines) and not lines[i + 1].strip().startswith("if TYPE_CHECKING"):
                    fixed_lines.extend(("", ""))

        return "\n".join(fixed_lines)

    def process_file(self, file_path: Path) -> bool:
        """Process a single file for PEP 8 compliance."""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            content = original_content

            # Apply fixes
            content = self.fix_import_order(content)
            content = self.fix_line_length(content)
            content = self.fix_whitespace_issues(content)
            content = self.fix_blank_line_issues(content)

            # Write back if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.fixes_applied += 1
                return True

            return False

        except Exception:
            return False

    def fix_all_files(self) -> None:
        """Fix all Python files in the project."""
        # Get all Python files
        src_files = list(Path("src").rglob("*.py"))
        example_files = list(Path("examples").glob("*.py"))
        root_files = [f for f in Path().glob("*.py")
                     if not f.name.startswith(("strict_pep", "comprehensive_pep", "apply_"))]

        all_files = src_files + example_files + root_files

        for file_path in all_files:
            self.process_file(file_path)
            self.files_processed += 1


def main() -> None:
    """Run comprehensive PEP 8 fixing."""
    fixer = ComprehensivePEP8Fixer()
    fixer.fix_all_files()

    import subprocess
    with contextlib.suppress(Exception):
        subprocess.run(
            ["python", "strict_pep_validator.py"],
            capture_output=True,
            text=True, check=False
        )


if __name__ == "__main__":
    main()

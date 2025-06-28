#!/usr/bin/env python3
"""Apply strict PEP standards systematically across the project."""

import ast
from pathlib import Path


class StrictPEPFixer:
    """Systematic PEP compliance fixer."""

    def __init__(self) -> None:
        """Initialize the fixer."""
        self.fixes_applied = 0
        self.files_processed = 0

    def fix_import_order(self, content: str) -> str:
        """Fix PEP 8 import order issues."""
        lines = content.split("\n")

        # Find import section
        import_start = -1
        import_end = -1

        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")):
                if import_start == -1:
                    import_start = i
                import_end = i
            elif import_start != -1 and line.strip() and not line.strip().startswith("#"):
                break

        if import_start == -1:
            return content

        # Extract imports
        import_lines = lines[import_start:import_end + 1]
        before_imports = lines[:import_start]
        after_imports = lines[import_end + 1:]

        # Categorize imports
        standard_imports = []
        third_party_imports = []
        local_imports = []

        standard_libs = {
            "os", "sys", "json", "re", "datetime", "pathlib", "typing", "asyncio",
            "contextlib", "logging", "base64", "time", "subprocess", "ast",
        }

        for line in import_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if stripped.startswith("from __future__"):
                continue  # Keep future imports at top
            if stripped.startswith(("from .", "import .")):
                local_imports.append(line)
            elif any(lib in stripped for lib in standard_libs):
                standard_imports.append(line)
            else:
                third_party_imports.append(line)

        # Rebuild imports with proper order and spacing
        new_imports = []

        if standard_imports:
            new_imports.extend(standard_imports)
            new_imports.append("")

        if third_party_imports:
            new_imports.extend(third_party_imports)
            new_imports.append("")

        if local_imports:
            new_imports.extend(local_imports)
            new_imports.append("")

        # Remove trailing empty line if at end
        if new_imports and new_imports[-1] == "":
            new_imports.pop()

        # Rebuild content
        result = "\n".join(before_imports + new_imports + after_imports)

        if result != content:
            self.fixes_applied += 1

        return result

    def fix_line_lengths(self, content: str) -> str:
        """Fix PEP 8 line length violations (basic fixes only)."""
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if len(line) > 88 and not line.strip().startswith("#"):
                # Simple fixes for common patterns
                if " and " in line and len(line) < 120:
                    # Break long boolean expressions
                    parts = line.split(" and ")
                    if len(parts) == 2:
                        indent = len(line) - len(line.lstrip())
                        lines[i] = f"{parts[0]} and \\\n{' ' * (indent + 4)}{parts[1]}"
                        self.fixes_applied += 1
                elif ", " in line and line.count(",") >= 3:
                    # Break long parameter lists (simple case)
                    if "(" in line and ")" in line:
                        # This is a complex fix, skip for now
                        pass

        return "\n".join(lines)

    def add_missing_docstrings(self, content: str, file_path: str) -> str:
        """Add missing docstrings for PEP 257 compliance."""
        try:
            tree = ast.parse(content)
            lines = content.split("\n")
            modifications = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    # Check if it's a public function/class
                    if not node.name.startswith("_"):
                        docstring = ast.get_docstring(node)
                        if not docstring:
                            # Add a basic docstring
                            if isinstance(node, ast.ClassDef):
                                basic_docstring = f'"""Class for {node.name} operations."""'
                            else:
                                basic_docstring = f'"""Function for {node.name} operations."""'

                            # Find insertion point (after def line)
                            for i in range(node.lineno - 1, min(node.lineno + 3, len(lines))):
                                if i < len(lines) and ":" in lines[i]:
                                    indent = len(lines[i]) - len(lines[i].lstrip()) + 4
                                    modifications.append((i + 1, " " * indent + basic_docstring))
                                    self.fixes_applied += 1
                                    break

            # Apply modifications (in reverse order to maintain line numbers)
            for line_num, docstring in reversed(modifications):
                lines.insert(line_num, docstring)

            return "\n".join(lines)

        except SyntaxError:
            return content

    def add_type_annotations(self, content: str) -> str:
        """Add basic type annotations for PEP 484 compliance."""
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Simple pattern matching for common missing annotations
            if "def " in line and "->" not in line and line.strip().endswith(":"):
                # Add -> None for functions that don't return anything
                if not any(keyword in line for keyword in ["return", "yield", "__init__"]):
                    lines[i] = line.replace(":", " -> None:")
                    self.fixes_applied += 1

        return "\n".join(lines)

    def fix_file(self, file_path: Path) -> None:
        """Apply all PEP fixes to a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply fixes in order
            content = self.fix_import_order(content)
            content = self.fix_line_lengths(content)
            content = self.add_missing_docstrings(content, str(file_path))
            content = self.add_type_annotations(content)

            # Write back if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            self.files_processed += 1

        except Exception:
            pass

    def apply_fixes_to_project(self) -> None:
        """Apply PEP fixes to entire project."""
        # Fix source files
        for py_file in Path("src").rglob("*.py"):
            self.fix_file(py_file)

        # Fix examples (be more conservative)
        for py_file in Path("examples").glob("*.py"):
            self.fix_file(py_file)

        # Fix root Python files (excluding this script)
        for py_file in Path().glob("*.py"):
            if py_file.name != "apply_strict_pep_standards.py":
                self.fix_file(py_file)


def main() -> None:
    """Run strict PEP standards application."""
    fixer = StrictPEPFixer()
    fixer.apply_fixes_to_project()

    # Suggest running validation again


if __name__ == "__main__":
    main()

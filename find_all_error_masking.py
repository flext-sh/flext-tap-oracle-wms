#!/usr/bin/env python3
"""Script sistemático para encontrar TODOS os padrões de mascaramento de erro.
Vai ser muito mais rigoroso que as verificações anteriores.
"""

from __future__ import annotations

import os
import re


def find_error_masking_patterns():
    """Encontrar todos os padrões de mascaramento de erro."""
    masking_patterns = []
    python_files = []

    # Encontrar todos os arquivos Python
    for root, _dirs, files in os.walk("src/tap_oracle_wms"):
        python_files.extend(
            os.path.join(root, file) for file in files if file.endswith(".py")
        )

    for f in python_files:
        pass

    for file_path in python_files:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        in_except_block = False
        except_line_num = 0
        except_block_lines = []

        for i, line in enumerate(lines, 1):
            line.strip()

            # Detectar início de bloco except
            if re.match(r"\s*except\s+.*:", line):
                if in_except_block and except_block_lines:
                    # Analisar bloco anterior antes de começar novo
                    analyze_except_block(
                        file_path, except_line_num, except_block_lines, masking_patterns
                    )

                in_except_block = True
                except_line_num = i
                except_block_lines = [line]
                continue

            # Se estamos em bloco except, coletar todas as linhas
            if in_except_block:
                # Verificar se saímos do bloco except (indentação menor)
                if (
                    line.strip()
                    and not line.startswith(" ")
                    and not line.startswith("\t")
                ):
                    # Fim do bloco except
                    analyze_except_block(
                        file_path, except_line_num, except_block_lines, masking_patterns
                    )
                    in_except_block = False
                    except_block_lines = []
                elif line.strip():  # Linha não vazia no bloco
                    except_block_lines.append(line)

        # Analisar último bloco se arquivo terminou em except
        if in_except_block and except_block_lines:
            analyze_except_block(
                file_path, except_line_num, except_block_lines, masking_patterns
            )

    if masking_patterns:
        for pattern in masking_patterns:
            if pattern["code_snippet"]:
                pass

    return masking_patterns


def analyze_except_block(file_path, line_num, block_lines, masking_patterns) -> None:
    """Analisar um bloco except para padrões de mascaramento."""
    block_text = "".join(block_lines)

    # 1. Verificar return sem raise
    if "return" in block_text and "raise" not in block_text:
        # Verificar se é return None, [], {}, etc.
        if any(
            pattern in block_text
            for pattern in [
                "return None",
                "return []",
                "return {}",
                'return ""',
                "return 0",
            ]
        ):
            masking_patterns.append(
                {
                    "file": file_path,
                    "line": line_num,
                    "type": "RETURN_WITHOUT_RAISE",
                    "issue": "Retorna valor padrão em vez de re-raise da exception",
                    "code_snippet": block_text.strip(),
                }
            )

    # 2. Verificar continue sem logging apropriado
    if "continue" in block_text and "logger." not in block_text:
        masking_patterns.append(
            {
                "file": file_path,
                "line": line_num,
                "type": "CONTINUE_WITHOUT_LOG",
                "issue": "Continue sem logging apropriado da exception",
                "code_snippet": block_text.strip(),
            }
        )

    # 3. Verificar pass
    if "pass" in block_text:
        masking_patterns.append(
            {
                "file": file_path,
                "line": line_num,
                "type": "PASS_STATEMENT",
                "issue": "Statement pass que silencia exception completamente",
                "code_snippet": block_text.strip(),
            }
        )

    # 4. Verificar apenas logger.debug/info para erros críticos
    if "logger.debug" in block_text or "logger.info" in block_text:
        if "raise" not in block_text and "return" in block_text:
            masking_patterns.append(
                {
                    "file": file_path,
                    "line": line_num,
                    "type": "LOW_SEVERITY_LOG",
                    "issue": "Usando debug/info para erro que deveria ser warning/error",
                    "code_snippet": block_text.strip(),
                }
            )

    # 5. Verificar except amplos demais (bare except, Exception)
    except_line = block_lines[0] if block_lines else ""
    if "except:" in except_line or "except Exception:" in except_line:
        if "raise" not in block_text:
            masking_patterns.append(
                {
                    "file": file_path,
                    "line": line_num,
                    "type": "BARE_EXCEPT",
                    "issue": "Except muito amplo que pode mascarar erros inesperados",
                    "code_snippet": block_text.strip(),
                }
            )

    # 6. Verificar blocos sem logging algum
    if (
        "logger." not in block_text
        and "print(" not in block_text
        and "raise" not in block_text
    ) and len(block_lines) > 1:  # Mais que só a linha except
        masking_patterns.append(
            {
                "file": file_path,
                "line": line_num,
                "type": "NO_LOGGING",
                "issue": "Bloco except sem logging nem re-raise",
                "code_snippet": block_text.strip(),
            }
        )


if __name__ == "__main__":
    os.chdir("/home/marlonsc/flext/flext-tap-oracle-wms")
    patterns = find_error_masking_patterns()

    if patterns:
        pass

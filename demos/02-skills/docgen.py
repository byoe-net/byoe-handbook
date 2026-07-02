"""byoe skill: docgen
用途：为 Python 模块/函数自动生成 docstring 与 README 片段。

安装：
    cp skills/docgen.py ~/.byoe/skills/docgen.py

Agent 内使用：
    load_skill("docgen")
    skill_docgen(args_json='{"file": "src/utils.py", "output": "inline"}')
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def run(
    file: str,
    output: str = "print",   # "print" | "inline" | "readme"
    style: str = "google",   # "google" | "numpy" | "sphinx"
) -> str:
    """Generate docstrings for all undocumented functions/classes in a file.

    Args:
        file:   Python source file path.
        output: Where to put generated docs.
                "print"  — return as string (default)
                "inline" — patch the file directly (rewrites)
                "readme" — generate a README.md section instead
        style:  Docstring style: google | numpy | sphinx

    Returns:
        Generated docstrings or a README section, as a string.
    """
    import byoe

    path = Path(file).expanduser()
    if not path.exists():
        return f"Error: file not found: {file}"
    if not file.endswith(".py"):
        return "Error: docgen currently supports Python files only"

    code = path.read_text(encoding="utf-8")
    symbols = _extract_undocumented(code)

    if not symbols:
        return f"✓ All symbols in {path.name} already have docstrings."

    system = (
        f"You are a technical writer. Generate {style}-style docstrings for Python. "
        "Be precise and concise. Include Args, Returns, Raises where applicable."
    )

    if output == "readme":
        prompt = (
            f"Generate a README.md 'API Reference' section for this Python module.\n"
            f"File: {path.name}\n```python\n{code}\n```"
        )
    else:
        items = "\n".join(f"- {s}" for s in symbols)
        prompt = (
            f"Generate {style}-style docstrings for these undocumented symbols "
            f"in {path.name}:\n{items}\n\n"
            f"Source:\n```python\n{code}\n```\n\n"
            "Return ONLY the symbol name followed by its docstring, like:\n"
            "### function_name\n```\n\"\"\"...\"\"\"\n```"
        )

    agent = byoe.create_agent(system=system, tools=[])
    result = agent.chat(prompt)

    if output == "inline":
        # Append generated docstrings as comments at end of file (safe, non-destructive)
        note = f"\n\n# ── AUTO-GENERATED DOCSTRINGS (docgen skill) ──\n# {result.replace(chr(10), chr(10) + '# ')}\n"
        with open(path, "a", encoding="utf-8") as f:
            f.write(note)
        return f"✓ Docstrings appended to {path.name}"

    return result


def _extract_undocumented(code: str) -> list[str]:
    """Return names of functions/classes with no docstring."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    missing = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
            ):
                missing.append(node.name)
    return missing


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python docgen.py <file.py> [output] [style]")
        sys.exit(1)
    output = sys.argv[2] if len(sys.argv) > 2 else "print"
    style = sys.argv[3] if len(sys.argv) > 3 else "google"
    print(run(file=sys.argv[1], output=output, style=style))

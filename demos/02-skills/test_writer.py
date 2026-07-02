"""byoe skill: test_writer
用途：为 Python 函数/类自动生成 pytest 单元测试。

安装：
    cp skills/test_writer.py ~/.byoe/skills/test_writer.py

Agent 内使用：
    load_skill("test_writer")
    skill_test_writer(args_json='{"file": "src/utils.py", "symbol": "parse_date"}')
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def run(
    file: str,
    symbol: str = "",          # specific function/class to test; empty = all
    framework: str = "pytest", # "pytest" | "unittest"
    coverage: str = "normal",  # "minimal" | "normal" | "thorough"
    output: str = "print",     # "print" | "file"
) -> str:
    """Generate unit tests for a Python source file.

    Args:
        file:      Source file path.
        symbol:    Target function or class name. Empty = generate for all.
        framework: Testing framework: pytest (default) or unittest.
        coverage:  Test depth: minimal (happy path only), normal, thorough (edge cases).
        output:    "print" returns the test code; "file" writes test_<filename>.py.

    Returns:
        Generated test code as a string, or a path message if output="file".
    """
    import byoe

    path = Path(file).expanduser()
    if not path.exists():
        return f"Error: file not found: {file}"

    code = path.read_text(encoding="utf-8")
    symbols_info = _extract_symbols(code)

    if symbol:
        target = f"for `{symbol}`"
    else:
        names = [s["name"] for s in symbols_info[:10]]  # cap to avoid huge prompts
        target = f"for: {', '.join(names)}" if names else "for all public symbols"

    coverage_hints = {
        "minimal": "Include only basic happy-path tests.",
        "normal": "Include happy path, one or two edge cases, and one failure case per function.",
        "thorough": "Include happy path, boundary values, type errors, empty inputs, large inputs, and concurrent safety where relevant.",
    }

    system = (
        "You are an expert Python test engineer. Write production-quality tests. "
        "Use fixtures, parametrize where appropriate. Each test should be independent."
    )
    prompt = (
        f"Write {framework} tests {target} for {path.name}.\n"
        f"Coverage level: {coverage_hints.get(coverage, '')}\n\n"
        f"Source:\n```python\n{code}\n```\n\n"
        "Output ONLY runnable Python test code, no explanation."
    )

    agent = byoe.create_agent(system=system, tools=[])
    result = agent.chat(prompt)

    # strip markdown fences if present
    result = result.strip()
    if result.startswith("```python"):
        result = result[9:]
    if result.startswith("```"):
        result = result[3:]
    if result.endswith("```"):
        result = result[:-3]
    result = result.strip()

    if output == "file":
        out_path = path.parent / f"test_{path.stem}.py"
        out_path.write_text(result, encoding="utf-8")
        return f"✓ Tests written to {out_path}"

    return result


def _extract_symbols(code: str) -> list[dict]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    symbols = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                symbols.append({"name": node.name, "lineno": node.lineno})
        elif isinstance(node, ast.ClassDef):
            symbols.append({"name": node.name, "lineno": node.lineno})
    return sorted(symbols, key=lambda x: x["lineno"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_writer.py <file.py> [symbol] [framework] [coverage]")
        sys.exit(1)
    symbol = sys.argv[2] if len(sys.argv) > 2 else ""
    framework = sys.argv[3] if len(sys.argv) > 3 else "pytest"
    coverage = sys.argv[4] if len(sys.argv) > 4 else "normal"
    print(run(file=sys.argv[1], symbol=symbol, framework=framework, coverage=coverage))

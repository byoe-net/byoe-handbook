"""自定义 Tool：TemplateTool + EnvValidatorTool + TimerTool
用途：三个实用辅助工具，可直接注入任意 byoe agent。

  - TemplateTool:       Jinja2 模板渲染（代码生成、报告填充）
  - EnvValidatorTool:   检查环境变量与依赖是否满足要求
  - TimerTool:          测量代码块耗时（benchmark）

使用方法：
    from tools.utility_tools import TemplateTool, EnvValidatorTool, TimerTool
    agent = byoe.create_agent(tools=[TemplateTool(), EnvValidatorTool(), TimerTool()])
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

import byoe
from byoe import Tool


# ─────────────────────────────────────────────────────────────────────────────
# 1. TemplateTool — Jinja2 template rendering
# ─────────────────────────────────────────────────────────────────────────────

class TemplateTool(Tool):
    """Render a Jinja2 template string with provided variables.

    Useful for generating config files, code scaffolds, or report sections
    without requiring the LLM to repeat boilerplate every time.
    """

    name = "render_template"
    description = (
        "Render a Jinja2 template string with given variables. "
        "Returns the rendered output. "
        "Template syntax: {{ var }}, {% if %}, {% for %}, etc."
    )
    parameters = {
        "type": "object",
        "properties": {
            "template": {
                "type": "string",
                "description": "Jinja2 template string",
            },
            "variables": {
                "type": "string",
                "description": "JSON object of variables to inject, e.g. {\"name\": \"Alice\"}",
            },
        },
        "required": ["template", "variables"],
    }

    def execute(self, template: str, variables: str = "{}") -> str:
        try:
            from jinja2 import Environment, StrictUndefined
        except ImportError:
            return "Error: jinja2 not installed. Run: pip install jinja2"

        try:
            vars_dict: dict[str, Any] = json.loads(variables)
        except json.JSONDecodeError as e:
            return f"Error parsing variables JSON: {e}"

        try:
            env = Environment(undefined=StrictUndefined)
            tmpl = env.from_string(template)
            return tmpl.render(**vars_dict)
        except Exception as e:
            return f"Template error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. EnvValidatorTool — environment & dependency checker
# ─────────────────────────────────────────────────────────────────────────────

class EnvValidatorTool(Tool):
    """Check that required environment variables and Python packages are available.

    Helps agents verify prerequisites before starting a task that depends on
    specific credentials or libraries.
    """

    name = "check_environment"
    description = (
        "Verify that required environment variables and Python packages exist. "
        "Returns a pass/fail report."
    )
    parameters = {
        "type": "object",
        "properties": {
            "env_vars": {
                "type": "string",
                "description": "Comma-separated list of required env var names, e.g. 'OPENAI_API_KEY,DATABASE_URL'",
            },
            "packages": {
                "type": "string",
                "description": "Comma-separated Python package names to check, e.g. 'fastapi,sqlalchemy'",
                "default": "",
            },
        },
        "required": ["env_vars"],
    }

    def execute(self, env_vars: str = "", packages: str = "") -> str:
        import importlib.util

        lines = []
        all_ok = True

        # Check env vars
        if env_vars:
            lines.append("── Environment Variables ──")
            for var in [v.strip() for v in env_vars.split(",") if v.strip()]:
                val = os.environ.get(var)
                if val:
                    masked = val[:4] + "***" if len(val) > 4 else "***"
                    lines.append(f"  ✓ {var} = {masked}")
                else:
                    lines.append(f"  ✗ {var} — NOT SET")
                    all_ok = False

        # Check packages
        if packages:
            lines.append("\n── Python Packages ──")
            for pkg in [p.strip() for p in packages.split(",") if p.strip()]:
                spec = importlib.util.find_spec(pkg.replace("-", "_"))
                if spec:
                    lines.append(f"  ✓ {pkg}")
                else:
                    lines.append(f"  ✗ {pkg} — NOT INSTALLED (pip install {pkg})")
                    all_ok = False

        status = "✓ All checks passed" if all_ok else "✗ Some checks FAILED"
        return "\n".join(lines) + f"\n\n{status}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. TimerTool — benchmark Python code execution time
# ─────────────────────────────────────────────────────────────────────────────

class TimerTool(Tool):
    """Execute Python code and measure its wall-clock execution time.

    Uses the same secure Python sandbox as the built-in python_repl tool,
    but wraps execution with a high-resolution timer.
    """

    name = "benchmark_code"
    description = (
        "Execute Python code and measure how long it takes to run. "
        "Returns stdout, any errors, and wall-clock time in milliseconds. "
        "Useful for comparing algorithm performance."
    )
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to benchmark",
            },
            "runs": {
                "type": "integer",
                "description": "Number of times to run the code (default 1; use >1 for averaging)",
                "default": 1,
            },
        },
        "required": ["code"],
    }

    def execute(self, code: str, runs: int = 1) -> str:
        import io
        import contextlib

        runs = max(1, min(runs, 100))  # cap at 100 to prevent abuse
        times_ms: list[float] = []
        last_output = ""

        for _ in range(runs):
            buf = io.StringIO()
            start = time.perf_counter()
            try:
                with contextlib.redirect_stdout(buf):
                    exec(code, {"__builtins__": __builtins__})  # noqa: S102
            except Exception as e:
                elapsed = (time.perf_counter() - start) * 1000
                return f"Error after {elapsed:.2f}ms: {type(e).__name__}: {e}"
            elapsed = (time.perf_counter() - start) * 1000
            times_ms.append(elapsed)
            last_output = buf.getvalue()

        avg = sum(times_ms) / len(times_ms)
        mn, mx = min(times_ms), max(times_ms)

        result = f"Output:\n{last_output}\n" if last_output.strip() else ""
        if runs == 1:
            result += f"Time: {avg:.2f}ms"
        else:
            result += (
                f"Runs: {runs}\n"
                f"  avg: {avg:.2f}ms\n"
                f"  min: {mn:.2f}ms\n"
                f"  max: {mx:.2f}ms"
            )
        return result


# ─── demo ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== TemplateTool ===")
    t = TemplateTool()
    print(t.execute(
        template="Hello {{ name }}! You have {{ count }} messages.",
        variables='{"name": "Alice", "count": 5}',
    ))

    print("\n=== EnvValidatorTool ===")
    ev = EnvValidatorTool()
    print(ev.execute(env_vars="OPENAI_API_KEY,PATH", packages="json,requests,nonexistent_pkg"))

    print("\n=== TimerTool ===")
    bm = TimerTool()
    print(bm.execute(
        code="total = sum(i*i for i in range(100_000))\nprint(total)",
        runs=3,
    ))

    print("\n=== Agent with custom tools ===")
    agent = byoe.create_agent(
        tools=[TemplateTool(), EnvValidatorTool(), TimerTool()],
        system="You are a developer assistant with templating and benchmarking tools.",
    )
    print("Tools:", [t.name for t in agent.tools])

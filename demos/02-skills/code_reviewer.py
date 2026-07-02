"""byoe skill: code_reviewer
用途：对单个代码文件执行 AI 代码审查，返回结构化问题报告。

安装（让 byoe agent 能加载此 skill）：
    cp skills/code_reviewer.py ~/.byoe/skills/code_reviewer.py

Agent 内部使用：
    load_skill("code_reviewer")
    skill_code_reviewer(args_json='{"file": "src/api.py"}')

直接调用：
    python skills/code_reviewer.py src/api.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


# ─── byoe skill entry point ───────────────────────────────────────────────────

def run(
    file: str,
    focus: str = "bugs,security,performance,style",
    model: str | None = None,
) -> str:
    """Review a source file and return a structured report.

    Args:
        file:   Path to the source file to review (relative or absolute).
        focus:  Comma-separated categories to check.
                Options: bugs, security, performance, style, maintainability
        model:  Override model (defaults to BYOE_MODEL env var).

    Returns:
        Structured review report as a string.
    """
    import byoe

    path = Path(file).expanduser()
    if not path.exists():
        return f"Error: file not found: {file}"

    code = path.read_text(encoding="utf-8", errors="replace")
    lang = _detect_lang(path.suffix)

    system = (
        "You are a senior code reviewer. Be concise and actionable. "
        "Format output as:\n"
        "## Summary\n"
        "## Issues (severity: CRITICAL/HIGH/MEDIUM/LOW)\n"
        "  - [SEVERITY] description (line N if applicable)\n"
        "## Quick Fixes\n"
        "## Overall Score (0-10)"
    )

    prompt = (
        f"Review this {lang} file focusing on: {focus}\n\n"
        f"File: {path.name}\n"
        f"```{lang}\n{code}\n```"
    )

    kwargs: dict = {}
    if model:
        kwargs["model"] = model

    agent = byoe.create_agent(system=system, tools=[], **kwargs)
    return agent.chat(prompt)


def _detect_lang(suffix: str) -> str:
    return {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".go": "go", ".rs": "rust", ".java": "java",
        ".cpp": "cpp", ".c": "c", ".rb": "ruby", ".php": "php",
    }.get(suffix.lower(), "text")


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python code_reviewer.py <file> [focus]")
        sys.exit(1)
    focus = sys.argv[2] if len(sys.argv) > 2 else "bugs,security,performance,style"
    print(run(file=sys.argv[1], focus=focus))

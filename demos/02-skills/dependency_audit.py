"""byoe skill: dependency_audit
用途：分析项目依赖（requirements.txt / pyproject.toml），找出已知漏洞、过期版本与替换建议。

安装：
    cp skills/dependency_audit.py ~/.byoe/skills/dependency_audit.py

Agent 内使用：
    load_skill("dependency_audit")
    skill_dependency_audit(args_json='{"path": "."}')
"""

from __future__ import annotations

import sys
from pathlib import Path


def run(
    path: str = ".",
    check: str = "all",   # "all" | "outdated" | "security" | "licenses"
) -> str:
    """Audit project dependencies for issues.

    Reads requirements.txt, requirements-dev.txt, or pyproject.toml from `path`.
    Uses AI to cross-reference known CVEs, deprecation notices, and alternatives.

    Args:
        path:  Project root directory. Defaults to current directory.
        check: What to check: all | outdated | security | licenses

    Returns:
        Audit report as a formatted string.
    """
    import byoe

    root = Path(path).expanduser().resolve()
    deps_text, source_files = _collect_deps(root)

    if not deps_text.strip():
        return f"No dependency files found in {root}. Looking for: requirements*.txt, pyproject.toml"

    # Also try to get installed versions via pip freeze
    installed = _pip_freeze()

    system = (
        "You are a Python security and dependency expert. "
        "Analyze the provided dependency list and report:\n"
        "1. Known security vulnerabilities (CVEs if known)\n"
        "2. Significantly outdated packages (> 1 major version behind)\n"
        "3. Deprecated or unmaintained packages with alternatives\n"
        "4. License compatibility issues (if check includes licenses)\n"
        "Format: grouped by severity (CRITICAL / HIGH / MEDIUM / INFO). Be concise."
    )

    check_note = {
        "all": "Check everything: security, outdated versions, deprecated packages, licenses.",
        "outdated": "Focus only on outdated packages. Suggest upgrade paths.",
        "security": "Focus only on known CVEs and security issues.",
        "licenses": "Focus only on license compatibility (GPL, LGPL, MIT, Apache, etc.).",
    }.get(check, "")

    prompt = (
        f"Audit these dependencies ({check_note}):\n\n"
        f"Source files: {', '.join(source_files)}\n\n"
        f"{deps_text}\n\n"
        + (f"Currently installed versions:\n{installed}\n" if installed else "")
    )

    agent = byoe.create_agent(system=system, tools=[])
    return agent.chat(prompt)


def _collect_deps(root: Path) -> tuple[str, list[str]]:
    parts, sources = [], []
    for pattern in ("requirements*.txt", "pyproject.toml", "setup.cfg"):
        for f in sorted(root.glob(pattern)):
            try:
                content = f.read_text(encoding="utf-8")
                parts.append(f"=== {f.name} ===\n{content}")
                sources.append(f.name)
            except OSError:
                pass
    return "\n\n".join(parts), sources


def _pip_freeze() -> str:
    """Return output of `pip freeze` or empty string on failure."""
    try:
        import subprocess
        result = subprocess.run(
            ["pip", "freeze"], capture_output=True, text=True, timeout=15
        )
        return result.stdout[:3000]  # cap at 3000 chars
    except Exception:
        return ""


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    check = sys.argv[2] if len(sys.argv) > 2 else "all"
    print(run(path=path, check=check))

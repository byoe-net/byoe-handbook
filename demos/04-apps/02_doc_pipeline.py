"""AI 应用模板 02：自动文档生成流水线
========================================
用 byoe Swarm 多 Agent 协作，自动为整个 Python 项目生成文档：
  Stage 1 (并行)：各文件独立分析 + 摘要
  Stage 2：整合所有摘要，生成统一 README.md
  Stage 3：生成 CHANGELOG 条目（基于 git log）

特点：
  - 并行处理多个源文件（大型项目用时更短）
  - 生成 README.md、docs/api.md 两个输出
  - 支持 --dry-run 模式（只打印不写文件）

运行：
    python apps/02_doc_pipeline.py [project_dir] [--dry-run]
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import byoe
from byoe.engine.tools.swarm_tool import SwarmTool


def collect_python_files(root: Path, max_files: int = 20) -> list[Path]:
    """Return up to max_files public .py files (exclude tests & __pycache__)."""
    files = []
    for f in sorted(root.rglob("*.py")):
        parts = f.parts
        if any(p in ("__pycache__", ".venv", "node_modules", "migrations") for p in parts):
            continue
        if f.name.startswith("test_") or f.stem.startswith("test"):
            continue
        files.append(f)
        if len(files) >= max_files:
            break
    return files


async def summarize_file(agent: byoe.Agent, path: Path, root: Path) -> tuple[str, str]:
    """Return (relative_path, summary) for one file."""
    code = path.read_text(encoding="utf-8", errors="replace")
    if len(code) > 8000:
        code = code[:8000] + "\n...(truncated)"
    rel = str(path.relative_to(root))
    prompt = (
        f"Summarize `{rel}` in 3-5 sentences: what it does, key classes/functions, "
        f"and any important notes.\n```python\n{code}\n```"
    )
    summary = await agent.achat(prompt)
    return rel, summary


async def parallel_summarize(root: Path) -> dict[str, str]:
    """Summarize all files in parallel."""
    files = collect_python_files(root)
    if not files:
        return {}

    # Use a lightweight agent (no file tools needed for read-only analysis)
    agents = [byoe.create_agent(tools=[]) for _ in files]

    tasks = [summarize_file(a, f, root) for a, f in zip(agents, files)]
    results = await asyncio.gather(*tasks)
    return dict(results)


def generate_readme(summaries: dict[str, str], project_name: str) -> str:
    """Use AI to synthesize file summaries into a README."""
    combined = "\n\n".join(f"### {path}\n{summ}" for path, summ in summaries.items())
    prompt = (
        f"Generate a professional README.md for the Python project '{project_name}'.\n\n"
        f"File summaries:\n{combined}\n\n"
        "Include: Overview, Key Features, Architecture (brief), Installation, Quick Start, API."
    )
    agent = byoe.create_agent(tools=[])
    return agent.chat(prompt)


def generate_changelog(project_dir: Path) -> str:
    """Generate a CHANGELOG entry from recent git log."""
    import subprocess
    try:
        log = subprocess.check_output(
            ["git", "log", "--oneline", "-20"],
            cwd=project_dir, text=True, stderr=subprocess.DEVNULL
        )
    except Exception:
        log = "(no git history available)"

    prompt = (
        f"Generate a CHANGELOG.md entry (Keep a Changelog format) "
        f"based on these recent commits:\n{log}\n\n"
        "Group changes into Added / Changed / Fixed / Removed sections."
    )
    agent = byoe.create_agent(tools=[])
    return agent.chat(prompt)


def main():
    parser = argparse.ArgumentParser(description="Auto-generate project documentation")
    parser.add_argument("project_dir", nargs="?", default=".", help="Project root directory")
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing files")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    project_name = root.name
    print(f"文档生成流水线 · 项目: {project_name} ({root})")

    # Stage 1: parallel file summarization
    print("\n[Stage 1] 并行分析源文件…")
    summaries = asyncio.run(parallel_summarize(root))
    print(f"  ✓ 分析了 {len(summaries)} 个文件")

    if not summaries:
        print("  未找到 Python 源文件，退出。")
        sys.exit(1)

    # Stage 2: generate README
    print("\n[Stage 2] 生成 README.md…")
    readme_content = generate_readme(summaries, project_name)

    # Stage 3: generate CHANGELOG entry
    print("\n[Stage 3] 生成 CHANGELOG 条目…")
    changelog_entry = generate_changelog(root)

    # Output
    if args.dry_run:
        print("\n" + "─" * 60)
        print("README.md (dry-run):\n")
        print(readme_content[:2000])
        print("\n…\n\nCHANGELOG entry (dry-run):\n")
        print(changelog_entry[:1000])
    else:
        readme_path = root / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")
        print(f"\n✓ README.md 写入: {readme_path}")

        changelog_path = root / "CHANGELOG.md"
        existing = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else ""
        changelog_path.write_text(changelog_entry + "\n\n" + existing, encoding="utf-8")
        print(f"✓ CHANGELOG.md 更新: {changelog_path}")

    print("\n文档生成完成！")


if __name__ == "__main__":
    main()

"""CI/CD one-shot bot for BYOE.

Usage:
    python cicd_bot.py --task "审查本次 PR 改动并输出风险报告" --output-file pr-review.md

Exit codes:
    0: success
    1: failed (LLM error or missing config)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def build_agent(cwd: Path):
    """Construct BYOE Agent from environment configuration."""
    try:
        import byoe
    except ImportError as exc:
        raise RuntimeError("未安装 byoe，请先执行: pip install byoe>=0.8.0") from exc

    # create_agent() reads OPENAI_API_KEY / BYOE_API_KEY / BYOE_MODEL etc. automatically
    return byoe.create_agent(cwd=str(cwd))


def run_task(task: str, cwd: Path) -> str:
    """Run a single BYOE task and return final response text."""
    agent = build_agent(cwd)
    return agent.chat(task)


def main() -> int:
    parser = argparse.ArgumentParser(description="BYOE CI/CD 单次执行机器人")
    parser.add_argument(
        "--task",
        required=True,
        help="要交给 BYOE 的单次任务，例如：审查本次 PR 的风险并输出报告",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="工作目录（默认当前目录）",
    )
    parser.add_argument(
        "--output-file",
        default="",
        help="可选：将结果写入文件，例如 pr-review.md",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    if not cwd.exists():
        print(f"工作目录不存在: {cwd}", file=sys.stderr)
        return 1

    try:
        result = run_task(args.task, cwd)
    except Exception as exc:  # noqa: BLE001
        print(f"BYOE 执行失败: {exc}", file=sys.stderr)
        return 1

    if args.output_file:
        output_path = Path(args.output_file)
        output_path.write_text(result, encoding="utf-8")
        print(f"结果已写入: {output_path}")
    else:
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

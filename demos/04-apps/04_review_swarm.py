"""AI 应用模板 04：多 Agent 代码评审流水线
========================================
用 byoe Swarm 模拟真实研发团队的代码评审流程：

  Stage 1 — 并行评审（3 个专家同时工作）：
    ├─ 安全工程师：漏洞扫描 + OWASP Top 10 检查
    ├─ 性能工程师：瓶颈分析 + 复杂度评估
    └─ 技术文档专家：可读性 + 命名规范
  
  Stage 2 — Tech Lead 汇总：
    合并三份报告，给出综合评分与优先级修复列表

  Stage 3（可选）—  自动修复：
    对 CRITICAL 问题自动提出修复 patch

运行：
    python apps/04_review_swarm.py <file_to_review> [--auto-fix]
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

import byoe


@dataclass
class ReviewResult:
    reviewer: str
    findings: str
    score: int   # 0-10


REVIEWER_PROMPTS = {
    "security": (
        "You are a security engineer specializing in OWASP Top 10. "
        "Review the code for: SQL injection, XSS, CSRF, insecure deserialization, "
        "hardcoded secrets, path traversal, weak crypto, auth bypass. "
        "Rate 0-10 (10=perfect). Format: ## Security Score: N/10\n## Issues\n## Fixes"
    ),
    "performance": (
        "You are a performance engineer. "
        "Review the code for: O(n²) algorithms, N+1 queries, missing indexes, "
        "unnecessary I/O in loops, memory leaks, blocking calls in async context. "
        "Rate 0-10. Format: ## Performance Score: N/10\n## Bottlenecks\n## Optimizations"
    ),
    "readability": (
        "You are a senior engineer focused on code quality. "
        "Review the code for: naming clarity, function length, complexity, "
        "missing docstrings, magic numbers, code duplication, SOLID principles. "
        "Rate 0-10. Format: ## Quality Score: N/10\n## Issues\n## Suggestions"
    ),
}


async def review_with_role(code: str, filename: str, role: str) -> ReviewResult:
    """Run one reviewer asynchronously."""
    agent = byoe.create_agent(system=REVIEWER_PROMPTS[role], tools=[])
    prompt = f"Review this code from `{filename}`:\n\n```python\n{code}\n```"
    findings = await agent.achat(prompt)

    # Parse score from output
    score = 7  # default
    for line in findings.splitlines():
        if "Score:" in line:
            try:
                score = int("".join(c for c in line.split("Score:")[-1] if c.isdigit())[:2])
                score = max(0, min(10, score))
            except ValueError:
                pass
            break

    return ReviewResult(reviewer=role, findings=findings, score=score)


async def parallel_review(code: str, filename: str) -> list[ReviewResult]:
    """Run all reviewers in parallel."""
    tasks = [review_with_role(code, filename, role) for role in REVIEWER_PROMPTS]
    return await asyncio.gather(*tasks)


def synthesize_report(results: list[ReviewResult], filename: str) -> str:
    """Tech Lead consolidates all reviews."""
    combined = "\n\n".join(
        f"=== {r.reviewer.upper()} (score {r.score}/10) ===\n{r.findings}"
        for r in results
    )
    avg_score = sum(r.score for r in results) / len(results)

    system = (
        "You are a Tech Lead synthesizing multiple code review reports. "
        "Be decisive and prioritize. Focus on what the developer needs to do NOW."
    )
    prompt = (
        f"Synthesize these code reviews for `{filename}` (avg score: {avg_score:.1f}/10).\n\n"
        f"{combined}\n\n"
        "Output format:\n"
        "## Overall Score: X/10\n"
        "## CRITICAL (fix before merge)\n"
        "## HIGH (fix this sprint)\n"
        "## MEDIUM (tech debt)\n"
        "## LOW (nice to have)\n"
        "## Verdict: APPROVE / REQUEST_CHANGES / REJECT"
    )
    agent = byoe.create_agent(system=system, tools=[])
    return agent.chat(prompt)


def auto_fix_critical(code: str, filename: str, report: str) -> str | None:
    """Generate a patch for CRITICAL issues."""
    # Extract CRITICAL section from report
    critical_section = ""
    in_critical = False
    for line in report.splitlines():
        if "## CRITICAL" in line:
            in_critical = True
        elif line.startswith("## ") and in_critical:
            break
        elif in_critical:
            critical_section += line + "\n"

    if not critical_section.strip():
        return None

    system = "You are a code fixer. Output ONLY the corrected code, no explanation."
    prompt = (
        f"Fix the CRITICAL issues in this code:\n\nIssues:\n{critical_section}\n\n"
        f"Original code (`{filename}`):\n```python\n{code}\n```\n\n"
        "Output the complete fixed file."
    )
    agent = byoe.create_agent(system=system, tools=[])
    fixed = agent.chat(prompt).strip()
    if fixed.startswith("```python"):
        fixed = fixed[9:]
    if fixed.startswith("```"):
        fixed = fixed[3:]
    if fixed.endswith("```"):
        fixed = fixed[:-3]
    return fixed.strip()


def main():
    parser = argparse.ArgumentParser(description="Multi-agent code review pipeline")
    parser.add_argument("file", help="Python file to review")
    parser.add_argument("--auto-fix", action="store_true", help="Auto-fix CRITICAL issues")
    args = parser.parse_args()

    path = Path(args.file).expanduser()
    if not path.exists():
        print(f"Error: {args.file} not found"); sys.exit(1)

    code = path.read_text(encoding="utf-8")
    print(f"代码评审流水线 · 文件: {path.name} ({len(code.splitlines())} 行)")

    # Stage 1: parallel review
    print("\n[Stage 1] 并行评审 (安全 | 性能 | 可读性)…")
    results = asyncio.run(parallel_review(code, path.name))
    for r in results:
        print(f"  {r.reviewer:15s} 评分: {r.score}/10")

    # Stage 2: synthesize
    print("\n[Stage 2] Tech Lead 汇总报告…")
    report = synthesize_report(results, path.name)
    print("\n" + "─" * 60)
    print(report)
    print("─" * 60)

    # Stage 3: optional auto-fix
    if args.auto_fix:
        print("\n[Stage 3] 自动修复 CRITICAL 问题…")
        fixed_code = auto_fix_critical(code, path.name, report)
        if fixed_code:
            fix_path = path.parent / f"{path.stem}_fixed{path.suffix}"
            fix_path.write_text(fixed_code, encoding="utf-8")
            print(f"✓ 修复后代码写入: {fix_path}")
        else:
            print("  (无 CRITICAL 问题，无需修复)")


if __name__ == "__main__":
    # Demo: review a self-contained example with known issues
    if len(sys.argv) == 1:
        import tempfile, os

        DEMO_CODE = '''
def get_user(user_id):
    import sqlite3
    db = sqlite3.connect("app.db")
    # SQL injection vulnerability!
    result = db.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
    db.close()
    return result

def slow_search(items, target):
    # O(n^2) — inefficient
    results = []
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == target and i == j:
                results.append(items[i])
    return results

def process(data):
    x = []
    for i in data:
        x.append(i * 2)
    return x
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(DEMO_CODE); tmp = f.name
        sys.argv = [sys.argv[0], tmp]
        main()
        os.unlink(tmp)
    else:
        main()

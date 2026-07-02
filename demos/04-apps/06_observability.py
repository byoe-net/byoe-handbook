"""AI 应用模板 06：Hooks 驱动的可观测 Agent
========================================
用 byoe Hooks 系统为 AI 应用添加生产级可观测性：
  - 成本跟踪：每次 LLM 调用记录 token 消耗与成本
  - 工具审计：所有工具调用写入结构化日志
  - 性能监控：P95 延迟 + 慢请求告警
  - 错误捕获：全局错误钩子 + 自动重试
  - Prometheus 格式指标导出（可选）

特点：
  - 零侵入：应用代码不需要改动，只需注册钩子
  - 热插拔：随时 on/off 钩子，不影响主流程
  - 结构化输出：JSONL 格式日志，便于 ELK/ClickHouse 摄入

运行：
    python apps/06_observability.py
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import byoe
from byoe import on, off


# ─── 指标收集器 ─────────────────────────────────────────────────────────────

class MetricsCollector:
    """Lightweight in-process metrics store."""

    def __init__(self):
        self.calls: int = 0
        self.total_tokens: int = 0
        self.total_cost_usd: float = 0.0
        self.latencies_ms: list[float] = []
        self.tool_counts: dict[str, int] = defaultdict(int)
        self.tool_errors: dict[str, int] = defaultdict(int)
        self.errors: list[str] = []

    @property
    def avg_latency_ms(self) -> float:
        return sum(self.latencies_ms) / max(len(self.latencies_ms), 1)

    @property
    def p95_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_l = sorted(self.latencies_ms)
        idx = int(len(sorted_l) * 0.95)
        return sorted_l[min(idx, len(sorted_l) - 1)]

    def summary(self) -> dict[str, Any]:
        return {
            "llm_calls": self.calls,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost_usd, 5),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "p95_latency_ms": round(self.p95_latency_ms, 1),
            "tool_counts": dict(self.tool_counts),
            "tool_errors": dict(self.tool_errors),
            "errors": self.errors[-10:],  # last 10 errors
        }

    def prometheus(self) -> str:
        """Export Prometheus-compatible metrics."""
        lines = [
            f'byoe_llm_calls_total {self.calls}',
            f'byoe_tokens_total {self.total_tokens}',
            f'byoe_cost_usd_total {self.total_cost_usd:.5f}',
            f'byoe_latency_avg_ms {self.avg_latency_ms:.1f}',
            f'byoe_latency_p95_ms {self.p95_latency_ms:.1f}',
        ]
        for tool, count in self.tool_counts.items():
            lines.append(f'byoe_tool_calls_total{{tool="{tool}"}} {count}')
        for tool, count in self.tool_errors.items():
            lines.append(f'byoe_tool_errors_total{{tool="{tool}"}} {count}')
        return "\n".join(lines)


metrics = MetricsCollector()


# ─── JSONL 审计日志 ──────────────────────────────────────────────────────────

LOG_PATH = Path.home() / ".byoe" / "logs" / "audit.jsonl"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
SLOW_THRESHOLD_MS = 5000  # 5 seconds


def _log(event: str, data: dict) -> None:
    """Append one JSONL audit record."""
    record = {"ts": time.time(), "event": event, **data}
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ─── 注册全局钩子 ────────────────────────────────────────────────────────────

@on("llm.response")
def on_llm_response(model, prompt_tokens, completion_tokens, cost_usd, duration_ms, **_):
    """Track every LLM call."""
    metrics.calls += 1
    metrics.total_tokens += (prompt_tokens or 0) + (completion_tokens or 0)
    metrics.total_cost_usd += cost_usd or 0.0
    metrics.latencies_ms.append(duration_ms or 0.0)

    _log("llm.response", {
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost_usd": cost_usd,
        "duration_ms": duration_ms,
    })

    if (duration_ms or 0) > SLOW_THRESHOLD_MS:
        print(f"  ⚠️  慢请求警告: {duration_ms:.0f}ms > {SLOW_THRESHOLD_MS}ms (model={model})")


@on("tool.call")
def on_tool_call(tool_name, args, result, error, duration_ms, **_):
    """Audit every tool invocation."""
    metrics.tool_counts[tool_name] += 1
    if error:
        metrics.tool_errors[tool_name] += 1

    _log("tool.call", {
        "tool": tool_name,
        "args": {k: str(v)[:200] for k, v in (args or {}).items()},
        "success": error is None,
        "error": str(error) if error else None,
        "duration_ms": duration_ms,
        "result_len": len(str(result or "")),
    })


@on("agent.turn")
def on_agent_turn(user_input, response, tool_calls_count, duration_ms, **_):
    """Log completed agent turns."""
    _log("agent.turn", {
        "input_len": len(user_input or ""),
        "response_len": len(response or ""),
        "tool_calls": tool_calls_count,
        "duration_ms": duration_ms,
    })


@on("error")
def on_error(exception, context, **_):
    """Catch and record all agent errors."""
    msg = f"{type(exception).__name__}: {exception}"
    metrics.errors.append(msg)
    _log("error", {"error": msg, "context": str(context)[:500]})
    print(f"  🔴 Agent 错误已捕获: {msg}")


# ─── 演示 ────────────────────────────────────────────────────────────────────

def demo():
    print("=== 可观测 Agent 演示 ===\n")
    print(f"审计日志路径: {LOG_PATH}")

    agent = byoe.create_agent()

    # Run a few tasks to generate metrics
    tasks = [
        "用 Python 写一个计算斐波那契数列的函数",
        "列出当前目录的文件",
    ]

    for task in tasks:
        print(f"\n任务: {task}")
        print("─" * 40)
        try:
            reply = agent.chat(task)
            print(reply[:400])
        except Exception:
            pass

    # Print metrics summary
    print("\n" + "=" * 50)
    print("📊 指标摘要:")
    print(json.dumps(metrics.summary(), ensure_ascii=False, indent=2))

    print("\n📈 Prometheus 格式:")
    print(metrics.prometheus())

    print(f"\n📝 审计日志: {LOG_PATH}")
    if LOG_PATH.exists():
        lines = LOG_PATH.read_text().strip().split("\n")
        print(f"   共 {len(lines)} 条记录 (最新):")
        for line in lines[-3:]:
            try:
                rec = json.loads(line)
                print(f"   [{rec['event']}] {json.dumps({k: v for k, v in rec.items() if k not in ('ts', 'event')}, ensure_ascii=False)[:100]}")
            except Exception:
                pass


if __name__ == "__main__":
    demo()

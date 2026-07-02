"""BYOE 全局事件钩子（Hooks）

演示如何通过 byoe.on() 注册全局钩子，实现：

  A. 成本追踪与预算保护
  B. 工具调用审计日志
  C. 对话级别指标收集
  D. 记忆写入监控
  E. 多钩子组合 + 运行时注销
  F. Entry-point 插件模式（第三方包自动注册）

可用事件：
  llm.response   每次 LLM API 调用结束后
  tool.call      每次工具执行结束后（含报错情况）
  agent.turn     每次用户→助手完整一轮结束后
  memory.write   每次记忆写入后

运行：
    python 09_hooks.py
"""

import time
import byoe
from byoe import LLM, Agent

# ── 辅助：创建测试用 Agent ─────────────────────────────────────────────────────

def make_agent():
    """从环境变量创建 Agent（使用最小工具集加快示例速度）。"""
    from byoe.engine.tools.memory_tool import MemoryTool
    from byoe.engine.tools.bash import BashTool
    return byoe.create_agent(tools=[MemoryTool(), BashTool()])


# ══════════════════════════════════════════════════════════════════════════════
# A. 成本追踪与预算保护
# ══════════════════════════════════════════════════════════════════════════════

print("=" * 60)
print("A. 成本追踪与预算保护")
print("=" * 60)

# 累计成本跟踪器
_session_cost = 0.0
BUDGET_USD = 0.10  # 演示：每次会话上限 $0.10

@byoe.on("llm.response")
def track_cost(model, prompt_tokens, completion_tokens, cost_usd, duration_ms, **_):
    global _session_cost
    cost = cost_usd or 0.0
    _session_cost += cost
    print(f"  [llm] {model}  {prompt_tokens}p/{completion_tokens}c  "
          f"${cost:.5f}  ({duration_ms:.0f}ms)  累计 ${_session_cost:.5f}")
    if _session_cost > BUDGET_USD:
        print(f"  ⚠️  预算超限（>${BUDGET_USD}），请注意成本！")

# 注销钩子后不再打印
print("\n  注册成本追踪钩子 ✓")
print("  (实际调用需真实 API Key，这里展示注册逻辑)")


# ══════════════════════════════════════════════════════════════════════════════
# B. 工具调用审计日志
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("B. 工具调用审计日志")
print("=" * 60)

import json
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG = Path.home() / ".byoe" / "audit.jsonl"

@byoe.on("tool.call")
def audit_tool(name, kwargs, result, duration_ms, error, **_):
    """将每次工具调用记录到 JSONL 审计日志。"""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": name,
        "args": kwargs,
        "status": "error" if error else "ok",
        "error": str(error) if error else None,
        "duration_ms": round(duration_ms, 1),
        "result_len": len(result) if result else 0,
    }
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    status = "❌" if error else "✓"
    print(f"  [tool {status}] {name}  {duration_ms:.0f}ms  → {AUDIT_LOG}")

print(f"  工具审计日志将写入: {AUDIT_LOG}")


# ══════════════════════════════════════════════════════════════════════════════
# C. 对话级别指标收集
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("C. 对话级别指标收集")
print("=" * 60)

_turn_metrics: list[dict] = []

@byoe.on("agent.turn")
def collect_turn_metrics(user_input, response, prompt_tokens,
                          completion_tokens, rounds, duration_ms, **_):
    metric = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "input_chars": len(user_input),
        "output_chars": len(response),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "tool_rounds": rounds,
        "duration_ms": round(duration_ms, 1),
    }
    _turn_metrics.append(metric)
    print(f"  [turn] rounds={rounds}  "
          f"{prompt_tokens}p/{completion_tokens}c  "
          f"{duration_ms:.0f}ms")

def print_session_summary():
    if not _turn_metrics:
        return
    total_p = sum(m["prompt_tokens"] for m in _turn_metrics)
    total_c = sum(m["completion_tokens"] for m in _turn_metrics)
    avg_ms  = sum(m["duration_ms"] for m in _turn_metrics) / len(_turn_metrics)
    print(f"\n  ── 会话摘要 ──")
    print(f"  对话轮数: {len(_turn_metrics)}")
    print(f"  总 tokens: {total_p}p / {total_c}c")
    print(f"  平均响应时间: {avg_ms:.0f}ms")

print("  对话指标收集钩子已注册 ✓")


# ══════════════════════════════════════════════════════════════════════════════
# D. 记忆写入监控
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("D. 记忆写入监控")
print("=" * 60)

@byoe.on("memory.write")
def monitor_memory(path, layer, was_update, **_):
    action = "更新" if was_update else "新建"
    print(f"  [memory {action}] {layer}:{path}")

print("  记忆监控钩子已注册 ✓")

# 触发一次记忆写入以展示效果
mem = byoe.get_memory()
mem.write(
    path="demo/hook-test",
    content="Hook 系统测试记忆",
    layer="session",
)
mem.write(
    path="demo/hook-test",    # 再次写入同路径 → 触发"更新"
    content="Hook 系统测试记忆（已更新）",
    layer="session",
)


# ══════════════════════════════════════════════════════════════════════════════
# E. 钩子的注销与清理
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("E. 钩子注销与清理")
print("=" * 60)

# 函数式注册（不用装饰器）
def one_time_hook(path, layer, was_update, **_):
    print(f"  [one-time] 只触发一次: {path}")

byoe.on("memory.write", one_time_hook)

# 触发一次
mem.write(path="demo/one-time", content="x", layer="session")

# 注销 → 之后不再触发
byoe.off("memory.write", one_time_hook)
mem.write(path="demo/after-off", content="y", layer="session")  # 不打印 one-time
print("  one_time_hook 已注销，后续写入不再触发它 ✓")

# 清理单个事件的所有钩子
# byoe.clear_hooks("memory.write")   # 取消注释以清除 memory.write 的全部钩子

# 清理所有钩子（测试结束时调用，避免污染其他测试）
# byoe.clear_hooks()


# ══════════════════════════════════════════════════════════════════════════════
# F. Prometheus 指标集成模式（展示架构，不实际运行）
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("F. Prometheus / 监控系统集成模式")
print("=" * 60)

PROMETHEUS_EXAMPLE = '''
# 方式一：直接在 hook 中推送指标
# pip install prometheus-client

from prometheus_client import Counter, Histogram, start_http_server

_token_counter = Counter("byoe_tokens_total", "Total LLM tokens", ["model", "type"])
_turn_duration = Histogram("byoe_turn_duration_seconds", "Agent turn duration")

@byoe.on("llm.response")
def push_llm_metrics(model, prompt_tokens, completion_tokens, **_):
    _token_counter.labels(model=model, type="prompt").inc(prompt_tokens)
    _token_counter.labels(model=model, type="completion").inc(completion_tokens)

@byoe.on("agent.turn")
def push_turn_metrics(duration_ms, **_):
    _turn_duration.observe(duration_ms / 1000)

# 启动 Prometheus 端口（默认 8000）
start_http_server(8000)


# 方式二：发布为 pip 包，用户 pip install 后自动生效
# pyproject.toml:
#   [project.entry-points."byoe.hooks"]
#   my_monitor = "mypackage.monitoring:setup"
#
# mypackage/monitoring.py:
#   def setup():
#       byoe.on("llm.response", push_llm_metrics)
#       byoe.on("agent.turn", push_turn_metrics)
'''

print(PROMETHEUS_EXAMPLE)


# ══════════════════════════════════════════════════════════════════════════════
# G. 使用装饰器 vs 函数调用的完整对比
# ══════════════════════════════════════════════════════════════════════════════

print("=" * 60)
print("G. 装饰器 vs 函数调用注册方式对比")
print("=" * 60)

byoe.clear_hooks()  # 清空之前注册的所有钩子

# 装饰器形式（推荐，可读性强）
@byoe.on("agent.turn")
def log_turn(user_input, response, **_):
    print(f"  [decorator] Q: {user_input[:30]}... A: {response[:30]}...")

# 函数调用形式（适合条件注册、动态注册）
def log_cost(model, cost_usd, **_):
    if cost_usd:
        print(f"  [function] cost ${cost_usd:.5f} on {model}")

byoe.on("llm.response", log_cost)

print("  两种注册方式均已演示 ✓")
print("\n  已注册钩子：")
from byoe.engine import hooks as _hooks_mod
for event, fns in _hooks_mod._registry.items():
    print(f"    {event}: {[f.__name__ for f in fns]}")

print("\n所有示例完成！")
print_session_summary()

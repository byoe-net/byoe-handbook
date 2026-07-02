"""BYOE Swarm 多 Agent 编排

演示两种 Swarm 执行模式：

  1. 串行中继（roles）
     A → B → C，每个 Agent 接收上一个的输出，适合流水线工作流。

  2. 并行分组（parallel_groups）
     [A, B] 并行运行，输出合并后交给 C，适合多角色并行评审场景。

运行：
    python 06_swarm.py
"""

import byoe

agent = byoe.create_agent()

# ── 串行中继：代码开发流水线 ──────────────────────────────────────────────────
print("=== 串行中继：需求 → 实现 → 测试 ===\n")

result = agent.chat(
    "swarm 协作：实现一个 Python 函数计算斐波那契数列",
    # 触发方式：在对话中直接让 Agent 使用 swarm 工具
    # 或直接调用工具：
)

# 也可以通过工具接口直接调用（适合 API 集成场景）
from byoe.engine.tools.swarm_tool import SwarmTool
from byoe.engine.agent import Agent
from byoe.engine.llm import LLM
import os

llm = LLM(model=os.environ.get("BYOE_MODEL", "gpt-4o"),
          api_key=os.environ.get("BYOE_API_KEY", ""))
main_agent = Agent(llm=llm, tools=byoe.engine.tools.ALL_TOOLS if False else [])

# 串行 roles：Coder → Reviewer → Technical Writer
swarm = SwarmTool()
swarm._parent_agent = byoe.create_agent()   # 借用 create_agent 的完整工具集

serial_result = swarm.execute(
    initial_task="实现一个线程安全的 Python 计数器类",
    roles=["backend-architect", "security-engineer", "technical-writer"],
    step_timeout_seconds=120,
)
print(serial_result[:800])
print("...\n")

# ── 并行分组：多角色并行评审 ──────────────────────────────────────────────────
print("=== 并行分组：安全 + 性能并行评审，再由 Tech Lead 汇总 ===\n")

parallel_result = swarm.execute(
    initial_task="""
    请评审以下 Python 代码：
    ```python
    def process_payment(user_id, amount, card_number):
        import sqlite3, requests
        db = sqlite3.connect("payments.db")
        db.execute(f"INSERT INTO payments VALUES ({user_id}, {amount}, '{card_number}')")
        db.commit()
        requests.post("https://payment-gateway.example.com/charge",
                     json={"card": card_number, "amount": amount}, timeout=30)
    ```
    """,
    parallel_groups=[
        ["security-engineer", "api-tester"],   # 第一组并行：安全 + 接口测试
        ["tech-lead"],                          # 第二组：汇总并给出最终建议
    ],
    step_timeout_seconds=120,
)
print(parallel_result[:1000])

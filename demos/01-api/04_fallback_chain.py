"""BYOE 模型降级链 (Fallback Chain)

当主模型不可用（限流、超时、网络故障）时，
LLM 自动按顺序尝试备用模型，对调用方完全透明。

两种使用方式：
  A. fallback_models  — 同一 Provider，不同模型（最常用）
  B. fallbacks        — 跨 Provider 完全独立的备用配置

运行：
    python 04_fallback_chain.py
"""

import byoe
from byoe import LLM, Agent

# ── A. 同 Provider 模型降级链 ─────────────────────────────────────────────────
# 常见场景：高峰期 gpt-4o 限流时自动降级到 gpt-4o-mini
import os

agent_a = byoe.create_agent(
    model="gpt-4o",
    api_key=os.environ.get("BYOE_API_KEY", ""),
    fallback_models=["gpt-4o-mini", "gpt-3.5-turbo"],
    # 顺序：gpt-4o → gpt-4o-mini → gpt-3.5-turbo
)

response = agent_a.chat("什么是 CAP 定理？")
print(f"[A] 使用模型: {agent_a.llm.model}")
print(response[:200])
print()

# ── B. 跨 Provider 降级链 ────────────────────────────────────────────────────
# 常见场景：OpenAI 不可用时切换到 DeepSeek 或 Qwen
agent_b = byoe.create_agent(
    model="gpt-4o",
    api_key=os.environ.get("OPENAI_API_KEY", ""),
    fallbacks=[
        {
            "model": "deepseek-chat",
            "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
            "base_url": "https://api.deepseek.com",
        },
        {
            "model": "qwen3-max",
            "api_key": os.environ.get("DASHSCOPE_API_KEY", ""),
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        },
    ],
)

response_b = agent_b.chat("用 Python 实现一个 LRU Cache")
print(response_b[:300])
print()

# ── C. 直接构造 LLM 对象 ──────────────────────────────────────────────────────
# 适合需要复用同一 LLM 实例于多个 Agent 的场景
llm = LLM(
    model="gpt-4o",
    api_key=os.environ.get("BYOE_API_KEY", ""),
    fallback_models=["gpt-4o-mini"],    # 同 provider 简写
    fallback_providers=[               # 跨 provider 完整配置
        {
            "model": "deepseek-chat",
            "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
            "base_url": "https://api.deepseek.com",
        }
    ],
)

agent_c = Agent(llm=llm, tools=[])
print(f"[C] 主模型: {llm.model}，备用链长度: {len(llm._fallback_providers)}")

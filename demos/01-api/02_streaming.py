"""BYOE 流式输出与异步调用

演示三种调用方式：
  1. chat()   — 同步阻塞，返回完整字符串
  2. stream() — 实时 token 流，迭代后可通过 .result 获取完整响应
  3. achat()  — asyncio 异步，适合 FastAPI / aiohttp 等框架

运行：
    python 02_streaming.py
"""

import asyncio
import byoe

agent = byoe.create_agent()

# ── 1. 同步 ───────────────────────────────────────────────────────────────────
print("=== 同步 chat() ===")
result = agent.chat("写一首关于 Python 的五言绝句")
print(result)
print()

# ── 2. 流式 stream() ──────────────────────────────────────────────────────────
print("=== 流式 stream() ===")
stream: byoe.StreamResponse = agent.stream("用 50 字解释快速排序")

for token in stream:
    print(token, end="", flush=True)
print()

# 迭代结束后 .result 包含完整文本（对需要存储响应的场景很有用）
full_text = stream.result
print(f"\n[完整长度: {len(full_text)} 字符]")
print()

# ── 3. 异步 achat() ──────────────────────────────────────────────────────────
print("=== 异步 achat() ===")

async def ask_async():
    # achat 支持所有 chat() 参数（on_token、response_model 等）
    tokens: list[str] = []
    result = await agent.achat(
        "写出冒泡排序的 Python 实现",
        on_token=tokens.append,
    )
    print(f"收到 {len(tokens)} 个 token，最终响应长度 {len(result)} 字符")
    print(result[:200], "...")

asyncio.run(ask_async())

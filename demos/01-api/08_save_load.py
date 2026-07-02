"""BYOE 会话持久化（save / load）

演示如何将 Agent 对话历史保存到 JSON 文件，
并在下次启动时恢复，实现跨进程的对话连续性。

运行：
    python 08_save_load.py
"""

import os
import tempfile
import byoe
from byoe import Agent, LLM

# ── 场景 1：保存并恢复单次对话 ────────────────────────────────────────────────
print("=== 场景 1：保存对话 ===")

agent = byoe.create_agent()
agent.chat("我叫王芳，是一名 Python 后端工程师")
agent.chat("我正在重构一个遗留的单体应用到微服务架构")

# 保存到指定路径
save_path = os.path.join(tempfile.gettempdir(), "byoe_demo_session.json")
path = agent.save(save_path)
print(f"已保存到: {path}")
print(f"消息数: {len(agent.messages)}")
print(f"Token 使用: prompt={agent.llm.total_prompt_tokens}, "
      f"completion={agent.llm.total_completion_tokens}")

# ── 场景 2：在新进程/新实例中恢复 ────────────────────────────────────────────
print("\n=== 场景 2：恢复对话 ===")

# 模拟重启：创建全新的 Agent 实例
new_agent = byoe.create_agent()
print(f"恢复前消息数: {len(new_agent.messages)}")

new_agent.load(save_path)
print(f"恢复后消息数: {len(new_agent.messages)}")

# 继续对话 — Agent 记得之前的上下文
response = new_agent.chat("我刚才说我在做什么工作？")
print(f"\nAgent 回复（应该知道上下文）：\n{response}")

# ── 场景 3：默认路径（自动命名） ──────────────────────────────────────────────
print("\n=== 场景 3：自动路径保存 ===")

agent2 = byoe.create_agent()
agent2.chat("这是一个测试消息")

# 不传路径 → 自动保存到 ~/.byoe/conversations/conv_YYYYMMDD_HHMMSS.json
auto_path = agent2.save()
print(f"自动保存路径: {auto_path}")

# ── 场景 4：结合 Web 框架使用 ────────────────────────────────────────────────
# 在 FastAPI 中实现多用户持久化会话的参考模式：
#
# from fastapi import FastAPI
# import byoe, os
#
# app = FastAPI()
# _agents: dict[str, byoe.Agent] = {}
#
# def get_agent(user_id: str) -> byoe.Agent:
#     if user_id not in _agents:
#         agent = byoe.create_agent()
#         session_path = f"~/.byoe/conversations/{user_id}.json"
#         if os.path.exists(os.path.expanduser(session_path)):
#             agent.load(session_path)    # 恢复历史
#         _agents[user_id] = agent
#     return _agents[user_id]
#
# @app.post("/chat/{user_id}")
# async def chat(user_id: str, message: str):
#     agent = get_agent(user_id)
#     response = await agent.achat(message)
#     agent.save(f"~/.byoe/conversations/{user_id}.json")   # 每轮后保存
#     return {"response": response}

print("\n[提示] 会话文件格式为标准 JSON，可直接查看/编辑/版本控制")
print(f"示例路径: {auto_path}")

# 清理临时文件
os.unlink(save_path)

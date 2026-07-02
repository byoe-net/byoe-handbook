"""BYOE 快速入门

最小可运行示例：用 create_agent() 工厂函数创建 Agent，
从环境变量读取 API Key 与模型名称，发送一条消息。

运行前准备：
    pip install byoe
    set BYOE_API_KEY=sk-...
    set BYOE_MODEL=gpt-4o          # 可选，默认 gpt-4o
    set OPENAI_BASE_URL=...        # 可选，OpenAI 兼容的第三方端点

运行：
    python 01_quickstart.py
"""

import byoe

# create_agent() 自动从环境变量读取配置，无需手动传递 api_key
agent = byoe.create_agent()

# 同步调用 — 返回完整字符串
response = agent.chat("用一句话解释什么是向量数据库")
print(response)

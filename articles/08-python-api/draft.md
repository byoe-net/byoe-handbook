# Python API 编程：把 AI 嵌入你的应用

> 一句话摘要：BYOE 不只是 CLI 工具，更是一个 Python 库 —— 三行代码就能在你的应用里嵌入一个 AI Agent。

---

## 1. 场景引入

假设你在开发一个企业内部工具，需要一个 AI 助手来：
- 自动分析用户上传的 CSV 数据
- 根据模板生成合同文档
- 定时检查服务器日志并告警

如果用 LangChain：
```python
from langchain import ...
from langchain.memory import ...
from langchain.tools import ...
# ... 30 行初始化代码
```

用 BYOE：
```python
import byoe
agent = byoe.create_agent()
response = agent.chat("分析这份 CSV 数据")
```

---

## 2. 核心 API

### create_agent() — 工厂函数

```python
import byoe

# 最简单的用法：自动读取环境变量
agent = byoe.create_agent()

# 手动配置
agent = byoe.create_agent(
    model="deepseek-chat",
    api_key="sk-xxx",
    base_url="https://api.deepseek.com",
    system="你是一个 Python 开发专家",  # 自定义 system prompt
)
```

### Agent.chat() — 同步调用

```python
response = agent.chat("用 Python 写一个斐波那契数列")
print(response)
# 输出完整的代码和解释
```

### Agent.stream() — 流式调用

```python
for token in agent.stream("写一篇关于 AI 的短文"):
    print(token, end="", flush=True)
```

适合需要实时显示输出、或处理长文本的场景。

### Agent.achat() — 异步调用

```python
response = await agent.achat("分析这份日志文件")
```

适合 FastAPI、Web 应用等异步框架。

---

## 3. 完整示例：智能问答机器人

```python
import byoe

# 创建 Agent
agent = byoe.create_agent(system="你是一个 Python 技术专家")

def ask_question(question: str) -> str:
    """向 AI 提问并返回回答"""
    return agent.chat(question)

# 交互式循环
while True:
    q = input("\n❓ 请输入问题（输入 exit 退出）: ")
    if q.lower() == "exit":
        break
    print(f"\n🤖 {ask_question(q)}")
```

---

## 4. 流式生成 Markdown 报告

```python
from byoe import create_agent

agent = create_agent()

report = ""
print("📝 正在生成技术报告...\n")
print("=" * 50)

for chunk in agent.stream(
    "写一份关于 Python 异步编程的技术报告，包含 asyncio、协程、事件循环"
):
    print(chunk, end="", flush=True)
    report += chunk

print("\n" + "=" * 50)
print(f"✅ 报告完成，共 {len(report)} 字")
```

---

## 5. 结构化输出

需要 AI 返回 JSON 而非自然语言？使用 `response_model`：

```python
from pydantic import BaseModel
from byoe import create_agent

class CodeReview(BaseModel):
    issues: list[str]
    severity: str  # "critical" | "major" | "minor"
    suggestion: str

agent = create_agent()
result = agent.chat(
    "审查这段代码：\ndef add(a, b):\n    return a+b",
    response_model=CodeReview
)

print(f"发现 {len(result.issues)} 个问题")
print(f"严重程度: {result.severity}")
print(f"建议: {result.suggestion}")
```

结合 `stream()` 和 `response_model`，可以实现秒级响应的结构化数据提取。

---

## 6. 模型 Fallback

API 不稳定时自动切换备用模型：

```python
agent = create_agent(
    model="gpt-4o",
    api_key="sk-openai...",
    fallback_models=["gpt-4o-mini", "deepseek-chat"],
    fallbacks=[
        {
            "model": "deepseek-chat",
            "api_key": "sk-deepseek...",
            "base_url": "https://api.deepseek.com",
        }
    ]
)
```

主模型重试耗尽后，自动依次尝试备用。一个都不剩才抛出异常。

---

## 7. 更多示例

本仓库 `demos/01-api/` 下按编号提供了 12 个独立示例：

| 编号 | 文件 | 内容 |
|------|------|------|
| 01 | `01_quickstart.py` | 最简对话 |
| 02 | `02_streaming.py` | 流式 + 异步 |
| 03 | `03_structured_output.py` | 结构化输出 |
| 04 | `04_fallback_chain.py` | Fallback 链 |
| 05 | `05_memory.py` | 长期记忆 |
| 06 | `06_swarm.py` | 多 Agent 协作 |
| 07 | `07_plugins.py` | 插件系统 |
| 08 | `08_save_load.py` | 会话持久化 |
| 09 | `09_hooks.py` | 事件钩子 |
| 10 | `10_mcp.py` | MCP 集成 |
| 11 | `11_multimodal.py` | 多模态图片 |

每个示例都可以直接运行：
```bash
export OPENAI_API_KEY=sk-xxx
python demos/01-api/03_structured_output.py
```

---

## 8. 要点总结

- 三行代码嵌入 AI：`import byoe` → `create_agent()` → `.chat()`
- 三种调用方式：同步 / 流式 / 异步
- 结构化输出：`response_model=PydanticModel` → 直接拿 JSON
- Fallback 链：主模型挂了自动切换到备用
- 12 个示例代码可直接运行
- 适用场景：智能客服、代码审查、数据分析、文档生成

## 下期预告

下一篇我们扩展 AI 的能力：**自定义 Tool** —— 让你的 AI 能做任何事。

---

📎 完整文档：[API 快速入门](../../docs/03-developer-guide/API-QUICKSTART-ZH.md)
📎 API 参考：[API-REFERENCE-ZH.md](../../docs/03-developer-guide/API-REFERENCE-ZH.md)
📎 示例代码：[demos/01-api/](../../demos/01-api/)

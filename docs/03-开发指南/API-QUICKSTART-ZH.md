# BYOE Python 库 API 新手教程

> 版本：v0.8.1 · byoe.net — 携智而来，决策随行  
> 预计阅读时间：15 分钟

本教程通过 8 个循序渐进的步骤，带你从零开始掌握 BYOE Python 库 API。  
不需要先了解 CLI 或 Web 界面，直接写代码即可。

---

## 前置条件

```bash
pip install byoe
```

配置 API Key（任选一种方式）：

```bash
# Windows
set OPENAI_API_KEY=sk-...
set BYOE_MODEL=gpt-4o       # 可选，默认 gpt-4o

# macOS / Linux
export OPENAI_API_KEY=sk-...
export BYOE_MODEL=gpt-4o
```

验证安装：

```python
import byoe
print(byoe.__version__)  # 应输出 0.8.0
```

> 支持所有 OpenAI 兼容的服务商：DeepSeek、Qwen、Kimi、Claude、Ollama 等。  
> 换 Provider 只需修改 `OPENAI_BASE_URL` 和 `OPENAI_API_KEY`，代码无需改动。

---

## 第一步：最简对话

BYOE 的核心就是 `Agent`。用 `create_agent()` 创建一个，然后调用 `.chat()`。

```python
import byoe

# create_agent() 自动读取环境变量中的 API Key 和模型名
agent = byoe.create_agent()

reply = agent.chat("用一句话解释什么是递归")
print(reply)
```

就这三行。`create_agent()` 会自动：
- 读取 `OPENAI_API_KEY` / `BYOE_API_KEY`
- 读取 `BYOE_MODEL`（默认 `gpt-4o`）
- 加载所有内置工具（文件读写、Bash、代码分析等）

> **完整示例**：[`api-demo/01_quickstart.py`](../api-demo/01_quickstart.py)

---

## 第二步：多轮对话

Agent 自动维护上下文，直接连续调用 `.chat()` 即可。

```python
import byoe

agent = byoe.create_agent()

# 第一轮
agent.chat("我叫 Alice，我在学习 Python")

# 第二轮——Agent 记得前面说过的话
reply = agent.chat("你还记得我叫什么名字吗？")
print(reply)  # → "你叫 Alice..."

# 查看当前消息历史
print(f"当前对话 {len(agent.messages)} 条消息")

# 开启新会话（清空历史，保留配置）
agent.reset()
```

---

## 第三步：流式输出

对于需要实时展示生成过程的场景（聊天界面、长文本生成），使用 `.stream()`。

```python
import byoe

agent = byoe.create_agent()

# stream() 返回 StreamResponse，可以像迭代器一样使用
stream = agent.stream("写一段 20 行的 Python 快速排序，加上注释")

for token in stream:
    print(token, end="", flush=True)  # 实时打印每个 token

print()  # 换行

# 迭代结束后，通过 .result 读取完整文本
full_code = stream.result
print(f"\n共生成 {len(full_code)} 个字符")
```

> `.stream()` 和 `.chat()` 功能完全相同，区别只是获取结果的方式。

> **完整示例**：[`api-demo/02_streaming.py`](../api-demo/02_streaming.py)

---

## 第四步：asyncio 异步调用

在 asyncio 应用（FastAPI、aiohttp、异步脚本）中使用 `.achat()`。

```python
import asyncio
import byoe

agent = byoe.create_agent()

async def main():
    # 单次异步调用
    result = await agent.achat("解释一下 Python 的 GIL")
    print(result)

    # 并发调用多个 Agent（真正的并行，各自独立上下文）
    agents = [byoe.create_agent() for _ in range(3)]
    questions = ["什么是 BFS？", "什么是 DFS？", "什么是 A* 算法？"]

    results = await asyncio.gather(*[
        a.achat(q) for a, q in zip(agents, questions)
    ])
    for q, r in zip(questions, results):
        print(f"\nQ: {q}\nA: {r[:100]}...")

asyncio.run(main())
```

> **完整示例**：[`api-demo/02_streaming.py`](../api-demo/02_streaming.py)

---

## 第五步：结构化输出

不想解析 LLM 返回的自然语言？传入 pydantic 模型，直接拿到结构化数据。

```bash
pip install byoe[structured]   # 需要 pydantic >= 2.0
```

```python
import byoe
from pydantic import BaseModel

# 定义你想要的数据结构
class BugReport(BaseModel):
    severity: str           # "critical" | "major" | "minor"
    description: str        # 问题描述
    affected_files: list[str]   # 受影响文件
    fix_suggestion: str     # 修复建议

agent = byoe.create_agent()

# response_model 参数让 Agent 返回验证过的 pydantic 实例
report: BugReport = agent.chat(
    "分析这段代码是否有安全隐患：\n"
    "query = 'SELECT * FROM users WHERE id = ' + user_input",
    response_model=BugReport,
)

print(f"严重程度: {report.severity}")
print(f"描述: {report.description}")
print(f"修复建议: {report.fix_suggestion}")
```

BYOE 会自动：
1. 将 `BugReport` 的 JSON Schema 注入系统提示词
2. 从 LLM 响应中提取 JSON（自动剥离 Markdown 代码块）
3. 用 pydantic 验证并返回实例

> **完整示例**：[`api-demo/03_structured_output.py`](../api-demo/03_structured_output.py)

---

## 第六步：会话持久化（保存 / 恢复）

跨进程保存对话历史，适合长期任务、服务重启恢复等场景。

```python
import byoe

# === 进程 A：开始对话并保存 ===
agent = byoe.create_agent()
agent.chat("我们正在设计一个电商系统的数据库")
agent.chat("用户表需要 id、email、created_at 三个字段")

# 保存到文件（默认路径 ~/.byoe/conversations/conv_*.json）
path = agent.save()
print(f"会话已保存：{path}")


# === 进程 B：恢复并继续 ===
agent2 = byoe.create_agent()
agent2.load(path)

# Agent 记得之前的设计决策
reply = agent2.chat("订单表应该有哪些字段？和用户表怎么关联？")
print(reply)  # 会引用之前讨论的用户表结构
```

保存的 JSON 文件包含：完整消息历史、token 统计、时间戳、模型信息。

> **完整示例**：[`api-demo/08_save_load.py`](../api-demo/08_save_load.py)

---

## 第七步：自定义工具

通过继承 `Tool` 给 Agent 添加新能力，让它能调用你的业务逻辑、外部 API 等。

```python
import byoe
from byoe import Tool
import json
import requests

class WeatherTool(Tool):
    name = "get_weather"                           # LLM 看到的工具名
    description = "查询指定城市的实时天气和温度"      # LLM 决定何时调用的依据
    parameters = {                                 # 参数 JSON Schema
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称，例如 '上海'、'北京'"
            }
        },
        "required": ["city"],
    }

    def execute(self, city: str) -> str:
        # 这里写真实逻辑（此处用模拟数据演示）
        return json.dumps({"city": city, "temp": "28°C", "condition": "晴"})


# 将自定义工具传给 Agent
agent = byoe.create_agent(tools=[WeatherTool()])

# LLM 会在需要时自动调用 get_weather
reply = agent.chat("上海今天天气适合出门跑步吗？")
print(reply)
```

### 工具 vs Skills（技能）的区别

很多新用户会混淆这两个概念：

| | 工具（Tool / Plugin） | 技能（Skill） |
|--|----------------------|---------------|
| **本质** | Python 代码，LLM 可调用的**函数** | Markdown 文件，注入**系统提示词** |
| **作用** | 让 Agent 执行新动作（查 API、写文件） | 让 Agent 扮演角色、遵守规范 |
| **触发** | LLM 主动决策调用（function calling） | 关键词匹配后自动附加 |
| **存储** | Python 类 → 注册到 Agent | `~/.byoe/skills/` 下的 `.md` 文件 |

简单记法：**工具让 Agent 多一只手，技能让 Agent 换一个脑袋。**

### 通过 Entry-point 发布插件

如果你想把自定义工具发布为 pip 包，让他人安装后自动生效：

```toml
# pyproject.toml（你的工具包）
[project.entry-points."byoe.tools"]
weather = "mypackage.tools:WeatherTool"
```

用户只需 `pip install your-package`，下次 `import byoe` 时工具自动注册。

> **完整示例**：[`api-demo/07_plugins.py`](../api-demo/07_plugins.py)

---

## 第八步：长期记忆

让 Agent 跨会话记住重要信息，适合个性化助手、知识积累等场景。

```python
import byoe

# get_memory() 返回全局单例 LightMemory（Agent 内部也使用同一实例）
mem = byoe.get_memory()

# 写入记忆（path 是唯一键，重复写入自动更新）
mem.write(
    path="user/preferences",
    content="用户偏好 Python，不喜欢 Java。习惯 PEP8 风格，变量名用下划线。",
    layer="long_term",    # session / short_term / long_term
    tags=["preferences", "python"],
)

# 搜索记忆（FTS5 全文搜索）
results = mem.search("Python 偏好", limit=5)
for r in results:
    print(f"[{r['layer']}] {r['path']}: {r['content'][:60]}...")

# 获取统计
stats = mem.stats()
print(f"总记忆条数: {stats['total']}")
```

### 启用语义搜索（向量相似度）

```bash
# 设置嵌入模型（复用已有 API Key，无需新依赖）
export BYOE_EMBEDDING_MODEL=text-embedding-3-small

# 第一次使用：为历史记忆生成向量
byoe metrics --reindex-memory
```

```python
# 此后 search() 自动融合关键词 + 语义两路排名
results = mem.search("代码风格规范")
# 即使搜索词和存储内容用词不完全一样，也能找到相关内容
```

> **完整示例**：[`api-demo/05_memory.py`](../api-demo/05_memory.py)

---

## 第九步：全局事件钩子

钩子（Hooks）用于处理**横切关注点**：成本追踪、审计日志、监控告警。注册一次，对所有 Agent 的所有调用自动生效。

```python
import byoe

# ── 成本追踪 ──────────────────────────────────────────────────────────────
_spent = 0.0

@byoe.on("llm.response")
def track_cost(model, prompt_tokens, completion_tokens, cost_usd, duration_ms, **_):
    global _spent
    _spent += cost_usd or 0
    print(f"[cost] {model}: ${cost_usd:.5f}  累计 ${_spent:.5f}")

# ── 工具审计 ──────────────────────────────────────────────────────────────
@byoe.on("tool.call")
def audit_tool(name, kwargs, result, duration_ms, error, **_):
    status = "❌" if error else "✓"
    print(f"[tool {status}] {name}  {duration_ms:.0f}ms")

# ── 轮次指标 ──────────────────────────────────────────────────────────────
@byoe.on("agent.turn")
def log_turn(user_input, rounds, duration_ms, **_):
    print(f"[turn] rounds={rounds}  {duration_ms:.0f}ms")

# ── 记忆写入监控 ──────────────────────────────────────────────────────────
@byoe.on("memory.write")
def watch_memory(path, layer, was_update, **_):
    print(f"[memory {'update' if was_update else 'new'}] {layer}:{path}")

# 正常使用 Agent，所有钩子自动触发
agent = byoe.create_agent()
agent.chat("列出当前目录下的 .py 文件")
```

### 四个可用事件

| 事件 | 触发时机 | 关键参数 |
|------|---------|---------|
| `llm.response` | 每次 LLM API 调用完成 | `model`, `prompt_tokens`, `completion_tokens`, `cost_usd`, `duration_ms` |
| `tool.call` | 每次工具执行结束 | `name`, `kwargs`, `result`, `duration_ms`, `error` |
| `agent.turn` | 每轮对话（含工具调用）完成 | `user_input`, `response`, `rounds`, `duration_ms` |
| `memory.write` | 每次记忆写入 | `path`, `layer`, `was_update` |

### 注销与清理

```python
# 注销单个钩子
byoe.off("llm.response", track_cost)

# 清除某事件的全部钩子
byoe.clear_hooks("tool.call")

# 清除所有钩子（测试清理时使用）
byoe.clear_hooks()
```

### 通过 pip 包自动注册（Entry-point）

```toml
# 你的监控包 pyproject.toml
[project.entry-points."byoe.hooks"]
monitor = "mypackage.monitor:setup"
```

```python
# mypackage/monitor.py
import byoe

def setup():
    byoe.on("llm.response", _track_tokens)
    byoe.on("agent.turn", _track_latency)
```

用户 `pip install your-package` 后，`import byoe` 即自动激活，无需改任何代码。

> **完整示例**：[`api-demo/09_hooks.py`](../api-demo/09_hooks.py)

---

## 综合示例：代码审查助手

把前面学到的所有技能组合起来，构建一个实用的代码审查工具。

```python
"""code_reviewer.py — 基于 BYOE 的代码审查助手"""
import asyncio
import byoe
from pydantic import BaseModel
from pathlib import Path


class ReviewResult(BaseModel):
    score: int                  # 0-100
    summary: str                # 总体评价
    critical_issues: list[str]  # 严重问题（需立即修复）
    improvements: list[str]     # 改进建议
    approved: bool              # 是否通过审查


async def review_file(filepath: str) -> ReviewResult:
    """对单个文件进行代码审查，返回结构化报告。"""
    agent = byoe.create_agent(cwd=str(Path(filepath).parent))

    code = Path(filepath).read_text(encoding="utf-8")
    prompt = f"""请对以下代码文件进行全面审查：

文件：{filepath}

```python
{code}
```

重点检查：安全漏洞、代码风格、性能问题、可维护性。"""

    result: ReviewResult = await agent.achat(prompt, response_model=ReviewResult)

    # 将审查结论存入长期记忆，方便后续查询趋势
    mem = byoe.get_memory()
    mem.write(
        path=f"reviews/{filepath.replace('/', '_')}",
        content=f"评分 {result.score}，通过:{result.approved}。严重问题:{result.critical_issues}",
        layer="long_term",
        tags=["code-review"],
    )

    return result


async def main():
    import sys
    files = sys.argv[1:] or ["main.py"]

    print(f"正在审查 {len(files)} 个文件...\n")

    # 并发审查所有文件
    results = await asyncio.gather(*[review_file(f) for f in files])

    for filepath, result in zip(files, results):
        status = "✅ 通过" if result.approved else "❌ 未通过"
        print(f"{status} {filepath}  评分: {result.score}/100")
        print(f"   {result.summary}")
        if result.critical_issues:
            for issue in result.critical_issues:
                print(f"   ⚠️  {issue}")
        print()

    # 保存会话供后续参考
    agent = byoe.create_agent()
    # (可选) 从记忆中查询历史审查趋势
    mem = byoe.get_memory()
    history = mem.search("code-review 评分", layer="long_term", limit=10)
    if history:
        print(f"历史审查记录：共 {len(history)} 次")


if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python code_reviewer.py src/api.py src/models.py
```

---

## Step 10：接入 MCP 服务器（v0.8.1）

BYOE 支持双向 MCP 集成：既可以作为**客户端**消费外部 MCP 工具，也可以作为**服务端**被 VS Code/Claude Desktop 调用。

### 10a. 作为 MCP 服务端（byoe mcp-server）

```bash
byoe mcp-server        # stdio 模式，配合 VS Code / Claude Desktop 使用
```

在项目根目录创建 `.vscode/mcp.json`：

```json
{
  "servers": {
    "byoe": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "byoe", "mcp-server"]
    }
  }
}
```

配置后，VS Code Copilot 即可调用 BYOE 的 bash、edit_file、git、web_search 等全部工具。

### 10b. 作为 MCP 客户端（create_agent）

```python
import byoe

agent = byoe.create_agent(
    mcp_servers=[
        # stdio 模式：自动启动子进程
        {"name": "fs", "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]},
        # HTTP 模式：连接已运行的服务
        {"name": "myapi", "url": "http://localhost:3000"},
    ]
)

# 远程工具自动注册，LLM 可以像使用本地工具一样调用
reply = agent.chat("用 fs 服务器读取 README.md 并总结")
print(reply)
```

工具命名规则：`mcp__<server_name>__<tool_name>`（如 `mcp__fs__read_file`）。

> **完整示例**：[`api-demo/10_mcp.py`](../api-demo/10_mcp.py)

---

## Step 11：多模态图片输入（v0.8.1）

需要支持视觉输入的模型（gpt-4o、claude-3、gemini-2.5-flash 等）。

### 11a. 用户传图

```python
import byoe

agent = byoe.create_agent()  # 配置支持视觉的模型

# 单图分析
reply = agent.chat(
    "这个错误截图说明了什么问题？如何修复？",
    images=["error_screenshot.png"],
)
print(reply)

# 多图对比
reply = agent.chat(
    "对比这两张截图，找出 UI 变化",
    images=["before.png", "after.png"],
)

# 流式 + 图片
for token in agent.stream("描述这张架构图", images=["arch.png"]):
    print(token, end="", flush=True)
print()
```

### 11b. Agent 主动读图（read_image 工具）

```python
# LLM 自主决策调用 read_image，无需用户手动传图
reply = agent.chat("读取 diagram.png 并分析其中的服务依赖关系")
# Agent 自动调用 read_image("diagram.png")，图片以视觉消息注入上下文
```

### 11c. 直接使用 read_image 工具

```python
from byoe.engine.tools.read_image import ReadImageTool

tool = ReadImageTool()
data_url = tool.execute("screenshot.png")
# 返回 "data:image/png;base64,iVBORw0KGgo..."
```

支持格式：JPEG、PNG、GIF、WebP，最大 20 MB。通过魔术字节自动检测 MIME 类型。

> **完整示例**：[`api-demo/11_multimodal.py`](../api-demo/11_multimodal.py)

---

## 下一步

| 想了解 | 文档 |
|--------|------|
| 完整 API 签名和参数说明 | [API-REFERENCE-ZH.md](./API-REFERENCE-ZH.md) |
| Hooks 事件参考 | [API-REFERENCE-ZH.md#hooks](./API-REFERENCE-ZH.md#hooks) |
| MCP 集成详解 | [USER-MANUAL-ZH.md#18-mcp-生态集成](./USER-MANUAL-ZH.md) |
| 多模态图片详解 | [USER-MANUAL-ZH.md#19-多模态图片输入](./USER-MANUAL-ZH.md) |
| Swarm 多专家协作 | [SWARM-GUIDE-ZH.md](./SWARM-GUIDE-ZH.md) |
| 技能（Skills）系统 | [SKILLS-GUIDE-ZH.md](./SKILLS-GUIDE-ZH.md) |
| 运行完整可执行示例 | [`../api-demo/`](../api-demo/)（00～11 系列） |
| 环境变量完整列表 | [configuration.md](./configuration.md) |
| Web/CLI 界面使用 | [USER-MANUAL-ZH.md](./USER-MANUAL-ZH.md) |

---

> **提示**：所有示例都可以直接运行。配好 `OPENAI_API_KEY` 之后：
> ```bash
> cd api-demo
> python 01_quickstart.py
> ```


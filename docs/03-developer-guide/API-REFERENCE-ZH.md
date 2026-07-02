# BYOE Python 库 API 参考手册

> 版本：v0.8.1 · 适用于 `byoe>=0.8.1`  
> byoe.net — 携智而来，决策随行

---

## 目录

1. [安装](#安装)
2. [create_agent()](#create_agent)
3. [Agent](#agent)
4. [StreamResponse](#streamresponse)
5. [LLM](#llm)
6. [Tool（自定义工具基类）](#tool)
7. [LightMemory](#lightmemory)
8. [get_memory()](#get_memory)
9. [Hooks（全局事件钩子）](#hooks)
10. [AgentScheduler](#agentscheduler)
11. [MCP 客户端（MCPSession）](#mcp-客户端-mcpsession)
12. [MCP 服务端（byoe mcp-server）](#mcp-服务端-byoe-mcp-server)
13. [环境变量速查](#环境变量速查)
14. [错误处理](#错误处理)

---

## 安装

```bash
pip install byoe                    # 基础安装
pip install byoe[structured]        # 含结构化输出支持（pydantic >= 2.0）
```

快速验证：

```python
import byoe
print(byoe.__version__)  # 0.8.1
```

---

## create_agent()

工厂函数，自动从环境变量读取配置，返回开箱即用的 `Agent`。

### 签名

```python
byoe.create_agent(
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    tools: list[Tool] | None = None,
    system: str | None = None,
    cwd: str | None = None,
    max_context_tokens: int | None = None,
    fallback_models: list[str] | None = None,
    fallbacks: list[dict] | None = None,
    mcp_servers: list[dict] | None = None,
) -> Agent
```

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | `str \| None` | 读取 `BYOE_MODEL` / `OPENAI_MODEL_NAME` / `"gpt-4o"` | 使用的模型名称 |
| `api_key` | `str \| None` | 读取 `BYOE_API_KEY` / `OPENAI_API_KEY` | API 鉴权密钥 |
| `base_url` | `str \| None` | 读取 `OPENAI_BASE_URL` | 自定义 API 端点（兼容 OpenAI 的所有服务商） |
| `tools` | `list[Tool] \| None` | 所有内置工具 | 传入自定义列表可覆盖默认工具集 |
| `system` | `str \| None` | 内置系统提示词 | 自定义系统提示词 |
| `cwd` | `str \| None` | 当前工作目录 | Agent 文件/Bash 操作的根目录 |
| `max_context_tokens` | `int \| None` | `128_000` | 上下文窗口大小（token 数），超出时自动压缩 |
| `fallback_models` | `list[str] \| None` | `None` | 同 Provider 备用模型（主模型失败时按序尝试） |
| `fallbacks` | `list[dict] \| None` | `None` | 跨 Provider 完整降级配置，每项包含 `model`、`api_key`、`base_url` |
| `mcp_servers` | `list[dict] \| None` | `None` | MCP 服务器列表，每项可含 `name`、`command`（stdio 模式）或 `url`（HTTP 模式） |

### 示例

```python
import byoe

# 最简：全部从环境变量读取
agent = byoe.create_agent()

# 指定模型和目录
agent = byoe.create_agent(model="deepseek-chat", cwd="/my/project")

# 配置降级链
agent = byoe.create_agent(
    model="gpt-4o",
    fallback_models=["gpt-4o-mini"],              # 同 Provider 简写
    fallbacks=[
        {"model": "deepseek-chat",
         "api_key": "sk-ds-...",
         "base_url": "https://api.deepseek.com"},
    ],
)

# 接入 MCP 服务器
agent = byoe.create_agent(
    mcp_servers=[
        {"name": "fs", "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]},
        {"name": "db", "url": "http://localhost:3000"},
    ]
)

---

## Agent

核心 Agent 类，封装 LLM 调用、工具执行、上下文压缩和会话管理。

### 构造器

```python
Agent(
    llm: LLM,
    tools: list[Tool] | None = None,
    system: str | None = None,
    cwd: str | None = None,
    max_rounds: int = 30,
    max_context_tokens: int = 128_000,
)
```

> 推荐使用 `create_agent()` 工厂函数代替直接构造。

### 方法

---

#### `chat()`

同步执行一轮对话。

```python
agent.chat(
    user_input: str,
    images: list[str] | None = None,
    on_token: Callable[[str], None] | None = None,
    on_tool: Callable[[str, dict], None] | None = None,
    on_tool_result: Callable[[str, dict, str], None] | None = None,
    on_compress: Callable[[str, int, int], None] | None = None,
    response_model: type | None = None,
) -> str | BaseModel
```

| 参数 | 说明 |
|------|------|
| `user_input` | 用户消息文本 |
| `images` | 图片文件路径列表（JPEG/PNG/GIF/WebP，≤20 MB），自动转换为 base64 data URL 注入多模态消息 |
| `on_token` | 流式回调 `fn(token: str)`，每个 token 调用一次 |
| `on_tool` | 工具调用前回调 `fn(tool_name: str, kwargs: dict)` |
| `on_tool_result` | 工具调用后回调 `fn(tool_name: str, kwargs: dict, result: str)` |
| `on_compress` | 上下文压缩回调 `fn(layer: str, before_tokens: int, after_tokens: int)` |
| `response_model` | pydantic 模型类，返回该模型实例（需 `byoe[structured]`） |

```python
# 普通调用
reply = agent.chat("解释快速排序")

# 多模态：传入图片
reply = agent.chat("这个截图有什么问题？", images=["error.png"])
reply = agent.chat("对比这两张图", images=["before.png", "after.png"])

# 带工具监控
def watch_tool(name, kwargs):
    print(f"[工具调用] {name}: {kwargs}")

reply = agent.chat("列出当前目录所有 .py 文件", on_tool=watch_tool)

# 结构化输出
from pydantic import BaseModel

class Summary(BaseModel):
    title: str
    points: list[str]
    confidence: float

result: Summary = agent.chat("总结这段代码的功能", response_model=Summary)
print(result.title, result.points)
```

---

#### `stream()`

流式调用，返回 `StreamResponse` 对象（可迭代）。

```python
agent.stream(
    user_input: str,
    images: list[str] | None = None,
    response_model: type | None = None,
) -> StreamResponse
```

```python
stream = agent.stream("写一段 Python 快速排序")
for token in stream:
    print(token, end="", flush=True)

# 流式 + 图片
for token in agent.stream("描述这张架构图", images=["arch.png"]):
    print(token, end="", flush=True)
print()

full_text = stream.result  # 迭代完成后可以读取完整文本
```

---

#### `achat()`

asyncio 异步包装，签名与 `chat()` 相同，返回 `Coroutine`。

```python
import asyncio

result = asyncio.run(agent.achat("解释 CAP 定理"))
```

---

#### `save()`

将当前会话（消息历史 + token 计数 + 元数据）序列化到 JSON 文件。

```python
agent.save(path: str | Path | None = None) -> str
```

- `path=None`：自动保存到 `~/.byoe/conversations/conv_<timestamp>.json`
- 返回实际写入路径

---

#### `load()`

从 JSON 文件恢复会话。

```python
agent.load(path: str | Path) -> None
```

```python
path = agent.save()
# ...在另一个进程中...
agent2 = byoe.create_agent()
agent2.load(path)
print(agent2.chat("上面我们讲到哪里了？"))
```

---

#### `reset()`

清除消息历史，保留 Agent 配置。

```python
agent.reset() -> None
```

---

#### `abort()`

从另一个线程中断当前正在执行的 `chat()` 调用。

```python
import threading

def stop_after(agent, seconds):
    threading.Timer(seconds, agent.abort).start()

stop_after(agent, 10)  # 10 秒后自动中断
reply = agent.chat("做一个非常耗时的任务...")
# 若超时，reply 为 "(aborted by user)"
```

---

#### `add_runtime_tool()`

在 Agent 运行时注册额外工具（无需重建 Agent）。

```python
agent.add_runtime_tool(tool: Tool) -> None
```

---

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `messages` | `list[dict]` | 当前会话历史（不含 system message） |
| `total_prompt_tokens` | `int` | 累计 prompt token 消耗 |
| `total_completion_tokens` | `int` | 累计 completion token 消耗 |
| `llm` | `LLM` | 底层 LLM 实例 |
| `tools` | `list[Tool]` | 当前工具集 |

---

## StreamResponse

`agent.stream()` 的返回值，支持迭代和结果读取。

```python
class StreamResponse:
    result: str | BaseModel  # 迭代完成后可读；未完成时为空字符串
```

### 使用方式

```python
stream = agent.stream("写 10 行关于 Python 的诗")

# 方式一：for 循环逐 token 打印
for token in stream:
    print(token, end="", flush=True)
poem = stream.result  # 迭代完成后读取

# 方式二：一次性消费
tokens = list(stream)
full_text = stream.result

# 方式三：配合结构化输出
from pydantic import BaseModel

class Poem(BaseModel):
    title: str
    lines: list[str]

stream = agent.stream("写一首诗", response_model=Poem)
for _ in stream:
    pass  # 消耗 token 流
poem: Poem = stream.result  # 返回 pydantic 实例
```

---

## LLM

LLM Provider 封装层，支持多 Provider 和自动降级链。

### 构造器

```python
LLM(
    model: str,
    api_key: str | None = None,
    base_url: str | None = None,
    fallback_providers: list[dict] | None = None,
    fallback_models: list[str] | None = None,
    **extra,
)
```

| 参数 | 说明 |
|------|------|
| `model` | 模型名称，例如 `"gpt-4o"`、`"deepseek-chat"` |
| `api_key` | API Key（不传则读取环境变量） |
| `base_url` | API 端点（不传则读取 `OPENAI_BASE_URL`） |
| `fallback_providers` | 跨 Provider 降级配置，每项 `{"model": ..., "api_key": ..., "base_url": ...}` |
| `fallback_models` | 同 Provider 不同模型降级，简写形式 |
| `**extra` | 透传给 `openai.OpenAI()` 的额外参数（如 `timeout`、`max_retries`） |

### 示例

```python
from byoe import LLM

# 基础用法
llm = LLM(model="gpt-4o", api_key="sk-...")

# 同 Provider 多模型降级
llm = LLM(
    model="gpt-4o",
    api_key="sk-...",
    fallback_models=["gpt-4o-mini", "gpt-3.5-turbo"],
)

# 跨 Provider 降级链
llm = LLM(
    model="gpt-4o",
    api_key="sk-openai...",
    fallback_providers=[
        {"model": "deepseek-chat",
         "api_key": "sk-ds...",
         "base_url": "https://api.deepseek.com"},
        {"model": "qwen3-max",
         "api_key": "sk-qwen...",
         "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    ],
)
```

### 内置价格表（按百万 token，美元）

LLM 内置主流模型价格，用于 `byoe metrics` 的费用估算，支持通过 `~/.byoe/pricing.json` 自定义。

```json
// ~/.byoe/pricing.json
{
  "my-local-llama": [0.0, 0.0],
  "custom-gpt4": [2.0, 8.0]
}
```

---

## Tool

自定义工具基类，继承后注册给 Agent 使用。

### 定义自定义工具

```python
from byoe import Tool

class WeatherTool(Tool):
    name = "get_weather"                       # 工具名（LLM 调用此名称）
    description = "获取指定城市的当前天气和温度"    # 工具描述（提供给 LLM）
    parameters = {                             # JSON Schema 参数定义
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称，例如 '上海'、'北京'"
            }
        },
        "required": ["city"],
    }

    def run(self, city: str) -> str:
        # 实际逻辑
        return f"{city} 当前晴天，28°C"
```

### 注册给 Agent

```python
import byoe

agent = byoe.create_agent(tools=[WeatherTool()])
print(agent.chat("上海今天天气怎么样？"))
```

### 运行时动态添加

```python
agent = byoe.create_agent()
agent.add_runtime_tool(WeatherTool())
```

### 通过 pip 包注册（Entry-point 插件）

在你的包的 `pyproject.toml` 中添加：

```toml
[project.entry-points."byoe.tools"]
weather = "mypackage.tools:WeatherTool"
```

安装后，下次 `import byoe` 时自动加载到 `create_agent()` 默认工具集。

---

## LightMemory

基于 SQLite FTS5 的轻量长期记忆，可选语义（向量）搜索。

### 构造器

```python
LightMemory(db_path: str | Path | None = None)
```

- `db_path=None`：使用默认路径 `~/.byoe/memory.db`

### 主要方法

---

#### `write()`

写入或更新一条记忆。

```python
memory.write(
    path: str,           # 记忆路径（唯一键），例如 "project/auth/design"
    content: str,        # 记忆内容
    layer: str = "long_term",    # 层级："session"、"short_term"、"long_term"
    summary: str = "",   # 摘要（可选）
    tags: list[str] | None = None,
    source: str = "agent",
) -> tuple[str, bool]    # 返回 (mem_id, was_update)
```

```python
mem_id, updated = memory.write(
    path="myproject/notes/api-design",
    content="认证模块使用 JWT，过期时间 7 天，刷新 token 有效期 30 天。",
    layer="long_term",
    tags=["auth", "jwt"],
)
print("新建" if not updated else "已更新")
```

---

#### `search()`

全文（FTS5 BM25）+ 可选语义（余弦相似度）融合搜索。

```python
memory.search(
    query: str,
    layer: str | None = None,    # 过滤层级，None = 所有层
    limit: int = 10,
) -> list[dict]
```

每项结果包含：`id`、`path`、`content`、`summary`、`tags`、`layer`、`score`。

```python
results = memory.search("JWT 认证", layer="long_term", limit=5)
for r in results:
    print(r["path"], r["score"], r["content"][:80])
```

---

#### `search_semantic()`

仅语义搜索（需设置 `BYOE_EMBEDDING_MODEL`）。

```python
memory.search_semantic(
    query: str,
    limit: int = 10,
    layer: str | None = None,
) -> list[dict]
```

---

#### `get()`

按路径精确获取一条记忆。

```python
memory.get(path: str) -> dict | None
```

---

#### `forget()`

删除一条记忆。

```python
memory.forget(path: str) -> bool  # True if existed and deleted
```

---

#### `stats()`

统计各层级记忆数量。

```python
memory.stats() -> dict[str, int]
# 示例返回: {"session": 12, "short_term": 45, "long_term": 201, "total": 258}
```

---

#### `reindex()`

为没有嵌入向量的存量记忆批量生成向量（需 `BYOE_EMBEDDING_MODEL`）。

```python
count = memory.reindex(
    batch_size: int = 100,         # 每批处理条数（越大越快，但占用更多内存）
    on_progress: Callable | None = None,  # 进度回调 fn(done: int, total: int)
) -> int
```

```python
def show_progress(done, total):
    print(f"\r  {done}/{total} 条", end="", flush=True)

count = memory.reindex(batch_size=200, on_progress=show_progress)
print(f"\n已为 {count} 条记忆生成向量")
```

---

## get_memory()

获取全局默认 `LightMemory` 单例（路径同 Agent 使用的实例）。

```python
byoe.get_memory() -> LightMemory
```

```python
mem = byoe.get_memory()
mem.write("my/note", "重要备忘录")
results = mem.search("备忘录")
```

---

## Hooks

全局发布/订阅事件总线，用于注入**横切关注点**：成本追踪、审计日志、安全监控、可观测性。

注册一次，对所有 Agent 的所有调用自动生效，无需修改每个调用点。

### 函数

| 函数 | 说明 |
|------|------|
| `byoe.on(event, fn=None)` | 注册钩子，支持装饰器和函数两种形式 |
| `byoe.off(event, fn)` | 注销一个钩子 |
| `byoe.emit(event, **kwargs)` | 手动触发一个事件（用于自定义集成） |
| `byoe.clear_hooks(event=None)` | 清除钩子；`event=None` 清除全部 |

### 注册方式

```python
import byoe

# 装饰器形式（推荐）
@byoe.on("llm.response")
def my_hook(model, prompt_tokens, completion_tokens, cost_usd, duration_ms, **_):
    print(f"[cost] {model}: ${cost_usd:.5f}")

# 函数调用形式（适合条件注册）
def log_cost(model, cost_usd, **_):
    print(f"${cost_usd:.5f}")

byoe.on("llm.response", log_cost)

# 注销
byoe.off("llm.response", log_cost)

# 清除单个事件的全部钩子
byoe.clear_hooks("llm.response")

# 清除所有钩子
byoe.clear_hooks()
```

> **注意**：钩子内部异常会被捕获并记录到 warn 级别日志，不会中断 Agent 执行。

### 可用事件

#### `llm.response`

每次 LLM API 调用完成后触发。

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | `str` | 模型名称，例如 `"deepseek-v4-flash"` |
| `prompt_tokens` | `int` | 本次调用的输入 token 数 |
| `completion_tokens` | `int` | 本次调用的输出 token 数 |
| `cost_usd` | `float \| None` | 本次费用估算（美元），模型不在价格表时为 `None` |
| `duration_ms` | `float` | API 调用耗时（毫秒） |

```python
@byoe.on("llm.response")
def track_cost(model, prompt_tokens, completion_tokens, cost_usd, duration_ms, **_):
    print(f"{model}: +{prompt_tokens}p/{completion_tokens}c = ${cost_usd:.5f} ({duration_ms:.0f}ms)")
```

---

#### `tool.call`

每次工具执行结束后触发（无论成功或失败）。

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 工具名称，例如 `"bash"`、`"read_file"` |
| `kwargs` | `dict` | 传给工具的参数 |
| `result` | `str` | 工具返回的字符串结果 |
| `duration_ms` | `float` | 工具执行耗时（毫秒） |
| `error` | `Exception \| None` | 执行异常，正常完成时为 `None` |

```python
import json
from datetime import datetime, timezone
from pathlib import Path

@byoe.on("tool.call")
def audit_tool(name, kwargs, result, duration_ms, error, **_):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": name,
        "status": "error" if error else "ok",
        "duration_ms": round(duration_ms, 1),
    }
    Path("~/.byoe/audit.jsonl").expanduser().open("a").write(
        json.dumps(entry) + "\n"
    )
```

---

#### `agent.turn`

每次用户→助手完整一轮（所有工具调用已完成）结束后触发。

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_input` | `str` | 本轮用户输入 |
| `response` | `str` | 最终助手输出 |
| `prompt_tokens` | `int` | 最后一次 LLM 调用的输入 token 数 |
| `completion_tokens` | `int` | 最后一次 LLM 调用的输出 token 数 |
| `rounds` | `int` | 本轮消耗的 LLM 调用次数（包含工具调用轮次） |
| `duration_ms` | `float` | 本轮总耗时（毫秒） |

```python
@byoe.on("agent.turn")
def log_turn(user_input, response, rounds, duration_ms, **_):
    print(f"[turn] rounds={rounds} {duration_ms:.0f}ms | Q: {user_input[:40]}")
```

---

#### `memory.write`

每次 `LightMemory.write()` 调用成功后触发。

| 参数 | 类型 | 说明 |
|------|------|------|
| `path` | `str` | 记忆路径（唯一键） |
| `layer` | `str` | 层级：`session` / `short_term` / `long_term` |
| `was_update` | `bool` | `True` = 更新已有记忆，`False` = 新建 |

```python
@byoe.on("memory.write")
def watch_memory(path, layer, was_update, **_):
    action = "updated" if was_update else "created"
    print(f"[memory] {action} {layer}:{path}")
```

---

### 实用模式

#### 成本预算保护

```python
import byoe

_spent = 0.0
BUDGET = 1.0  # 超过 $1.00 时告警

@byoe.on("llm.response")
def budget_guard(cost_usd, model, **_):
    global _spent
    _spent += cost_usd or 0
    if _spent > BUDGET:
        print(f"⚠️ 累计花费 ${_spent:.4f} 超出预算 ${BUDGET}")
```

#### Prometheus 指标

```python
# pip install prometheus-client
from prometheus_client import Counter, Histogram, start_http_server
import byoe

tokens = Counter("byoe_tokens_total", "LLM tokens", ["model", "type"])
latency = Histogram("byoe_turn_seconds", "Turn latency")

@byoe.on("llm.response")
def push_tokens(model, prompt_tokens, completion_tokens, **_):
    tokens.labels(model=model, type="prompt").inc(prompt_tokens)
    tokens.labels(model=model, type="completion").inc(completion_tokens)

@byoe.on("agent.turn")
def push_latency(duration_ms, **_):
    latency.observe(duration_ms / 1000)

start_http_server(8000)  # 暴露 /metrics 端点
```

#### Entry-point 插件自动注册

第三方监控包可通过 `byoe.hooks` entry-point 在 `import byoe` 时自动注册：

```toml
# pyproject.toml（你的监控包）
[project.entry-points."byoe.hooks"]
my_monitor = "mypackage.monitoring:setup"
```

```python
# mypackage/monitoring.py
import byoe

def setup():
    byoe.on("llm.response", _track_cost)
    byoe.on("agent.turn", _track_latency)
```

用户只需 `pip install your-monitor-package`，`import byoe` 时自动激活。

> **完整示例**：[`api-demo/09_hooks.py`](../api-demo/09_hooks.py)

---

## AgentScheduler

Web 模式下的任务调度器，通常由 `byoe web` 自动管理，不需要手动使用。

```python
AgentScheduler(agent: Agent, session_id: str | None = None)
```

| 方法 | 说明 |
|------|------|
| `submit(task: str)` | 提交一个任务（非阻塞，加入队列） |
| `cancel()` | 取消当前任务 |
| `is_running` | 属性，是否有任务正在执行 |

---

## MCP 客户端（MCPSession）

> v0.8.1 新增

通过 `create_agent(mcp_servers=[...])` 接入外部 MCP 服务器。远程工具自动注册为 `mcp__<server>__<tool>` 命名空间。

### create_agent() 接入方式

```python
agent = byoe.create_agent(
    mcp_servers=[
        # stdio 模式：启动子进程
        {"name": "fs", "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]},
        # HTTP 模式：连接远程服务器
        {"name": "db", "url": "http://localhost:3000"},
    ]
)
# LLM 可调用 mcp__fs__read_file, mcp__db__query 等远程工具
```

### 手动使用 MCPSession

```python
from byoe.engine.mcp import MCPSession

# stdio 模式
async_session = MCPSession.from_stdio(
    name="fs",
    command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "."],
)
tools = async_session.get_tools()   # 返回 list[Tool]

# HTTP 模式
http_session = MCPSession.from_http(name="db", url="http://localhost:3000")
tools = http_session.get_tools()
```

### connect_servers()

```python
from byoe.engine.mcp import connect_servers

tools = connect_servers([
    {"name": "fs", "command": [...]},
    {"name": "db", "url": "http://..."},
])
# tools: list[Tool]，每个工具名为 mcp__<server>__<tool>
```

### 环境变量配置

```bash
export BYOE_MCP_SERVERS='[{"name":"fs","command":["npx","-y","@modelcontextprotocol/server-filesystem","."]}]'
```

---

## MCP 服务端（byoe mcp-server）

> v0.8.1 新增

将 BYOE 的 23 个内置工具暴露为 MCP 服务端，供 VS Code Copilot、Claude Desktop、Cursor 等客户端调用。

### 命令行启动

```bash
byoe mcp-server                     # stdio 模式（VS Code / Claude Desktop / Cursor）
byoe mcp-server --http --port 3000  # HTTP 模式（Docker / 远程部署）
byoe mcp-server --cwd /my/project   # 指定工作目录
```

### VS Code 配置（.vscode/mcp.json）

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

### Claude Desktop 配置（~/.claude/claude_desktop_config.json）

```json
{
  "mcpServers": {
    "byoe": {
      "command": "python",
      "args": ["-m", "byoe", "mcp-server"]
    }
  }
}
```

### Python API

```python
from byoe.engine.mcp_server import MCPServer, run_stdio, run_http

# 手动运行（通常用 CLI）
run_stdio()                   # 从 stdin 读取 JSON-RPC，输出到 stderr-redirected stdout
run_http(host="0.0.0.0", port=3000)  # HTTP 模式，/health + /tools + /messages
```

---

## 环境变量速查

### 核心配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENAI_API_KEY` / `BYOE_API_KEY` | — | API 鉴权密钥（必填） |
| `BYOE_MODEL` / `OPENAI_MODEL_NAME` | `deepseek-v4-flash` | 默认模型名 |
| `OPENAI_BASE_URL` | OpenAI 官方 | API 端点（换 Provider 时设置） |
| `BYOE_MAX_CONTEXT_TOKENS` | `128000` | 上下文窗口大小 |

### 语义记忆

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_EMBEDDING_MODEL` | 空（禁用） | 嵌入模型名，设置后启用语义搜索 |
| `BYOE_EMBEDDING_API_KEY` | 同主 key | 嵌入专用 API Key |
| `BYOE_EMBEDDING_BASE_URL` | 同主 URL | 嵌入专用端点 |

### 记忆 GC

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_MEMORY_MAX_ROWS` | `5000` | 记忆最大行数 |
| `BYOE_MEMORY_SESSION_TTL_DAYS` | `30` | session 层过期天数 |
| `BYOE_MEMORY_SHORT_TTL_DAYS` | `14` | short_term 层过期天数 |
| `BYOE_MEMORY_GC_EVERY_WRITES` | `50` | 每 N 次写入触发一次 GC |

### Web / 安全

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_WEB_PORT` | `7860` | Web 服务端口 |
| `BYOE_ALLOWED_ORIGINS` | 空 | 逗号分隔的允许跨域来源（精确 scheme+host+port 匹配） |
| `BYOE_CHAT_RATE_LIMIT` | `0`（禁用） | 每 IP 每分钟最大请求数 |
| `BYOE_BASH_TIMEOUT` | `600` | Bash 工具执行超时（秒，最小 30） |

### MCP

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_MCP_SERVERS` | `[]` | JSON 数组，每项含 `name` + `command` 或 `url`，等同 `create_agent(mcp_servers=[...])` |

### 日志与调试

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_LOG` | `0` | `1` 启用结构化 JSONL 日志 |
| `BYOE_LOG_LEVEL` | `info` | `debug` / `info` / `warning` / `error` |

---

## 错误处理

### 常见错误

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `RuntimeError: 缺少 API Key` | 未设置 `OPENAI_API_KEY` 或 `BYOE_API_KEY` | 设置对应环境变量 |
| `openai.AuthenticationError` | API Key 错误或过期 | 检查并更新 Key |
| `openai.APIConnectionError` | 网络不通或 base_url 错误 | 检查网络、代理设置 |
| `ImportError: pydantic` | 使用 `response_model` 但未安装 pydantic | `pip install byoe[structured]` |
| `(aborted by user)` | `abort()` 被调用或超时中断 | 正常，检查业务逻辑 |

### 推荐错误处理模式

```python
import byoe
from openai import APIError

agent = byoe.create_agent()

try:
    result = agent.chat("你好")
except APIError as e:
    print(f"LLM 调用失败: {e.status_code} — {e.message}")
except RuntimeError as e:
    print(f"配置错误: {e}")
```

---

## 完整示例

```python
"""综合示例：流式对话 + 结构化输出 + 会话保存 + 记忆检索"""
import byoe
from pydantic import BaseModel

class CodeReview(BaseModel):
    score: int
    critical_issues: list[str]
    suggestions: list[str]

# 1. 创建 Agent（从环境变量读取配置）
agent = byoe.create_agent(cwd="./my-project")

# 2. 流式对话
stream = agent.stream("介绍一下这个项目的目录结构")
for tok in stream:
    print(tok, end="", flush=True)
print()

# 3. 结构化输出
review: CodeReview = agent.chat(
    "帮我做一次代码质量审查",
    response_model=CodeReview,
)
print(f"质量评分: {review.score}/100")
print(f"严重问题: {review.critical_issues}")

# 4. 保存会话
path = agent.save()
print(f"会话已保存: {path}")

# 5. 操作记忆
mem = byoe.get_memory()
mem.write(
    path="project/review/2026-06-30",
    content=f"评分 {review.score}，主要问题: {', '.join(review.critical_issues)}",
    layer="long_term",
    tags=["code-review"],
)
print("记忆已保存")
```

---

> 更多示例见 [`byoe/api-demo/`](../byoe/api-demo/) 目录（01～08 系列文件）。

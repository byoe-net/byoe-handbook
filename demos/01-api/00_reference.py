"""BYOE Python Library API — 完整参考手册

本文件是 BYOE v0.8.0 Python 库 API 的完整文档，
涵盖所有公开类、方法、参数和环境变量。

目录：
  1. 快速安装与配置
  2. create_agent() — 工厂函数
  3. Agent — 核心 Agent 类
  4. LLM — 语言模型层
  5. Tool — 工具基类
  6. LightMemory — 长期记忆
  7. AgentScheduler — 任务调度
  8. 环境变量参考
  9. CLI 命令参考
"""

# =============================================================================
# 1. 快速安装与配置
# =============================================================================
#
#   pip install byoe                           # 基础安装
#   pip install byoe[dotenv]                   # 支持 .env 文件
#   pip install byoe[fast]                     # 更快的 token 计数（tiktoken）
#   pip install byoe[structured]               # 结构化输出（pydantic）
#
# 最小配置：
#   set BYOE_API_KEY=sk-...
#   set BYOE_MODEL=gpt-4o                      # 可选，默认 gpt-4o
#   set OPENAI_BASE_URL=https://...            # 可选，兼容第三方端点


# =============================================================================
# 2. create_agent() — 工厂函数
# =============================================================================
#
# byoe.create_agent(
#     model: str | None = None,
#     api_key: str | None = None,
#     base_url: str | None = None,
#     tools: list[Tool] | None = None,
#     system: str | None = None,
#     cwd: str | None = None,
#     max_context_tokens: int | None = None,
#     fallback_models: list[str] | None = None,
#     fallbacks: list[dict] | None = None,
# ) -> Agent
#
# 参数：
#   model              模型名称。None → 读取 BYOE_MODEL / OPENAI_MODEL_NAME / "gpt-4o"
#   api_key            API 密钥。None → 读取 BYOE_API_KEY / OPENAI_API_KEY
#   base_url           API 端点。None → 读取 OPENAI_BASE_URL
#   tools              工具列表。None → 使用全部 22 个内置工具
#   system             系统提示覆盖。None → 使用内置系统提示（含 Crew 上下文）
#   cwd                工作目录，用于 bash/文件工具的沙箱根目录
#   max_context_tokens 上下文窗口大小（默认 128_000）
#   fallback_models    同 Provider 备用模型列表
#   fallbacks          跨 Provider 备用配置列表，每项为 {model, api_key, base_url}

import byoe
import os

agent = byoe.create_agent(
    model="gpt-4o",
    api_key=os.environ.get("BYOE_API_KEY", ""),
    fallback_models=["gpt-4o-mini"],
    cwd=".",
)


# =============================================================================
# 3. Agent — 核心类
# =============================================================================
#
# 构造：
#   Agent(
#       llm: LLM,
#       tools: list[Tool] | None = None,
#       max_context_tokens: int = 128_000,
#       max_rounds: int = 50,
#       system: str | None = None,
#       cwd: str | None = None,
#   )
#
# 主要方法：
#
#   chat(user_input, on_token=None, on_tool=None, on_tool_result=None,
#        on_compress=None, response_model=None) -> str | Any
#     同步对话。response_model 传入 Pydantic 类时返回模型实例。
#
#   stream(user_input, on_tool=None, on_tool_result=None,
#          on_compress=None, response_model=None) -> StreamResponse
#     返回可迭代 StreamResponse，实时 yield token；
#     迭代完成后 .result 包含完整响应（含 response_model 解析结果）。
#
#   achat(user_input, **kwargs) -> Awaitable[str | Any]
#     asyncio 异步版本，接受所有 chat() 的关键字参数。
#
#   save(path: str | Path | None = None) -> str
#     将消息历史序列化到 JSON 文件，返回文件路径。
#     默认路径：~/.byoe/conversations/conv_<timestamp>.json
#
#   load(path: str | Path) -> None
#     从 save() 生成的 JSON 恢复消息历史和 token 计数器。
#
#   reset() -> None
#     清空消息历史、changed_files、token 计数器，重建系统提示。
#
#   abort() -> None
#     通知正在运行的 chat() 循环在当前步骤完成后停止。
#
#   add_runtime_tool(tool: Tool) -> None
#     运行时动态注册工具（替换同名旧工具）。
#
# 属性：
#   messages        list[dict]  当前对话历史（OpenAI 格式）
#   changed_files   set[str]    本会话中被修改过的文件路径
#   llm             LLM         关联的 LLM 实例
#   tools           list[Tool]  已注册的工具列表
#
# 回调参数类型：
#   on_token(token: str)                       每个流式 token 到达时调用
#   on_tool(name: str, kwargs: dict)           工具调用前调用
#   on_tool_result(name, kwargs, result: str)  工具调用后调用
#   on_compress(layer: str, before: int, after: int)  上下文压缩时调用

from byoe import Agent, LLM

llm = LLM(model="gpt-4o", api_key=os.environ.get("BYOE_API_KEY", ""))
_agent = Agent(llm=llm, tools=[])


# =============================================================================
# 4. LLM — 语言模型层
# =============================================================================
#
# LLM(
#     model: str,
#     api_key: str,
#     base_url: str | None = None,
#     fallback_providers: list[dict] | None = None,
#     fallback_models: list[str] | None = None,
#     **kwargs,                               # 透传给 openai.ChatCompletion
# )
#
# 属性：
#   model                  str    当前使用的模型名称
#   total_prompt_tokens    int    本会话累计输入 token
#   total_completion_tokens int   本会话累计输出 token
#   estimated_cost         float  按内置价格表估算的 USD 费用（无法识别的模型返回 None）
#
# 方法：
#   reconfigure(model, api_key, base_url) -> None
#     运行时切换模型/Provider，新 Provider 时自动重置 token 计数。
#
# fallback_models 与 fallback_providers 区别：
#   fallback_models    同 Provider、同 api_key，仅切换模型名称（简写）
#   fallback_providers 完整配置 {model, api_key, base_url}，可跨 Provider
#
# 内置价格表覆盖（~/.byoe/pricing.json）：
#   { "my-model": [input_per_million, output_per_million] }

from byoe import LLM as _LLM

_llm = _LLM(
    model="gpt-4o",
    api_key="sk-...",
    fallback_models=["gpt-4o-mini"],           # 同 provider 简写
    fallback_providers=[                       # 跨 provider 完整配置
        {"model": "deepseek-chat",
         "api_key": "sk-ds-...",
         "base_url": "https://api.deepseek.com"},
    ],
    temperature=0.0,                           # 额外参数透传给 OpenAI SDK
    max_tokens=4096,
)


# =============================================================================
# 5. Tool — 工具基类
# =============================================================================
#
# 继承 Tool 并实现三个类属性 + execute 方法：
#
# class MyTool(Tool):
#     name        = "tool_name"          # 唯一标识，LLM 调用时使用
#     description = "..."                # 功能说明，影响 LLM 的调用决策
#     parameters  = {                    # JSON Schema，定义参数
#         "type": "object",
#         "properties": { "arg": {"type": "string"} },
#         "required": ["arg"],
#     }
#
#     def execute(self, **kwargs) -> str:
#         # 返回字符串，作为 tool_result 传回 LLM
#         return "result"
#
# 通过 Entry-point 注册插件（pyproject.toml）：
#   [project.entry-points."byoe.tools"]
#   my_tool = "my_package.tools:MyTool"
#
# pip install 后自动发现，无需修改 BYOE 源码。

from byoe import Tool


class ExampleTool(Tool):
    name = "example"
    description = "示例工具"
    parameters = {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
        },
        "required": ["message"],
    }

    def execute(self, message: str) -> str:
        return f"收到: {message}"


# =============================================================================
# 6. LightMemory — 长期记忆
# =============================================================================
#
# 存储位置：~/.byoe/memory.db（SQLite）
# 获取单例：byoe.get_memory() -> LightMemory
# 构造新实例：LightMemory(db_path="custom/path.db")
#
# 方法：
#
#   write(path, content, layer="knowledge", tags=None, summary="",
#         source="agent") -> tuple[str, bool]
#     写入或更新记忆。返回 (mem_id, was_update)。
#     layer 可选值：knowledge / short_term / session / ephemeral
#
#   search(query, limit=5) -> list[dict]
#     FTS5 关键词搜索 + 可选语义融合（设置 BYOE_EMBEDDING_MODEL 时）。
#     每条结果包含：id, path, content, summary, tags, layer, score
#
#   search_semantic(query, limit=5) -> list[dict]
#     纯向量相似度搜索（需要 BYOE_EMBEDDING_MODEL）。
#
#   read(path) -> dict | None       按路径精确读取
#   forget(path) -> bool            按路径删除
#   gc(...) -> dict                 垃圾回收（自动定期触发）
#   reindex() -> int                为所有 embedding=NULL 的记忆生成向量
#
# 语义搜索配置（env）：
#   BYOE_EMBEDDING_MODEL    e.g. text-embedding-3-small  (必须设置才生效)
#   BYOE_EMBEDDING_API_KEY  嵌入专用 key（默认复用 BYOE_API_KEY）
#   BYOE_EMBEDDING_BASE_URL 嵌入专用端点（默认复用 OPENAI_BASE_URL）
#
# GC 配置（env）：
#   BYOE_MEMORY_MAX_ROWS             最大行数（默认 5000）
#   BYOE_MEMORY_SESSION_TTL_DAYS     session layer TTL（默认 30）
#   BYOE_MEMORY_SHORT_TTL_DAYS       short_term layer TTL（默认 14）
#   BYOE_MEMORY_GC_EVERY_WRITES      每 N 次写入触发一次 GC（默认 50）

from byoe import get_memory, LightMemory

mem: LightMemory = get_memory()
mem_id, created = mem.write("/demo/note", "这是一条示例记忆", layer="knowledge")


# =============================================================================
# 7. AgentScheduler — 任务调度
# =============================================================================
#
# AgentScheduler 提供基于时间或事件的自动执行能力（Loop Engineering）。
# 通常通过 `byoe loop` CLI 使用，也可直接导入进行编程控制。
#
# from byoe import AgentScheduler
# scheduler = AgentScheduler(agent, prompt="每日报告", every="1h")
# scheduler.start()   # 非阻塞
# scheduler.stop()

from byoe import AgentScheduler


# =============================================================================
# 8. 环境变量参考
# =============================================================================
#
# 模型与 API
#   BYOE_API_KEY              主 API 密钥（兼容 OPENAI_API_KEY）
#   BYOE_MODEL                主模型名（兼容 OPENAI_MODEL_NAME，默认 gpt-4o）
#   OPENAI_BASE_URL           API 端点（OpenAI 兼容协议）
#   BYOE_EMBEDDING_MODEL      嵌入模型（启用语义记忆，如 text-embedding-3-small）
#   BYOE_EMBEDDING_API_KEY    嵌入专用 key（可选）
#   BYOE_EMBEDDING_BASE_URL   嵌入专用端点（可选）
#
# Web 服务
#   BYOE_CHAT_RATE_LIMIT      每分钟最大请求数（默认 0 = 不限）
#   BYOE_AUTH_TOKEN           Web UI 访问令牌（空=不鉴权）
#
# 记忆
#   BYOE_MEMORY_MAX_ROWS          最大记忆行数（默认 5000）
#   BYOE_MEMORY_SESSION_TTL_DAYS  session TTL（默认 30）
#   BYOE_MEMORY_SHORT_TTL_DAYS    short_term TTL（默认 14）
#   BYOE_MEMORY_GC_EVERY_WRITES   GC 触发频率（默认 50）
#
# 用量跟踪
#   用量自动记录到 ~/.byoe/usage.jsonl（Web 服务运行时）
#   byoe metrics --days 7  查看最近 7 天用量
#
# 自定义价格表
#   ~/.byoe/pricing.json：{"model-name": [input_per_million, output_per_million]}


# =============================================================================
# 9. CLI 命令参考
# =============================================================================
#
# byoe version                              版本信息
# byoe doctor                               配置检查与 LLM 连通性测试
#
# byoe chat [-m MODEL] [-r SESSION_ID]      交互式 Agent（推荐日常使用）
# byoe web [--port PORT] [--host HOST]      启动 Web UI（浏览器自动打开）
# byoe loop -p "任务描述" --every 30m       定时自动执行
#
# byoe memory stats                         记忆统计
# byoe memory search <关键词>               搜索记忆
# byoe memory list [--layer knowledge]      列出记忆
# byoe memory show <path>                   查看记忆内容
# byoe memory forget <path>                 删除记忆
# byoe metrics [--days 30] [--model MODEL]  Token 用量统计
# byoe metrics --reindex-memory             为存量记忆生成嵌入向量
#
# byoe init                                 初始化 Crew 工作区
# byoe plan <name>                          创建变更计划
# byoe status                               查看活跃变更
# byoe release                              归档已完成变更
# byoe agents                               列出可用领域专家
# byoe sessions list / show / delete        管理对话会话
# byoe sober [path]                         代码质量体检

print("BYOE v0.8.0 API 参考 — 运行各 demo 文件查看具体示例")
print("  01_quickstart.py        快速入门")
print("  02_streaming.py         流式输出与异步")
print("  03_structured_output.py 结构化输出")
print("  04_fallback_chain.py    模型降级链")
print("  05_memory.py            长期记忆")
print("  06_swarm.py             多 Agent 编排")
print("  07_plugins.py           自定义工具插件")
print("  08_save_load.py         会话持久化")

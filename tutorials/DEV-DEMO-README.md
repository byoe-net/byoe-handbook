# dev-demo — 用 byoe Python 类库开发 AI 应用

> 面向开发者的 byoe 实战代码库，涵盖 Skills、自定义工具、完整应用模板。  
> 版本：byoe >= 1.0.0 · Python 3.10+

---

## 目录结构

```
dev-demo/
├── skills/                 # byoe Skills（可被 Agent 动态加载的功能模块）
│   ├── code_reviewer.py    # 代码审查：Bug/安全/性能/风格分析
│   ├── docgen.py           # 文档生成：Docstring + README 自动生成
│   ├── test_writer.py      # 测试生成：自动编写 pytest 测试用例
│   ├── dependency_audit.py # 依赖审计：漏洞扫描 + 过期依赖检测
│   └── api_spec_gen.py     # API 设计：生成 OpenAPI 规范 + Pydantic 模型
│
├── tools/                  # 自定义 Tool 子类（注入 byoe.create_agent）
│   ├── db_tool.py          # SQLite 工具：查询 + Schema 检查（只读安全模式）
│   └── utility_tools.py    # 三合一：TemplateTool + EnvValidatorTool + TimerTool
│
└── apps/                   # 完整应用模板（可直接运行）
    ├── 01_code_assistant.py    # 本地代码助手（流式 REPL + 会话持久化）
    ├── 02_doc_pipeline.py      # 文档生成流水线（异步并行 + Swarm 汇总）
    ├── 03_structured_extractor.py  # 结构化提取（发票/简历/会议纪要）
    ├── 04_review_swarm.py      # 多 Agent 代码评审（安全/性能/质量并行）
    ├── 05_chatbot_with_memory.py   # 持久化 Chatbot（短/中/长期三层记忆）
    └── 06_observability.py     # 可观测 Agent（Hooks + 审计日志 + Prometheus）
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install byoe                      # 基础安装
pip install 'byoe[structured]'        # 含结构化输出（Pydantic）
pip install jinja2                    # TemplateTool 需要
```

### 2. 配置 API Key

```bash
# .env 或环境变量（任选其一）
export OPENAI_API_KEY=sk-xxxxxxxx

# DeepSeek
export OPENAI_API_KEY=sk-xxxxxxxx
export OPENAI_BASE_URL=https://api.deepseek.com
export BYOE_MODEL=deepseek-chat

# 通义千问
export OPENAI_API_KEY=sk-xxxxxxxx
export OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
export BYOE_MODEL=qwen-max
```

### 3. 运行示例

```bash
# 代码助手（最常用）
python apps/01_code_assistant.py . my_session

# 文档生成（异步并行，传入项目目录）
python apps/02_doc_pipeline.py ../my_project --dry-run

# 发票信息提取
python apps/03_structured_extractor.py --schema invoice

# 多 Agent 代码评审
python apps/04_review_swarm.py path/to/your/code.py

# 持久化 Chatbot
python apps/05_chatbot_with_memory.py --persona "小明"

# 可观测 Agent（查看 Hooks 和审计日志）
python apps/06_observability.py
```

---

## Skills 使用说明

Skills 是可被 byoe Agent 在对话中**动态加载**的 Python 模块，  
每个 skill 文件只需提供一个 `run(**kwargs) -> str` 函数。

### 安装 Skills（注册到 Agent）

```bash
# 方式 A：复制到 ~/.byoe/skills/（推荐）
cp skills/*.py ~/.byoe/skills/

# 方式 B：在对话中让 Agent 自己安装
byoe chat
> 请将 skills/code_reviewer.py 的内容创建为名为 code_reviewer 的 skill
```

### 在 Agent 对话中使用

```
# byoe chat 中
> load_skill("code_reviewer")
> 用 code_reviewer 审查 src/api.py，重点关注安全问题

> load_skill("test_writer")
> 为 src/utils.py 的所有公开函数生成 pytest 测试，输出到文件

> load_skill("dependency_audit")
> 审计当前项目的依赖，找出有安全漏洞的包
```

### 在 Python 代码中直接调用

```python
from skills.code_reviewer import run as review
from skills.test_writer import run as write_tests

# 代码审查
report = review(file="src/api.py", focus="security,bugs")
print(report)

# 生成测试
tests = write_tests(file="src/utils.py", coverage="thorough", output="file")
print(tests)
```

---

## 自定义 Tool 使用说明

继承 `byoe.Tool` 创建自定义工具，注入 `create_agent()` 即可：

```python
import byoe
from tools.db_tool import SQLiteTool, SQLiteSchemaInspectorTool
from tools.utility_tools import TemplateTool, EnvValidatorTool, TimerTool

# 组合内置工具 + 自定义工具
agent = byoe.create_agent(
    tools=[
        # 自定义工具
        SQLiteTool(allow_writes=False),
        SQLiteSchemaInspectorTool(),
        TemplateTool(),
        EnvValidatorTool(),
        TimerTool(),
    ]
)

# 现在 agent 可以查询数据库、渲染模板、检查环境
reply = agent.chat("查询 users.db 中注册用户最多的城市")
```

---

## 应用模板说明

| 文件 | 适用场景 | 关键技术 |
|------|---------|---------|
| `01_code_assistant.py` | 本地开发、日常编码辅助 | stream + save/load + Hooks |
| `02_doc_pipeline.py` | 项目文档自动化 | asyncio.gather + 并行 Agent |
| `03_structured_extractor.py` | 文档/邮件/合同信息提取 | response_model + Pydantic |
| `04_review_swarm.py` | 代码评审自动化 | Swarm 并行 + 汇总 |
| `05_chatbot_with_memory.py` | 客服/助手产品 | LightMemory 三层记忆 |
| `06_observability.py` | 生产级 AI 应用 | Hooks + JSONL 日志 + Prometheus |

---

## 设计模式速查

### 模式一：最简 Agent

```python
import byoe

agent = byoe.create_agent()
print(agent.chat("Hello"))
```

### 模式二：流式输出

```python
agent = byoe.create_agent()
for token in agent.stream("写一段 Python 快速排序"):
    print(token, end="", flush=True)
```

### 模式三：结构化输出

```python
from pydantic import BaseModel
import byoe

class Result(BaseModel):
    name: str
    score: float
    tags: list[str]

agent = byoe.create_agent()
result: Result = agent.chat("分析这段文本...", response_model=Result)
print(result.score)
```

### 模式四：自定义工具

```python
from byoe import Tool
import byoe

class MyTool(Tool):
    name = "my_tool"
    description = "What this tool does"
    parameters = {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    }
    def execute(self, query: str) -> str:
        return f"Result for: {query}"

agent = byoe.create_agent(tools=[MyTool()])
```

### 模式五：并行异步

```python
import asyncio, byoe

async def parallel_tasks():
    agents = [byoe.create_agent() for _ in range(3)]
    tasks = [a.achat(f"任务 {i}") for i, a in enumerate(agents)]
    results = await asyncio.gather(*tasks)
    return results

results = asyncio.run(parallel_tasks())
```

### 模式六：Hooks 监控

```python
import byoe
from byoe import on

@on("llm.response")
def track(model, prompt_tokens, completion_tokens, cost_usd, **_):
    print(f"[{model}] {prompt_tokens}p/{completion_tokens}c  ${cost_usd:.5f}")

@on("tool.call")
def audit(tool_name, args, error, **_):
    status = "✗" if error else "✓"
    print(f"{status} {tool_name}({list(args or {}).keys()})")

agent = byoe.create_agent()
agent.chat("列出当前目录的 .py 文件")
```

### 模式七：MCP 服务器接入

```python
agent = byoe.create_agent(
    mcp_servers=[
        {"name": "fs", "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]},
        {"name": "remote", "url": "http://localhost:3000"},
    ]
)
# 远程工具自动注册为 mcp__fs__read_file 等
```

### 模式八：多模态图片

```python
agent = byoe.create_agent()  # 需要 gpt-4o / claude-3 等视觉模型

# 用户传图
reply = agent.chat("分析这个错误截图", images=["error.png"])

# 流式 + 图片
for token in agent.stream("描述这张架构图", images=["arch.png"]):
    print(token, end="")
```

---

## 完整 API 参考

- [API-REFERENCE-ZH.md](../byoe/docs/API-REFERENCE-ZH.md)
- [API-QUICKSTART-ZH.md](../byoe/docs/API-QUICKSTART-ZH.md)
- [VSCODE-MCP-GUIDE-ZH.md](../byoe/docs/VSCODE-MCP-GUIDE-ZH.md)
- [USER-MANUAL-ZH.md](../byoe/docs/USER-MANUAL-ZH.md)

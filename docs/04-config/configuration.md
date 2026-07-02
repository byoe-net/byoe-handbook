# 卜一智航 · BYOE 配置参考

> byoe.net · [byoe.net](https://byoe.net)

---

## 环境变量

### API Key（按优先级尝试）

| 变量 | 说明 |
|------|------|
| `BYOE_API_KEY` | BYOE 专属 key（最高优先级） |
| `OPENAI_API_KEY` | OpenAI 或兼容服务的 key |
| `DEEPSEEK_API_KEY` | DeepSeek 专属 key |
| `ANTHROPIC_API_KEY` | Anthropic key（通过兼容代理使用） |
| `CORECODER_API_KEY` | 遗留兼容，等同于 `OPENAI_API_KEY` |

### 模型与端点

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_MODEL` | `gpt-4o` | 模型名称 |
| `BYOE_BASE_URL` | `https://api.openai.com/v1` | API 基础 URL |
| `OPENAI_BASE_URL` | — | 兼容 fallback（`BYOE_BASE_URL` 未设时使用） |

### Agent 行为

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_TEMPERATURE` | `0` | LLM 温度（0=确定性最高） |
| `BYOE_MAX_TOKENS` | `16384` | 单次回复最大 token |
| `BYOE_MAX_CONTEXT` | `128000` | 上下文压缩触发阈值（token 数） |

### 特殊模式

| 变量 | 值 | 说明 |
|------|-----|------|
| `BYOE_WECHAT` | `1` | 激活 Wechatbot 接管模式 |

### 调试与可观测性

| 变量 | 值 | 说明 |
|------|-----|------|
| `BYOE_LOG` | `1` | 启用结构化 JSONL 日志，写入 `~/.byoe/logs/agent.jsonl` |
| `BYOE_LOG` | `debug` | 启用 debug 级别日志（含完整消息体，内容较多） |

日志文件超过 5 MB 时自动轮转。每条日志为一行 JSON，包含 `ts`（时间戳）、`event`（事件类型）等字段，可用 `jq` 解析：

```bash
# 查看最近 20 条工具调用记录
tail -n 100 ~/.byoe/logs/agent.jsonl | jq 'select(.event=="tool_call")'

# 统计每种工具的调用次数
cat ~/.byoe/logs/agent.jsonl | jq -r '.tool // empty' | sort | uniq -c | sort -rn
```

### 语义记忆（Embedding）

开启后 `search_memory` 自动融合 FTS5 关键词分数与向量余弦相似度，零额外依赖（复用已有 OpenAI SDK）。

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_EMBEDDING_MODEL` | 空（禁用） | 嵌入模型名，例如 `text-embedding-3-small`。设置后即启用语义搜索 |
| `BYOE_EMBEDDING_API_KEY` | 同 `BYOE_API_KEY` | 嵌入专用 key（可选，默认复用主 key） |
| `BYOE_EMBEDDING_BASE_URL` | 同 `OPENAI_BASE_URL` | 嵌入专用端点（可选，适合用不同 provider 做嵌入） |

```bash
# 启用语义记忆（最小配置）
export BYOE_EMBEDDING_MODEL=text-embedding-3-small
export BYOE_API_KEY=sk-...

# 首次启用时，为历史记忆补充向量
byoe metrics --reindex-memory
```

### 长期记忆 GC

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_MEMORY_MAX_ROWS` | `5000` | 记忆最大条数，超出时优先删除旧的 session/short_term 层 |
| `BYOE_MEMORY_SESSION_TTL_DAYS` | `30` | session 层记忆的过期天数 |
| `BYOE_MEMORY_SHORT_TTL_DAYS` | `14` | short_term 层记忆的过期天数 |
| `BYOE_MEMORY_GC_EVERY_WRITES` | `50` | 每写入 N 条触发一次 GC |

### Web 限速

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_CHAT_RATE_LIMIT` | `0`（禁用） | 每个 IP 每分钟最大请求数，`0` = 不限速 |

```bash
# 开放给多人使用时建议设置
export BYOE_CHAT_RATE_LIMIT=20
```

### Shell 执行

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BYOE_BASH_TIMEOUT` | `600` | Bash 工具单条命令最大执行秒数（默认 600 秒，最小 30 秒）|

对于耗时很长的构建任务（如 `npm run build`、`docker build`），可以适当调大：

```bash
export BYOE_BASH_TIMEOUT=1800  # 允许最长 30 分钟
```

### LLM 高可用（Fallback Chain）

当主 LLM 连续失败时，BYOE 可自动切换到备用提供商。在代码/API 层设置：

```python
from byoe.engine.llm import LLM

llm = LLM(
    model="gpt-4o",
    api_key="sk-primary...",
    fallback_providers=[
        {
            "model": "deepseek-chat",
            "api_key": "sk-deepseek...",
            "base_url": "https://api.deepseek.com",
        },
        {
            "model": "qwen3-max",
            "api_key": "sk-qwen...",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        },
    ]
)
```

主 LLM 在重试耗尽后，依次尝试 `fallback_providers` 列表，全部失败才抛出异常。

**快捷写法 `fallback_models`**：若备用模型与主模型使用同一 Provider，可以直接传模型名数组：

```python
from byoe import LLM

llm = LLM(
    model="gpt-4o",
    api_key="sk-...",
    fallback_models=["gpt-4o-mini", "gpt-3.5-turbo"],  # 同 Provider 简写
)
```



## 常用提供商配置

### OpenAI

```bash
export OPENAI_API_KEY=sk-...
export BYOE_MODEL=gpt-4o
```

### DeepSeek

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.deepseek.com
export BYOE_MODEL=deepseek-chat
```

深度思考模型：
```bash
export BYOE_MODEL=deepseek-reasoner
```

### Qwen（通义千问）

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
export BYOE_MODEL=qwen3-max
```

其他 Qwen 模型：`qwen3-plus`、`qwen3-235b-a22b`、`qwen2.5-coder-32b-instruct`

### Kimi（月之暗面）

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.moonshot.cn/v1
export BYOE_MODEL=moonshot-v1-128k
```

### Claude via OpenRouter

```bash
export OPENAI_API_KEY=sk-or-...
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export BYOE_MODEL=anthropic/claude-sonnet-4-5
```

### Ollama（本地）

```bash
export OPENAI_API_KEY=ollama
export OPENAI_BASE_URL=http://localhost:11434/v1
export BYOE_MODEL=qwen2.5-coder:32b
```

---

## Windows PowerShell

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:OPENAI_BASE_URL = "https://api.deepseek.com"
$env:BYOE_MODEL = "deepseek-chat"
```

或写入 `~/.byoe/.env`（自动加载）：

```dotenv
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com
BYOE_MODEL=deepseek-chat
```

> `.env` 文件路径为 `%USERPROFILE%\.byoe\.env`（Windows）或 `~/.byoe/.env`（Unix）。

---

## `crew.yaml` — 项目配置

由 `byoe init` 自动生成，可手动编辑后入库：

```yaml
project:
  name: my-project
  description: "项目简介（可选）"

workflow:
  default_mode: standard        # standard | express | prototype
  concurrent_changes: true      # 是否允许并发变更

verify:
  test_command: ""              # 空 = AI 审查；填写命令则执行并检查退出码
  # 例: test_command: "pytest tests/ -q"

git:
  ignore_crew: true             # 自动将 crew/ 加入 .gitignore

specialists:                    # 可选：激活领域专家
  - frontend-specialist
  - security-engineer
```

---

## `~/.byoe/pricing.json` — 自定义定价

覆盖内置定价或添加私有模型。格式：`"model-name": [input_per_M, output_per_M]`（美元/百万 token）

```json
{
  "my-fine-tuned-model": [1.5, 3.0],
  "gpt-4o": [2.5, 10.0],
  "deepseek-chat": [0.27, 1.10]
}
```

---

## CLI 参数覆盖

CLI 参数优先级高于环境变量：

```bash
byoe chat -m deepseek-chat        # 覆盖 BYOE_MODEL
byoe chat -r session_20260415_xxx # 恢复会话
byoe chat -p "生成单元测试"        # 非交互式单次执行
byoe web --port 8080 --host 0.0.0.0  # Web UI 绑定到所有接口
```

---

## 会话文件

存储于 `~/.byoe/sessions/`，JSON 格式：

```json
{
  "id": "session_20260415_143022",
  "model": "deepseek-chat",
  "saved_at": "2026-04-15T14:30:22",
  "preview": "帮我实现 JWT 登录...",
  "messages": [...],
  "changed_files": ["src/auth.py"]
}
```

管理命令：

```bash
byoe sessions               # 列出
byoe sessions show <id>     # 查看详情
byoe sessions delete <id>   # 删除
```

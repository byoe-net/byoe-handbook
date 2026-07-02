# VS Code × 卜一智航 MCP 集成指南

> 版本：v1.0 · byoe.net — 携智而来，决策随行  
> 适用：VS Code 1.99+（GitHub Copilot）、byoe >= 1.0.0

---

## 目录

1. [什么是 BYOE MCP Server](#1-什么是-byoe-mcp-server)
2. [前置条件](#2-前置条件)
3. [快速配置（5 分钟）](#3-快速配置5-分钟)
4. [详细配置说明](#4-详细配置说明)
5. [23 个可用工具详解](#5-23-个可用工具详解)
6. [在 Copilot Chat 中使用工具](#6-在-copilot-chat-中使用工具)
7. [工作目录与环境变量](#7-工作目录与环境变量)
8. [HTTP 模式（远程/Docker 部署）](#8-http-模式远程docker-部署)
9. [常见问题排查](#9-常见问题排查)
10. [与 Claude Desktop / Cursor 对比](#10-与-claude-desktop--cursor-对比)

---

## 1. 什么是 BYOE MCP Server

**Model Context Protocol（MCP）** 是 Anthropic 发布的 AI 工具互联标准，允许 VS Code Copilot、Claude Desktop、Cursor 等 AI 客户端调用外部工具。

**BYOE MCP Server** 将 byoe 的 **23 个内置工具**统一暴露为 MCP 协议端点：

```
VS Code Copilot
    │   ← JSON-RPC 2.0 (stdio)
    ▼
byoe mcp-server
    │   调用
    ▼
23 个内置工具（bash / read_file / edit_file / git / web_search / ...）
    │
    ▼
你的项目文件系统 & 网络
```

配置完成后，你在 Copilot Chat 中的提问会自动触发 BYOE 工具，无需手动切换终端或编辑器。

---

## 2. 前置条件

| 项目 | 要求 |
|------|------|
| Python | 3.10 或以上 |
| byoe | >= 1.0.0（`pip install byoe`） |
| VS Code | 1.99 或以上 |
| GitHub Copilot | 已订阅并登录（含 Agent 模式） |
| API Key | 任意 byoe 支持的模型 Key |

验证 byoe 安装：

```bash
byoe --version
# 卜一智航 1.0.0 · byoe.net
```

验证 MCP server 能启动：

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}' | python -m byoe mcp-server
# 应输出类似：{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05", ...}}
```

---

## 3. 快速配置（5 分钟）

### 步骤一：创建 `.vscode/mcp.json`

在你的**项目根目录**创建（或打开）`.vscode/mcp.json`：

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

> **提示**：VS Code 1.99+ 会自动检测 `.vscode/mcp.json`，无需手动启用扩展。

### 步骤二：配置 API Key

在项目目录创建 `.env`（byoe 会自动读取）：

```bash
# 选择任意一个支持的模型
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# 或 DeepSeek
OPENAI_API_KEY=sk-xxxxxxxx
OPENAI_BASE_URL=https://api.deepseek.com
BYOE_MODEL=deepseek-chat

# 或通义千问
OPENAI_API_KEY=sk-xxxxxxxx
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
BYOE_MODEL=qwen-max
```

### 步骤三：重新加载 VS Code

按 `Ctrl+Shift+P` → `Developer: Reload Window`，或直接关闭并重开窗口。

### 步骤四：验证工具已接入

打开 Copilot Chat（`Ctrl+Alt+I`），切换到 **Agent 模式**，输入：

```
@byoe 列出当前目录所有 Python 文件
```

如果看到 Copilot 调用了 `glob` 工具并返回文件列表，说明配置成功。

---

## 4. 详细配置说明

### 4.1 基础配置结构

`.vscode/mcp.json` 完整结构：

```json
{
  "servers": {
    "byoe": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "byoe", "mcp-server", "--cwd", "${workspaceFolder}"],
      "env": {
        "OPENAI_API_KEY": "${env:OPENAI_API_KEY}",
        "BYOE_MODEL": "gpt-4o",
        "BYOE_BASH_TIMEOUT": "120"
      }
    }
  }
}
```

| 字段 | 说明 |
|------|------|
| `type` | 固定为 `"stdio"`（进程间 JSON-RPC） |
| `command` | Python 可执行文件路径，建议使用虚拟环境的全路径 |
| `args` | `["-m", "byoe", "mcp-server"]` + 可选 `--cwd <dir>` |
| `env` | 注入到子进程的环境变量，支持 `${env:VAR}` 语法 |

### 4.2 指定虚拟环境

如果 byoe 安装在特定虚拟环境中：

```json
{
  "servers": {
    "byoe": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/Scripts/python",
      "args": ["-m", "byoe", "mcp-server", "--cwd", "${workspaceFolder}"]
    }
  }
}
```

Windows 用 `Scripts/python.exe`，macOS/Linux 用 `bin/python`。

### 4.3 指定工作目录（--cwd）

`--cwd` 参数控制 bash、read_file、edit_file 等工具的根目录。  
不指定时默认为 byoe 进程的启动目录。

```json
"args": ["-m", "byoe", "mcp-server", "--cwd", "/my/project"]
```

### 4.4 多项目配置（workspace 级别）

如果你管理多个项目，可以在 workspace 文件中分别配置：

```json
{
  "servers": {
    "byoe-frontend": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "byoe", "mcp-server", "--cwd", "${workspaceFolder}/frontend"]
    },
    "byoe-backend": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "byoe", "mcp-server", "--cwd", "${workspaceFolder}/backend"]
    }
  }
}
```

---

## 5. 23 个可用工具详解

配置成功后，以下工具均可在 Copilot Chat 中使用：

### 📁 文件系统操作

| 工具名 | 功能 |
|--------|------|
| `read_file` | 按行读取文件内容，支持 session 级缓存（相同文件重复读取不重复 I/O） |
| `write_file` | 创建新文件或完整覆盖已有文件 |
| `edit_file` | 精确字符串替换（必须唯一匹配），适合小范围修改 |
| `glob` | 用 glob 模式查找文件（支持 `**` 递归匹配） |
| `grep` | 正则搜索文件内容，返回匹配行与文件路径 |
| `list_dir` | 以树形列出目录内容，显示文件大小 |
| `diff_file` | 显示文件的 unified diff（单路径时显示 git diff） |

### 🖥️ 代码执行

| 工具名 | 功能 |
|--------|------|
| `bash` | 执行 Shell 命令，返回 stdout / stderr / 退出码 |
| `python_repl` | 执行 Python 代码，返回 stdout + stderr（适合数据处理与调试） |
| `run_tests` | 运行项目测试套件，返回结构化通过/失败摘要 |

### 🌐 网络与搜索

| 工具名 | 功能 |
|--------|------|
| `fetch_url` | 获取 URL 内容（默认 GET），适合读取文档或 API |
| `web_search` | 用 DuckDuckGo 搜索，返回标题 + 摘要 + URL |

### 🗂️ Git 版本控制

| 工具名 | 功能 |
|--------|------|
| `git` | 在当前目录运行 git 命令；危险操作（push/reset --hard）会请求确认 |

### 🧠 记忆与知识

| 工具名 | 功能 |
|--------|------|
| `record_memory` | 将重要信息（经验、Bug、技巧）写入长期记忆数据库 |
| `search_memory` | 全文/语义搜索长期记忆，找出历史经验与解决方案 |
| `get_repo_map` | 生成仓库结构地图（类、函数、导入），帮助理解大型代码库 |

### 🤖 Agent 能力

| 工具名 | 功能 |
|--------|------|
| `agent` | 启动子 Agent 处理复杂子任务，独立工具调用循环 |
| `swarm_collaboration` | 发起多 Agent 协作流水线（顺序接力或并行独立）|
| `todo` | 管理私有 TODO 列表，追踪执行进度 |

### 🛠️ 代码质量

| 工具名 | 功能 |
|--------|------|
| `sober_scan` | 扫描代码库中的 AI 编码技术债与代码异味 |

### 🧩 技能系统

| 工具名 | 功能 |
|--------|------|
| `create_skill` | 创建可复用的 Python 技能文件并保存，供未来调用 |
| `load_skill` | 加载已保存的技能作为运行时工具 |

### 🖼️ 多模态

| 工具名 | 功能 |
|--------|------|
| `read_image` | 读取图片（JPEG/PNG/GIF/WebP，≤20 MB），返回 base64 data URL 供视觉模型分析 |

---

## 6. 在 Copilot Chat 中使用工具

### 6.1 触发方式

在 Copilot Chat 中切换到 **Agent 模式**（图标为 `⚡`），BYOE 工具会自动出现在可用工具列表中。你可以直接描述任务，Copilot 会自动选择并调用合适的工具。

### 6.2 典型使用示例

**读取与分析代码**

```
帮我分析 src/api.py 的性能瓶颈，重点关注数据库查询部分
```
→ Copilot 自动调用 `read_file("src/api.py")` + `get_repo_map()` 分析

---

**搜索并修改代码**

```
把项目里所有使用 requests.get 的地方改为带超时参数 timeout=30
```
→ 自动调用 `grep("requests\.get", "**/*.py")` → 对每个匹配文件调用 `edit_file()`

---

**运行测试并修复**

```
运行测试，如果有失败的用例，分析原因并修复
```
→ `run_tests()` → 读取失败信息 → `read_file()` + `edit_file()` 修复 → 再次 `run_tests()`

---

**Git 操作**

```
查看最近 5 次提交，然后把当前改动提交，message 用中文描述
```
→ `git("log --oneline -5")` → `git("add -A")` → `git("commit -m '...'")` （会弹出确认）

---

**网络搜索 + 编码**

```
搜索 FastAPI 最新的 WebSocket 用法，然后在 main.py 里添加一个 /ws 端点
```
→ `web_search("FastAPI WebSocket 2025")` → `fetch_url(文档链接)` → `edit_file("main.py", ...)`

---

**多模态图片分析**

```
读取 screenshots/error.png，告诉我这个错误是什么，怎么修复
```
→ `read_image("screenshots/error.png")` → 图片注入视觉上下文 → 给出分析

---

**代码质量扫描**

```
对整个 src/ 目录做一次代码体检，列出主要问题
```
→ `sober_scan("src/")` → 返回分类问题报告

---

### 6.3 手动指定工具（高级）

在提问中可以明确要求使用特定工具：

```
用 python_repl 执行以下代码，查看输出：
import pandas as pd
df = pd.read_csv("data.csv")
print(df.describe())
```

```
用 bash 运行 docker ps，看看有哪些容器在跑
```

### 6.4 工具权限确认

涉及以下操作时，Copilot 会暂停并请求你确认：

| 操作级别 | 示例命令 | 默认行为 |
|----------|---------|----------|
| 普通读取 | `read_file`、`glob`、`git log` | 自动执行 |
| 文件写入 | `write_file`、`edit_file` | 自动执行（建议开启 git 追踪） |
| risky git | `git add`、`git commit`、`git checkout` | ⚠ 显示确认提示 |
| dangerous git | `git push`、`git reset --hard` | 🚫 默认拒绝，须明确允许 |
| bash 命令 | `rm -rf`、`dd` 等危险命令 | 取决于 `BYOE_BASH_TIMEOUT` 沙箱 |

---

## 7. 工作目录与环境变量

### 7.1 工作目录优先级

byoe mcp-server 的文件操作根目录按以下顺序确定：

1. `--cwd` 命令行参数（最高优先级）
2. `.vscode/mcp.json` 中的 `cwd` 字段（VS Code 扩展支持）
3. VS Code 打开的 workspace 根目录
4. byoe 进程的启动目录（fallback）

推荐显式指定 `--cwd ${workspaceFolder}` 避免路径混乱。

### 7.2 环境变量参考

在 `.vscode/mcp.json` 的 `env` 字段中设置，或在系统环境中预设：

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENAI_API_KEY` | 模型 API Key（必填） | `sk-xxx` |
| `BYOE_MODEL` | 默认模型 | `gpt-4o`、`deepseek-chat`、`qwen-max` |
| `OPENAI_BASE_URL` | 自定义 API 端点 | `https://api.deepseek.com` |
| `BYOE_BASH_TIMEOUT` | bash 超时秒数（默认 600） | `120` |
| `BYOE_MAX_CONTEXT_TOKENS` | 上下文窗口（默认 128000） | `32000` |
| `BYOE_LOG` | 启用结构化日志 | `1` |
| `BYOE_MCP_SERVERS` | 级联接入其他 MCP 服务器 | JSON 数组 |

完整示例 `.vscode/mcp.json`（生产推荐）：

```json
{
  "servers": {
    "byoe": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m", "byoe", "mcp-server",
        "--cwd", "${workspaceFolder}"
      ],
      "env": {
        "OPENAI_API_KEY": "${env:OPENAI_API_KEY}",
        "BYOE_MODEL": "gpt-4o",
        "BYOE_BASH_TIMEOUT": "120",
        "BYOE_LOG": "0"
      }
    }
  }
}
```

> **安全提示**：不要将 `OPENAI_API_KEY` 的值硬编码在 `.vscode/mcp.json` 中，应使用 `${env:OPENAI_API_KEY}` 从系统环境变量读取，并将 `.vscode/mcp.json` 加入 `.gitignore`（或只提交不含 Key 的模板版本）。

---

## 8. HTTP 模式（远程/Docker 部署）

除 stdio 外，byoe mcp-server 还支持 **HTTP 模式**，适合 Docker 容器化或远程服务器部署。

### 8.1 启动 HTTP 服务

```bash
byoe mcp-server --http --host 0.0.0.0 --port 3000
```

可用端点：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查，返回 `{"status":"ok","tools":23}` |
| `/tools` | GET | 列出所有工具（MCP 格式） |
| `/messages` | POST | 接受 JSON-RPC 2.0 消息 |

### 8.2 Docker Compose 示例

```yaml
# docker-compose.yml
services:
  byoe-mcp:
    image: python:3.12-slim
    command: >
      bash -c "pip install byoe && byoe mcp-server --http --host 0.0.0.0 --port 3000 --cwd /workspace"
    ports:
      - "3000:3000"
    volumes:
      - .:/workspace
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - BYOE_MODEL=${BYOE_MODEL:-gpt-4o}
    restart: unless-stopped
```

### 8.3 VS Code 连接 HTTP 模式

VS Code 目前原生 MCP 只支持 stdio，HTTP 模式需通过 stdio-to-http 代理：

```json
{
  "servers": {
    "byoe-remote": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://your-server:3000"]
    }
  }
}
```

---

## 9. 常见问题排查

### Q1：VS Code 提示"MCP server failed to start"

**原因 A：** `python` 命令不在 PATH 或版本过低  
```bash
# 检查
python --version   # 应 >= 3.10
which python       # 或 where python (Windows)
```
**解决：** 在 `command` 中使用 Python 全路径，例如 `"C:/Python312/python.exe"`

---

**原因 B：** byoe 未安装或版本过低  
```bash
pip show byoe   # 检查版本
pip install -U byoe
```

---

**原因 C：** `.vscode/mcp.json` 语法错误  
```bash
python -c "import json; json.load(open('.vscode/mcp.json'))"
```
确认输出无报错。

---

### Q2：工具能列出，但 bash/read_file 报路径错误

**原因：** 工作目录不是预期的项目根目录  
**解决：** 在 args 中显式指定 `"--cwd"`, `"${workspaceFolder}"`

---

### Q3：`git push` 被拒绝

这是预期行为 — BYOE 将 `git push`、`git reset --hard` 等视为 **dangerous** 操作，默认拒绝。  
如需允许，可在 chat 中明确说：`"执行 git push，我确认允许"` 或在提问时加上 `(已确认)`。

---

### Q4：API Key 未生效 / 返回 401

检查 `.vscode/mcp.json` 的 `env` 字段是否正确，或直接在系统环境变量中设置：

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-xxx"
```

```bash
# macOS/Linux
export OPENAI_API_KEY=sk-xxx
```

重新加载 VS Code 窗口后生效。

---

### Q5：调试 MCP server 的原始 JSON-RPC 消息

```bash
# 手动发送消息，查看服务器响应
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python -m byoe mcp-server
```

或启用日志：

```json
"env": { "BYOE_LOG": "1", "BYOE_LOG_LEVEL": "debug" }
```

日志写入 `~/.byoe/logs/`（stderr，不污染 JSON-RPC stdout 流）。

---

### Q6：工具调用超时

默认 bash 超时为 600 秒。对于长时间运行的命令（如 `npm install`），可调整：

```json
"env": { "BYOE_BASH_TIMEOUT": "300" }
```

---

## 10. 与 Claude Desktop / Cursor 对比

| 特性 | VS Code Copilot | Claude Desktop | Cursor |
|------|-----------------|----------------|--------|
| 配置文件 | `.vscode/mcp.json` | `~/.claude/claude_desktop_config.json` | `mcp_config.json` |
| 传输方式 | stdio ✅ | stdio ✅ | stdio ✅ |
| 工具数量 | 23 个 ✅ | 23 个 ✅ | 23 个 ✅ |
| 工具确认 UI | Copilot 内嵌弹窗 | Claude 内嵌弹窗 | Cursor 内嵌弹窗 |
| 多模态图片 | 需模型支持 | 原生支持 | 需模型支持 |
| 工作目录控制 | `--cwd` 参数 | `--cwd` 参数 | `--cwd` 参数 |

**Claude Desktop 配置（参考）**

```json
// ~/.claude/claude_desktop_config.json
{
  "mcpServers": {
    "byoe": {
      "command": "python",
      "args": ["-m", "byoe", "mcp-server", "--cwd", "/your/project"],
      "env": {
        "OPENAI_API_KEY": "sk-xxx",
        "BYOE_MODEL": "claude-3-7-sonnet-20250219"
      }
    }
  }
}
```

---

## 附录 A：完整 `.vscode/mcp.json` 模板

```json
{
  "$schema": "https://schemas.vscode.dev/mcp/1.0",
  "servers": {
    "byoe": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "byoe",
        "mcp-server",
        "--cwd",
        "${workspaceFolder}"
      ],
      "env": {
        "OPENAI_API_KEY": "${env:OPENAI_API_KEY}",
        "BYOE_MODEL": "gpt-4o",
        "OPENAI_BASE_URL": "",
        "BYOE_BASH_TIMEOUT": "120",
        "BYOE_MAX_CONTEXT_TOKENS": "128000",
        "BYOE_LOG": "0"
      }
    }
  }
}
```

将此文件提交到 `.vscode/mcp.json`，团队成员 clone 后只需设置各自的 `OPENAI_API_KEY` 环境变量即可立即使用。

---

## 附录 B：工具完整参数速查

| 工具 | 关键参数 | 说明 |
|------|---------|------|
| `bash` | `command: str`, `timeout: int?` | 执行 shell 命令 |
| `read_file` | `file_path: str`, `start_line: int?`, `end_line: int?` | 按行读取 |
| `write_file` | `file_path: str`, `content: str` | 写入完整内容 |
| `edit_file` | `file_path: str`, `old_string: str`, `new_string: str` | 精确替换 |
| `glob` | `pattern: str`, `path: str?` | 文件匹配 |
| `grep` | `pattern: str`, `path: str?`, `include: str?` | 正则搜索 |
| `list_dir` | `path: str` | 目录树 |
| `diff_file` | `path: str`, `other: str?` | 显示 diff |
| `python_repl` | `code: str` | 执行 Python |
| `run_tests` | `path: str?`, `extra_args: str?` | 运行测试 |
| `fetch_url` | `url: str`, `method: str?`, `body: str?` | HTTP 请求 |
| `web_search` | `query: str`, `max_results: int?` | 网络搜索 |
| `git` | `args: str` | git 命令字符串 |
| `record_memory` | `content: str`, `layer: str?`, `tags: list?` | 记忆写入 |
| `search_memory` | `query: str`, `layer: str?`, `limit: int?` | 记忆搜索 |
| `get_repo_map` | `path: str?`, `depth: int?` | 仓库地图 |
| `agent` | `task: str`, `tools: list?` | 启动子 Agent |
| `swarm_collaboration` | `task: str`, `mode: str?` | 多 Agent 协作 |
| `todo` | `action: str`, `content: str?` | TODO 管理 |
| `sober_scan` | `path: str`, `rules: list?` | 代码扫描 |
| `create_skill` | `name: str`, `code: str`, `description: str` | 创建技能 |
| `load_skill` | `name: str` | 加载技能 |
| `read_image` | `file_path: str` | 读取图片 |

---

> **相关文档**
> - [API-REFERENCE-ZH.md](./API-REFERENCE-ZH.md) — Python 库 API 完整参考
> - [USER-MANUAL-ZH.md](./USER-MANUAL-ZH.md) — 产品用户手册（§18 MCP 生态集成）
> - [API-QUICKSTART-ZH.md](./API-QUICKSTART-ZH.md) — Step 10 MCP 集成快速教程
> - [`../api-demo/10_mcp.py`](../api-demo/10_mcp.py) — 可运行的 MCP 演示代码

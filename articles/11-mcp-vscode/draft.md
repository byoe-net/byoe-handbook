# MCP + VS Code：在编辑器里召唤 AI

> 一句话摘要：MCP 是 AI 世界的 USB-C —— 统一接口，连接一切。BYOE 既是 MCP 客户端也是 MCP 服务端。

---

## 1. 场景引入

你已经在用 VS Code 写代码，不想切到终端或浏览器用 BYOE。

或者你的团队有自己的一套内部工具（发布系统、监控平台、数据库管理面板），希望 AI 也能调用它们。

MCP（Model Context Protocol）就是来解决这两个问题的。

---

## 2. MCP 是什么

MCP 是 Anthropic 提出的开放协议，类比：

```
USB-C：统一硬件外设接口
MCP ：统一 AI 工具接口
```

**BYOE 在 MCP 生态中的位置：**

```
     VS Code Copilot  ──┐
     Claude Desktop  ───┤──→  MCP Client ──→  BYOE MCP Server
     Cursor ────────────┘                           │
                                              ┌─────┴─────┐
                                              │  23 个工具  │
                                              │  Skills    │
                                              └───────────┘
```

BYOE 是**双向**的：
- **MCP Server 模式**：把 BYOE 的 23 个工具暴露给 VS Code / Claude Desktop 等 MCP 客户端
- **MCP Client 模式**：让 BYOE 的 Agent 调用外部 MCP 服务器的工具

---

## 3. MCP Server：BYOE 工具 → VS Code

### 配置方式

```bash
# 启动 BYOE MCP Server（默认 stdio 模式）
byoe mcp-server
```

在 VS Code 的 `settings.json` 中添加：

```json
{
  "mcp": {
    "servers": {
      "byoe": {
        "command": "byoe",
        "args": ["mcp-server"],
        "env": {
          "OPENAI_API_KEY": "sk-xxx",
          "OPENAI_BASE_URL": "https://api.deepseek.com",
          "BYOE_MODEL": "deepseek-chat"
        }
      }
    }
  }
}
```

重启 VS Code 后，Copilot Chat 中就多了一组 BYOE 工具：

> 插入 VS Code MCP 工具列表截图

```
byoe_read_file     — 读取文件
byoe_write_file    — 写入文件
byoe_edit_file     — 编辑文件
byoe_bash          — 执行命令
byoe_grep          — 搜索文本
byoe_web_search    — 联网搜索
...
```

在 VS Code 里直接让 AI 操作文件系统：

> 插入 VS Code 中使用 BYOE MCP 的截图

---

## 4. MCP Client：外部工具 → BYOE Agent

BYOE 也可以作为 MCP Client，连接外部的 MCP Server 来扩展自身能力。

```python
import byoe

agent = byoe.create_agent(
    mcp_servers=[
        {
            "url": "http://localhost:8000/mcp",  # HTTP 传输
            "name": "my-tools",
        },
        {
            "command": "node",                   # Stdio 传输
            "args": ["dist/server.js"],
            "name": "custom-server",
        },
    ]
)

# Agent 现在可以使用两个 MCP 服务器的所有工具
agent.chat("查询生产环境的服务器状态")
```

MCP Server 只需要实现标准的工具列表 + 工具调用接口。任何语言都可以写（Python、Node.js、Go、Rust）。

---

## 5. 使用场景

| 场景 | 方案 | 效果 |
|------|------|------|
| VS Code 中读写文件 | BYOE MCP Server | Copilot 获得完整文件操作能力 |
| 查询内部数据库 | 自建 MCP Server + BYOE Client | AI 可以直接查数据库 |
| 调用部署系统 | 自建 MCP Server | AI 可以一键部署 |
| 连接社区工具 | 安装社区 MCP Server | AI 可以发邮件、操作 Jira、查监控 |
| Claude Desktop 用户 | BYOE MCP Server | Claude 获得代码执行能力 |

### 示例：自建一个 MCP Server

```python
# server.py — 一个简单的 MCP Server
from byoe.engine.mcp_server import MCPServer, Tool

class WeatherTool(Tool):
    name = "get_weather"
    description = "查询天气"
    def execute(self, city: str):
        return f"{city} 今日 25°C，晴"

server = MCPServer(tools=[WeatherTool()])
server.run()
```

```bash
python server.py
```
```python
# BYOE 连接这个 MCP Server
agent = create_agent(mcp_servers=[{"command": "python", "args": ["server.py"]}])
agent.chat("北京今天天气怎么样？")
```

---

## 6. MCP 生态中的位置

```
                    ┌──────────────────┐
                    │   MCP 生态        │
                    │                   │
  ┌─────────────────┼─────────────────┐│
  │  MCP Client     │  MCP Server     ││
  │  (消费工具)      │  (提供工具)      ││
  ├─────────────────┼─────────────────┤│
  │ VS Code Copilot │ BYOE MCP Server ││
  │ Claude Desktop  │ 自定义 MCP Server │
  │ Cursor          │ 社区 MCP Server  ││
  │ BYOE Agent      │                 ││
  └─────────────────┴─────────────────┘│
                    └──────────────────┘
```

BYOE 是少数**同时支持 Client 和 Server** 的工具，这意味着它既可以消费生态，也可以贡献生态。

---

## 7. 要点总结

- MCP = AI 工具的 USB-C 接口，统一协议标准
- BYOE MCP Server：把 23 个工具暴露给 VS Code / Claude Desktop / Cursor
- BYOE MCP Client：让 Agent 调用外部 MCP Server 的工具
- 双向角色：既是消费者也是提供者
- 适用场景：VS Code 集成、内部系统对接、社区工具生态

## 下期预告

下一篇我们进入自动化运维：**循环工程** —— 让 AI 7×24 小时无人值守处理任务。

---

📎 完整文档：[VS Code MCP 集成指南](../../docs/03-developer-guide/VSCODE-MCP-GUIDE-ZH.md)
📎 示例代码：[10_mcp.py](../../demos/01-api/10_mcp.py)

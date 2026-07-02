"""api-demo/10_mcp.py — MCP 集成完整示例（v0.8.1）

演示内容：
  A. MCP 客户端 — 连接外部 MCP 服务器，将远程工具注入 Agent
  B. MCP 服务端 — 以编程方式启动 BYOE MCP 服务器供其他工具接入
  C. 端到端验证 — BYOE MCP server 自己充当 MCP server，另一个 Agent 作为 MCP client

注意：A 部分需要 Node.js（npx）才能运行真实 MCP 服务器。
      B/C 部分纯 Python，无额外依赖。

运行:
    python api-demo/10_mcp.py
"""

import json
import subprocess
import sys
import tempfile
import threading
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import byoe
from byoe.engine.mcp import MCPSession, MCPError, connect_servers
from byoe.engine.mcp_server import MCPServer, run_stdio


# ══════════════════════════════════════════════════════════════════════════════
# A. MCP 客户端 — 使用 Mock Transport 演示（无需 Node.js）
# ══════════════════════════════════════════════════════════════════════════════

print("=" * 60)
print("A. MCP 客户端演示（Mock Transport）")
print("=" * 60)

# 创建一个模拟 MCP 服务器 transport，返回两个工具
mock_transport = MagicMock()
mock_transport.request.side_effect = lambda method, params=None: {
    "initialize": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "serverInfo": {"name": "mock-server", "version": "1.0"},
    },
    "tools/list": {
        "tools": [
            {
                "name": "query_db",
                "description": "查询数据库",
                "inputSchema": {
                    "type": "object",
                    "properties": {"sql": {"type": "string", "description": "SQL 语句"}},
                    "required": ["sql"],
                },
            },
            {
                "name": "send_email",
                "description": "发送邮件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["to", "subject", "body"],
                },
            },
        ]
    },
    "tools/call": {
        "content": [{"type": "text", "text": "Mock result: OK"}]
    },
}[method]

session = MCPSession(mock_transport, name="mockdb")
tools = session.get_tools()

print(f"\n已发现 {len(tools)} 个远程工具：")
for t in tools:
    print(f"  • {t.name}: {t.description}")

# 将远程工具注入 Agent
# （此处不真正调用 LLM，展示 add_runtime_tool 用法）
# agent = byoe.create_agent()
# for t in tools:
#     agent.add_runtime_tool(t)
# print("\n所有 MCP 工具已注入 Agent，LLM 现在可以调用 mcp__mockdb__query_db 等工具")

# 直接调用远程工具
result = tools[0].execute(sql="SELECT * FROM users LIMIT 10")
print(f"\n直接调用 {tools[0].name}:")
print(f"  结果: {result}")


# ══════════════════════════════════════════════════════════════════════════════
# B. MCP 服务端 — 验证协议响应
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("B. MCP 服务端协议验证")
print("=" * 60)

server = MCPServer()

# initialize
resp = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
print(f"\ninitialize → protocolVersion: {resp['result']['protocolVersion']}")
print(f"  serverInfo: {resp['result']['serverInfo']}")

# notifications/initialized（无响应）
resp = server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
assert resp is None
print("notifications/initialized → (无响应，符合协议)")

# tools/list
resp = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
tools_list = resp["result"]["tools"]
print(f"\ntools/list → {len(tools_list)} 个工具")
print("  前 5 个工具：")
for t in tools_list[:5]:
    print(f"    {t['name']}: {t['description'][:50]}...")

# tools/call
resp = server.handle({
    "jsonrpc": "2.0", "id": 3, "method": "tools/call",
    "params": {"name": "bash", "arguments": {"command": "echo hello-from-mcp-server"}},
})
text = resp["result"]["content"][0]["text"]
print(f"\ntools/call bash → {text.strip()}")

# 未知工具
resp = server.handle({
    "jsonrpc": "2.0", "id": 4, "method": "tools/call",
    "params": {"name": "nonexistent_tool", "arguments": {}},
})
print(f"\n未知工具 → error code: {resp['error']['code']}")

# 未知方法
resp = server.handle({"jsonrpc": "2.0", "id": 5, "method": "not/a/method"})
print(f"未知方法 → error code: {resp['error']['code']}")


# ══════════════════════════════════════════════════════════════════════════════
# C. 端到端：run_stdio 管道模拟
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("C. run_stdio 完整管道测试")
print("=" * 60)

messages = [
    json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
    json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
    json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
    json.dumps({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "bash", "arguments": {"command": "echo pipeline-ok"}},
    }),
]

fake_stdin = StringIO("\n".join(messages) + "\n")
fake_stdout = StringIO()

with patch("sys.stdin", fake_stdin), patch("sys.stdout", fake_stdout):
    with patch("sys.stderr", StringIO()):
        run_stdio()

output_lines = [l for l in fake_stdout.getvalue().splitlines() if l.strip()]
print(f"\n收到 {len(output_lines)} 条响应：")
for line in output_lines:
    resp = json.loads(line)
    result = resp.get("result", resp.get("error"))
    print(f"  id={resp.get('id')} → {str(result)[:80]}...")


# ══════════════════════════════════════════════════════════════════════════════
# D. create_agent() 接入真实 MCP Server（需要 Node.js）
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("D. create_agent(mcp_servers=[...]) 用法参考")
print("=" * 60)

print("""
# 接入本地文件系统 MCP 服务器（需要 Node.js + npx）：
agent = byoe.create_agent(
    mcp_servers=[
        {
            "name": "fs",
            "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."],
        }
    ]
)
# Agent 现在拥有 mcp__fs__read_file, mcp__fs__write_file 等工具

# 接入 HTTP MCP 服务器：
agent = byoe.create_agent(
    mcp_servers=[{"name": "myapi", "url": "http://localhost:3000"}]
)

# 通过环境变量配置（JSON 数组）：
# export BYOE_MCP_SERVERS='[{"name":"fs","command":["npx","-y","@modelcontextprotocol/server-filesystem","."]}]'
agent = byoe.create_agent()   # 自动读取 BYOE_MCP_SERVERS
""")


# ══════════════════════════════════════════════════════════════════════════════
# E. VS Code / Claude Desktop 配置参考
# ══════════════════════════════════════════════════════════════════════════════

print("=" * 60)
print("E. IDE 接入配置参考")
print("=" * 60)

vscode_config = {
    "servers": {
        "byoe": {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "byoe", "mcp-server"],
        }
    }
}

claude_config = {
    "mcpServers": {
        "byoe": {
            "command": "python",
            "args": ["-m", "byoe", "mcp-server"],
        }
    }
}

print("\nVS Code (.vscode/mcp.json):")
print(json.dumps(vscode_config, indent=2, ensure_ascii=False))

print("\nClaude Desktop (~/.claude/claude_desktop_config.json):")
print(json.dumps(claude_config, indent=2, ensure_ascii=False))

print("\nHTTP 模式（Docker / 远程访问）：")
print("  byoe mcp-server --http --port 3000")
print("  # GET  http://localhost:3000/health  →  就绪探针")
print("  # GET  http://localhost:3000/tools   →  查看所有工具（调试用）")
print("  # POST http://localhost:3000/messages →  JSON-RPC 2.0")

print("\n✅ api-demo/10_mcp.py 完成")

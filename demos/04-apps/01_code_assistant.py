"""AI 应用模板 01：本地代码助手
========================================
使用 byoe Python API 构建一个有记忆、有工具的本地代码助手。
特点：
  - 自动读取项目目录树（get_repo_map）建立上下文
  - 内置全部文件操作工具（read/write/edit/bash/grep）
  - session 持久化：会话保存/恢复，跨次运行记住上下文
  - 流式输出，实时看到 Agent 思考过程
  - Ctrl+C 优雅退出并保存会话

运行：
    set BYOE_API_KEY=sk-...
    python apps/01_code_assistant.py [project_dir] [session_id]

示例：
    python apps/01_code_assistant.py . my_session
"""

from __future__ import annotations

import os
import signal
import sys
from pathlib import Path

import byoe
from byoe.engine.hooks import on


# ─── 配置 ────────────────────────────────────────────────────────────────────

PROJECT_DIR = sys.argv[1] if len(sys.argv) > 1 else "."
SESSION_ID  = sys.argv[2] if len(sys.argv) > 2 else None
SESSIONS_DIR = Path.home() / ".byoe" / "conversations"

SYSTEM_PROMPT = """你是一位资深全栈工程师，运行在本地开发环境中。
你的项目目录是 {cwd}。

工作原则：
1. 修改代码前先读取文件，理解现有实现
2. 使用 get_repo_map 建立全局代码视野，不盲目读取海量文件
3. edit_file 用于精确修改，write_file 用于创建新文件
4. 运行测试前确认测试框架（pytest / unittest / jest）
5. git 操作前确认分支状态
6. 遇到不确定的事先问用户，不要擅自做重大变更
"""


# ─── 成本监控 hook ──────────────────────────────────────────────────────────

_total_tokens = 0

@on("llm.response")
def _track_tokens(prompt_tokens, completion_tokens, **_):
    global _total_tokens
    _total_tokens += (prompt_tokens or 0) + (completion_tokens or 0)


# ─── main ────────────────────────────────────────────────────────────────────

def main():
    cwd = str(Path(PROJECT_DIR).expanduser().resolve())
    system = SYSTEM_PROMPT.format(cwd=cwd)

    # Create agent with all built-in tools
    agent = byoe.create_agent(system=system, cwd=cwd)
    print(f"卜一智航 代码助手 · 项目目录: {cwd}")
    print(f"模型: {agent.llm.model}  工具: {len(agent.tools)} 个")

    # Try to restore previous session
    session_file = None
    if SESSION_ID:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        session_file = SESSIONS_DIR / f"{SESSION_ID}.json"
        if session_file.exists():
            try:
                agent.load(str(session_file))
                msgs = len(agent.messages)
                print(f"✓ 已恢复会话 '{SESSION_ID}'（{msgs} 条历史消息）")
            except Exception as e:
                print(f"⚠ 无法恢复会话: {e}")
        else:
            print(f"新建会话: {SESSION_ID}")

    print("输入 'exit' 或按 Ctrl+C 退出\n" + "─" * 50)

    # Graceful Ctrl+C handler
    def _save_and_exit(sig=None, frame=None):
        if session_file and agent.messages:
            try:
                agent.save(str(session_file))
                print(f"\n✓ 会话已保存: {session_file}")
            except Exception as e:
                print(f"\n⚠ 保存失败: {e}")
        print(f"本次消耗约 {_total_tokens:,} tokens")
        sys.exit(0)

    signal.signal(signal.SIGINT, _save_and_exit)

    # ── REPL ────────────────────────────────────────────────────────────────
    while True:
        try:
            user_input = input("\n你: ").strip()
        except EOFError:
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye", "/exit"):
            break
        if user_input == "/clear":
            agent.reset()
            print("✓ 对话已清除")
            continue
        if user_input == "/save":
            if session_file:
                agent.save(str(session_file))
                print(f"✓ 已保存到 {session_file}")
            continue
        if user_input == "/tokens":
            print(f"累计: {_total_tokens:,} tokens | "
                  f"prompt={agent.total_prompt_tokens:,} completion={agent.total_completion_tokens:,}")
            continue

        print("\nAgent: ", end="", flush=True)
        try:
            for token in agent.stream(user_input):
                print(token, end="", flush=True)
            print()
        except byoe.engine.agent.Agent.__class__.__base__.__class__.__base__:  # type: ignore
            pass
        except Exception as e:
            print(f"\n[错误] {e}")

    _save_and_exit()


if __name__ == "__main__":
    main()

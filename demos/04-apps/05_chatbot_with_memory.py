"""AI 应用模板 05：带长期记忆的持久化 Chatbot
========================================
构建一个记忆会话内容的聊天机器人：
  - 短期：当前对话上下文（Agent.messages）
  - 中期：save/load 会话持久化（跨次运行）
  - 长期：LightMemory（FTS5 + 可选语义搜索）——记住用户偏好、历史决策、领域知识

特点：
  - 每次对话自动提取关键信息写入长期记忆
  - 回答前先检索相关记忆注入上下文
  - /remember 命令手动记录重要事项
  - /recall 命令搜索历史记忆

运行：
    python apps/05_chatbot_with_memory.py [--persona <name>]
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import byoe
from byoe import LightMemory, get_memory


# ─── 记忆辅助 ────────────────────────────────────────────────────────────────

def _auto_extract_memory(mem: LightMemory, user_msg: str, assistant_reply: str) -> None:
    """Heuristically extract facts worth remembering from a conversation turn."""
    # Extract: preferences, decisions, names, facts
    trigger_phrases = [
        "我叫", "我是", "我喜欢", "我不喜欢", "我用", "我们决定",
        "记住", "别忘了", "重要", "以后", "下次",
        "my name is", "i prefer", "i use", "we decided", "remember",
    ]
    combined = (user_msg + " " + assistant_reply).lower()
    if any(p in combined for p in trigger_phrases):
        # Let AI extract the key facts
        extractor = byoe.create_agent(tools=[])
        fact = extractor.chat(
            f"Extract 1-2 key facts worth remembering from this exchange (or say NONE):\n"
            f"User: {user_msg[:500]}\nAssistant: {assistant_reply[:500]}"
        )
        if fact.strip().upper() != "NONE" and len(fact.strip()) > 10:
            mem.write(fact.strip(), layer="long_term", tags=["auto_extracted"])


def _search_relevant_memory(mem: LightMemory, query: str, limit: int = 3) -> str:
    """Return formatted memory context relevant to the query."""
    results = mem.search(query, limit=limit)
    if not results:
        return ""
    items = "\n".join(f"- {r['content']}" for r in results)
    return f"\n[Relevant memory]\n{items}\n"


# ─── main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Persistent chatbot with long-term memory")
    parser.add_argument("--persona", default="AI 助手", help="Bot persona name")
    parser.add_argument("--session", default="chatbot_default", help="Session ID for save/load")
    args = parser.parse_args()

    mem = get_memory()  # global singleton, persisted at ~/.byoe/memory.db
    sessions_dir = Path.home() / ".byoe" / "conversations"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session_file = sessions_dir / f"{args.session}.json"

    system = (
        f"你是 {args.persona}，一个友好、聪明的 AI 助手。\n"
        "你有长期记忆能力——你可以记住用户的偏好和历史对话中的重要信息。\n"
        "回答时如果有相关记忆，自然地融入使用，不要明显说'我记得你之前说过'这类机械的话。\n"
        "语言风格：自然、简洁、实用。"
    )

    agent = byoe.create_agent(
        system=system,
        tools=[],  # pure conversation, no file tools
    )

    # Restore session if exists
    if session_file.exists():
        try:
            agent.load(str(session_file))
            print(f"✓ 恢复会话 '{args.session}'（{len(agent.messages)} 条历史）")
        except Exception:
            pass

    print(f"\n{args.persona} 已启动 (session: {args.session})")
    print("命令: /remember <内容>  /recall <关键词>  /clear  /save  /exit\n")

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            agent.save(str(session_file))
            print("\n✓ 会话已保存，再见！")
            break

        if not user_input:
            continue

        # ── 内置命令 ──────────────────────────────────────────────────────────
        if user_input.startswith("/remember "):
            content = user_input[10:].strip()
            mem.write(content, layer="long_term", tags=["manual"])
            print(f"  ✓ 已记录到长期记忆: {content[:80]}")
            continue

        if user_input.startswith("/recall "):
            query = user_input[8:].strip()
            results = mem.search(query, limit=5)
            if results:
                print("  相关记忆:")
                for r in results:
                    print(f"    [{r.get('layer', '?')}] {r['content'][:120]}")
            else:
                print("  (未找到相关记忆)")
            continue

        if user_input == "/clear":
            agent.reset()
            print("  ✓ 对话已清除（长期记忆保留）")
            continue

        if user_input == "/save":
            agent.save(str(session_file))
            print(f"  ✓ 已保存到 {session_file}")
            continue

        if user_input.lower() in ("/exit", "/quit"):
            agent.save(str(session_file))
            print("✓ 会话已保存，再见！")
            break

        # ── 普通对话 ─────────────────────────────────────────────────────────
        # Retrieve relevant memories and prepend to message
        memory_ctx = _search_relevant_memory(mem, user_input)
        full_input = (memory_ctx + user_input) if memory_ctx else user_input

        print(f"\n{args.persona}: ", end="", flush=True)
        try:
            reply_parts = []
            for token in agent.stream(full_input):
                print(token, end="", flush=True)
                reply_parts.append(token)
            print()
            reply = "".join(reply_parts)

            # Auto-extract facts to long-term memory in background
            # (non-blocking: use a thread so it doesn't slow the REPL)
            import threading
            threading.Thread(
                target=_auto_extract_memory, args=(mem, user_input, reply), daemon=True
            ).start()

        except Exception as e:
            print(f"\n[错误] {e}")


if __name__ == "__main__":
    main()

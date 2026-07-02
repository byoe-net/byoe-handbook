"""自定义 Tool：SQLiteTool
用途：让 byoe agent 直接执行 SQLite 查询操作，适合本地数据库驱动的 AI 应用。

使用方法：
    from tools.db_tool import SQLiteTool
    import byoe

    agent = byoe.create_agent(tools=[*byoe.engine.tools.ALL_TOOLS, SQLiteTool()])
    agent.chat("查询 users 表中最近 10 条注册记录")
"""

from __future__ import annotations

import json
import sqlite3
import textwrap
from pathlib import Path

import byoe
from byoe import Tool


class SQLiteTool(Tool):
    """Execute read-only SQL queries against a SQLite database file.

    Write operations (INSERT/UPDATE/DELETE/DROP) are blocked by default;
    set ``allow_writes=True`` to enable them (use with caution).
    """

    name = "sqlite_query"
    description = (
        "Execute a SQL query against a SQLite database file. "
        "Returns results as JSON rows. Read-only by default."
    )
    parameters = {
        "type": "object",
        "properties": {
            "db_path": {
                "type": "string",
                "description": "Path to the .db or .sqlite file",
            },
            "sql": {
                "type": "string",
                "description": "SQL statement to execute (SELECT preferred)",
            },
            "limit": {
                "type": "integer",
                "description": "Max rows to return (default 100)",
                "default": 100,
            },
        },
        "required": ["db_path", "sql"],
    }

    def __init__(self, allow_writes: bool = False) -> None:
        self._allow_writes = allow_writes

    def execute(self, db_path: str, sql: str, limit: int = 100) -> str:
        path = Path(db_path).expanduser().resolve()
        if not path.exists():
            return f"Error: database not found: {db_path}"

        sql = sql.strip()
        if not self._allow_writes:
            first_word = sql.split()[0].upper() if sql.split() else ""
            blocked = {"INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE"}
            if first_word in blocked:
                return (
                    f"Error: write operation '{first_word}' is blocked. "
                    "Initialize SQLiteTool(allow_writes=True) to enable writes."
                )

        try:
            conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            cur = conn.execute(sql)
            rows = cur.fetchmany(limit)
            data = [dict(r) for r in rows]
            conn.close()
            return json.dumps(data, ensure_ascii=False, default=str, indent=2)
        except sqlite3.Error as e:
            return f"SQLite error: {e}"


class SQLiteSchemaInspectorTool(Tool):
    """Inspect SQLite schema — lists tables, columns, and row counts."""

    name = "sqlite_schema"
    description = "List all tables, columns, and row counts in a SQLite database."
    parameters = {
        "type": "object",
        "properties": {
            "db_path": {
                "type": "string",
                "description": "Path to the .db or .sqlite file",
            },
        },
        "required": ["db_path"],
    }

    def execute(self, db_path: str) -> str:
        path = Path(db_path).expanduser().resolve()
        if not path.exists():
            return f"Error: database not found: {db_path}"
        try:
            conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            result = {}
            for (tbl,) in tables:
                cols = conn.execute(f"PRAGMA table_info({tbl})").fetchall()
                count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
                result[tbl] = {
                    "row_count": count,
                    "columns": [{"name": c[1], "type": c[2], "nullable": not c[3]} for c in cols],
                }
            conn.close()
            return json.dumps(result, ensure_ascii=False, indent=2)
        except sqlite3.Error as e:
            return f"SQLite error: {e}"


# ─── quick demo ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile, os

    # Create a demo database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, created_at TEXT)")
    conn.executemany(
        "INSERT INTO users VALUES (?,?,?,?)",
        [(1, "Alice", "alice@example.com", "2025-01-01"),
         (2, "Bob", "bob@example.com", "2025-01-15"),
         (3, "Carol", "carol@example.com", "2025-02-01")],
    )
    conn.commit(); conn.close()

    print("=== Schema Inspector ===")
    inspector = SQLiteSchemaInspectorTool()
    print(inspector.execute(db_path))

    print("\n=== SQL Query Tool ===")
    tool = SQLiteTool()
    print(tool.execute(db_path, "SELECT * FROM users ORDER BY created_at DESC", limit=10))

    print("\n=== Agent with DB Tools ===")
    agent = byoe.create_agent(
        tools=[SQLiteTool(), SQLiteSchemaInspectorTool()],
        system="You are a data analyst. Use the SQLite tools to answer questions.",
    )
    print("Agent ready. Tools:", [t.name for t in agent.tools])

    os.unlink(db_path)

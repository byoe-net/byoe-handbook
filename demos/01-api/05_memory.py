"""BYOE 长期记忆（FTS5 + 语义搜索）

演示 LightMemory 的写入、检索与语义搜索能力。

BYOE 默认使用 SQLite FTS5（关键词搜索）。
设置 BYOE_EMBEDDING_MODEL 后自动升级为关键词 + 语义双路融合搜索。

记忆存储位置：~/.byoe/memory.db

运行：
    python 05_memory.py

可选（启用语义搜索）：
    set BYOE_EMBEDDING_MODEL=text-embedding-3-small
    set BYOE_API_KEY=sk-...
"""

import byoe
from byoe import get_memory, LightMemory

mem: LightMemory = get_memory()

# ── 写入记忆 ──────────────────────────────────────────────────────────────────
mem_id, was_update = mem.write(
    path="/project/auth",
    content="使用 JWT + Redis 实现无状态鉴权。Token 有效期 2 小时，刷新 Token 7 天。",
    layer="knowledge",
    tags=["auth", "jwt", "redis"],
    summary="JWT 鉴权方案",
)
print(f"{'更新' if was_update else '新建'} 记忆 ID: {mem_id}")

mem.write(
    path="/project/database",
    content="PostgreSQL 主库 + Redis 缓存。热点数据 TTL 10 分钟，用 write-through 策略保持一致性。",
    layer="knowledge",
    tags=["database", "postgresql", "redis", "cache"],
    summary="数据库架构",
)

mem.write(
    path="/session/current-task",
    content="正在实现用户登录 API，需要对接上述 JWT 鉴权和 PostgreSQL 用户表。",
    layer="session",
)

# ── FTS5 关键词搜索 ───────────────────────────────────────────────────────────
print("\n=== FTS5 关键词搜索: 'JWT 鉴权' ===")
results = mem.search("JWT 鉴权", limit=3)
for r in results:
    print(f"  [{r['score']:.2f}] {r['path']}: {r['summary'] or r['content'][:60]}")

# ── 语义搜索（需要 BYOE_EMBEDDING_MODEL） ────────────────────────────────────
import os
if os.environ.get("BYOE_EMBEDDING_MODEL"):
    print("\n=== 语义搜索: '如何做用户认证' ===")
    results = mem.search_semantic("如何做用户认证", limit=3)
    for r in results:
        print(f"  [cos={r['score']:.3f}] {r['path']}: {r['summary'] or r['content'][:60]}")

    # 为存量记忆补充向量（首次启用 embedding 时运行一次）
    count = mem.reindex()
    print(f"\n补充向量: {count} 条记忆已嵌入")
else:
    print("\n[提示] 设置 BYOE_EMBEDDING_MODEL=text-embedding-3-small 可启用语义搜索")

# ── 在 Agent 对话中自动使用记忆 ──────────────────────────────────────────────
print("\n=== 在 Agent 中使用记忆 ===")
# Agent 携带 search_memory / record_memory 工具，会在需要时自动检索
agent = byoe.create_agent()
# 内置工具 search_memory 会在 Agent 认为需要查阅历史时自动调用
# 也可以在代码中直接操作：
res = mem.read("/project/auth")
if res:
    print(f"直接读取 /project/auth: {res['content'][:80]}")

# ── 垃圾回收 ─────────────────────────────────────────────────────────────────
stats = mem.gc(session_ttl_days=30, short_term_ttl_days=14, max_rows=5000)
print(f"\nGC 结果: 删除过期 {stats['deleted_expired']} 条，剩余 {stats['remaining']} 条")

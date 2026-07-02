# 记忆 + 钩子 + 多模态：进阶能力

> 一句话摘要：让 AI 记住过去（Memory）、汇报每次操作（Hooks）、看懂图片（Multimodal）。

---

## 1. 场景引入

到了进阶篇。这三个能力分别解决三个问题：

- **记忆**：AI 重启后还认识你吗？还记得之前的项目背景吗？
- **钩子**：AI 每次调用了什么工具？花了多少钱？你能审计吗？
- **多模态**：AI 能「看懂」截图、PDF、手绘图吗？

---

## 2. LightMemory：三层记忆系统

BYOE 的记忆系统有一个简单的前提：**不要学 Pinecone，不要搞向量数据库**。

```python
from byoe import LightMemory

mem = LightMemory(db_path="~/.byoe/memory.db")

# 写入记忆
mem.write(
    content="用户偏好使用 FastAPI 框架，ORM 用 SQLAlchemy",
    layer="long_term",
    tags=["tech-stack", "user-preference"]
)

# 搜索记忆
results = mem.search("技术栈选择", layer="long_term", limit=5)
for r in results:
    print(f"{r['score']:.2f} {r['content']}")
```

### 三层结构

```
短期 (short_term)  → 当前对话上下文（自动过期 14 天）
中期 (session)     → 跨会话记忆（自动过期 30 天）
长期 (long_term)   → 永久知识（手动管理）
```

### 搜索机制

BYOE 的搜索不需要任何外部依赖：

```
1. FTS5 全文搜索（SQLite 内置） → 关键词匹配
2. LIKE 模糊搜索（SQLite 内置） → 兜底方案
3. 语义搜索（可选） → 需要配置 embedding 模型
```

第一步和第二步是零依赖的，用 SQLite 自带功能实现。第三步需要设置 `BYOE_EMBEDDING_MODEL` 环境变量。

### 自动 GC

记忆默认上限 5000 条，超出的自动清理最旧的短期/中期记忆：

```bash
# 查看记忆统计
byoe memory --stats

# 手动清理
byoe memory --gc

# 搜索记忆
byoe memory search "FastAPI"
```

---

## 3. Hooks：事件钩子系统

Hooks 让你监听 AI 的每一次操作：

```python
import byoe
from byoe import on, off

# 注册钩子
@on("tool.call")
def log_tool_call(tool_name, args, result):
    print(f"[AUDIT] {tool_name}({args}) → {result[:100]}...")
    # 写入审计日志
    with open("audit.log", "a") as f:
        f.write(f"{datetime.now()}\t{tool_name}\t{args}\n")

@on("llm.response")
def track_cost(model, input_tokens, output_tokens):
    cost = estimate_cost(model, input_tokens, output_tokens)
    print(f"[COST] {model}: ${cost:.4f}")

@on("agent.turn")
def track_turn(turn_number, duration):
    print(f"[TURN] #{turn_number} took {duration:.1f}s")

agent = byoe.create_agent()
agent.chat("写一个 Python 爬虫")
```

### 内置事件

| 事件 | 触发时机 | 适用场景 |
|------|---------|---------|
| `llm.response` | LLM 返回结果后 | 费用统计 |
| `tool.call` | 工具执行前后 | 审计日志 |
| `agent.turn` | 每轮 Agent 循环 | 性能监控 |
| `memory.write` | 记忆写入 | 同步到外部系统 |

### 预算保护示例

```python
@on("llm.response")
def budget_guard(model, input_tokens, output_tokens, **_):
    total_cost = read_running_total()
    total_cost += estimate_cost(model, input_tokens, output_tokens)
    if total_cost > 10.0:  # 超过 $10 停止
        print("🚫 预算超限，停止执行")
        exit(1)
```

---

## 4. 多模态：让 AI 看懂图片

支持 OpenAI 视觉模型（gpt-4o、gpt-4o-mini 等）：

```python
# 方式一：使用内置工具
agent.chat("这张架构图有什么问题？", images=["architecture.png"])

# 方式二：指定图片 URL
agent.chat(
    "这个网页布局需要改进",
    images=["https://example.com/screenshot.png"]
)

# 方式三：多图片
agent.chat(
    "对比这两张设计稿",
    images=["design_v1.png", "design_v2.png"]
)
```

### 适用场景

- 📸 看 UI 截图提修改意见
- 📊 分析图表数据
- 📝 识别手绘流程图
- 🐛 看错误截图诊断问题
- 📄 读取 PDF/扫描件内容

---

## 5. 三者联动

```python
import byoe
from byoe import on

agent = byoe.create_agent()

# 1. 每次工具调用都记录到记忆
@on("tool.call")
def remember_tool_call(tool_name, args, result, **_):
    agent.memory.write(
        content=f"执行 {tool_name}({args}) → {result[:200]}",
        layer="session",
        tags=[tool_name]
    )

# 2. 多轮对话后，AI 记得之前的操作
agent.chat("帮我画一个登录页面，用 HTML + CSS")
agent.chat("改成深色主题", images=["login_v1.png"])
agent.chat("把上次的数据库查询工具优化一下")  # 从记忆中找到上下文
```

---

## 6. 要点总结

- 记忆：三层存储（短期/中期/长期），FTS5 搜索零依赖，自动 GC
- 钩子：监听 `tool.call` / `llm.response` / `agent.turn`，适合审计、计费、监控
- 多模态：gpt-4o 视觉能力，支持本地图片和 URL
- 三者联动：钩子记录到记忆，记忆给多轮对话提供上下文，多模态扩展输入形式

## 下期预告

最后一期：**从 Demo 到生产 —— 最佳实践与 FAQ**。

---

📎 完整文档：[API 参考 §LightMemory + Hooks](../../docs/03-developer-guide/API-REFERENCE-ZH.md)
📎 示例代码：[05_memory.py](../../demos/01-api/05_memory.py) · [09_hooks.py](../../demos/01-api/09_hooks.py) · [11_multimodal.py](../../demos/01-api/11_multimodal.py)

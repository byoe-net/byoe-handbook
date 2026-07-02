# 自定义工具：扩展 AI 的能力边界

> 一句话摘要：BYOE 内置 23 个工具，但真正的威力在于 —— 你可以用 10 行 Python 给 AI 增加任意能力。

---

## 1. 场景引入

内置工具有 read_file、write_file、bash、grep…… 但如果我需要 AI 做这些：

> 「查询公司内部数据库」、「发一封邮件」、「调用内部 API」、「读取二维码」

你不需要等 BYOE 更新版本。自己写一个 Tool 就行。

---

## 2. Tool 基类

一个 Tool 就是一个 Python 类，继承 `byoe.Tool`：

```python
from byoe import Tool

class CurrentTimeTool(Tool):
    """获取当前时间的工具"""

    name = "current_time"
    description = "获取当前的系统日期和时间"

    def execute(self, format: str = "%Y-%m-%d %H:%M:%S", **kwargs) -> str:
        from datetime import datetime
        return datetime.now().strftime(format)
```

注入到 Agent：

```python
import byoe

agent = byoe.create_agent(tools=[CurrentTimeTool()])

# AI 现在可以在需要时自动调用 current_time
agent.chat("现在几点？")
```

就这么简单。

---

## 3. 工作原理

```
AI 决定调用 current_time
  → LLM 输出: {"tool": "current_time", "args": {"format": "%H:%M:%S"}}
  → Agent 调用 CurrentTimeTool.execute(format="%H:%M:%S")
  → 返回: "14:30:00"
  → AI 基于结果回复: "现在是下午 2 点 30 分。"
```

BYOE 不限制 Tool 能做什么 —— 只要能跑 Python，就能做任何事。

---

## 4. 实战：SQLite 数据库查询工具

```python
import sqlite3
from byoe import Tool

class SQLiteTool(Tool):
    """只读 SQLite 查询工具"""

    name = "query_db"
    description = "对 SQLite 数据库执行只读 SQL 查询"

    def __init__(self, db_path: str = "app.db"):
        super().__init__()
        self.db_path = db_path

    def execute(self, sql: str, **kwargs) -> str:
        # 写保护：禁止修改数据库
        if sql.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "DROP", "ALTER")):
            return "❌ 只允许 SELECT 查询"

        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchmany(20)
            cols = [desc[0] for desc in cur.description]
            result = "\n".join([str(cols)] + [str(r) for r in rows])
            return f"✅ 查询成功 ({len(rows)} 行):\n{result}"
        finally:
            conn.close()
```

```python
agent = create_agent(tools=[SQLiteTool("analytics.db")])
agent.chat("查询这个月每天的活跃用户数")
```

---

## 5. 更复杂的工具

看 `demos/03-tools/utility_tools.py`，一个文件里实现了三个工具：

| 工具 | 功能 | 依赖 |
|------|------|------|
| `TemplateTool` | 用 Jinja2 渲染模板 | `jinja2` |
| `EnvValidatorTool` | 检查环境变量和依赖 | 无 |
| `TimerTool` | 代码块执行时间基准测试 | 无 |

以 `TimerTool` 为例：

```python
class TimerTool(Tool):
    name = "time_execution"
    description = "测量一段 Python 代码的执行时间"

    def execute(self, code: str, repeat: int = 3, **kwargs) -> str:
        import timeit
        times = timeit.repeat(code, repeat=repeat, number=1)
        avg = sum(times) / len(times)
        return f"✅ 执行 {repeat} 次，平均耗时 {avg*1000:.1f}ms"
```

---

## 6. 一键注入 vs 技能系统

Tool 和 Skill 的区别：

```
Tool（Python 类）
  ├── 注入方式: create_agent(tools=[...])
  ├── 生效范围: 当前 Agent 实例
  └── 适用场景: 需要稳定可靠的能力扩展

Skill（Python 文件）
  ├── 注入方式: 放 ~/.byoe/skills/ 目录
  ├── 生效范围: 全局 / 所有对话
  └── 适用场景: 运行时动态加载的热插拔能力
```

简单说：**Tool 是编译时注入，Skill 是运行时加载**。

---

## 7. Tool 编写规范

```
✅ 必须做：
  - 继承 byoe.Tool
  - 设置 name 和 description
  - 实现 execute(**kwargs) → str
  - 写清晰的参数 docstring
  - 做好异常处理，返回明确信息

❌ 不要做：
  - 不要在 execute 里调 LLM（会死循环）
  - 不要返回超长结果（AI 上下文有限）
  - 不要让工具执行超过 5 分钟（设超时）
```

---

## 8. 要点总结

- 继承 `byoe.Tool` → 实现 `execute()` → 注入 Agent，三步即可
- 可以做任何事情：数据库、API 调用、文件处理、硬件交互
- 对比 Skill：Tool 是代码注入，Skill 是运行时热加载
- 安全建议：写保护、超时控制、异常处理
- 示例参考：`demos/03-tools/`（SQLite 查询 + 三个实用工具）

## 下期预告

下一篇我们连接整个 MCP 生态：**MCP + VS Code** —— 让 BYOE 集成数千个社区工具。

---

📎 完整文档：[API 参考 §Tool](../../docs/03-developer-guide/API-REFERENCE-ZH.md)
📎 示例代码：[demos/03-tools/](../../demos/03-tools/)

# BYOE 四层架构：Agent + LLM + Tools + Skills

> 一句话摘要：BYOE 用四层解耦设计实现「轻量但能打」—— 任何一层都可以独立替换。

---

## 1. 场景引入

上期我们说 BYOE 可以用一句话让 AI 改代码。但你有没有想过：

> 它和 LangChain、AutoGPT 这些框架有什么本质区别？
> 为什么它能做到 `pip install` 就用，而其他框架动辄几百兆？

答案藏在它的**架构设计**里。

---

## 2. 四层架构总览

> 插入四层架构图 (articles/02-architecture/images/)

```
┌─────────────┐
│  用户界面层   │  CLI · Web UI · Python API
├─────────────┤
│  Agent 层    │  核心循环 · 工具调度 · 技能匹配
├─────────────┤
│  LLM 层      │  OpenAI / DeepSeek / Ollama · Fallback
├─────────────┤
│  Tools 层    │  内置工具 · Skills · MCP
└─────────────┘
```

### 第 1 层：用户界面

三种接入方式，共享同一个 Agent 核心：

```python
# 方式一：CLI
byoe chat

# 方式二：Web UI
byoe web

# 方式三：Python API
import byoe
agent = byoe.create_agent()
agent.chat("写一个 Python 脚本")
```

**设计要点**：界面层只负责输入输出格式转换，不包含任何业务逻辑。这意味着你可以基于 Python API 构建自己的前端（FastAPI、Gradio、甚至是钉钉机器人）。

### 第 2 层：Agent（核心）

这是 BYOE 的心脏，约 **600 行 Python 代码** (`byoe/engine/agent.py`)。

它做的事：

```
用户输入 "帮我重构这个函数" 
  → Agent 拆解任务
    → 调用 read_file 读取代码
    → 调用 LLM 生成新代码
    → 调用 write_file 写入修改
    → 调用 bash 跑测试
    → 检查测试结果
  → 返回执行报告
```

**与其他框架的关键区别**：

| 特性 | LangChain | AutoGPT | BYOE |
|------|-----------|---------|------|
| Agent 核心代码 | ~5000 行 | ~3000 行 | ~600 行 |
| 依赖项 | 30+ | 20+ | 3 (openai, rich, prompt_toolkit) |
| 学习曲线 | 陡峭 | 中等 | 平缓 |
| 可自定义程度 | 极高 | 低 | 高 |

BYOE 的 Agent 故意保持简单：**没有复杂的 Chain、没有 Graph、没有记忆抽象层**。上下文压缩、工具调用、技能注入都在一个文件里搞定。

### 第 3 层：LLM

LLM 层是 BYOE 最薄的封装（`byoe/engine/llm.py`）。

```python
# 核心就一个 LLM 类
llm = LLM(
    model="gpt-4o",
    api_key="sk-...",
    fallback_models=["gpt-4o-mini", "deepseek-chat"]
)

# 统一流式接口
for token in llm.stream(messages):
    print(token, end="")
```

支持任意 OpenAI 兼容接口：DeepSeek、Qwen、Kimi、Ollama、vLLM、LM Studio。

**Fallback 链**是 LLM 层的杀手特性：

```
主模型 gpt-4o 调用失败
  → 自动重试 × 3（指数退避）
    → 切换到 gpt-4o-mini
      → 切换到 deepseek-chat
        → 全部失败 → 抛出异常
```

零额外代码即可实现高可用。

### 第 4 层：Tools + Skills

这是 BYOE 的扩展层，也是最灵活的一层。

**内置工具（23 个）**：

```
文件操作：read_file, write_file, edit_file, list_dir, grep
命令执行：bash
网络：fetch_url, web_search
代码：python_repl, git
审查：sober_scan
智能体：swarm_collaboration, sub_agent
```

**技能系统**是 BYOE 区别于其他框架的最大亮点：

用户可以在不修改代码的前提下，通过 JSON 或 Python 文件扩展 Agent 能力：

```json
// 认知型技能（JSON）：给 AI 注入领域知识
{
  "name": "api-reviewer",
  "trigger": "审查API",
  "instructions": "审查 API 设计时，检查：\n1. 是否使用名词复数 ..."
}
```

```python
# 动作型技能（Python）：让 AI 获得新能力
def run(title: str, message: str, **kwargs):
    """发送桌面通知"""
    # 跨平台通知实现
    return f"✅ 已发送通知：{title}"
```

**MCP 集成**让 BYOE 可以连接整个 MCP 生态的工具。

---

## 3. 为什么说它比 LangChain 更轻？

一个直观对比：

```bash
# BYOE
pip install byoe
du -sh ~/.pyenv/versions/*/lib/python*/site-packages/byoe
# → ~500KB

# LangChain
pip install langchain
du -sh ~/.pyenv/versions/*/lib/python*/site-packages/langchain
# → ~5MB
```

BYOE 的核心信念：**Agent 框架应该像瑞士军刀，而不是瑞士军工厂**。

---

## 4. 效果

> 插入架构图

这张图说明了为什么 BYOE 只有 3 个核心依赖：
- UI 层 → 无额外依赖（CLI 用 stdlib，Web 用 stdlib）
- Agent 层 → 只有 `openai` SDK
- LLM 层 → 复用 `openai` SDK
- Tools 层 → 几乎全是 Python 标准库

---

## 5. 要点总结

- BYOE 四层架构：**UI → Agent → LLM → Tools**，每层可独立替换
- Agent 层仅 600 行代码，比 LangChain 简洁 10 倍
- LLM 层支持任意 OpenAI 兼容接口 + Fallback 链
- Tools 层三层扩展：**内置工具 → 技能系统 → MCP 生态**
- 核心设计哲学：**轻量**，能放在一个包里就不拆成十个

## 下期预告

下一篇我们动手实践：**5 分钟安装 BYOE 并完成第一个对话**。

---

📎 完整架构源码：[byoe/engine/](https://github.com/byoenet/byoe)

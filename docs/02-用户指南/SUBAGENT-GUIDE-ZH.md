# BYOE Sub-agent（子智能体）使用指南

> 适用版本：v0.7.2 及以上

---

## 什么是 Sub-agent？

**Sub-agent（子智能体）** 是 BYOE 提供的 `agent` 工具，允许主 Agent 将一个复杂子任务**完全委派**给一个拥有**独立上下文**的子 Agent 执行。

子 Agent 特性：
- 拥有**全新的、干净的上下文窗口**，不受主 Agent 对话历史影响；
- 可以运行完整的工具调用（读写文件、执行命令、联网等），最多 20 轮；
- 执行结果以**摘要报告**的形式返回给主 Agent（超过 5000 字时自动压缩）；
- 若设置 `inherit_crew_context=true`，子 Agent 自动获得当前项目的 Crew 上下文（INSTRUCTIONS.md、crew.yaml、resume.md）。

---

## 为什么需要 Sub-agent？

### 直接对话的问题

| 问题 | 表现 |
|------|------|
| 上下文污染 | 长时间对话后，历史工具结果填满上下文，影响后续推理质量 |
| 专注力分散 | 主 Agent 同时处理多个子任务时容易遗漏细节 |
| 并行子任务困难 | 单 Agent 无法同时"派出"两条独立调查路线 |

### Sub-agent 解决了什么

| 场景 | 效果 |
|------|------|
| 大型代码库探索 | 子 Agent 独立扫描，返回干净的分析报告 |
| 长链路实现任务 | 子 Agent 在隔离上下文里完成，不污染主对话 |
| 专家角色委派 | 子 Agent 扮演安全专家/测试工程师等进行专项审查 |
| 复杂信息收集 | 子 Agent 调研后返回摘要，主 Agent 用于决策 |

---

## 快速示例

### 1. 自然语言触发（推荐）

在 `byoe chat` 或 `byoe web` 对话中直接说：

🗣：`"请用 agent 工具，委派一个安全专家子 Agent，让它独立审查 src/auth/ 目录下的所有文件，找出潜在的安全漏洞，然后把报告给我。"`

主 Agent 会自动调用 `agent` 工具，子 Agent 在隔离上下文中完成安全审查并返回报告。

### 2. 常见委派场景指令示例

```
# 代码库探索
"用 agent 工具派一个子 Agent 帮我梳理 ./backend 目录的模块结构，
 用 tree 格式加一句话说明输出给我。"

# 隔离实现
"用 agent 工具，角色设定为'资深 Python 工程师'，
 让它独立实现 crew/changes/auth-feature/design.md 里描述的功能，
 实现完毕后给我一个修改摘要。"

# 专项审查
"用 agent 工具，角色为安全工程师，
 让它在隔离上下文里检查 API 接口是否有 SQL 注入或越权漏洞。"

# 并行子任务
"用两个 agent 分别：
 1. 检查前端 src/ 的 TypeScript 类型错误
 2. 检查后端 api/ 的缺失测试覆盖
 然后把两份报告都给我。"
```

---

## Python API 直接调用

```python
from byoe.engine.agent import Agent
from byoe.engine.llm import LLM

llm = LLM(model="deepseek-chat")

# 主 Agent
main_agent = Agent(llm=llm, cwd="./my-project")

# 方式一：通过主 Agent 的 chat 触发（最简单）
result = main_agent.chat(
    "用 agent 工具，role='You are a senior test engineer.'，"
    "让子 Agent 帮我为 src/auth/login.py 生成完整的单元测试，"
    "inherit_crew_context=true"
)
print(result)
```

### 直接在代码中构建子 Agent

```python
from byoe.engine.agent import Agent
from byoe.engine.llm import LLM
from byoe.engine.prompt import system_prompt

llm = LLM(model="deepseek-chat")

# 子 Agent 使用独立上下文
sub_system = "You are a security engineer specializing in Python web APIs.\n\n" + system_prompt([])
sub_agent = Agent(
    llm=llm,
    system=sub_system,
    cwd="./my-project",
    max_rounds=15,
)

report = sub_agent.chat(
    "审查 src/api/ 目录下所有路由文件，"
    "识别：SQL 注入、路径遍历、缺少鉴权的接口，以 Markdown 表格输出报告。"
)
print(report)
```

---

## 参数说明

`agent` 工具接受以下参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task` | string | ✅ | 子 Agent 需要完成的任务描述 |
| `role` | string | ❌ | 子 Agent 的角色人格（如 `"You are a senior backend architect."`） |
| `inherit_crew_context` | boolean | ❌ | 是否注入项目 Crew 上下文（INSTRUCTIONS.md 等），默认 `true` |

### `inherit_crew_context` 作用

- `true`（默认）：子 Agent 获得 `INSTRUCTIONS.md`、`crew.yaml`、`resume.md`、`blockers.md` 的内容，了解项目背景
- `false`：子 Agent 以最小系统提示启动，适合纯粹的通用任务（如信息检索）

---

## Sub-agent vs Swarm 选择指南

| 使用 Sub-agent 当… | 使用 Swarm 当… |
|-------------------|---------------|
| 需要独立沙盒执行避免上下文污染 | 需要多个领域专家顺序接力（设计→实现→审查） |
| 任务边界清晰、可委派一个人搞定 | 任务本质上是多步流水线 |
| 复杂信息收集（探索代码库、收集资料） | 跨角色协作，后者基于前者的输出继续工作 |
| 并行多路子任务（分别交给不同子 Agent） | 需要最终综合所有专家的意见 |

---

## 常见问题

**Q: 子 Agent 会看到主 Agent 的对话历史吗？**  
A: 不会。子 Agent 拥有完全独立的上下文，除非 `inherit_crew_context=true`（仅注入 Crew 文件，不含对话记录）。

**Q: 子 Agent 能修改文件吗？**  
A: 可以。子 Agent 拥有与主 Agent 相同的工具访问权限（除了 `agent` 工具本身，防止无限递归），可以读写文件、执行命令。

**Q: 子 Agent 失败了怎么办？**  
A: `agent` 工具会捕获异常并返回 `Sub-agent error: <原因>`，主 Agent 可以据此决定重试或改变策略。

**Q: 子 Agent 最多运行多少轮？**  
A: 默认 20 轮。若任务在 20 轮内未完成，子 Agent 会返回当前进度给主 Agent。

**Q: 子 Agent 的输出太长怎么办？**  
A: 超过 5000 字时，会自动调用主 Agent 的 LLM 进行摘要压缩，保留关键决策点、修改文件路径、错误信息和最终结论。

---

## 与其他功能配合

### 配合 Swarm 使用

可以先用 Sub-agent 独立探索，再用 Swarm 流水线实现：

```
"先用 agent 工具让子 Agent 把这个代码库的主要模块梳理清楚，
 返回报告后，再用 swarm_collaboration 工具（backend-architect + security-engineer）
 基于这份报告设计改造方案并审查。"
```

### 配合 Skills 使用

可以在 Python Skill 里封装 Sub-agent 调用，实现标准化委派流程：

```python
# ~/.byoe/skills/security_audit.py
def run(target_dir: str = "src", **kwargs) -> str:
    """对指定目录发起独立子 Agent 安全审计，返回漏洞报告。"""
    # 通过 agent tool 在主 Agent 上下文中触发，返回结果
    return f"请用 agent 工具，role='You are a security engineer.'，" \
           f"task='审查 {target_dir} 目录，找出所有安全漏洞并以 Markdown 表格输出'，" \
           f"inherit_crew_context=true"
```

---

*更多高级用法见 [Swarm 群智协作指南](./SWARM-GUIDE-ZH.md) 和 [Loop Engineering 教程](../../loop-demo/LOOP-ENGINEERING-TUTORIAL.md)。*

# BYOE Swarm 群智协作网络机制使用指南

> 适用版本：v0.8.0 及以上

## 什么是 Swarm (群智协作)？

在传统的 AI 编码工具中，大多数时候是你面对一个全能但缺乏深度的“通用 Agent”。而在 **BYOE (Bring Your Own Executive AI)** 中，系统底层的哲学一直是“专家协作（Crew）”。

随着 **SwarmTool** 的引入，BYOE 真正实现了零额外依赖的 **串行跨行流水线功能**。

这就像是你开了一家微型的软件外包公司。当你下发了一个长链条任务（例如“帮我重构登录模块并添加防刷机制”），主 Agent（扮演项目经理 PM 的角色）会自动：
1. 找出最合适的几名子专家（从内置的 29 位专家库中挑选）。
2. 将任务丢给第一个专家。
3. 第一位专家完成后，**将其上下文和输出毫无保留地塞给第二位专家**。
4. 第二位专家在第一位的基础上接着干（或者找茬审查）。
5. ……依此类推，最后生成一份浓缩的最终交接物。

---

## 典型工作流范例：从构思到上线

假设主 Agent 调度了以下流水线：`['backend-architect', 'frontend-specialist', 'security-engineer']`。

1. **`backend-architect`（后端架构师）接到任务**：
   - 行为：不写具体业务代码，而是制定 RESTful API 规范、JSON 结构格式、缓存方案等。
   - 输出：《登录模块 API 设计规范》。

2. **接力棒传给 `frontend-specialist`（前端专家）**：
   - 行为：他收到了你的最初诉求，以及刚才后端架构师写出来的《规范》。立刻开始撰写 React/Vue 接口对接代码和 UI 样式。
   - 输出：《前端页面交互代码及 API 联调方案》。

3. **接力棒传给 `security-engineer`（安全工程师）**：
   - 行为：此时他审视的是全栈的设计。他会重点审查刚才两人的产出是否存在 SQL 注入、XSS、或者接口防刷（Rate Limiting）机制漏配。
   - 输出：《漏洞审核清单与加固修正代码》。

4. **最终结果返回**：
   - 如果产生的文本量过大（几万字），Swarm 引擎会自动调用归纳总结算法，为你提供包含了核心决策点与代码执行修改成果的报告。

---

## 我该如何触发 Swarm？

对于最终使用者而言，**一切都是无感且全自动的！**

BYOE 的“工具调用（Tool Calling）”系统能自我感知任务复杂度。当你在 `byoe chat` 或者 `byoe web` 对话框里提交**极度复杂的多重身份交叉任务**时：
> *“帮我设计一个高并发的秒杀抢购系统的方案，然后挑最棘手的部分写成代码，最后审查一下这段新代码有没有漏洞隐患。”*

主 Agent 就会意识到自己孤军奋战容易丢失上下文细节或者力不从心，它便会自发执行 `swarm_collaboration` 工具，生成 `['backend-architect', 'security-engineer', 'api-tester']` 帮您一键跑完这漫长的长征。

---

## 支持调用的角色词典

如果想明确命令 AI 利用指定专家协作，你也可以显式地使用指令，参考角色列表（匹配 `byoe/agents/` 目录中的配置）：
- `backend-architect` (后端架构师)
- `frontend-specialist` (前端专家)
- `mobile-developer` (移动开发)
- `game-designer` (游戏设计)
- `security-engineer` (安全工程师)
- `database-specialist` (数据库专家)
- `devops-engineer` (运维工程师)
- `api-tester` (API测试)
- `technical-writer` (技术作家/文档编写)
...及其他 29 位专家，详细列表可以使用 `byoe agents` 命令行获取。

---

## 如何显式指定 Swarm 流水线？

除了让主 Agent 自动判断，你也可以在提示词里 **明确命令** AI 使用特定专家组合：

🗣：`"请用 swarm 模式，依次调用 backend-architect、security-engineer、technical-writer 帮我完成：设计高并发抢购系统的架构、审查安全漏洞，并生成一份 README 文档。"`

这样 AI 会直接调用 `swarm_collaboration` 工具而不经过自动判断。

### Python API 直接调用

如果你在自己的脚本里需要触发 Swarm 流水线，可以这样做：

```python
from byoe import create_agent

agent = create_agent()  # 从环境变量自动读取配置

# 直接在 chat() 里告诉主 Agent 调用 swarm_collaboration
result = agent.chat(
    "用 swarm_collaboration 工具，roles=['backend-architect','security-engineer']，"
    "完成任务：设计并审查用户认证模块的 API 接口规范。"
)
print(result)
```

### 单次无状态执行（CI/CD 脚本）

```bash
# 单次命令，不进入交互模式
byoe chat "用 swarm 模式（backend-architect + api-tester）帮我生成这个 PR 的代码审查报告。"
```

---

## 并行分组（scatter-gather）

从 v0.8.0 起，Swarm 新增 `parallel_groups` 模式：同组内的专家**并发执行**，组与组之间串行传递合并输出。

### 何时使用

- 同组内专家任务互相独立（例如安全审查和性能审查可以同时进行）
- 需要在最后由"主管"角色汇总所有意见

### 使用示例

```python
from byoe import create_agent

agent = create_agent()

# 安全工程师和性能工程师并发评审，Tech Lead 再汇总
result = agent.chat(
    "用 swarm_collaboration 工具，parallel_groups=[['security-engineer','performance-reviewer'],['tech-lead']]，"
    "评审并优化我们的数据库查询层。"
)
print(result)
```

也可通过 `SwarmTool` 直接调用：

```python
from byoe.engine.tools.swarm_tool import SwarmTool
from byoe import LLM

swarm = SwarmTool(llm=LLM(model="gpt-4o", api_key="sk-..."))
result = swarm.execute(
    initial_task="评审数据库查询层的安全性和性能",
    parallel_groups=[
        ["security-engineer", "performance-reviewer"],  # 第一轮并发
        ["tech-lead"],                                  # 第二轮汇总
    ],
    step_timeout_seconds=300,   # 每步超时（秒）
)
print(result)
```

### 模式对比

| 维度 | 串行接力 (`roles`) | 并行分组 (`parallel_groups`) |
|------|-------------------|------------------------------|
| **执行顺序** | 严格串行 | 组内并发，组间串行 |
| **上下文传递** | 前一位输出作为后一位输入 | 同组各自独立执行，组内结果合并后传给下一组 |
| **适合场景** | 设计→实现→审查（有依赖关系） | 安全+性能同时审查，再由主管汇总 |
| **速度** | 顺序执行 | 同组内加速，总时间 ≈ 最慢专家 |
| **参数** | `roles=[...]` | `parallel_groups=[[...], [...]]` |

---

## 错误恢复与部分结果

从 v0.7.2 起，Swarm 引入了 **容错传播机制**：

- 若流水线中某一位专家失败（网络超时、LLM 报错等），错误信息会被注入下一位专家的上下文，让后续专家有机会感知并绕过问题继续工作；
- 若超过一半的专家均失败（例如 5 人组中有 3 人失败），Swarm 会 **提前中止** 并返回 `[SWARM ABORTED]` 标记，附带已完成专家的部分输出；
- 主 Agent 收到部分结果后，会向用户说明完成情况，而不会静默崩溃。

```
[Swarm 执行日志示例]
✓ backend-architect  完成 (2.1s)
✗ frontend-specialist  失败 — LLM timeout，错误已传递给下一位
✓ security-engineer  完成（已感知上游故障，跳过前端相关审查）
最终：2/3 专家完成，返回部分结果。
```

---

## Sub-agent（子智能体）与 Swarm 如何选择？

BYOE 提供了两种多 Agent 协作机制，用途不同：

| 维度 | Swarm 流水线 | Sub-agent（子智能体） |
|------|-------------|----------------------|
| **调用方式** | `swarm_collaboration` 工具 | `agent` 工具 |
| **上下文** | 专家按序共享接力上下文 | 子 Agent 拥有完全独立的上下文 |
| **适合场景** | 跨角色接力（后端→前端→安全） | 隔离委派（专注子任务，不污染主上下文） |
| **输出形式** | 最终综合报告 | 子 Agent 的完整对话结果（自动摘要） |
| **专家深度** | 每位专家专注自己领域 | 子 Agent 可扮演任意角色 |
| **典型指令** | "帮我设计+实现+审查" | "帮我独立研究这个代码库，告诉我主要模块" |

**经验法则**：
- 任务需要**多个领域按顺序叠加**（设计→实现→审查）→ 用 **Swarm**
- 任务需要**独立沙盒执行**（避免污染主上下文）或**委派复杂子任务** → 用 **Sub-agent**

更详细的 Sub-agent 用法请参阅 [Sub-agent 使用指南](./SUBAGENT-GUIDE-ZH.md)。

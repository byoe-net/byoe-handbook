# Swarm + Sub-agent：多 AI 协作的艺术

> 一句话摘要：当一个问题太复杂，一个 AI 搞不定时，BYOE 会自动拆解成多个子任务，交给多个 AI 并行处理。

---

## 1. 场景引入

一个 AI 的上下文窗口是有限的。当你在一个超长对话中让 AI 同时做这些事情：

- 设计数据库 Schema
- 写后端 API
- 写前端页面
- 写单元测试
- 写部署脚本

AI 会越来越「糊涂」—— 上下文太长，记忆衰减，前后矛盾。

BYOE 的解决方案不是让一个 AI 硬扛，而是**拆**。

---

## 2. 两种协作模式

```
多 AI 协作
├── Sub-agent（子智能体） → 任务委派，深挖细节
└── Swarm（群智协作）     → 流水线 + 并行专家组
```

### Sub-agent：委派模式

主 Agent 觉得某个子任务太复杂，会创建一个独立的子 Agent 去处理：

```
主 Agent: "实现一个 JWT 认证模块"
  └─→ Sub-agent: "调研 JWT 库选型"
  └─→ Sub-agent: "实现 auth.py 核心逻辑"
  └─→ Sub-agent: "编写 test_auth.py 测试"
      └─→ 子 Sub-agent: "mock 异步数据库连接"  ← 子 Agent 还可以递归
```

每个 Sub-agent 拥有**独立的上下文窗口**。主 Agent 只关心最终结果，不关心中间过程。

```
特点：
- 深度优先：一个任务可以递归拆到很细
- 隔离性：子任务的上下文不影响主任务
- 上限：最多 20 层工具调用链（防止无限递归）
```

### Swarm：流水线模式

Swarm 处理的是「多个不同角度」的任务：

**串行流水线（Serial Relay）：**

```
架构师 → 后端开发 → 前端开发 → 安全审查 → 测试
        ↓        ↓         ↓         ↓        ↓
    产出API设计  实现接口   实现页面   检查漏洞   验证通过
```

各角色顺序执行，上游产出是下游输入。

**并行专家组（Parallel Groups）：**

```
            ┌── 安全审查 ──┐
            ├── 性能分析 ──┤
代码提交 →  ├── 代码规范 ──┤ → 技术负责人汇总
            ├── 测试覆盖 ──┤
            └── 文档检查 ──┘
```

5 个专家同时审查，然后由技术负责人汇总。总耗时 ≈ 最慢的那个专家。

---

## 3. 实战：Swarm 代码审查

来看一个真实的 Swarm 应用。假设你提交了一个 PR：

```python
# api/user.py
@app.post("/users")
async def create_user(data: CreateUserReq):
    user = await User.create(data)
    return {"id": user.id}
```

用 `demos/01-api/06_swarm.py` 的方式，BYOE 自动拆解：

```
串行流水线模式：
  1. 架构师：检查表结构设计
  2. 后端专家：检查 API 路由和状态码
  3. 安全工程师：检查 SQL 注入和权限
  4. 技术负责人：汇总并生成报告

每个角色看到的只有自己专业领域的上下文。
```

最终产出：

```
📋 审查报告

🔴 严重 (1)
  - 缺少输入验证: email 字段未格式校验

🟡 建议 (3)
  - 建议添加 rate limiting
  - 建议添加事务回滚
  - 建议添加操作日志

✅ 合规 (5)
  - RESTful 命名规范 ✓
  - 异步处理 ✓
  - 错误处理 ✓
```

---

## 4. 实战：Sub-agent 复杂任务

用 `demos/04-apps/02_doc_pipeline.py` 的场景：

```python
# 用户只输入了一句话
"为这个项目生成完整的开发文档"

# 主 Agent 自动拆解：
# → Sub-agent 1: 扫描代码结构（读取所有文件）
# → Sub-agent 2: 分析 API 路由（grep 路由定义）
# → Sub-agent 3: 生成 README.md 大纲
# → Sub-agent 4: 生成 API 文档
# → 主 Agent: 汇总并写入文件
```

全程无人干预。

---

## 5. Sub-agent 的工作机制

```
flowchart TD
    A[用户输入] --> B[主 Agent 分析任务]
    B --> C{需要子任务?}
    C -->|否| D[直接执行]
    C -->|是| E[创建 Sub-agent]
    E --> F[分配独立上下文]
    F --> G[Sub-agent 独立执行]
    G --> H[返回结果给主 Agent]
    H --> B
```

关键设计：
- 每个 Sub-agent 从零开始，不受主对话上下文污染
- Sub-agent 也可以再创建 Sub-agent（递归，最多 20 层）
- 主 Agent 可以等待结果，也可以继续做其他事
- 超时机制：Sub-agent 超过时间限制自动终止

---

## 6. 适用场景建议

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| 代码审查 | Swarm 并行 | 多个专家各自独立审查 |
| 新功能开发 | Sub-agent 委派 | 拆解为独立模块并行实现 |
| 文档生成 | Swarm 串行 | 架构→API→使用说明 有顺序依赖 |
| Bug 修复 | Sub-agent | 独立环境排查，不影响主任务 |
| 架构重构 | Sub-agent + Swarm | 先拆模块（Sub-agent），再并行审查（Swarm） |

---

## 7. 要点总结

- Sub-agent：**深度优先**，任务委派给独立的子 Agent
- Swarm：**广度优先**，流水线 + 并行专家组
- 独立上下文：每个子任务有干净的环境
- 递归支持：Sub-agent 可以再创建 Sub-agent（最多 20 层）
- 适用场景：复杂项目、代码审查、文档生成、架构重构

## 下期预告

下一篇我们连接外部世界：**MCP + VS Code** —— 让 BYOE 的工具扩展到整个 MCP 生态。

---

📎 完整文档：[Swarm 指南](../../docs/02-user-guide/SWARM-GUIDE-ZH.md) · [Sub-agent 指南](../../docs/02-user-guide/SUBAGENT-GUIDE-ZH.md)
📎 示例代码：[06_swarm.py](../../demos/01-api/06_swarm.py) · [04_review_swarm.py](../../demos/04-apps/04_review_swarm.py)

# Crew 工作流：Plan → Run → Release

> 一句话摘要：BYOE 的 Crew 模式让 AI 从「单兵作战」升级为「有组织、有流程的工程团队」。

---

## 1. 场景引入

当你让 AI 做一个复杂任务时，最常见的问题是：

> 「AI 经常做一半跑偏」、「改了 A 忘了 B」、「上一个版本还能用，改了一下反而坏了」

这些问题不是因为 AI 不够聪明，而是缺少**工程化的工作流程**。

Crew 模式就是 BYOE 的答案：一个完整的 AI 项目管理和执行框架。

---

## 2. 什么是 Crew？

Crew 不是一个「多 Agent 聊天群」，而是一个**工作区结构**：

```
my-project/
├── crew.yaml             # 项目配置文件
└── crew/                 # Crew 工作区（自动生成）
    ├── resume.md         # 当前进展
    ├── blockers.md       # 阻塞项
    ├── changes/          # 变更计划（可并行多个）
    │   ├── feat-login/
    │   │   ├── proposal.md
    │   │   └── design.md
    │   └── fix-timeout/
    └── specs/            # 项目规范（可选）
```

---

## 3. PDEVI 五步工作流

Crew 的核心是 **PDEVI 流程**：

```
Plan（计划）→ Design（设计）→ Execute（执行）→ Verify（验证）→ Iterate（迭代）
```

### 第一步：初始化项目

```bash
cd my-project
byoe init
```

这会生成 `crew.yaml`：

```yaml
project:
  name: my-project
  description: ""

workflow:
  default_mode: standard   # standard | express | prototype
  concurrent_changes: true

verify:
  test_command: "pytest tests/ -q"

git:
  ignore_crew: true
```

### 第二步：创建变更计划

```bash
byoe plan feat-login
```

AI 会自动：
1. 分析现有代码库结构
2. 生成 `proposal.md`（变更提案）
3. 生成 `design.md`（技术设计）

> 插入 proposal.md 示例截图

### 第三步：执行

```bash
byoe run
```

AI 按照设计文档逐步执行：
- 读取现有代码
- 实现新功能
- 编写/更新测试
- 持续验证

### 第四步：查看状态

```bash
byoe status
```

显示当前变更的进度：
- ✅ 已完成：auth.py, models.py
- 🔄 进行中：tests/test_auth.py
- ⏳ 待开始：集成测试

### 第五步：发布

```bash
byoe release
```

- 运行最终验证
- 输出变更摘要
- 清理工作区

---

## 4. 三种工作模式

| 模式 | 适用场景 | 特点 |
|------|---------|------|
| **Express** | 快速原型、简单 bug 修复 | 跳过 Design 阶段，直接出代码 |
| **Standard** | 常规功能开发 | Plan → Design → Execute → Verify |
| **Prototype** | 探索性研究、复杂架构 | 深入 Design，多轮迭代 |

切换模式：

```bash
byoe plan feat-login --mode express
```

---

## 5. 并发变更

Crew 支持并行处理多个独立变更：

```bash
byoe plan feat-login        # 创建变更 1
byoe plan fix-timeout       # 创建变更 2
byoe status                 # 查看所有变更
byoe run --change feat-login  # 只执行变更 1
```

每个变更计划完全独立，互不干扰。

---

## 6. Web 界面中的 Crew

> 插入 Crew 面板截图

在 Web UI 的 Crew 面板中，你可以：
- 可视化所有变更计划
- 拖拽排序执行优先级
- 查看每个变更的详细 diff
- 一键接受/回滚变更

---

## 7. 领域专家（Specialists）

在 `crew.yaml` 中配置领域专家：

```yaml
specialists:
  - frontend-specialist
  - security-engineer
  - database-specialist
```

AI 会根据任务类型自动调用对应的专家角色。BYOE 内置 **30+ 个领域专家**（后端、前端、安全、数据库、DevOps、移动端等）。

---

## 8. 要点总结

- Crew = 带工作流的 AI 工程框架
- PDEVI 五步：Plan → Design → Execute → Verify → Iterate
- 三种模式：Express（快速）、Standard（标准）、Prototype（深度）
- 支持并发变更：多个独立 Plan 并行执行
- 30+ 内置领域专家可配置
- 建议小项目用 Express，大项目用 Standard

## 下期预告

下一篇我们介绍 BYOE 最独特的设计之一：**技能系统** —— 让 AI 记住过去的经验，不再每次从零开始。

---

📎 完整文档：[PDEVI 流程指南](../../docs/03-developer-guide/PDEVI-GUIDE-ZH.md)

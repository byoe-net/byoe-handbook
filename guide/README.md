# BYOE 入门到精通 · 公众号系列文章

> 14 篇精炼系列，覆盖 BYOE 从入门到生产落地。
> 每篇 2000-4000 字，周更 2 篇，同步发布至微信公众号「卜一智航」。

---

## 文章列表

| # | 标题 | 对应文档 | 示例代码 | 配图 | 状态 |
|---|------|---------|---------|------|------|
| 1 | BYOE 是什么：从 Copilot 到数字员工 | — | — | 架构图 | 📝 草稿 |
| 2 | BYOE 架构：Agent + LLM + Tools + Skills | 新增 | — | ★ 四层架构图 | 📝 草稿 |
| 3 | 5 分钟装好你的 AI 工程师 | [configuration.md](../docs/04-config/configuration.md) | [01_quickstart.py](../demos/01-api/01_quickstart.py) | 终端截图 | 📝 草稿 |
| 4 | CLI 聊天入门：一句话让 AI 改代码 | [USER-MANUAL §21](../docs/02-user-guide/USER-MANUAL-ZH.md) | — | CLI 动图 | 📝 草稿 |
| 5 | Web 界面：可视化 AI 工作台 | [USER-MANUAL §3](../docs/02-user-guide/USER-MANUAL-ZH.md) | — | Web 截图 | 📝 草稿 |
| 6 | Crew 工作流：Plan → Run → Release | [PDEVI 指南](../docs/03-developer-guide/PDEVI-GUIDE-ZH.md) | — | 流程图 | 📝 草稿 |
| 7 | 技能系统：给 AI 注入领域经验 | [SKILLS-GUIDE](../docs/02-user-guide/SKILLS-GUIDE-ZH.md) + [教程](../tutorials/SKILLS-TUTORIAL.md) | [02-skills/](../demos/02-skills/) | JSON/Python 截图 | 📝 草稿 |
| 8 | Python API 编程：把 AI 嵌入你的应用 | [API-QUICKSTART](../docs/03-developer-guide/API-QUICKSTART-ZH.md) | [01-api/](../demos/01-api/) | 代码块 | 📝 草稿 |
| 9 | 自定义工具：扩展 AI 的能力边界 | [API-REFERENCE §Tool](../docs/03-developer-guide/API-REFERENCE-ZH.md) | [03-tools/](../demos/03-tools/) | 类图 | 📝 草稿 |
| 10 | Swarm + Sub-agent：多 AI 协作 | [Swarm](../docs/02-user-guide/SWARM-GUIDE-ZH.md) + [Sub-agent](../docs/02-user-guide/SUBAGENT-GUIDE-ZH.md) | [06_swarm.py](../demos/01-api/06_swarm.py) | 流程图 | 📝 草稿 |
| 11 | MCP + VS Code：在编辑器里召唤 AI | [VSCODE-MCP 指南](../docs/03-developer-guide/VSCODE-MCP-GUIDE-ZH.md) | [10_mcp.py](../demos/01-api/10_mcp.py) | VS Code 截图 | 📝 草稿 |
| 12 | 循环工程：无人值守的 AI 运维 | [Loop 教程](../tutorials/LOOP-ENGINEERING-TUTORIAL.md) | [05-loops/](../demos/05-loops/) | 架构图 | 📝 草稿 |
| 13 | 记忆 + 钩子 + 多模态：进阶能力 | [API-REFERENCE](../docs/03-developer-guide/API-REFERENCE-ZH.md) | [05_memory.py](../demos/01-api/05_memory.py), [09_hooks.py](../demos/01-api/09_hooks.py) | 示意图 | 📝 草稿 |
| 14 | 从 Demo 到生产：最佳实践与 FAQ | [TROUBLESHOOTING](../docs/04-config/TROUBLESHOOTING-ZH.md) + [PLAYBOOK](../docs/04-config/PLAYBOOK-NONDEV-ZH.md) | — | 清单图 | 📝 草稿 |

---

## 写作模板

每篇文章正文格式：

```markdown
# 标题

> 一句话摘要

---

## 1. 场景引入

> 用一个真实痛点开头

## 2. 是什么

> 核心概念，1-2 段

## 3. 怎么做

> 操作步骤 + 代码/CLI 示例

## 4. 效果

> 执行结果截图 + 说明

## 5. 要点总结

- 要点 1
- 要点 2
- 要点 3

## 下期预告

> 引流到下一篇

---

📎 相关代码：[demos/...](...)
📖 完整文档：[docs/...](...)
```

## 配图清单

| 文章 | 需要配图 | 说明 |
|------|---------|------|
| 1 | BYOE 产品截图、与 Cursor/Devin 对比表 | 首篇要有视觉冲击 |
| 2 | ★ **四层架构图**（最重要） | Agent ↔ LLM ↔ Tools ↔ Skills |
| 3 | 终端安装过程截图 | 简单但必要 |
| 4 | CLI 聊天录屏 GIF | 动态效果最好 |
| 5 | Web UI 全屏截图 + 各个面板 | 多张 |
| 6 | Plan → Run → Release 流程图 | 工作流可视化 |
| 7 | Skills 目录截图 + JSON 示例 | 直观展示文件结构 |
| 8 | Python 代码块 | 纯代码 |
| 9 | Tool 类继承图 | 类关系 |
| 10 | Swarm 串行/并行流程图 | 关键配图 |
| 11 | VS Code MCP 配置截图 | 实操必配 |
| 12 | Loop 架构图 | 时间/事件/CI 三种模式 |
| 13 | 记忆层次图 | 三层存储 |
| 14 | 最佳实践清单 | 信息图 |

## 发布计划

- 每周 2 篇，预计 7 周完成
- 首篇配图最多，需要提前准备架构图 + 截图
- 每篇在 `articles/N-title/` 目录下完成草稿，配图放 `images/`
- 定稿后同步发布到微信公众号 + GitHub

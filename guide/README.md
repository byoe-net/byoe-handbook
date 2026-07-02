# BYOE 入门到精通 · 系列文章

> 本系列将 BYOE 的核心能力拆解为独立文章，适合按顺序阅读，每篇 5-10 分钟。
> 同步发布至微信公众号「卜一智航」，也可在 GitHub 在线阅读完整版。

---

## 文章列表

| # | 文章标题 | 对应文档 | 示例代码 | 状态 |
|---|---------|---------|---------|------|
| 1 | 什么是 BYOE — AI 编程助手还是数字员工？ | [快速入门](../docs/01-快速入门/) | — | 📝 草稿 |
| 2 | 5 分钟安装与配置 | [配置参考](../docs/04-配置与运维/configuration.md) | — | 📝 草稿 |
| 3 | 30 分钟快速上手：第一个 AI 项目 | [快速上手](../docs/01-快速入门/STARTER-GUIDE-ZH.md) | [01-quickstart.py](../demos/01-api/01_quickstart.py) | 📝 草稿 |
| 4 | CLI 命令行模式：终端党的首选 | [用户手册 §21](../docs/02-用户指南/USER-MANUAL-ZH.md) | — | 📝 草稿 |
| 5 | Web 界面全览：可视化 AI 工作台 | [用户手册 §3](../docs/02-用户指南/USER-MANUAL-ZH.md) | — | 📝 草稿 |
| 6 | Crew 工作区：让 AI 团队协作 | [用户手册 §7](../docs/02-用户指南/USER-MANUAL-ZH.md) | — | 📝 草稿 |
| 7 | 技能系统：给 AI 注入专属经验 | [技能指南](../docs/02-用户指南/SKILLS-GUIDE-ZH.md) | [skills/](../demos/02-skills/) | 📝 草稿 |
| 8 | Swarm 群智协作：多 Agent 并行工作 | [Swarm 指南](../docs/02-用户指南/SWARM-GUIDE-ZH.md) | [01-api/06_swarm.py](../demos/01-api/06_swarm.py) | 📝 草稿 |
| 9 | Sub-agent 子智能体：任务委派的艺术 | [Sub-agent 指南](../docs/02-用户指南/SUBAGENT-GUIDE-ZH.md) | — | 📝 草稿 |
| 10 | 定时任务：让 AI 7×24 自动值守 | [用户手册 §11](../docs/02-用户指南/USER-MANUAL-ZH.md) | [05-loops/](../demos/05-loops/) | 📝 草稿 |
| 11 | Python API 编程：把 AI 嵌入你的应用 | [API 快速入门](../docs/03-开发指南/API-QUICKSTART-ZH.md) | [01-api/](../demos/01-api/) | 📝 草稿 |
| 12 | 自定义工具：扩展 AI 的能力边界 | [API 参考 §Tool](../docs/03-开发指南/API-REFERENCE-ZH.md) | [03-tools/](../demos/03-tools/) | 📝 草稿 |
| 13 | MCP 生态集成：连接一切工具 | [VS Code MCP 指南](../docs/03-开发指南/VSCODE-MCP-GUIDE-ZH.md) | [01-api/10_mcp.py](../demos/01-api/10_mcp.py) | 📝 草稿 |
| 14 | 多模态图片输入：AI 也能"看懂"图片 | [API 参考 §多模态](../docs/03-开发指南/API-REFERENCE-ZH.md) | [01-api/11_multimodal.py](../demos/01-api/11_multimodal.py) | 📝 草稿 |
| 15 | 记忆管理：让 AI 记住每件事 | [用户手册 §15](../docs/02-用户指南/USER-MANUAL-ZH.md) | [01-api/05_memory.py](../demos/01-api/05_memory.py) | 📝 草稿 |
| 16 | 事件钩子系统：可观测的 AI | [API 参考 §Hooks](../docs/03-开发指南/API-REFERENCE-ZH.md) | [01-api/09_hooks.py](../demos/01-api/09_hooks.py) | 📝 草稿 |
| 17 | Loop 循环工程：无人值守的 AI 运维 | [教程](../tutorials/LOOP-ENGINEERING-TUTORIAL.md) | [05-loops/](../demos/05-loops/) | 📝 草稿 |
| 18 | SOBER 代码审查：AI 写的代码谁把关？ | [SOBER 指南](../docs/02-用户指南/SOBER-GUIDE-ZH.md) | — | 📝 草稿 |
| 19 | 非研发场景落地：HR、财务、营销也能用 | [非研发手册](../docs/04-配置与运维/PLAYBOOK-NONDEV-ZH.md) | [06-other/](../demos/06-other/) | 📝 草稿 |
| 20 | VS Code + MCP：在编辑器中调用 AI | [VS Code MCP 指南](../docs/03-开发指南/VSCODE-MCP-GUIDE-ZH.md) | — | 📝 草稿 |
| 21 | 常见问题与排查 | [故障排查](../docs/04-配置与运维/TROUBLESHOOTING-ZH.md) | — | 📝 草稿 |

---

## 写作约定

每篇文章建议包含：

1. **场景引入** — 用实际问题引出本节内容
2. **核心概念** — 1-2 句话说清楚是什么
3. **操作步骤** — 可复现的 CLI/代码示例
4. **执行结果** — 截图或文字输出
5. **要点总结** — 3-5 条 takeaways
6. **下期预告** — 引流到下一篇

## 发布计划

- 每周 2-3 篇，从第 1 篇开始依次发布
- 每篇文章控制在 2000-3000 字
- 代码示例以 GitHub 链接形式嵌入

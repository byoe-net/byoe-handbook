<p align="center">
  <img src="https://byoe.net/favicon.svg" width="80" alt="BYOE">
</p>

<h1 align="center">BYOE · 卜一智航 Handbook</h1>

<p align="center">
  <em>Documentation, examples & tutorials for the BYOE AI Agent framework</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/byoe/"><img src="https://badge.fury.io/py/byoe.svg" alt="PyPI version"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
</p>

<p align="center">
  <a href="#english">English</a> ·
  <a href="#chinese">中文</a>
</p>

---

<h2 id="english">English</h2>

**BYOE** (Bring Your Own Executive AI) is a lightweight AI coding Agent with Crew orchestration. It turns any LLM into a full-stack developer teammate that reads/writes files, runs commands, plans projects, and collaborates in multi-agent swarms.

This repository is the **official handbook** — documentation, runnable demos, tutorials, and article series.

### Quick Start

```bash
pip install byoe
```

```python
import byoe
agent = byoe.create_agent()
print(agent.chat("Hello!"))
```

### Features & Capabilities

| Capability | How BYOE implements it |
|------------|----------------------|
| **Agent loop** | Tool-calling loop with sync / stream / async modes |
| **23 built-in tools** | Bash, file I/O, grep, git, web search, Python REPL, image reader, memory, skills, and more |
| **Model fallback chain** | Same-provider & cross-provider cascading fallback |
| **Context compression** | 3-tier: Snip (50%) → Summarize (70%) → Collapse (90%) |
| **Structured output** | `response_model=` param, auto JSON Schema + Pydantic validation |
| **Memory (LightMemory)** | SQLite + local embedding, zero external deps, auto GC |
| **Multi-agent (Swarm)** | Serial pipeline (roles) + parallel groups |
| **MCP bidirectional** | Both MCP Server (expose tools) and MCP Client (consume tools) |
| **Multimodal** | `read_image` tool + `agent.chat(images=[...])` |
| **Hooks / Observability** | `@on("llm.response")`, `@on("tool.call")`, `@on("agent.turn")` |
| **Skills plugin system** | Hot-load Python modules with `run(**kwargs) -> str` |
| **Scheduled tasks** | AgentScheduler: CRON + heartbeat + retry |
| **Project context** | Auto-injects `INSTRUCTIONS.md` + `crew.yaml` into system prompt |
| **Crew orchestration** | PDEVI flow (Plan→Design→Execute→Verify→Iterate) with 6 built-in roles |
| **Code quality scanning** | `byoe sober`: dead code, security, architecture violation detection |

### Use Case Guide

| Scenario | Recommended approach |
|----------|--------------------|
| Full-featured AI coding assistant + team orchestration | **BYOE** — only product with Agent + Crew + Web UI + Python API in one |
| Pure terminal coding agent | OpenCode / Claude Code — simpler, single binary |
| IDE-native development | Cline / Continue — VSCode extension |
| Complex multi-agent applications | CrewAI / LangGraph — graph-based orchestration |
| Embedding AI Agent into Python apps | BYOE / Pydantic AI — BYOE's 23 tools give it an edge |
| Quick MVP validation | **BYOE** — pip install and go, zero external deps |
| Production-grade agent framework | OpenAI Agents SDK / LangGraph — mature enterprise ecosystem |
| On-premise / air-gapped deployment | **BYOE + Ollama** — zero external deps, any OpenAI-compatible endpoint |

### One-Sentence Positioning

| Audience | Message |
|----------|---------|
| **Developers** | "`pip install byoe` — you get an AI dev team, not just a chat window." |
| **Enterprise / Fintech CIO** | "Fully on-prem, zero data egress. More compliance-friendly than Claude Code or CrewAI." |
| **Legal firms** | "Contract review on autopilot — BYOE Skills handle first-pass compliance 24/7." |
| **Marketing directors** | "One person + BYOE = content factory: audience analysis → copy → compliance, fully automated." |
| **Educators** | "BYOE + DeepSeek = zero-cost AI teaching assistant. Code grading, lab guidance, lit reviews." |
| **SMB owners** | "No need to hire AI engineers — pip install an AI employee that writes docs, reviews contracts, generates daily reports." |

### Repository Structure

```
byoe-handbook/
├── docs/         # Full reference documentation (in Chinese)
├── demos/        # Runnable examples by category
│   ├── 01-api/   # Python API basics (12 demos)
│   ├── 02-skills/ # Skill examples (JSON + Python)
│   ├── 03-tools/ # Custom Tool examples
│   ├── 04-apps/  # Full application templates (6 apps)
│   ├── 05-loops/ # Loop engineering bots (4 bots)
│   └── 06-other/ # Cross-industry scenarios
├── tutorials/    # In-depth tutorials
├── guide/        # WeChat article series plan
└── wheel/        # Pre-built wheel (pip install from local)
```

### Documentation

| Section | Description |
|---------|-------------|
| [Quick Start](docs/01-quickstart/) | Get started in 30 minutes (Chinese) |
| [User Guide](docs/02-user-guide/) | Full manual, Skills, Swarm, Sub-agent, SOBER |
| [Developer Guide](docs/03-developer-guide/) | API reference, PDEVI workflow, MCP |
| [Configuration](docs/04-config/) | Environment variables, troubleshooting |
| [Demos](demos/) | Runnable Python scripts |
| [Tutorials](tutorials/) | Skill dev, Loop engineering, cross-industry |

### Install from Local Wheel

```bash
pip install wheel/byoe-1.0.0-py3-none-any.whl
```

### License

[MIT](LICENSE) © byoe.net

---

<h2 id="chinese">简体中文</h2>

**BYOE（卜一智航，Bring Your Own Executive AI）** —— 一款轻量级 AI 编程 Agent + Crew 编排工具。让任何 LLM 变身全栈开发队友：读写文件、执行命令、规划项目、多 Agent 群智协作。

本仓库是 **官方开发者手册**，包含完整中文文档、可运行示例、教程和公众号系列文章。

### 快速开始

```bash
pip install byoe                    # 从 PyPI 安装
pip install wheel/byoe-1.0.0-py3-none-any.whl  # 或从本地安装
```

```python
import byoe
agent = byoe.create_agent()         # 自动读取环境变量
print(agent.chat("你好！"))
```

### 功能矩阵

| 能力 | 实现方式 |
|------|---------|
| **Agent 循环** | 工具调用循环，支持 sync / stream / async |
| **23 个内置工具** | Bash、文件读写、grep、git、Web 搜索、Python REPL、图片识别、记忆、技能等 |
| **模型降级链** | 同 Provider 与跨 Provider 双重 fallback |
| **上下文压缩** | 三级策略：Snip（50%）→ Summarize（70%）→ Collapse（90%） |
| **结构化输出** | `response_model=` 参数，自动 JSON Schema + Pydantic 校验 |
| **记忆系统** | LightMemory：SQLite + 本地 Embedding，零外部依赖，自动 GC |
| **多 Agent（Swarm）** | 串行流水线（roles）+ 并行分组（parallel_groups） |
| **MCP 双向集成** | 既是 MCP Server（暴露工具）也是 MCP Client（消费工具） |
| **多模态输入** | `read_image` 工具 + `agent.chat(images=[...])` |
| **Hooks 可观测性** | `@on("llm.response")` / `@on("tool.call")` / `@on("agent.turn")` |
| **Skills 插件系统** | 动态加载 Python 模块 `run(**kwargs) -> str` |
| **定时调度** | AgentScheduler：CRON 触发 + 心跳监控 + 重试策略 |
| **项目上下文** | 自动注入 `INSTRUCTIONS.md` + `crew.yaml` 到 System Prompt |
| **Crew 编排** | PDEVI 流程（Plan→Design→Execute→Verify→Iterate），6 角色内建 |
| **代码质量扫描** | `byoe sober`：死代码、安全漏洞、架构违规检测 |

### 场景推荐

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 全功能 AI 编程助手 + 团队协作 | **BYOE** | 唯一同时提供 Agent + Crew + Web UI + Python API 的产品 |
| 终端里写代码的 AI | OpenCode / Claude Code | 更纯粹，单二进制，零配置 |
| VS Code 原生开发 | Cline / Continue | IDE 深度集成 |
| 构建复杂多 Agent 应用 | CrewAI / LangGraph | 图编排更灵活 |
| Python 项目嵌入 AI Agent | BYOE / Pydantic AI | BYOE 内置 23 个工具有天然优势 |
| MVP 快速验证 | **BYOE** | pip install 即用，零外部依赖 |
| 生产级 Agent 框架 | OpenAI Agents SDK / LangGraph | 企业生态更成熟 |
| 本地私有化部署 | **BYOE + Ollama** | 零外部依赖，支持任意 OpenAI 兼容端点 |

### 一句话定位

| 受众 | 一句话 |
|------|--------|
| **开发者** | "`pip install byoe`，你得到一个 AI 研发团队，而不只是一个聊天窗口。" |
| **金融 CIO** | "全本地化部署 + 零数据出境，比 Claude Code/CrewAI 更适合你的合规要求。" |
| **律所主任** | "合同审查不再等待——BYOE Skills 让 AI 24 小时处理第一轮合规筛查。" |
| **营销总监** | "一个人 + BYOE = 内容工厂：受众分析 → 多平台文案 → 合规审查，全自动。" |
| **大学老师** | "BYOE + DeepSeek = 零成本的 AI 助教，支持代码评分、实验指导、文献综述。" |
| **中小企业主** | "不用招 AI 工程师，pip install 就有的 AI 员工——会写文档、能审合同、能做日报。" |

### 目录结构

```
byoe-handbook/
├── docs/            # 完整参考文档（按主题分章）
├── demos/           # 示例代码（按类别分组）
│   ├── 01-api/      # Python API 基础示例（12个）
│   ├── 02-skills/   # 技能示例（JSON认知型 + Python动作型）
│   ├── 03-tools/    # 自定义 Tool 示例
│   ├── 04-apps/     # 完整应用模板（6个）
│   ├── 05-loops/    # 循环工程示例（4个）
│   └── 06-other/    # 其他场景（营销、GitHub Actions）
├── tutorials/       # 完整教程（技能开发、循环工程等）
├── guide/           # 公众号系列文章计划
└── wheel/           # BYOE 发行版安装包
```

### 文档导航

| 章节 | 说明 |
|------|------|
| [01-快速入门](docs/01-quickstart/) | 30 分钟上手 BYOE |
| [02-用户指南](docs/02-user-guide/) | 用户手册、技能、Swarm、Sub-agent、SOBER |
| [03-开发指南](docs/03-developer-guide/) | API 参考、PDEVI 流程、VS Code MCP 集成 |
| [04-配置与运维](docs/04-config/) | 环境变量、故障排查、非研发场景 |
| [示例代码](demos/) | 可直接运行的 Python 脚本 |
| [系列文章](guide/) | 公众号发布计划与文章草稿 |

### 许可证

[MIT](LICENSE) © byoe.net

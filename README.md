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
| [Quick Start](docs/01-快速入门/) | Get started in 30 minutes (Chinese) |
| [User Guide](docs/02-用户指南/) | Full manual, Skills, Swarm, Sub-agent, SOBER |
| [Developer Guide](docs/03-开发指南/) | API reference, PDEVI workflow, MCP |
| [Configuration](docs/04-配置与运维/) | Environment variables, troubleshooting |
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
| [01-快速入门](docs/01-快速入门/) | 30 分钟上手 BYOE |
| [02-用户指南](docs/02-用户指南/) | 用户手册、技能、Swarm、Sub-agent、SOBER |
| [03-开发指南](docs/03-开发指南/) | API 参考、PDEVI 流程、VS Code MCP 集成 |
| [04-配置与运维](docs/04-配置与运维/) | 环境变量、故障排查、非研发场景 |
| [示例代码](demos/) | 可直接运行的 Python 脚本 |
| [系列文章](guide/) | 公众号发布计划与文章草稿 |

### 许可证

[MIT](LICENSE) © byoe.net

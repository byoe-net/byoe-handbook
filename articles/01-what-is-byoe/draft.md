# BYOE 是什么：从 Copilot 到数字员工

> 一句话摘要：BYOE 不是又一个 AI 编码助手，它是一套可以让 AI 完整接管软件工程任务的轻量级 Agent 框架。

---

## 1. 场景引入

### 一个典型的工作日

早上 10 点，产品经理甩过来一个需求：「给用户模块加上 JWT 认证，支持 refresh token，下午 3 点上线。」

如果你在用 Cursor 或 Copilot，你的工作流大概是：
1. 手动分析需求，想好技术方案
2. 在编辑器里逐文件敲代码（或让 AI 补全）
3. 手动打开终端运行测试
4. 发现报错，切回编辑器修 bug
5. 循环 3-4 次直到跑通
6. 手动 commit → push → 部署

每一步都需要你在场。

### 如果换一种方式

如果有一个 AI，它能：
- **自己读代码库**，理解现有架构
- **自己写代码、改文件、跑命令**
- 做错了**自己看日志修 bug**
- 做完了**自己 commit 并通知你**

你只需要说一句：「给用户模块加上 JWT 认证，支持 refresh token。」

这就是 BYOE。

---

## 2. 是什么

**BYOE（Bring Your Own Executive AI）** 是一个轻量级的 AI Agent 框架。它不只是一个「聊天机器人」，而是一个**能完整执行软件工程任务**的 AI 工程师。

### 和同类工具的对比

BYOE 不是又一个 Copilot 替代品。它走的是一条不同的路。我们把它放在两类产品中看：

#### 对比 Coding Agent（编程助手类）

| 能力 | BYOE | OpenCode | Claude Code | Aider | Cline |
|------|:----:|:--------:|:-----------:|:-----:|:-----:|
| 代码补全 | — | — | — | — | ✅ (VSCode) |
| 多文件编辑 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 执行终端命令 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 自主读代码库 | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Crew 编排** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Python 可编程 API** | ✅ | ❌ Go 二进制 | ❌ 闭源 CLI | ✅ 部分 | ❌ TS 扩展 |
| **Swarm 多 Agent** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **MCP Server**（对外暴露） | ✅ | ❌ | ❌ | ❌ | ❌ |
| **MCP Client**（接入外部） | ✅ | ❌ | ❌ | ❌ | ✅ |
| **定时调度** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **上下文压缩** | ✅ 三级策略 | ❌ | ❌ | ❌ | ❌ |
| **结构化输出** | ✅ Pydantic | ❌ | ❌ | ❌ | ❌ |
| **记忆系统** | ✅ LightMemory | ❌ | ❌ | ❌ | ✅ |
| **Hooks 可观测性** | ✅ 事件系统 | ❌ | ❌ | ❌ | ❌ |
| **Web UI** | ✅ React Helm | ❌ | ❌ | ❌ | ✅ (VSCode 内) |
| **本地/私有化** | ✅ pip install | ✅ 单二进制 | ❌ 闭源 | ✅ | ✅ |
| **工具数量** | **23** | ~8 | ~10 | ~6 | ~12 |

#### 对比 Agent 框架（编排类）

| 能力 | BYOE | CrewAI | LangGraph | OpenAI SDK | Pydantic AI |
|------|:----:|:------:|:---------:|:----------:|:-----------:|
| **内置编码工具** | ✅ 23 个 | ❌ | ❌ | ❌ | ❌ |
| **开箱即用** | ✅ pip install 即可聊天 | ❌ 需搭建管道 | ❌ 需定义图 | ❌ 需写代码 | ❌ 需写代码 |
| **项目上下文自动注入** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **代码质量检测** | ✅ `byoe sober` | ❌ | ❌ | ❌ | ❌ |
| **CLI 完整工作流** | ✅ plan/status/release | ❌ | ❌ | ❌ | ❌ |
| **Skills 热加载** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **包体积** | ~340 KB .whl | ~5 MB+ | ~10 MB+ | ~500 KB | ~1 MB |

BYOE 的核心差异在于：
- **轻量**：`pip install byoe` 就装好了，340 KB .whl + 3 个基础依赖，却集成了 23 个工具 + Swarm + MCP + Web UI + Crew 编排
- **可编程**：Python API 可以嵌入你自己的应用
- **可扩展**：Tools、Skills、MCP 三层扩展机制
- **唯一全栈**：同时提供 Agent + Crew + Web UI + Python API 的产品

---

## 3. 怎么做

先不写代码，先感受一下：

```bash
# 安装
pip install byoe

# 设置 API Key（以 DeepSeek 为例）
export OPENAI_API_KEY=sk-xxx
export OPENAI_BASE_URL=https://api.deepseek.com
export BYOE_MODEL=deepseek-chat

# 启动 Web 界面
byoe web
```

浏览器打开 `http://localhost:7860`，你就看到了 BYOE 的 Web 工作台。

---

## 4. 效果

> 插入 Web UI 截图

左上角是对话面板，右侧是文件变更追踪，底部的状态栏可以打开技能、任务、日志等面板。

---

## 5. 要点总结

- BYOE 是一个**轻量级 AI Agent 框架**，不是又一个 Copilot 替代品
- 核心差异：自主执行、多 Agent 协作、`pip install` 即用、私有化部署
- 适合场景：代码生成、项目重构、CI/CD 自动化、定时任务
- 不适合场景：需要图形化 IDE 深度集成的工作流（用 Cursor 更合适）

## 下期预告

下一期我们深入 BYOE 的**四层架构**：Agent 如何调用 LLM？Tools 和 Skills 有什么区别？为什么说它比 LangChain 更轻？

---

📎 完整文档：[快速入门](../../docs/01-quickstart/STARTER-GUIDE-ZH.md)

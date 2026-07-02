# 卜一智航（BYOE）用户手册

> 版本：v0.8.1 · 更新日期：2026-07-01

---

## 阅读导航（新手必看）

- 30 分钟快速上手：`STARTER-GUIDE-ZH.md`
- **Python 库 API 新手教程**：`API-QUICKSTART-ZH.md`（新增）
- **Python 库 API 完整参考**：`API-REFERENCE-ZH.md`（新增）
- 非研发场景落地：`PLAYBOOK-NONDEV-ZH.md`
- 故障排查手册：`TROUBLESHOOTING-ZH.md`
- 技能系统详解：`SKILLS-GUIDE-ZH.md`
- 群智协作详解：`SWARM-GUIDE-ZH.md`

建议阅读顺序：快速上手 -> 本手册功能全览 -> 场景手册与专项指南。

---

## 目录

1. [产品简介](#1-产品简介)
2. [快速开始](#2-快速开始)
3. [界面总览](#3-界面总览)
4. [对话功能](#4-对话功能)
5. [专家智能体](#5-专家智能体)
6. [技能（Skill）系统](#6-技能-skill-系统)
7. [Crew 工作区](#7-crew-工作区)
8. [文件操作](#8-文件操作)
9. [会话管理](#9-会话管理)
10. [Cosmos 可视化模式](#10-cosmos-可视化模式)
11. [定时任务](#11-定时任务)
12. [Swarm 群智协作流](#12-swarm-群智协作流)
13. [Sub-agent 子智能体](#13-sub-agent-子智能体)
14. [使用统计](#14-使用统计)
15. [记忆管理（byoe memory）](#15-记忆管理-byoe-memory)
16. [版本与诊断](#16-版本与诊断)
17. [Python 库 API](#17-python-库-api)
18. [MCP 生态集成](#18-mcp-生态集成)
19. [多模态图片输入](#19-多模态图片输入)
20. [设置说明](#20-设置说明)
21. [命令行模式（byoe chat）](#21-命令行模式-byoe-chat)
22. [安全与隐私](#22-安全与隐私)
23. [非软件研发跨界应用](#23-非软件研发跨界应用)
24. [常见问题](#24-常见问题)
25. [版本历史](#25-版本历史)

---

## 1. 产品简介

**卜一智航（BYOE，Build Your Own Engineer）** 是一款将 AI 大语言模型变为完整编程工程师的工具。

### 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 **多模型支持** | OpenAI、DeepSeek、智谱、Ollama 本地模型、自定义 OpenAI 兼容接口 |
| 🛠️ **工具调用** | 读写文件、执行 Bash 命令、搜索代码、Git 操作、网页抓取（23 个内置工具）|
| 🧠 **上下文压缩** | 三层自动压缩（裁剪 → 摘要 → 折叠），支持超长会话 |
| 👨‍💼 **专家智能体** | 29 位领域专家（后端架构师、安全工程师、游戏设计师等） |
| ✦ **技能系统** | 可创建、保存、激活自定义指令集（Skill） |
| 📋 **Crew 工作区** | PDEVI 工作流（Plan→Design→Execute→Verify→Iterate） |
| 🌐 **Web UI + CLI** | 浏览器界面（`byoe web`）+ 终端交互（`byoe chat`） |
| 🎤 **语音输入** | 浏览器原生 Web Speech API，支持中/英文 |
| ♻️ **会话持久化** | 自动保存、跨设备会话恢复 |
| 🔌 **MCP 生态** | 连接任意 MCP 服务器（客户端）；自身也可作为 MCP 服务端供 VS Code/Claude 调用 |
| 🖼️ **多模态图片** | `read_image` 工具 + `chat(images=[...])` 支持视觉分析 |

---

## 2. 快速开始

### 安装

```bash
pip install byoe
```

### 启动 Web UI

```bash
# 使用环境变量配置 API Key
export OPENAI_API_KEY=sk-...   # 或 DEEPSEEK_API_KEY / BYOE_API_KEY

# 启动 Web 界面（自动打开浏览器）
byoe web

# 可选参数
byoe web --port 8080           # 自定义端口
byoe web --model gpt-4o        # 指定模型
byoe web --no-browser          # 不自动打开浏览器
```

启动后终端会显示类似：

```
============================================================
  BYOE Web UI  —  v0.6.1
  Model : gpt-4o
  CWD   : /your/project
============================================================

  URL:  http://127.0.0.1:7860/?token=abc123xyz

  Ctrl+C to stop
```

复制 URL 到浏览器即可使用。Token 作为鉴权凭据，每次启动随机生成。

### 直接聊天（CLI）

```bash
byoe chat                      # 交互式终端对话
byoe chat "帮我列出所有 .py 文件"  # 单次提问
```

---

## 3. 界面总览

```
┌─────────────────────────────────────────────────────────┐
│  状态栏：模型 | 工作目录 | 智能体 | Token 用量 | 操作按钮  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                    对话区（ChatPanel）                    │
│              欢迎屏 / 消息气泡 / 工具调用块               │
│                                                         │
├─────────────────────────────────────────────────────────┤
│   📎 上传  🎤 语音  [输入框 ···]           [发送/停止]    │
└─────────────────────────────────────────────────────────┘
```

### 状态栏按钮说明

| 按钮 | 功能 |
|------|------|
| 模型名称徽章 | 当前使用模型 |
| 📁 目录 | 点击切换工作目录（仅 BYOE 模式） |
| ✦（新对话） | 开启新会话，清空当前对话 |
| History | 历史会话面板 |
| Logs | 系统日志面板 |
| Agent | 选择专家智能体 |
| Crew | Crew 工作区面板 |
| Skills | 技能管理面板 |
| Settings | 设置 |
| 🌙/☀️/⚙ | 切换深色/浅色/系统主题 |
| EN/中文 | 切换界面语言 |

---

## 4. 对话功能

### 发送消息

- 在输入框输入内容，按 **Enter** 发送
- 按 **Shift+Enter** 换行
- 按 **Ctrl+K**（Mac: ⌘K）快速开启新对话

### 欢迎屏示例提示

首次进入时显示 5 个可点击的示例提示，点击即发送：

- 帮我写一个带 JWT 的 Flask 登录接口
- 列出当前目录所有 .py 文件
- 创建一个 React Todo 组件
- 运行测试并修复报错
- 解释一下这个代码库的功能

### 消息气泡操作

| 操作 | 说明 |
|------|------|
| 悬停消息 | 显示时间戳和操作按钮 |
| ⎘（复制按钮） | 复制整条 AI 回复到剪贴板 |
| ↺（重新生成） | 删除当前回复，重新用同一问题生成 |
| 代码块右上角 Copy | 复制代码块内容 |

### 工具调用展示

AI 执行工具时，每个调用以折叠块显示：

```
✓ bash           echo "hello"                   0.3s
✗ read_file      /nonexistent.py               Error
  ↳ FileNotFoundError: ...
```

- 绿色 ✓ = 成功
- 红色 ✗ = 失败（自动展开显示错误详情）
- 点击可展开/折叠完整结果

### 语音输入

点击输入框左侧 🎤 按钮：

- 说话，识别结果自动追加到输入框
- 按钮变红闪烁表示正在录音
- 再次点击停止录音
- 支持中文（zh-CN）和英文（en-US），随界面语言自动切换
- 需要浏览器支持（Chrome/Edge/Safari）

### 文件上传

点击 📎（ImportButton）按钮上传文件：
- 支持文本和二进制文件
- 文件写入工作目录，AI 可直接读取

### Markdown 渲染

AI 回复支持完整 Markdown：
- 代码高亮（支持 JS/TS/Python/Bash/JSON/HTML/CSS）
- 表格、列表、标题
- 内联公式（通过 KaTeX）

---

## 5. 专家智能体

> 仅在 **BYOE Provider** 模式下可用。

点击状态栏 **Agent** 按钮打开智能体选择器。

### 什么是专家智能体

专家智能体 = **默认系统提示词 + 领域专家指令**。切换专家后，AI 在回答时会遵循该领域的最佳实践、输出格式和阶段职责。

### 可用专家（共 29 位）

#### 🎮 游戏开发（8）
| 专家 | 擅长 |
|------|------|
| 游戏设计师 | GDD、游戏循环、经济平衡 |
| 关卡设计师 | 关卡节奏、难度曲线 |
| 叙事设计师 | 剧情架构、对话系统 |
| 技术美术 | Shader、性能美术、管线 |
| 游戏音频工程师 | Wwise/FMOD、空间音效 |
| Unity 专家 | DOTS/ECS、URP/HDRP |
| Godot 专家 | GDScript/C#、Scene 树 |
| Unreal 专家 | Blueprint/C++、Nanite/Lumen |

#### 🎨 UI/UX（3）
| 专家 | 擅长 |
|------|------|
| UI 设计师 | 设计系统、组件库 |
| UX 架构师 | 信息架构、流程设计 |
| UX 研究员 | 用户访谈、可用性测试 |

#### 🔧 工程（8）
| 专家 | 擅长 |
|------|------|
| 后端架构师 | 系统设计、API、数据库 |
| 前端专家 | React/Vue、性能优化 |
| 移动开发者 | iOS/Android、跨平台 |
| DevOps 工程师 | CI/CD、容器化、云部署 |
| SRE | 可观测性、故障响应 |
| 数据工程师 | 数据管道、ETL |
| 数据库专家 | 索引、查询优化、分库分表 |
| 性能工程师 | 分析、基准测试、调优 |

#### 🔐 安全（2）
| 专家 | 擅长 |
|------|------|
| 安全工程师 | 渗透测试、漏洞分析、OWASP |
| Solidity 工程师 | 智能合约、DeFi 安全 |

#### 其他（8）
无障碍审计师、AI 工程师、API 测试师、嵌入式工程师、事故响应指挥、技术作家、XR 开发者、visionOS 工程师

### 切换专家

1. 点击状态栏 **Agent**
2. 选择专家，点击激活
3. 当前对话会被清空（切换会重置上下文）
4. 状态栏模型徽章旁出现专家名称标识

### 恢复通用助手

在智能体选择器中点击 **通用助手（Default Agent）** 即可恢复。

---

## 6. 技能（Skill）系统

技能是一段**可复用的自定义指令**，激活后注入 AI 的系统提示词中。

### 创建技能

1. 点击状态栏 **Skills**
2. 填写技能名称、描述、指令内容
3. 可选：设置触发短语（在聊天中输入该短语自动激活）
4. 点击保存

示例技能：
```
名称：code-review-strict
描述：严格代码审查模式
指令：
你现在是一位严格的代码审查员。对所有代码：
1. 指出潜在的 bug 和安全问题
2. 检查命名规范和代码风格
3. 评估时间/空间复杂度
4. 提出具体改进建议
不要放过任何问题，哪怕是小问题。
```

### 激活技能

方法一：在 Skills 面板点击激活  
方法二：聊天中输入 `/skill <名称>`

激活后，状态栏会显示 `✓ skill-name` 紫色徽章。

### 管理技能

```
/skill list          # 列出所有技能
/skill <name>        # 激活指定技能
/skill off           # 关闭当前技能
```

技能存储于服务端 `~/.byoe/skills/<name>.json`，最多 50 个（自动清理最旧的）。

### 编写与分享自定义 Python 技能 (进阶)

BYOE 的架构允许开发者使用 Python 编写强大的自定义技能。只要在特定位置放入 `skill_name.json` 或者 `skill_name.py` 即可被自动发现。

详见：[Skills 开发者指南](./SKILLS-GUIDE-ZH.md) 和 `c:\vibe\skills-demo` 的参考范例。

---

## 7. Crew 工作区

Crew 是 BYOE 的**结构化项目管理系统**，基于 PDEVI 工作流。

### PDEVI 工作流

```
Plan → Design → Execute → Verify → Iterate
计划    设计      执行       验证      迭代
```

### 初始化工作区

在项目根目录执行：

```bash
byoe init
```

或在 Web UI 的 Crew 面板点击 **初始化工作区**。

初始化后生成：
```
your-project/
├── INSTRUCTIONS.md     # 项目规范（自动注入 AI 上下文）
├── crew.yaml           # 项目配置
└── crew/
    ├── resume.md       # 当前进展摘要
    ├── blockers.md     # 待解决问题
    └── changes/        # 活跃变更
```

### 创建变更计划

```bash
byoe plan "login-feature"         # 标准模式
byoe plan "hotfix" --express      # 快速模式（跳过 Design）
byoe plan "poc" --prototype       # 原型模式（宽松约束）
```

或在 Crew 面板输入变更名称，选择模式后点击创建。

### 工作流阶段

**Plan（计划）阶段**
- AI 生成 `crew/changes/<name>/proposal.md`
- 包含：目标、范围、验收标准、风险
- 需要人工确认（点击 ✓ 确认计划）后才能进入下一阶段

**Design（设计）阶段**
- AI 创建 `crew/changes/<name>/design.md`
- 包含：技术决策、受影响文件、实现步骤

**Execute（执行）阶段**
- AI 按 design.md 的任务清单逐步实现
- 可在 Crew 面板点击 🤖 **让 AI 执行** 自动发送执行提示

**Verify（验证）阶段**
- 运行测试，确认实现符合验收标准
- 点击 ✓ 标记完成后可归档

### Crew 面板操作

| 操作 | 说明 |
|------|------|
| 🤖 让 AI 执行 | 自动构建阶段提示词，发送给 AI |
| ✓ 确认计划 | 设置 plan_confirmed: true |
| ✓ 标记完成 | 设置 verify_confirmed: true |
| 归档 | 移动到 crew/archive/ |
| 删除 | 永久删除变更目录 |
| 查看 | 查看 proposal.md 和 design.md |

---

## 8. 文件操作

### 切换工作目录

在状态栏点击 **📁 目录名**，输入新目录路径。

切换目录会：
- 重置 Bash 沙箱根目录
- 更新系统提示词中的环境信息
- 清空当前对话（避免上下文混乱）

### 文件上传

点击 📎 按钮，选择本地文件。文件会被写入当前工作目录，AI 可直接通过 `read_file` 工具访问。

支持：
- 文本文件：UTF-8 写入
- 二进制文件：Base64 解码后写入

### 查看改动文件

状态栏显示 `N 个文件` 改动数量，点击打开 **Changed Files** 面板：
- 列出所有被 AI 修改的文件
- 显示 `git diff` 差异内容
- 新文件显示完整内容（前 200 行）

### 导出对话

对话区右上角 **↓ md** 按钮：将当前完整对话导出为 Markdown 文件下载。

---

## 9. 会话管理

### 自动保存

- 对话达到 5 条消息时自动保存一次
- 之后每 10 条消息自动更新保存
- 保存位置：`~/.byoe/sessions/<id>.json`
- 最多保存 200 个会话（自动清理最旧的）

### 手动保存

点击状态栏 **History → 保存** 或 Ctrl+S（部分浏览器需要服务端支持）。

### 查看历史

点击状态栏 **History** 打开会话面板：
- 搜索框支持按标题关键词过滤
- 点击会话条目恢复对话和模型
- 点击 🗑 删除会话

### 恢复会话（CLI）

```bash
byoe web --resume sess_20260417_143022_abcd
```

---

## 10. Cosmos 可视化模式

Cosmos 将对话可视化为**节点图**，每个 AI 回复、工具调用都是一个气泡节点。

### 开启

点击状态栏 **Cosmos** 按钮（或在设置中开启）。

### 断链功能

在 Cosmos 模式下，输入框左侧出现 ⛓ 按钮：
- 点击 ⛓ → ✂，下一条消息将开启新话题
- 发送后自动恢复连接状态

---

## 11. 定时任务

通过 `/schedule` 命令管理定时自动执行任务。
  
```bash
# 列出所有任务
/schedule list

# 添加任务（每天早上 9 点）
/schedule add daily-report "0 9 * * *" "生成今日代码变更摘要并发送给我"

# 暂停/恢复
/schedule pause <id>
/schedule resume <id>

# 删除
/schedule remove <id>
```

触发规则支持 Cron 表达式。

### Loop Engineering 高级应用方式

BYOE 也是一个能让你的工作流彻底无人化的引擎平台。除了上述提供的基础 cron 定时任务以外，你完全可以通过 Python 代码编写全自动化的后台守护进程 Loop bots，通过 BYOE 引擎执行周期性的项目扫描、分析并在有结果时与你互动。

详见示范教程：[Loop Engineering 高级教程](../loop-demo/LOOP-ENGINEERING-TUTORIAL.md) 及该目录下配合工作的 `daemon_bot.py` 等源码。

---

## 12. Swarm 群智协作流

BYOE 的顶层魅力在其“自动化编排”。通过强大的工具调度体系，AI 能够通过触发原生的**多专家群智协作接力流水线（Swarm Collaboration Pipeline）**。

当遇到繁重、跨越多个专业环节的系统搭建任务（比如需要前端代码配合后端接口规范并且附加安全检查），主 Agent（如同架构规划 PM）不再会尝试自己勉强一个人拉通全局，而是自动拉起一整支内置的专家团队逐个击破！

无需外置重型环境、完全 100% 自动！有关这个引擎的深度机制和运行日志查看解析，可以仔细参阅专门配套撰写的 [BYOE Swarm 架构详解](./SWARM-GUIDE-ZH.md)。

### 串行接力（roles）

```
"用 swarm_collaboration 工具，roles=['backend-architect','security-engineer']，
帮我设计并审查用户认证模块。"
```

### 并行分组（parallel_groups）— v0.8.0 新增

同组专家**并发执行**，节省时间；组间串行传递合并输出：

```
"用 swarm_collaboration 工具，
parallel_groups=[['security-engineer','performance-reviewer'],['tech-lead']]，
评审我们的数据库查询层。"
```

### 容错机制

v0.7.2 起，若流水线中某专家失败，错误上下文会传递给后续专家继续工作；失败率超过 50% 时提前中止并返回部分结果，不静默崩溃。

---

## 13. Sub-agent 子智能体

**Sub-agent** 允许主 Agent 将复杂子任务委派给拥有**独立上下文**的子 Agent 执行，避免污染主对话历史。

### 典型场景

| 场景 | 示例指令 |
|------|----------|
| 代码库探索 | `"用 agent 工具让子 Agent 梳理 ./backend 的模块结构"` |
| 隔离实现 | `"用 agent 工具，role='资深 Python 工程师'，独立实现 design.md 的功能"` |
| 专项审查 | `"用 agent 工具，role='安全工程师'，检查 API 接口越权漏洞"` |

子 Agent 执行结果超过 5000 字时自动压缩摘要返回主 Agent。

完整文档：[Sub-agent 使用指南](./SUBAGENT-GUIDE-ZH.md)

### Swarm vs Sub-agent 速查

| 选 Swarm | 选 Sub-agent |
|---------|-------------|
| 多领域依次叠加（设计→实现→审查） | 独立委派一个隔离子任务 |
| 流水线接力，后者基于前者输出 | 避免上下文污染主对话 |

---

## 14. 使用统计

点击状态栏 Token 数量，打开 **Usage 面板**：

| 指标 | 说明 |
|------|------|
| Prompt Tokens | 输入消耗 |
| Completion Tokens | 输出消耗 |
| Total Tokens | 总消耗 |
| Est. Cost | 预估费用（基于内置价格表） |
| Sessions | 历史会话数 |

使用记录持久化在 `~/.byoe/usage.jsonl`，每次对话追加一条。

支持自定义价格（用于本地/私有模型）：

```json
// ~/.byoe/pricing.json
{
  "my-local-model": [0.0, 0.0],
  "custom-gpt4": [2.0, 8.0]
}
```

### 命令行统计（`byoe metrics`）

```bash
# 最近 7 天用量（默认）
byoe metrics

# 最近 30 天，按模型分组
byoe metrics --days 30

# 只看某个模型
byoe metrics --model gpt-4o

# JSON 格式输出（适合脚本处理）
byoe metrics --json

# 为存量记忆补充嵌入向量（需要 BYOE_EMBEDDING_MODEL）
byoe metrics --reindex-memory
```

---

## 15. 记忆管理（`byoe memory`）

BYOE 的长期记忆存储在 `~/.byoe/memory.db`（SQLite），可通过命令行直接查询和管理。

### 常用命令

```bash
# 搜索记忆（全文 + 语义融合，如开启了 BYOE_EMBEDDING_MODEL）
byoe memory search "React 性能优化"
byoe memory search "数据库索引" --layer long_term

# 列出所有记忆
byoe memory list
byoe memory list --layer short_term    # 过滤层级

# 查看一条记忆的完整内容
byoe memory show ~/.byoe/memory.db:42

# 删除一条记忆
byoe memory forget ~/.byoe/memory.db:42

# 统计各层级记忆数量
byoe memory stats
```

### 记忆层级

| 层级 | 说明 | 默认 TTL |
|------|------|----------|
| `session` | 当前会话临时记忆 | 30 天 |
| `short_term` | 短期工作记忆 | 14 天 |
| `long_term` | 永久保留的重要知识 | 不过期 |

### 语义搜索

设置 `BYOE_EMBEDDING_MODEL` 后，`byoe memory search` 自动融合关键词（FTS5）和语义（余弦相似度）两路排名：

```bash
export BYOE_EMBEDDING_MODEL=text-embedding-3-small
byoe memory search "异步编程最佳实践"
```

---

## 16. 版本与诊断

```bash
# 查看版本信息（含 Python 版本、openai 包版本）
byoe version

# 一键自检（API 连通性、记忆库、工具插件）
byoe doctor
```

---

## 17. Python 库 API

从 v0.8.0 起，BYOE 同时提供**可编程 Python 库 API**，适合嵌入脚本、后端服务、Jupyter Notebook。

```bash
pip install byoe
```

### 快速开始

```python
import byoe

# 工厂函数——自动从环境变量读取 API key 和模型名
agent = byoe.create_agent()

# 同步调用
reply = agent.chat("用一句话解释 BFS")
print(reply)

# 流式调用
stream = agent.stream("写一段快速排序代码")
for token in stream:
    print(token, end="", flush=True)
full_code = stream.result  # 迭代完成后获取完整文本

# 异步调用（asyncio）
import asyncio
result = asyncio.run(agent.achat("解释一下 CAP 定理"))
```

### 结构化输出

```python
from pydantic import BaseModel
import byoe

class CodeReview(BaseModel):
    score: int          # 0-100
    issues: list[str]   # 问题列表
    verdict: str        # 总体评价

agent = byoe.create_agent()
review: CodeReview = agent.chat(
    "审查这段 SQL：SELECT * FROM users WHERE id = " + user_input,
    response_model=CodeReview,
)
print(f"评分：{review.score}，问题：{review.issues}")
```

### 会话持久化

```python
agent = byoe.create_agent()
agent.chat("你好，我叫 Alice")

# 保存会话到文件
path = agent.save()    # 默认 ~/.byoe/conversations/conv_<ts>.json
print(f"已保存：{path}")

# 在另一个进程/脚本中恢复
agent2 = byoe.create_agent()
agent2.load(path)
print(agent2.chat("我叫什么名字？"))  # → "你叫 Alice"
```

### 模型降级链

```python
from byoe import LLM, create_agent

llm = LLM(
    model="gpt-4o",
    api_key="sk-...",
    fallback_models=["gpt-4o-mini"],          # 同 Provider 简写
    fallback_providers=[                       # 跨 Provider
        {"model": "deepseek-chat",
         "api_key": "sk-ds-...",
         "base_url": "https://api.deepseek.com"},
    ],
)
agent = byoe.create_agent(fallbacks=llm._fallback_providers)
```

### 自定义工具

```python
from byoe import Tool, create_agent

class WeatherTool(Tool):
    name = "get_weather"
    description = "获取指定城市的当前天气"

    def run(self, city: str) -> str:
        return f"{city} 今天晴，26°C"

agent = create_agent(tools=[WeatherTool()])
print(agent.chat("上海今天天气怎么样？"))
```

### 多模态图片输入（v0.8.1 新增）

```python
# 用户直接传图
agent.chat("这个截图有什么错误？", images=["error.png"])

# Agent 主动读取图片（LLM 调用 read_image 工具）
agent.chat("读取 diagram.png 并分析架构")
```

支持 JPEG、PNG、GIF、WebP，最大 20 MB。需要支持视觉的模型（gpt-4o、claude-3 等）。

### MCP 服务器集成（v0.8.1 新增）

```python
# 接入外部 MCP 服务器
agent = byoe.create_agent(
    mcp_servers=[
        {"name": "fs", "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]},
        {"name": "myapi", "url": "http://localhost:3000"},
    ]
)
# 远程工具自动注册为 mcp__fs__read_file 等
```

### 公开 API 速查

| 符号 | 说明 |
|------|------|
| `byoe.create_agent(...)` | 工厂函数，从环境变量自动初始化 |
| `byoe.Agent` | 核心 Agent 类 |
| `byoe.LLM(model, api_key, ...)` | LLM 封装，支持降级链 |
| `byoe.Tool` | 自定义工具基类 |
| `byoe.StreamResponse` | `agent.stream()` 返回值，可迭代，`.result` 获取完整结果 |
| `byoe.LightMemory` | 长期记忆（FTS5 + 可选语义搜索） |
| `byoe.get_memory()` | 获取默认全局记忆实例 |
| `byoe.AgentScheduler` | 任务调度（Web 模式使用） |

---

## 18. MCP 生态集成

MCP（Model Context Protocol）是 AI 工具的通用互联标准。BYOE 同时支持**客户端**（调用其他 MCP 服务器）和**服务端**（自身暴露为 MCP 服务器）。

### MCP 服务端（byoe mcp-server）

以 BYOE 作为 MCP 服务器运行，将其 23 个内置工具暴露给任何 MCP 客户端：

```bash
byoe mcp-server              # stdio 模式（VS Code / Claude Desktop / Cursor 使用）
byoe mcp-server --http --port 3000   # HTTP 模式（Docker / 远程部署）
```

**接入 VS Code Copilot**（在项目根目录创建 `.vscode/mcp.json`）：

```json
{
  "servers": {
    "byoe": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "byoe", "mcp-server"]
    }
  }
}
```

**接入 Claude Desktop**（`~/.claude/claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "byoe": {
      "command": "python",
      "args": ["-m", "byoe", "mcp-server"]
    }
  }
}
```

配置后，VS Code Copilot 和 Claude Desktop 即可调用 BYOE 的 bash、edit_file、run_tests、git、web_search 等所有工具。

### MCP 客户端（Python API）

```python
import byoe

agent = byoe.create_agent(
    mcp_servers=[
        # stdio 模式：启动子进程
        {"name": "fs", "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]},
        # HTTP 模式：连接远程服务器
        {"name": "db", "url": "http://localhost:3000"},
    ]
)
# 远程工具自动注册，LLM 可调用 mcp__fs__read_file, mcp__db__query 等
```

通过环境变量配置（JSON 数组）：

```bash
export BYOE_MCP_SERVERS='[{"name":"fs","command":["npx","-y","@modelcontextprotocol/server-filesystem","."]}]'
```

> **完整示例**：[`api-demo/10_mcp.py`](../api-demo/10_mcp.py)

---

## 19. 多模态图片输入

BYOE 支持将图片传入 LLM 进行视觉分析，需要支持多模态的模型（gpt-4o、claude-3、gemini-2.5-flash 等）。

### 方式一：用户传图（chat 参数）

```python
import byoe

agent = byoe.create_agent()   # 需配置支持视觉的模型

# 单图
reply = agent.chat(
    "这个错误截图说明了什么问题？怎么修复？",
    images=["error_screenshot.png"],
)

# 多图对比
reply = agent.chat(
    "对比这两张截图，找出 UI 变化",
    images=["before.png", "after.png"],
)

# 流式 + 图片
for token in agent.stream("描述这张架构图", images=["arch.png"]):
    print(token, end="", flush=True)
```

### 方式二：Agent 主动读取（read_image 工具）

Agent 会在需要时自动调用 `read_image` 工具并注入视觉上下文：

```python
agent.chat("读取 design.png 并分析其中的服务依赖关系")
# LLM 会主动调用 read_image("design.png")
# 图片自动注入为视觉消息，LLM 可以看到图片内容
```

### 支持格式

| 格式 | MIME 类型 | 大小限制 |
|------|-----------|----------|
| PNG | image/png | ≤ 20 MB |
| JPEG | image/jpeg | ≤ 20 MB |
| GIF | image/gif | ≤ 20 MB |
| WebP | image/webp | ≤ 20 MB |

> **完整示例**：[`api-demo/11_multimodal.py`](../api-demo/11_multimodal.py)

---

## 20. 设置说明

### Provider（服务商）

| Provider | 说明 |
|----------|------|
| OpenAI | 直连 OpenAI API，需要 API Key |
| DeepSeek | DeepSeek API |
| 智谱 | 智谱 AI（GLM 系列） |
| Ollama | 本地运行，无需 Key |
| BYOE | 通过本地 `byoe web` 服务端 |
| Custom | 自定义 OpenAI 兼容接口 |

### BYOE Provider 特殊设置

```
Server URL: http://localhost:7860    # byoe web 启动的地址
BYOE Token: abc123xyz               # 终端中显示的 token
```

### 主题

支持深色、浅色、跟随系统三种。

### 语言

中文/English，影响 UI 文字和语音输入语言。

### 模型选择（BYOE 模式）

打开设置对话框时，会自动从 `/api/models` 拉取可用模型列表，可以从下拉框选择。

---

## 21. 命令行模式（byoe chat）

```bash
byoe chat                            # 交互式 REPL
byoe chat "你的问题"                  # 单次提问
byoe chat --model gpt-4o             # 指定模型
byoe chat --resume <session-id>      # 恢复历史会话
```

### 斜杠命令

```
/help               # 显示所有命令
/clear              # 清空对话历史
/status             # 显示当前状态（模型、Token 等）
/model              # 显示当前模型
/plan <目标>         # 进入计划模式
/next               # 推进计划阶段
/skill <名称>        # 激活技能
/skill off          # 关闭技能
/skill list         # 列出所有技能
/skill mine [name] [trigger]  # 从最近一次成功对话自动沉淀技能草案
/schedule ...       # 管理定时任务
/auto on|off        # 切换自主模式
/runtime            # 显示运行时环境信息
```

### 其他 CLI 子命令

```bash
byoe sessions                        # 列出历史会话（含 Token 用量和费用）
byoe doctor                          # 环境自检：API Key / 模型连通性 / 内存库 / 技能目录
byoe agents                          # 列出所有可用专家智能体
byoe sober [目录] --out report.txt   # 运行代码质量扫描，可导出报告
byoe loop -p "任务提示词" --every 30m  # 时间驱动循环执行（Loop Engineering）
byoe loop -p "任务提示词" --at 09:00 --max-runs 1  # 每日定时执行
byoe mcp-server                      # 以 MCP 服务端模式运行（VS Code / Claude Desktop）
byoe mcp-server --http --port 3000   # HTTP 模式
```

### Web API 调度能力（服务端统一调度）

从 v0.8.0 起，BYOE Web 提供后端统一调度中枢，可通过 API 管理任务与 heartbeat：

```http
GET  /api/schedule                  # 查看任务列表 + heartbeat 状态
POST /api/schedule/add              # 新增任务（name/prompt/trigger/max_runs）
POST /api/schedule/remove           # 删除任务（id）
POST /api/schedule/pause            # 暂停任务（id）
POST /api/schedule/resume           # 恢复任务（id）
GET  /api/schedule/retry            # 查看全局重试策略（base/multiplier/max/max_errors）
POST /api/schedule/retry            # 设置全局重试策略
GET  /api/schedule/audit            # 查询调度审计事件（支持 limit/task_id）

GET  /api/auto                      # 查看 heartbeat 状态
POST /api/auto                      # 设置 heartbeat（enabled/interval_ms/prompt）
```

说明：

- 重试策略采用指数退避：$delay = min(max, base * multiplier^{(error\_count-1)})$
- 当 `max_errors` 大于 0 且达到阈值时，任务会被标记为 `failed`，停止继续调度
- 审计事件默认写入 `~/.byoe/logs/scheduler.jsonl`，可通过 Web API 拉取最近记录

### Helm 任务面板增强

- 支持任务列表搜索（名称/提示词/触发表达式）
- 支持状态筛选（all/active/paused/completed/failed）
- 支持排序（next run / created / errors）
- 在 BYOE 模式下可直接配置重试策略，提升线上运维效率

### 质量保障建议（发布前）

```bash
cd byoe
pytest tests/test_scheduler.py -q
```

通过该测试可验证：

- 重试策略是否按配置生效
- 失败截止（max_errors）是否正确将任务转为 failed
- 审计读取接口所依赖的读取逻辑是否正确处理 limit/filter

触发规则示例：

```text
interval:30s
interval:5m
interval:1h
once:2026-06-30T09:00:00
*/15 * * * *
```

### `byoe doctor` 输出示例

```
┌─────────────────────────────────────────────────────┐
│  BYOE Doctor — 环境自检报告                          │
├──────────────────┬───────────────────────────────────┤
│  API Key         │  ✓ 已设置 (sk-...xxxx)            │
│  Model           │  ✓ deepseek-chat                  │
│  LLM 连通性      │  ✓ 响应正常 (1.23s)               │
│  内存数据库       │  ✓ ~/.byoe/memory.db (2.3 MB)     │
│  Skills 目录     │  ✓ ~/.byoe/skills/ (7 个技能)     │
└──────────────────┴───────────────────────────────────┘
```

---

## 22. 安全与隐私

### API Key 存储

- Key 仅保存在浏览器 `localStorage`（key: `byoe-config`）
- **不会**发送到任何 BYOE 服务器
- BYOE 模式下 Key 通过 HTTPS 直接发往您的模型 Provider

### BYOE 服务端安全

- 每次启动随机生成 16 字节 Token（URL-safe Base64）
- 所有 `/api/*` 请求需携带 Token（Header 或 Query Param）
- 默认只允许 localhost 访问
- 请求体限制 4 MB
- 文件上传路径严格限制在工作目录内

### CSP 策略

Web UI 响应头包含：
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; ...
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
```

### Bash 沙箱

- 危险命令（`rm -rf /`、`format C:`、`diskpart` 等）被拦截
- 工作目录限制（沙箱根目录）防止跨目录操作

---

## 23. 非软件研发跨界应用

虽然 BYOE 默认内置的是技术研发领域的 29 位专家，但得益于强大的 **PDEVI 工作流编排**与**自定义 Skill 系统**，您完全可以跨界将其应用在日常办公、法务合规、财务分析和内容创作领域。

详细示例与配置可以参见 [跨界应用指南与范例演示](../other-demo/CROSS-INDUSTRY-GUIDE.md)。只需要为系统载入如“资深法务顾问”的 Skill，它就能从程序员瞬间化身为合同文案审核员。

---

## 24. 常见问题

**Q: 启动后浏览器白屏怎么办？**  
A: 确认 `byoe/static/` 目录存在，或重新安装：`pip install --upgrade byoe`

**Q: Token 每次重启都变了，怎么固定？**  
A: 目前设计如此（安全考虑）。如需固定端口，可用 `byoe web --port 7860` 固定端口，并将 URL 加入书签。

**Q: Ollama 本地模型连不上？**  
A: 确认 Ollama 已启动（`ollama serve`），且 CORS 配置允许 localhost 跨域请求。

**Q: 专家智能体选项是灰色/空的？**  
A: 专家智能体仅在 **BYOE Provider** 模式下可用。使用 `byoe web` 启动后，在 Web UI 选择 Provider 为 BYOE。

**Q: 语音输入按钮点击没反应？**  
A: 需要浏览器支持 Web Speech API（Chrome/Edge/Safari），且需要麦克风权限。Firefox 不支持。

**Q: 如何使用自定义模型的 Token 价格？**  
A: 创建 `~/.byoe/pricing.json`，填入 `{"your-model": [input_price, output_price]}`（单位：美元/百万 Token）。

**Q: 上下文太长了怎么办？**  
A: BYOE 有三层自动压缩。也可手动 `Ctrl+K` 开启新会话，或用 `/clear` 命令。
  
---

## 25. 版本历史

### v0.8.1（2026-07-01）

**MCP 生态**
- 新增 `byoe mcp-server` 命令（stdio + HTTP 双传输），将 BYOE 全部工具暴露为 MCP 服务端
- 新增 MCP 客户端（`byoe.engine.mcp`），支持通过 `create_agent(mcp_servers=[...])` 接入任意 MCP 服务器
- `Config` 新增 `mcp_servers` 字段，支持 `BYOE_MCP_SERVERS` 环境变量（JSON 数组）
- `MCPSession`：`from_stdio()` / `from_http()` 工厂方法，`get_tools()` 返回 BYOE `Tool` 包装

**多模态图片**
- 新增 `read_image` 工具（JPEG/PNG/GIF/WebP，魔术字节 MIME 检测，≤20 MB）
- `Agent.chat(images=[...])` / `stream(images=[...])` / `achat(images=[...])` 支持图片传入
- Agent 自动检测 `read_image` 工具返回的 `data:image/` 结果，注入为视觉消息
- 修复 `estimate_tokens()` 对多模态消息列表的 `TypeError`

**安全与稳定**
- CLI 交互模式下 risky git 操作（add/commit/checkout）显示 ⚠ 确认提示，dangerous 操作（push/pull/force）默认拒绝
- `GitTool.set_confirm_fn()` 可插拔确认回调，非 TTY 环境自动非阻塞处理
- `read_file` session 级内容缓存（`mtime_ns + size` 校验），`edit_file` / `write_file` 写入后自动失效

**测试**
- 新增 `tests/test_mcp.py`（MCP 客户端 + 服务端，42 个测试）
- `tests/test_tools.py` 新增 ReadFileCache / ReadImageTool / GitTool 确认回调（37 个新测试）
- 总计：187 个测试通过

**示例文件**
- `api-demo/10_mcp.py`：MCP 客户端 + 服务端完整演示
- `api-demo/11_multimodal.py`：多模态图片输入演示

### v0.8.0（2026-06-30）

**Python 库与 API 开放**
- ✨ `from byoe import Agent, LLM, Tool, create_agent, StreamResponse` — 正式对外开放 Python 库 API
- ✨ `Agent.stream()` 返回 `StreamResponse`（可迭代，`.result` 属性持有完整文本）
- ✨ `Agent.achat()` — asyncio 原生异步接口
- ✨ `Agent.save()` / `Agent.load()` — 会话序列化与恢复
- ✨ `agent.chat(response_model=MyModel)` — 单轮结构化输出（pydantic 验证）
- ✨ `LLM(fallback_models=[...])` — 同 Provider 多模型降级简写

**CLI 增强**
- ✨ `byoe version` — 版本信息（含 Python/openai 版本）
- ✨ `byoe memory search/list/show/forget/stats` — 命令行直接管理长期记忆
- ✨ `byoe metrics [--days N] [--model M] [--json]` — Token 用量与费用统计
- ✨ `byoe metrics --reindex-memory` — 为存量记忆补充嵌入向量

**Swarm 并行分组**
- ✨ `parallel_groups=[["role-a","role-b"],["role-c"]]` — scatter-gather 并发模式，同组内专家并发执行

**语义记忆**
- ✨ `BYOE_EMBEDDING_MODEL` 环境变量：启用 FTS5 + 余弦相似度双路融合搜索
- ✨ `LightMemory.search_semantic()` 独立语义搜索
- ✨ `LightMemory.reindex()` 批量补充向量

**工具插件**
- ✨ `pyproject.toml` entry-point `byoe.tools` — pip 安装后自动注册第三方工具

**其他**
- ✨ Web API 滑动窗口限速（`BYOE_CHAT_RATE_LIMIT`）
- 🏷️ `py.typed` PEP 561 标记，IDE 类型推断完整支持
- 🧪 测试套件扩展至 144 个（覆盖库 API、语义记忆、Swarm 并行）

---

- ✨ Sub-agent（`agent` 工具）：委派复杂子任务到独立上下文，结果自动压缩摘要
- ✨ Swarm 容错传播：专家失败时错误上下文传递，失败率 >50% 自动中止返回部分结果
- ✨ Skills Trigger 自动注入：确定性关键词匹配替代 AI 感知，同轮结束后恢复
- ✨ Skills LRU 清理：按 `last_used` 时间戳淘汰，不再按文件名顺序
- ✨ `byoe doctor` 命令：API/模型连通性/内存库/技能目录一键自检
- ✨ `byoe sessions` 显示 Token 用量和费用明细列
- ✨ 结构化 JSONL 日志（`BYOE_LOG=1`），支持 debug 级别，自动轮转
- ✨ `BYOE_BASH_TIMEOUT` 环境变量：自定义 Bash 超时（默认 600s，最小 30s）
- ✨ LLM Fallback Chain：主模型失败时自动切换备用提供商
- ✨ Shell 自动补全（需安装 `argcomplete`：`pip install argcomplete`）
- 🔒 Web 并发请求非阻塞锁（0.3s 超时 + SSE 错误响应，防止请求积压）
- 🔒 Token 鉴权优先 `X-BYOE-Token` 请求头，降低 URL 日志泄露风险
- 🔒 Dynamic Skill 路径遍历防护（`Path.resolve().relative_to()` 验证）
- 🐛 SoberTool 移至正确模块（`engine/tools/sober.py`）
- 🐛 `byoe sober --out` 导出纯文本报告功能完整实现
- 🧪 FTS5 三段式搜索策略（短语/AND/OR）+ 时效衰减加权，内存检索更精准

### v0.6.1（2026-04-17）
- 🐛 修复 `_handle_set_cwd` 和 `_handle_agent_activate` 中 `NameError` 崩溃
- 🐛 修复 `MessageBubble` React Hooks 违规（`useState` 在条件渲染后调用）
- ✨ SSE 连接 keep-alive 心跳（每 15 秒），防止长推理超时断开
- ✨ 语音识别实例正确清理（unmount/停止时释放）
- ✨ OnboardingScreen 示例按钮在 Agent 未初始化时禁用
- 🔒 错误消息过滤本机目录路径，避免信息泄露
- 🧪 97/97 测试全部通过

### v0.6.0（2026-04-17）
- ✨ 代码块复制按钮修复（DOMPurify 兼容 `data-copy-text` 属性 + 事件委托）
- ✨ 欢迎屏（OnboardingScreen）：5 个可点击示例提示
- ✨ 语音输入（Web Speech API，支持中/英文）
- ✨ 移动端优化（viewport-fit=cover，touch-action）
- 🧪 新增 `test_session.py`（12 个）、`test_skills.py`（11 个）单元测试

### v0.5.10（2026-04-16）
- 🔒 DOMPurify XSS 防护
- 🐛 `_handle_agent_activate` 使用 `_read_body()`
- ✨ 消息气泡"从此处重新生成"功能
- ✨ `X-Frame-Options: SAMEORIGIN`

### v0.5.9（2026-04-15）
- ✨ 工作目录切换（`/api/cwd`）
- ✨ activeAgent 持久化
- ✨ Base64 文件上传
- 🔒 CSP `connect-src`

---

*© 2026 byoe.net*

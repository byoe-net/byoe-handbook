# BYOE Loop Engineering: 打造无人值守的自动化 AI 员工 

>  **Loop Engineering (闭环/循环工程)** 是目前 AI 架构设计 (如 OpenClaw 等) 中的前沿热门方向。它标志着 AI 从 **“被动听命的 Copilot 助手”** 进化为了 **“定时打卡上班、自发干活的 Daemon 员工”**。

这套模式在结合了 `BYOE 0.8.0` 提供的一级诊断武器后威力极强。本文将带你通过编写少量的 Python 胶水代码，使用 BYOE 原生的引擎库，将其打造成一只能够 7x24 小时不间断帮你改 Bug、扫垃圾的代码护卫。

## 📁 本目录文件一览

| 文件 | 触发机制 | 说明 |
|------|---------|------|
| `daemon_bot.py` | ⏰ 定时器 | 每隔 N 分钟唤醒 Agent 执行巡检，适合夜间定期运维 |
| `cicd_bot.py` | 🚀 单次执行 | 零守护进程，适合 CI/CD 流水线调用，有明确 exit code |
| `event_bot.py` | ⚡ 文件变动 / Webhook | 文件修改或 Sentry 等平台推送时立即触发 |
| `logwatch_bot.py` | 📋 日志 tail | 实时监控日志文件，匹配 ERROR/Traceback 后自动诊断修复 |
| `.github/workflows/byoe-review.yml` | 🐙 GitHub Actions | PR 自动 AI 审查工作流，开箱即用 |

---

## 🧐 1. 什么是 Loop Engineering 模式？

传统的 AI 助理是基于 `Chat` 模型的：
> 用户输入问题 -> AI 思考调用工具 -> AI 给出回覆 -> **AI 挂起等待人类的下一句话**。

而 Loop Engineering 打破了这个局限，引入了 **事件/定时器 (Cron/Event Trigger)** 作为触发器：
> 凌晨 3:00 (定时器触发) -> AI 被强制唤醒 -> 执行给定的**封闭目标** (扫码体检、自动删减死代码、跑单元测试) -> 修复后自动提交 Git -> **休眠**。

由于 `BYOE` 的底层架构已经实现了彻底的“UI 层与引擎层解耦”(见核心的 `Agent` 与 `LLM` 类)，因此实现这一目标极为简单。

---

## 🛠️ 2. 实战运行这套代码

我们在本目录下为你提供了一份极简的基于定时器流派的 `daemon_bot.py`。
它利用了 Python 最广泛使用的 `schedule` 库作为任务驱动，利用 `BYOE` 引擎作为智能执行体。

### 环境准备

因为我们需要用到系统的定时库，请先确保安装了第三方依赖：
```bash
pip install schedule
pip install byoe>=0.8.0
```

### 代码挂载执行

打开你的命令行，导航到你需要被“智能监控”的代码项目录，然后直接将机器人常参挂起执行：
```bash
# 方式 A：在目标项目目录执行（推荐）
cd /你的待托管项目目录/
python ../loop-demo/daemon_bot.py

# 方式 B（Windows PowerShell）
Set-Location D:\your\project
python D:\vibe\loop-demo\daemon_bot.py
```

### 运行时表现

启动后，控制台会输出如下表现（它将脱离人类控制进行无限循环作业）：

```text
🚀 BYOE Loop Engineering (无人值守机器人) 已经启动！

==================================================
🤖 [Loop Engineering] 守护进程已唤醒，开始自动执行项目体检与修复...
==================================================
  ⚡ AI 自动触发动作 -> sober_scan({'directory': '.'})
  ⚡ AI 自动触发动作 -> edit_file({'filePath': 'auth.js', 'explanation': '清理掉废弃无用的导入依赖'})
  ⚡ AI 自动触发动作 -> bash({'command': 'git add auth.js && git commit -m "chore(auto): AI 全自动清理代码坏味道"', 'background': False})

✅ [本次巡检完毕，AI 的总结报告]:
在本次凌晨体检中，我调用了 sober 发现了 auth.js 拥有未使用的垃圾导入问题。已自动进行了剪裁并利用 Git 提交。

💤 进入休眠，等待下一次巡检...
```

### 官方一等公民命令：`byoe loop`

从 v0.8.0 开始，你可以不写任何 Python 守护脚本，直接用内置命令启动时间驱动循环：

```bash
# 每 30 分钟执行一次
byoe loop -p "用 sober_scan 扫描当前仓库并修复 High 风险问题" --every 30m

# 每天 09:00 执行一次日报任务
byoe loop -p "汇总昨日代码变更并生成日报" --at 09:00

# 执行 3 次后自动退出
byoe loop -p "跑测试并修复失败用例" --every 10m --max-runs 3
```

这让 Loop Engineering 从“示例脚本能力”升级为“CLI 原生能力”。

此外，`byoe web` 也已具备服务端统一调度 API（`/api/schedule`、`/api/auto`），
可让前端面板、脚本、以及后端守护逻辑共享同一套任务状态。

---

## 🚀 3. 进阶玩法

`daemon_bot.py` 是**定时器触发**的模式。Loop Engineering 还有两种更高级的触发方式，本目录均提供了完整的可运行代码：

| 文件 | 触发方式 | 适用场景 |
|------|---------|---------|
| `daemon_bot.py` | ⏰ 定时器（schedule） | 夜间巡检、定期清理、日报生成 |
| `event_bot.py`  | ⚡ 文件变动 / Webhook | 代码提交时审查、Sentry 报警即时修复 |
| `logwatch_bot.py` | 📋 日志文件 tail | 线上服务报错自动诊断、异常智能收敛 |
| `cicd_bot.py`   | 🚀 CI/CD 单次执行   | PR 自动审查、GitHub Actions 集成 |

---

### 3.1 事件驱动模式：`event_bot.py`

`event_bot.py` 支持两种子模式：

**模式 A：文件变动监听**（需要 `pip install watchdog`，不安装时自动降级为轮询）

```bash
# 监听 src/ 目录，每次 .py 文件修改后自动触发 AI 审查
python event_bot.py --mode file --watch ./src --filter "*.py" --cwd .

# 自定义任务模板（{name} 会被替换为实际文件名）
python event_bot.py --mode file --watch . --filter "*.py" \
    --task "文件 {name} 刚刚被修改，请检查是否引入了新的安全漏洞或逻辑错误。"
```

**模式 B：Webhook 接收**（零依赖，内置 HTTP 服务器）

```bash
# 启动 Webhook 接收端（默认端口 9988）
python event_bot.py --mode webhook --port 9988 --cwd .

# 测试触发（模拟 Sentry 报警）
curl -X POST http://localhost:9988/trigger \
     -H "Content-Type: application/json" \
     -d '{"event":"sentry.error","message":"NullPointerException in auth.py:42"}'

# 健康检查
curl http://localhost:9988/health
```

**Sentry 集成**：在 Sentry 控制台 → Settings → Integrations → WebHooks 中，将 URL 配置为 `http://your-server:9988/trigger`，即可在报警触发后自动拉起 BYOE 修复。

**冷却控制**：同一事件默认 60 秒内只触发一次 Agent，防止报警风暴（`--cooldown 秒数` 可调整）。

---

### 3.2 日志监控模式：`logwatch_bot.py`

`logwatch_bot.py` 实现了类 `tail -f` 的实时日志监控，纯标准库，无需额外依赖。

```bash
# 监控 app.log，匹配 ERROR/CRITICAL/Traceback（默认模式）
python logwatch_bot.py --log ./app.log --cwd .

# 自定义触发模式和冷却时间
python logwatch_bot.py --log /var/log/gunicorn.log \
    --pattern "ERROR|CRITICAL|OOM" --cooldown 120

# 发送更多上下文行给 Agent（有助于诊断完整堆栈）
python logwatch_bot.py --log ./app.log --context-lines 40

# 作为后台进程常驻（Linux/macOS）
nohup python logwatch_bot.py --log ./app.log --cwd /your/project \
    > ~/.byoe/logs/logwatch.log 2>&1 &
```

**工作原理**：
1. 跳到日志文件末尾（不重放历史），持续轮询新行
2. 检测到匹配行时，将最近 N 行作为上下文发送给 BYOE Agent
3. Agent 读取源码，分析 Root Cause，尝试 `edit_file` 修复
4. 支持日志轮转检测（文件被截断后自动重新从头读取）

---

### 3.3 其他进阶场景

利用以上模板，只需修改传给 `agent.chat(prompt)` 的指令，还可实现：

- **夜间翻译/清理机器人**：把 `daemon_bot.py` 的 prompt 改为"将今天新写的源文件加上 Docstring 注释并翻译注释为英文"，凌晨自动执行。
- **多机器人协同**：同时启动 `daemon_bot.py`（定时体检）和 `logwatch_bot.py`（实时报错响应），互不干扰，覆盖全时段。
- **自定义 Webhook 路由**：修改 `event_bot.py` 中的 `do_POST`，根据 `event_data["event"]` 字段路由到不同的 prompt 模板（如 Sentry 用修复 prompt，GitHub 用代码审查 prompt）。

---

## 🔧 4. 调试 Loop Bot

调试无人值守进程最难的问题是"它在干嘛"。开启结构化日志：

```bash
export BYOE_LOG=1          # 基础日志（推荐生产环境）
export BYOE_LOG=debug      # 含完整消息体（调试时使用）
```

日志写入 `~/.byoe/logs/agent.jsonl`，每条一行 JSON，可实时追踪：

```bash
# 实时追踪工具调用
tail -f ~/.byoe/logs/agent.jsonl | python -c "
import sys, json
for line in sys.stdin:
    e = json.loads(line)
    if e.get('event') in ('tool_call', 'tool_result'):
        print(f\"{e['ts']} [{e['event']}] {e.get('tool','')} {e.get('elapsed_ms','')}ms\")
"
```

如果 Loop Bot 触发 bash 命令超时，可调大上限：

```bash
export BYOE_BASH_TIMEOUT=1800  # 允许最长 30 分钟
```

---

## 🚀 5. CI/CD Pipeline 集成

无需守护进程和 `schedule` 库。将 BYOE 嵌入 CI/CD 流水线，每次 PR 自动触发 AI 审查或修复。

### 方式一：byoe chat 单次执行

```bash
# 直接在 Shell 里单次运行，执行完自动退出
byoe chat "用 sober_scan 扫描当前目录，找出所有 High 级问题，逐一修复并提交 Git。"
```

### 方式二：Python 脚本（推荐，无外部依赖）

本目录下的 `cicd_bot.py` 展示了一个零依赖的 CI/CD 集成示例：

```bash
# 在项目根目录运行，退出码 0=成功 1=发现未修复问题
cd /your/project
python ../loop-demo/cicd_bot.py --task "扫描并修复所有 High 级代码质量问题"
```

### 方式三：GitHub Actions 工作流

本目录已提供完整的工作流文件，直接复制到你的项目即可：

```bash
# 将工作流文件复制到你的项目根目录
cp loop-demo/.github/workflows/byoe-review.yml .github/workflows/

# 在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加：
# OPENAI_API_KEY = sk-...
```

工作流文件 `.github/workflows/byoe-review.yml` 的功能：
- PR 提交时自动触发（支持 `main`、`develop`、`release/**` 分支）
- 支持 `workflow_dispatch` 手动触发并自定义任务
- 审查报告上传为 Artifact（保留 30 天）
- 可选：自动将报告摘要评论到 PR（已内置，开箱即用）

> **安全提示**：将 `OPENAI_API_KEY` 加入 GitHub Repository Secrets，绝不要硬编码在代码或工作流文件中。

### 方式四：系统 Crontab（Linux/macOS）

```bash
# 每天凌晨 2 点自动执行代码体检
# crontab -e 添加以下行：
0 2 * * * OPENAI_API_KEY=sk-... BYOE_MODEL=deepseek-chat \
  byoe chat "用 sober_scan 扫描 /your/project，修复 High 级问题并提交 Git" \
  --cwd /your/project >> /var/log/byoe-nightly.log 2>&1
```

### 方式五：Windows 任务计划程序

```powershell
# 创建每日凌晨 2 点执行的计划任务
$action = New-ScheduledTaskAction `
    -Execute "byoe" `
    -Argument 'chat "用 sober_scan 扫描当前目录并修复 High 级问题"' `
    -WorkingDirectory "D:\your\project"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2)
Register-ScheduledTask -TaskName "BYOE Nightly Review" `
    -Action $action -Trigger $trigger -Settings $settings
```

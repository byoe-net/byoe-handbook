# 循环工程：无人值守的 AI 运维

> 一句话摘要：把 AI 从「随叫随到的助手」变成「7×24 小时自动巡逻的保安」。

---

## 1. 场景引入

你是否有这些需求：

> 「每天凌晨 3 点自动检查服务器日志，发现错误自动修复」
> 「每次 Git push 让 AI 自动做代码审查」
> 「监控某个文件，一有变化就让 AI 处理」
> 「每隔 30 分钟检查一次线上服务状态」

这些场景的共同点：**不想手动触发**，希望 AI 自动持续运行。

BYOE 的 Loop 工程就是为此而生。

---

## 2. 四种循环模式

```
Loop 循环工程
├── 定时模式 (Timer)    → 每 N 分钟执行一次
├── CI/CD 模式 (CI)     → 一次性执行，适合嵌入流水线
├── 事件模式 (Event)    → 文件变化/Webhook 触发
└── 日志监控 (Logwatch) → 实时 tail -f 分析
```

---

## 3. 定时模式：Timer Bot

```bash
byoe loop -p "检查未处理事项并输出今日计划" --every 30m
```

每隔 30 分钟执行一次。适合：
- 定时生成日报
- 周期性检查服务健康
- 轮询监控指标

一次性定时：

```bash
byoe loop -p "生成今日项目周报" --at 18:00 --max-runs 1
```

每天下午 6 点只执行一次。

---

## 4. CI/CD 模式：CI Bot

```bash
# 在 GitHub Actions 中调用
byoe loop -p "审查这个 PR 的代码变更" --once
```

`--once` 模式：执行一次，输出结果，退出。退出码 0 表示成功，1 表示失败。
适合嵌入 CI/CD 流水线：

```yaml
# .github/workflows/code-review.yml
name: BYOE Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install byoe
      - run: byoe loop -p "审查 PR #${{ github.event.number }}" --once
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## 5. 事件模式：Event Bot

监听文件变化或接收 Webhook：

```bash
# 文件变化触发
byoe loop -p "处理新上传的文件" --on-file "./uploads/*.csv"

# Webhook 触发
byoe loop -p "处理 Sentry 告警" --on-webhook :9000
```

Webhook 模式启动一个 HTTP 服务，外部系统可以 POST 事件：

```bash
# Sentry 配置 Webhook → http://your-server:9000
# GitHub Webhook → http://your-server:9000
```

BYOE 收到事件后自动分析并处理。

---

## 6. 日志监控模式：Logwatch Bot

```bash
byoe loop -p "监控 /var/log/app/error.log 中的异常" --tail
```

实时 `tail -f` 日志文件：

```
[14:30:01] 监控 /var/log/app/error.log ...
[14:32:15] ⚠️ 检测到 ERROR: Connection timeout to database
           → AI 正在分析...
           → 根因: 数据库连接池耗尽
           → 自动修复: 重启连接池 (已执行)
[14:32:18] ✅ 异常已处理
```

AI 发现异常 → 分析根因 → 尝试自愈 → 记录结果。完全无人值守。

---

## 7. 实战：组装一个 DevOps 巡逻兵

```python
# patrol_bot.py
import subprocess
import json
from datetime import datetime

def run(**kwargs) -> str:
    """定时巡逻：检查服务状态、磁盘、内存"""
    report = []

    # 1. 检查服务
    services = ["nginx", "postgresql", "redis"]
    for svc in services:
        ret = subprocess.run(
            ["systemctl", "is-active", svc],
            capture_output=True, text=True
        )
        status = "✅" if ret.stdout.strip() == "active" else "❌"
        report.append(f"{status} {svc}: {ret.stdout.strip()}")

    # 2. 检查磁盘
    ret = subprocess.run(
        ["df", "-h", "--output=pcent,avail,target"],
        capture_output=True, text=True
    )
    report.append(f"磁盘:\n{ret.stdout}")

    # 3. 检查内存
    ret = subprocess.run(
        ["free", "-h"],
        capture_output=True, text=True
    )
    report.append(f"内存:\n{ret.stdout}")

    return "\n".join(report)
```

```bash
# 每 5 分钟巡逻一次
byoe loop -p "运行 patrol_bot 并汇报异常" --every 5m
```

---

## 8. 安全提示

Loop Bot 是无人值守的，请确保：
- API Key 有**权限限制**（只读优先）
- 关键操作需要**人工确认**
- 设置命令**超时时间**（默认 600 秒）
- 日志监控建议设置**冷却时间**（同一错误不重复告警）
- 先用 `--dry-run` 测试再上线

---

## 9. 要点总结

- 四种模式：**定时 / CI/CD / 事件 / 日志监控**
- 定时：`--every 30m`，适合周期性任务
- CI/CD：`--once`，适合嵌入流水线
- 事件：`--on-file` 或 `--on-webhook`，适合响应式自动化
- 日志：`--tail`，24 小时实时监控
- 安全：权限限制、超时控制、冷却时间、dry-run

## 下期预告

下一篇我们回归 Python API 的进阶特性：**记忆、钩子和多模态输入**。

---

📎 完整教程：[LOOP-ENGINEERING-TUTORIAL.md](../../tutorials/LOOP-ENGINEERING-TUTORIAL.md)
📎 示例代码：[demos/05-loops/](../../demos/05-loops/)

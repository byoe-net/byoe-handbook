"""实时日志监控 BYOE Loop Bot — tail -f 风格的错误自动修复。

监听指定日志文件，当检测到 ERROR / CRITICAL / Traceback 等模式时，
自动触发 BYOE Agent 诊断并尝试修复相关代码。

特性：
  - 纯标准库实现，零外部依赖（仅 byoe）
  - 跨平台：Windows / Linux / macOS 均可运行
  - 支持日志轮转（文件被截断后自动重新从头读取）
  - 冷却机制防止错误风暴触发过多 Agent 调用
  - 并发执行：Agent 在独立线程中运行，不阻塞日志监听

用法：
    # 最简用法（监听 app.log，使用默认触发模式）
    python logwatch_bot.py --log ./app.log

    # 自定义触发模式与冷却时间
    python logwatch_bot.py --log /var/log/gunicorn.log \\
        --pattern "ERROR|CRITICAL|Traceback" --cooldown 120

    # 发送更多上下文行给 Agent（帮助诊断堆栈）
    python logwatch_bot.py --log ./app.log --context-lines 40 --cwd /your/project

    # 监控多个进程的日志（分别启动两个实例）
    python logwatch_bot.py --log ./worker1.log &
    python logwatch_bot.py --log ./worker2.log &

    # 与 byoe web 联动：将诊断结果 POST 到本地 Web 面板
    # （修改 run_agent 中的 prompt 即可定制报告格式）

环境变量：
    OPENAI_API_KEY    必填
    BYOE_MODEL        可选，默认 gpt-4o
    BYOE_LOG          设为 1 开启 byoe 内部日志

集成 Supervisor / systemd：
    # supervisord.conf
    [program:logwatch]
    command=python /path/to/logwatch_bot.py --log /var/log/app.log
    autostart=true
    autorestart=true
    environment=OPENAI_API_KEY="%(ENV_OPENAI_API_KEY)s"
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from collections import deque
from pathlib import Path
from threading import Thread

logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger("logwatch_bot")

DEFAULT_PATTERN = r"(ERROR|CRITICAL|Traceback \(most recent call last\)|FATAL|Unhandled exception)"
DEFAULT_COOLDOWN = 120   # 两次触发 Agent 的最小间隔（秒）
DEFAULT_CONTEXT_LINES = 25  # 发送给 Agent 的上下文行数
DEFAULT_POLL_INTERVAL = 0.5  # 无新行时的轮询间隔（秒）


# ---------------------------------------------------------------------------
# Agent 执行
# ---------------------------------------------------------------------------
def run_agent(log_excerpt: str, log_file: str, cwd: str) -> None:
    """在独立线程中调用 BYOE Agent 诊断日志片段。"""
    try:
        import byoe
    except ImportError:
        log.error("未安装 byoe，请先执行: pip install byoe>=0.8.0")
        return

    prompt = f"""\
你是一名 24 小时值班的自动运维工程师。

以下是来自日志文件 `{log_file}` 的最新报错片段：

```
{log_excerpt}
```

请按照以下步骤处理：
1. **根因分析**：分析错误的根本原因（Root Cause），说明是哪行代码/哪个模块触发了该异常。
2. **定位代码**：使用 `read_file` 工具读取最可能出错的源代码文件（从堆栈信息中推断路径）。
3. **尝试修复**：如果可以安全修复（例如空指针防护、类型检查、异常捕获），直接用 `edit_file` 修复。
4. **总结报告**：用 2-3 句话说明：发现了什么问题、是否已修复、如未修复原因是什么。

如果错误来自第三方库或运行时环境，无法直接修复代码，请给出具体的排查建议。
"""

    log.info("触发 BYOE Agent 诊断（上下文 %d 行）", log_excerpt.count("\n") + 1)

    def on_tool(name: str, kwargs: dict) -> None:
        log.info("  ⚡ 调用工具: %s(%s)", name, str(kwargs)[:80])

    try:
        agent = byoe.create_agent(cwd=cwd)
        reply = agent.chat(prompt, on_tool=on_tool)
        # 输出带分隔线的诊断报告
        log.info("─" * 60)
        log.info("诊断报告:\n%s", reply)
        log.info("─" * 60)
    except Exception as exc:
        log.error("Agent 执行失败: %s", exc)


# ---------------------------------------------------------------------------
# 日志尾随与触发逻辑
# ---------------------------------------------------------------------------
def tail_and_watch(
    log_file: str,
    pattern: str,
    context_lines: int,
    cooldown: int,
    cwd: str,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
) -> None:
    """持续读取日志文件新行，匹配触发模式后启动 Agent。"""
    path = Path(log_file)
    if not path.exists():
        log.error("日志文件不存在: %s", log_file)
        sys.exit(1)

    compiled = re.compile(pattern, re.IGNORECASE)
    buf: deque[str] = deque(maxlen=context_lines)  # 滑动窗口保存最近 N 行
    last_triggered = 0.0

    log.info("开始监控: %s", log_file)
    log.info("  触发模式: %s", pattern)
    log.info("  冷却时间: %ds  上下文行数: %d", cooldown, context_lines)

    with open(path, encoding="utf-8", errors="replace") as fh:
        # 跳到文件末尾，只处理新增内容（不重放历史日志）
        fh.seek(0, 2)
        prev_size = path.stat().st_size

        while True:
            line = fh.readline()

            if not line:
                # 检测日志轮转：文件被截断（大小比当前指针小）
                try:
                    current_size = path.stat().st_size
                    if current_size < prev_size:
                        log.info("检测到日志轮转，重新从头读取")
                        fh.seek(0)
                        buf.clear()
                    prev_size = current_size
                except OSError:
                    pass
                time.sleep(poll_interval)
                continue

            line = line.rstrip()
            buf.append(line)

            if not compiled.search(line):
                continue

            # 命中触发模式 — 检查冷却
            now = time.time()
            elapsed = now - last_triggered
            if elapsed < cooldown:
                remaining = int(cooldown - elapsed)
                log.debug("冷却中（剩余 %ds），跳过本次触发", remaining)
                continue

            last_triggered = now
            excerpt = "\n".join(buf)
            log.info("命中触发模式: %r", line[:100])

            # 在独立线程中运行 Agent，不阻塞日志读取
            Thread(
                target=run_agent,
                args=(excerpt, log_file, cwd),
                daemon=True,
                name="byoe-agent",
            ).start()


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="实时日志监控 BYOE Loop Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--log", required=True,
        help="要监控的日志文件路径",
    )
    parser.add_argument(
        "--pattern", default=DEFAULT_PATTERN,
        help=f"触发正则模式（默认已覆盖 ERROR/CRITICAL/Traceback/FATAL）",
    )
    parser.add_argument(
        "--context-lines", type=int, default=DEFAULT_CONTEXT_LINES,
        help=f"发送给 Agent 的上下文行数（默认 {DEFAULT_CONTEXT_LINES}）",
    )
    parser.add_argument(
        "--cooldown", type=int, default=DEFAULT_COOLDOWN,
        help=f"两次触发的最小间隔秒数（默认 {DEFAULT_COOLDOWN}）",
    )
    parser.add_argument(
        "--cwd", default=".",
        help="Agent 工作目录（默认当前目录，建议设为被监控的项目根目录）",
    )
    parser.add_argument(
        "--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL,
        help=f"无新行时的轮询间隔秒数（默认 {DEFAULT_POLL_INTERVAL}）",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="输出 DEBUG 级别日志",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        tail_and_watch(
            log_file=args.log,
            pattern=args.pattern,
            context_lines=args.context_lines,
            cooldown=args.cooldown,
            cwd=str(Path(args.cwd).resolve()),
            poll_interval=args.poll_interval,
        )
    except KeyboardInterrupt:
        log.info("监控已停止")


if __name__ == "__main__":
    main()

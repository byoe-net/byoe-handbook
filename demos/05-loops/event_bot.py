"""事件驱动 BYOE Loop Bot — 响应文件变动或 Webhook 通知。

两种触发模式：
  file     监听目录文件变动（优先使用 watchdog，不可用时自动降级为轮询）
  webhook  监听 HTTP POST 请求（使用 Python 内置 http.server，零依赖）

用法：
    # 监听当前目录的 .py 文件变动
    python event_bot.py --mode file --watch . --filter "*.py"

    # 监听特定目录，文件变动后让 AI 自动审查
    python event_bot.py --mode file --watch ./src --filter "*.py" --cwd .

    # 启动 Webhook 接收端（接收 Sentry / GitHub / 自定义推送）
    python event_bot.py --mode webhook --port 9988

Webhook 调用格式（JSON POST to /trigger）：
    curl -X POST http://localhost:9988/trigger \\
         -H "Content-Type: application/json" \\
         -d '{"event":"sentry.error","message":"NullPointerException in auth.py:42"}'

    # Sentry Webhook 示例（在 Sentry → Settings → Integrations → WebHooks 配置）
    # URL: http://your-server:9988/trigger

环境变量：
    OPENAI_API_KEY   必填
    BYOE_MODEL       可选，默认 gpt-4o
    BYOE_LOG         设为 1 开启 byoe 内部日志

依赖（可选，用于 file 模式）：
    pip install watchdog
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import logging
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Lock, Thread
from typing import Any

logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger("event_bot")

# ---------------------------------------------------------------------------
# 冷却控制：防止同一事件频繁触发
# ---------------------------------------------------------------------------
_last_run: dict[str, float] = {}
_lock = Lock()
DEFAULT_COOLDOWN = 60  # 秒


def should_run(key: str, cooldown: int) -> bool:
    """若距上次触发已超过 cooldown 秒则返回 True，并更新时间戳。"""
    now = time.time()
    with _lock:
        if now - _last_run.get(key, 0) < cooldown:
            return False
        _last_run[key] = now
        return True


# ---------------------------------------------------------------------------
# Agent 执行
# ---------------------------------------------------------------------------
DEFAULT_TASK = (
    "检测到事件：{event}。\n"
    "详情：{message}\n\n"
    "请分析可能的原因，定位相关代码文件，诊断问题并尝试修复。"
    "修复后用一句话总结你做了什么。"
)


def run_agent(event_data: dict[str, Any], task_template: str, cwd: str) -> None:
    """在独立线程中运行 BYOE Agent，不阻塞监听主循环。"""
    try:
        import byoe
    except ImportError:
        log.error("未安装 byoe，请先执行: pip install byoe>=0.8.0")
        return

    # 用 event_data 的字段填充 task 模板，缺失字段用空字符串代替
    data_with_defaults = {"event": "", "message": "", "path": "", "name": "", **event_data}
    prompt = task_template.format_map(data_with_defaults)
    log.info("触发 BYOE Agent — 任务: %s", prompt[:160])

    def on_tool(name: str, kwargs: dict) -> None:
        log.info("  ⚡ 调用工具: %s(%s)", name, str(kwargs)[:80])

    try:
        agent = byoe.create_agent(cwd=cwd)
        reply = agent.chat(prompt, on_tool=on_tool)
        log.info("Agent 完成:\n%s", reply)
    except Exception as exc:
        log.error("Agent 执行失败: %s", exc)


# ---------------------------------------------------------------------------
# 文件监听模式
# ---------------------------------------------------------------------------
def _run_with_watchdog(
    watch_dir: str,
    glob_filter: str,
    task_template: str,
    cwd: str,
    cooldown: int,
) -> bool:
    """尝试使用 watchdog 监听；若未安装则返回 False。"""
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        return False

    class _Handler(FileSystemEventHandler):
        def on_modified(self, event) -> None:  # type: ignore[override]
            if event.is_directory:
                return
            path: str = event.src_path
            if glob_filter and not fnmatch.fnmatch(Path(path).name, glob_filter):
                return
            if not should_run(path, cooldown):
                log.debug("冷却中，跳过: %s", path)
                return
            log.info("文件变动: %s", path)
            data = {"event": "file_changed", "path": path, "name": Path(path).name, "message": f"文件 {path} 已修改"}
            Thread(target=run_agent, args=(data, task_template, cwd), daemon=True).start()

    observer = Observer()
    observer.schedule(_Handler(), watch_dir, recursive=True)
    observer.start()
    log.info("watchdog 监听中: %s  过滤: %s", watch_dir, glob_filter or "*")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    return True


def _run_polling(
    watch_dir: str,
    glob_filter: str,
    task_template: str,
    cwd: str,
    cooldown: int,
) -> None:
    """watchdog 不可用时的跨平台轮询降级方案（每 5 秒检查）。"""
    log.warning("watchdog 未安装，使用轮询模式。建议: pip install watchdog")
    mtimes: dict[str, float] = {}
    root = Path(watch_dir)
    first_scan = True

    while True:
        try:
            for f in root.rglob("*"):
                if not f.is_file():
                    continue
                if glob_filter and not fnmatch.fnmatch(f.name, glob_filter):
                    continue
                try:
                    mtime = f.stat().st_mtime
                except OSError:
                    continue
                key = str(f)
                prev = mtimes.get(key, 0)
                mtimes[key] = mtime
                if first_scan or mtime <= prev:
                    continue
                if not should_run(key, cooldown):
                    continue
                log.info("文件变动: %s", f)
                data = {"event": "file_changed", "path": key, "name": f.name, "message": f"文件 {f.name} 已修改"}
                Thread(target=run_agent, args=(data, task_template, cwd), daemon=True).start()
        except Exception as exc:
            log.error("轮询出错: %s", exc)
        first_scan = False
        time.sleep(5)


def run_file_mode(
    watch_dir: str,
    glob_filter: str,
    task_template: str,
    cwd: str,
    cooldown: int,
) -> None:
    if not _run_with_watchdog(watch_dir, glob_filter, task_template, cwd, cooldown):
        _run_polling(watch_dir, glob_filter, task_template, cwd, cooldown)


# ---------------------------------------------------------------------------
# Webhook 模式
# ---------------------------------------------------------------------------
def run_webhook_mode(port: int, task_template: str, cwd: str, cooldown: int) -> None:
    """启动轻量 HTTP 服务器，接收 JSON POST /trigger 触发 Agent。"""

    class _WebhookHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:  # 静默 HTTP 访问日志
            pass

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/trigger":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                event_data: dict[str, Any] = json.loads(body) if body else {}
            except json.JSONDecodeError:
                event_data = {"event": "webhook", "message": body.decode(errors="replace")}

            key = str(event_data.get("event", "webhook"))
            if not should_run(key, cooldown):
                self.send_response(429)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"cooldown"}')
                return

            log.info("收到 Webhook: %s", json.dumps(event_data, ensure_ascii=False)[:200])
            Thread(target=run_agent, args=(event_data, task_template, cwd), daemon=True).start()

            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"accepted"}')

        def do_GET(self) -> None:  # noqa: N802
            """健康检查端点。"""
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            else:
                self.send_error(404)

    server = HTTPServer(("0.0.0.0", port), _WebhookHandler)
    log.info("Webhook 服务器已启动")
    log.info("  触发端点: http://localhost:%d/trigger  (POST JSON)", port)
    log.info("  健康检查: http://localhost:%d/health   (GET)", port)
    log.info("  Sentry 配置: Settings → Integrations → WebHooks → URL 填写上方触发端点")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Webhook 服务器已关闭")


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="事件驱动 BYOE Loop Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--mode", choices=["file", "webhook"], default="webhook",
        help="触发模式（默认 webhook）",
    )
    parser.add_argument("--watch", default=".", help="[file] 监听的目录（默认当前目录）")
    parser.add_argument(
        "--filter", default="", dest="glob_filter",
        help="[file] 文件名 glob 过滤器，例如 '*.py'（默认不过滤）",
    )
    parser.add_argument("--port", type=int, default=9988, help="[webhook] 监听端口（默认 9988）")
    parser.add_argument("--cwd", default=".", help="Agent 的工作目录（默认当前目录）")
    parser.add_argument(
        "--cooldown", type=int, default=DEFAULT_COOLDOWN,
        help=f"同一 key 两次触发的最小间隔秒数（默认 {DEFAULT_COOLDOWN}）",
    )
    parser.add_argument(
        "--task", default=DEFAULT_TASK,
        help="传给 Agent 的任务模板，支持 {event} {message} {path} {name} 占位符",
    )
    args = parser.parse_args()

    cwd = str(Path(args.cwd).resolve())
    log.info("BYOE Event Bot 启动 — 模式: %s  工作目录: %s", args.mode, cwd)

    if args.mode == "file":
        run_file_mode(
            watch_dir=str(Path(args.watch).resolve()),
            glob_filter=args.glob_filter,
            task_template=args.task,
            cwd=cwd,
            cooldown=args.cooldown,
        )
    else:
        run_webhook_mode(
            port=args.port,
            task_template=args.task,
            cwd=cwd,
            cooldown=args.cooldown,
        )


if __name__ == "__main__":
    main()

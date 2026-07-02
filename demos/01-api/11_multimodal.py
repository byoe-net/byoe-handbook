"""api-demo/11_multimodal.py — 多模态图片输入完整示例（v0.8.1）

演示内容：
  A. read_image 工具 — 读取图片文件，Agent 自动获得视觉理解能力
  B. chat(images=[...]) — 用户直接传图给 Agent
  C. 多图并行 — 同时传入多张图
  D. 数据 URL 格式说明

运行:
    python api-demo/11_multimodal.py

注意：实际视觉分析需要支持多模态的模型（gpt-4o、claude-3、gemini-2.5-flash 等）。
      本示例演示 API 用法和消息结构，不实际调用 LLM。
"""

import base64
import json
from pathlib import Path
from unittest.mock import MagicMock

import byoe
from byoe.engine.tools.read_image import ReadImageTool, _detect_mime


# ══════════════════════════════════════════════════════════════════════════════
# 工具函数：创建测试图片
# ══════════════════════════════════════════════════════════════════════════════

def make_test_png(path: Path) -> Path:
    """创建一个最小的 1×1 白色 PNG 文件（用于演示，不需要 Pillow）。"""
    # 最小合法 PNG（68 字节）
    PNG_1X1 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
        "z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
    )
    path.write_bytes(base64.b64decode(PNG_1X1))
    return path


# ══════════════════════════════════════════════════════════════════════════════
# A. read_image 工具 — 基础用法
# ══════════════════════════════════════════════════════════════════════════════

print("=" * 60)
print("A. read_image 工具")
print("=" * 60)

import tempfile
tmp = Path(tempfile.mkdtemp())
img_path = make_test_png(tmp / "screenshot.png")

tool = ReadImageTool()
result = tool.execute(str(img_path))

print(f"\n图片路径: {img_path}")
print(f"返回格式: {result[:40]}...")
print(f"完整长度: {len(result)} 字符")

# 解析 data URL
mime, b64_data = result.split(";base64,", 1)
mime_type = mime.replace("data:", "")
decoded = base64.b64decode(b64_data)
print(f"MIME 类型: {mime_type}")
print(f"原始大小: {len(decoded)} 字节")
print(f"Base64 大小: {len(b64_data)} 字符")


# ══════════════════════════════════════════════════════════════════════════════
# B. MIME 类型自动检测
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("B. MIME 类型自动检测（魔术字节）")
print("=" * 60)

test_headers = {
    "PNG": b"\x89PNG\r\n\x1a\n" + b"\x00" * 8,
    "JPEG": b"\xff\xd8\xff" + b"\x00" * 13,
    "GIF": b"GIF89a" + b"\x00" * 10,
    "WebP": b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 4,
    "Unknown": b"\x00\x01\x02\x03" * 4,
}

print()
for name, header in test_headers.items():
    mime = _detect_mime(header)
    print(f"  {name:10s} → {mime}")


# ══════════════════════════════════════════════════════════════════════════════
# C. Agent.chat(images=[...]) — 消息结构展示
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("C. chat(images=[...]) 消息结构")
print("=" * 60)

# 创建第二张测试图
img2_path = make_test_png(tmp / "diagram.png")

# 展示消息构建逻辑（不实际调用 LLM）
from byoe.engine.agent import _image_to_data_url

data_url = _image_to_data_url(str(img_path))
user_message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "这个截图里有什么问题？"},
        {"type": "image_url", "image_url": {"url": data_url}},
    ],
}

print("\nchat('描述这张图', images=['screenshot.png']) 构建的消息结构：")
# 截断 base64 以便展示
display_msg = json.loads(json.dumps(user_message))
for part in display_msg["content"]:
    if part.get("type") == "image_url":
        url = part["image_url"]["url"]
        part["image_url"]["url"] = url[:40] + f"...({len(url)} chars total)"
print(json.dumps(display_msg, indent=2, ensure_ascii=False))


# ══════════════════════════════════════════════════════════════════════════════
# D. read_image + Agent 对话流（模拟）
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("D. read_image 在 Agent 对话中的流转（Mock LLM）")
print("=" * 60)

from byoe.engine.llm import LLMResponse, ToolCall
from byoe.engine.agent import Agent


class _ImageLLM:
    """模拟 LLM：第1轮调用 read_image，第2轮返回分析结果。"""
    model = "gpt-4o"
    total_prompt_tokens = 0
    total_completion_tokens = 0
    _turn = 0

    def chat(self, messages, tools=None, on_token=None):
        self._turn += 1
        if self._turn == 1:
            # 返回 read_image 工具调用
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="read_image",
                        arguments={"file_path": str(img_path)},
                    )
                ],
            )
        else:
            # 第2轮：图片已在消息中，返回分析
            # 检查图片是否已被注入到消息里
            has_image = any(
                isinstance(m.get("content"), list)
                and any(p.get("type") == "image_url" for p in m["content"])
                for m in messages
            )
            text = "✅ 图片已注入视觉上下文" if has_image else "❌ 图片未注入"
            return LLMResponse(content=f"图片分析完成。{text}")


agent = Agent(llm=_ImageLLM())
result = agent.chat("读取 screenshot.png 并描述其中的内容")

print(f"\nAgent 回复: {result}")

# 检查消息历史中是否有图片消息
image_messages = [
    m for m in agent.messages
    if isinstance(m.get("content"), list)
    and any(isinstance(p, dict) and p.get("type") == "image_url" for p in m["content"])
]
print(f"消息历史中的图片消息数: {len(image_messages)}")
if image_messages:
    url = image_messages[0]["content"][0]["image_url"]["url"]
    print(f"图片数据 URL 前缀: {url[:50]}...")


# ══════════════════════════════════════════════════════════════════════════════
# E. 实际使用示例代码（注释，需要真实 API Key）
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("E. 实际使用示例（需要多模态模型 + API Key）")
print("=" * 60)

print("""
# 方式 1：用户直接传图（chat 时附带截图）
import byoe
agent = byoe.create_agent()   # 需要 OPENAI_API_KEY 且模型支持视觉（gpt-4o 等）

reply = agent.chat(
    "这个错误截图说明了什么问题？怎么修复？",
    images=["error_screenshot.png"],
)
print(reply)


# 方式 2：Agent 主动读取图片（LLM 决策调用 read_image）
reply = agent.chat("读取 architecture_diagram.png 并分析其中的服务依赖关系")
# LLM 会自动调用 read_image 工具，图片内容注入后继续分析


# 方式 3：多图对比
reply = agent.chat(
    "对比这两张截图，找出 UI 变化",
    images=["before.png", "after.png"],
)


# 方式 4：流式输出（配合图片）
stream = agent.stream(
    "描述这张架构图",
    images=["arch.png"],
)
for token in stream:
    print(token, end="", flush=True)
print()


# 适合多模态的模型：
# OpenAI:    gpt-4o, gpt-4o-mini, gpt-4.1
# Anthropic: claude-3-*, claude-sonnet-4-*
# Google:    gemini-2.5-pro, gemini-2.5-flash
# 支持图片输入的 DeepSeek / Qwen 模型（需确认 API 支持）
""")

# 清理临时文件
import shutil
shutil.rmtree(tmp, ignore_errors=True)

print("✅ api-demo/11_multimodal.py 完成")

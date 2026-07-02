"""BYOE 自定义工具插件

演示两种方式扩展 BYOE 工具集：

  A. 运行时动态注册（add_runtime_tool）— 适合单次会话
  B. Entry-point 插件（pyproject.toml）— 适合发布为独立 pip 包

运行：
    python 07_plugins.py
"""

import json
import byoe
from byoe import Tool, Agent, LLM
import os

# ── A. 运行时注册工具 ─────────────────────────────────────────────────────────

class WeatherTool(Tool):
    """查询指定城市的当前天气（示例：模拟返回固定数据）。"""
    name = "get_weather"
    description = "查询指定城市的当前天气信息"
    parameters = {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称，例如 '北京'"},
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "温度单位",
            },
        },
        "required": ["city"],
    }

    def execute(self, city: str, unit: str = "celsius") -> str:
        # 实际场景中这里调用真实天气 API
        temp = 28 if unit == "celsius" else 82
        return json.dumps({
            "city": city,
            "temperature": temp,
            "unit": unit,
            "condition": "晴",
            "humidity": "45%",
        }, ensure_ascii=False)


class StockTool(Tool):
    """查询股票价格（示例：模拟数据）。"""
    name = "get_stock_price"
    description = "查询指定股票代码的最新价格"
    parameters = {
        "type": "object",
        "properties": {
            "symbol": {"type": "string", "description": "股票代码，例如 'AAPL'"},
        },
        "required": ["symbol"],
    }

    def execute(self, symbol: str) -> str:
        prices = {"AAPL": 195.3, "TSLA": 248.7, "NVDA": 875.2}
        price = prices.get(symbol.upper(), "未找到")
        return f"{symbol.upper()}: ${price}"


# 创建 Agent 并动态注册自定义工具
llm = LLM(
    model=os.environ.get("BYOE_MODEL", "gpt-4o"),
    api_key=os.environ.get("BYOE_API_KEY", ""),
)
agent = Agent(llm=llm, tools=[WeatherTool(), StockTool()])

print("=== 使用自定义工具 ===")
response = agent.chat("北京今天天气怎么样？另外 NVDA 现在多少钱？")
print(response)
print()

# ── B. Entry-point 插件（发布为 pip 包的方式） ────────────────────────────────
# 在你的 pyproject.toml 中声明：
#
#   [project.entry-points."byoe.tools"]
#   my_weather = "my_package.tools:WeatherTool"
#   my_stock   = "my_package.tools:StockTool"
#
# pip install 后 BYOE 在下次启动时自动发现并注册这些工具。
# 无需修改 BYOE 源码。

# 验证插件发现机制（开发时可用 monkeypatch 测试）
from byoe.engine.tools import _load_plugin_tools, ALL_TOOLS
plugins = _load_plugin_tools()
print(f"当前环境已安装插件工具: {len(plugins)} 个")
print(f"内置工具总数: {len(ALL_TOOLS)} 个")
print()

# ── C. 通过 create_agent() 传入自定义工具列表 ─────────────────────────────────
# 如果只想在特定 Agent 中使用部分工具（不带全部内置工具）：
lightweight_agent = byoe.create_agent(
    tools=[WeatherTool(), StockTool()],   # 只有这两个工具，轻量级
)
print(f"轻量 Agent 工具数: {len(lightweight_agent.tools)}")

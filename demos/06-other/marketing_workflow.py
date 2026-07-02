"""
营销文案生成工作流 — BYOE Agent 真实调用示范

演示功能：
- 使用 BYOE 引擎驱动完整 PDEVI 营销工作流
- 通过 Sub-agent 工具委派受众痛点分析子任务
- 使用 Swarm 工具进行多专家接力创作（文案+技术写作）
- 最终进行品牌合规内容审查

运行方式：
    pip install byoe
    export OPENAI_API_KEY=sk-...  # 或 DEEPSEEK_API_KEY 等
    python marketing_workflow.py --product-name "智能耳机X1" \
        --target-audience "25-35岁都市白领" \
        --selling-point "主动降噪+40小时续航"
"""

import argparse
import sys
import os


def run_marketing_workflow(product_name: str, target_audience: str, selling_point: str) -> None:
    """使用 BYOE Agent 驱动完整营销文案工作流。"""
    try:
        from byoe.engine.agent import Agent
        from byoe.engine.llm import LLM
    except ImportError:
        print("未安装 byoe，请先运行：pip install byoe")
        sys.exit(1)

    api_key = (
        os.environ.get("BYOE_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("DEEPSEEK_API_KEY")
    )
    if not api_key:
        print("请设置 API Key 环境变量（OPENAI_API_KEY / DEEPSEEK_API_KEY / BYOE_API_KEY）")
        sys.exit(1)

    base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("BYOE_BASE_URL")
    model = os.environ.get("BYOE_MODEL", "deepseek-chat")

    print("\n" + "=" * 60)
    print(f"  BYOE 营销文案工作流")
    print(f"  产品：{product_name}")
    print(f"  受众：{target_audience}")
    print(f"  卖点：{selling_point}")
    print("=" * 60 + "\n")

    llm_kwargs: dict = {"model": model, "api_key": api_key}
    if base_url:
        llm_kwargs["base_url"] = base_url

    llm = LLM(**llm_kwargs)
    agent = Agent(llm=llm)

    # 阶段 1：委派子 Agent 做受众痛点分析
    print("阶段 1 / 4：受众痛点深度分析（Sub-agent 委派中）...")
    pain_task = (
        "你是一位消费者行为研究员。"
        f"目标受众：{target_audience}。产品：{product_name}（卖点：{selling_point}）。"
        "输出该受众 Top 5 痛点及对应情绪关键词，以 Markdown 表格呈现。"
    )
    pain_analysis = agent.chat(
        f"用 agent 工具，role='你是一位消费者行为研究员'，"
        f"task='{pain_task}'，inherit_crew_context=false"
    )
    print(pain_analysis)

    # 阶段 2：Swarm 多专家接力生成多平台文案
    print("\n阶段 2 / 4：多平台文案矩阵生成（Swarm 流水线）...")
    swarm_task = (
        f"产品：{product_name}，卖点：{selling_point}，受众：{target_audience}。\n"
        f"受众痛点摘要：{pain_analysis[:600]}\n\n"
        "请依次：\n"
        "1. copywriter 写 3 条小红书情绪化短文案\n"
        "2. technical-writer 写一篇 800 字微信公众号深度科普文\n"
        "汇总两份输出。"
    )
    copy_matrix = agent.chat(
        "用 swarm_collaboration 工具，roles=['copywriter','technical-writer']，"
        f"task='{swarm_task}'"
    )
    print(copy_matrix)

    # 阶段 3：生成短视频脚本
    print("\n阶段 3 / 4：15 秒短视频脚本生成...")
    video_script = agent.chat(
        f"写一个 15 秒竖版短视频脚本（抖音/Reels 风格），产品：{product_name}，"
        f"卖点：{selling_point}，受众：{target_audience}。\n"
        "格式：前3秒钩子 -> 5秒产品出现 -> 7秒卖点展示 -> 15秒行动号召。\n"
        "给出画面描述 + 配音文案。"
    )
    print(video_script)

    # 阶段 4：内容合规审查
    print("\n阶段 4 / 4：文案合规审查...")
    review = agent.chat(
        "以品牌合规审查员视角检查上面所有文案：\n"
        "1. 是否存在无法验证的极端用词（'最强'、'第一'等）？\n"
        "2. 是否存在平台风险敏感词？\n"
        f"3. 是否与卖点（{selling_point}）保持一致？\n"
        "以 OK/WARN 格式输出审查清单并给出修改建议。"
    )
    print(review)

    print("\n" + "=" * 60)
    print("  营销文案工作流完成！")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="BYOE 营销文案工作流演示（真实 Agent 调用）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python marketing_workflow.py \
      --product-name "智能耳机X1" \
      --target-audience "25-35岁都市白领" \
      --selling-point "主动降噪+40小时续航"

环境变量：
  OPENAI_API_KEY  / DEEPSEEK_API_KEY  -- LLM API Key
  OPENAI_BASE_URL / BYOE_BASE_URL     -- API 基础 URL（可选）
  BYOE_MODEL                          -- 模型名称（默认 deepseek-chat）
        """,
    )
    parser.add_argument("--product-name", required=True, help="产品名称")
    parser.add_argument("--target-audience", required=True, help="目标受众群体")
    parser.add_argument("--selling-point", required=True, help="核心卖点/差异化优势")

    args = parser.parse_args()
    run_marketing_workflow(args.product_name, args.target_audience, args.selling_point)


if __name__ == "__main__":
    main()
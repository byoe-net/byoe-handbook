import os
import time

import schedule

import byoe


def autonomous_patrol():
    """
    全自动巡检任务：由定时器触发，无需人类干预。
    """
    print("\n" + "="*50)
    print("🤖 [Loop Engineering] 守护进程已唤醒，开始自动执行项目体检与修复...")
    print("="*50)

    # create_agent() 自动读取 OPENAI_API_KEY / BYOE_API_KEY / BYOE_MODEL 等环境变量
    try:
        agent = byoe.create_agent(cwd=os.getcwd())
    except Exception as exc:
        print(f"❌ 初始化失败，请检查环境变量（OPENAI_API_KEY / BYOE_MODEL）：{exc}")
        return

    # 3. 制定无人值守的闭环 Prompt
    # 注意这里一定要给大模型下达封闭式的指令，明确它的终点。
    prompt = """
    你现在处于 [无人值守的全自动流 (Loop Engineering)] 模式，无需等待人类确认。
    请遵循以下自动化巡检工序：
    1. 调用 `sober_scan` 对当前目录代码债务进行诊断。
    2. 如果存在评测扣分项 (例如 死代码、上帝文件、安全密钥泄露)，请直接用 `edit_file` 将它们就地修复。
    3. 如果进行了修复操作，请通过 `bash` 自动调用 `git add .` 和 `git commit -m "chore(auto): AI 全自动清理代码坏味道"` 进行提交。
    4. 执行完毕后，只用一句话总结完成了哪些修复。
    """

    # 4. 回调函数：将 AI 的中间思考与执行流打印到终端日志
    def on_token(t): 
        pass # 静默执行，不打印逐字啰嗦的回复，只需要看最终结果
        
    def on_tool(name, kwargs):
        print(f"  ⚡ AI 自动触发动作 -> {name}({kwargs})")

    # 5. 引爆执行闭环
    try:
        reply = agent.chat(prompt, on_token=on_token, on_tool=on_tool)
        print("\n✅ [本次巡检完毕，AI 的总结报告]:")
        print(reply)
    except Exception as e:
        print(f"❌ 自动任务运行中发生崩溃: {e}")
        
    print("💤 进入休眠，等待下一次巡检...\n")


if __name__ == "__main__":
    print("🚀 BYOE Loop Engineering (无人值守机器人) 已经启动！")
    
    # 【运行机制】
    # 每隔 60 分钟自动唤醒跑一次巡检
    # 也可以改为 schedule.every().day.at("03:00").do(autonomous_patrol) 在凌晨 3 点跑
    schedule.every(60).minutes.do(autonomous_patrol)
    
    # 首次启动先立刻跑一次看看效果
    autonomous_patrol()

    # 挂起持续运行的主循环
    while True:
        schedule.run_pending()
        time.sleep(5)

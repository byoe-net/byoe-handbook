# CLI 聊天入门：一句话让 AI 改代码

> 一句话摘要：`byoe chat` 不只是聊天，它是一个完整的终端 AI 工作台。

---

## 1. 场景引入

你的同事跑过来说：

> 「帮我把登录页面的样式从 CSS 改成 Tailwind，另外把表单验证加上。」

如果是 Copilot，你需要：
1. 打开登录页面组件
2. 逐行改写 CSS class
3. 找到表单逻辑加验证
4. 测试

如果是 BYOE CLI：

```
byoe chat
You: 把登录页面改成 Tailwind 样式，加上表单验证
```

AI 自己读文件、改代码、跑测试。你只需要看结果。

---

## 2. 启动 CLI

```bash
byoe chat
```

进入交互模式后，你会看到提示符：

```
╭─ BYOE Chat ───────────────────────────────╮
│ 输入 /help 查看命令列表                      │
│ 输入 /exit 退出                            │
╰────────────────────────────────────────────╯
You:
```

---

## 3. 核心命令

### `/help` — 查看所有内置命令

```
可用命令：
  /exit          退出
  /save          保存会话
  /load <id>     恢复会话
  /reset         重置上下文
  /skill <name>  手动激活技能
  /skills        列出可用技能
  /plan          切换到规划模式
  /cost          查看本次会话费用
```

### `/save` — 保存当前会话

```bash
You: /save
Assistant: ✅ 会话已保存 (session_20260702_143022)
```

### `/load` — 恢复历史会话

```bash
You: /load session_20260702_143022
Assistant: ✅ 已恢复会话（共 12 条消息）
```

---

## 4. 实战：让 AI 完成一个真实任务

### 任务：给现有项目加单元测试

假设你有一个 Python 项目，里面有一个 `utils.py`：

```python
# utils.py
def calculate_discount(price: float, level: str) -> float:
    """根据会员等级计算折扣价"""
    discounts = {"normal": 1.0, "vip": 0.8, "svip": 0.6}
    return price * discounts.get(level, 1.0)
```

在 CLI 中输入：

```
You: 给 utils.py 的 calculate_discount 函数写单元测试
```

AI 会做的事情：

1. **读取文件** → 调用 `read_file` 理解原代码
2. **分析函数** → 识别参数、返回值、边界情况
3. **生成测试** → 调用 `write_file` 写入 `test_utils.py`
4. **运行测试** → 调用 `bash pytest test_utils.py -v`
5. **报告结果** → 返回测试通过情况

### 结果

```
Assistant: ✅ 已完成！测试文件 test_utils.py 已创建。

测试覆盖了：
  1. normal 会员 → 原价
  2. vip 会员 → 8 折
  3. svip 会员 → 6 折
  4. 未知等级 → 原价
  5. 价格为 0 → 免费
  6. 负数价格 → 返回负数

运行结果：
  ✓ test_normal_member
  ✓ test_vip_member
  ✓ test_svip_member
  ✓ test_unknown_level
  ✓ test_zero_price
  ✓ test_negative_price
  6 passed in 0.12s
```

全程你只说了一句话。

---

## 5. 非交互模式

适合脚本和 CI/CD：

```bash
# 单次执行，自动退出
byoe chat -p "统计当前目录下的 Python 文件行数"

# 带上下文（类似 continue）
byoe chat -r session_20260702_143022 -p "再给我加一个 CLI 入口"
```

---

## 6. CLI 流式输出的效果

> 插入 CLI 流式输出的录屏 GIF

AI 生成代码时，token 逐个输出到终端，就像有人在现场打字给你看。你可以随时按 `Ctrl+C` 中断。

---

## 7. 要点总结

- 启动：`byoe chat` → 输入需求 → AI 自动执行
- 核心命令：`/save`, `/load`, `/skill`, `/cost`
- 非交互模式：`byoe chat -p "指令"`（适合 CI/CD）
- AI 自动链式调用工具：读文件 → 改代码 → 跑测试 → 报告
- 随时按 `Ctrl+C` 中断执行

## 下期预告

下一篇我们打开 Web 界面：**比 CLI 更直观，面板化管理 Skills、Tasks、会话和 Cosmos 可视化**。

---

📎 完整文档：[用户手册 §21 CLI 模式](../../docs/02-user-guide/USER-MANUAL-ZH.md)

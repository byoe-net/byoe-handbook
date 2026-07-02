# 从 Demo 到生产：最佳实践与 FAQ

> 一句话摘要：14 篇文章学完了，但实际用起来有哪些坑？这篇帮你避开。

---

## 1. 场景引入

你读完了前面 13 篇，安装了 BYOE，跑通了 demo，感觉还不错。

然后你开始用在真实项目上：

> 「AI 把我的代码改坏了怎么办？」
> 「API 调用太频繁，费用蹭蹭涨」
> 「AI 有时会乱用工具」
> 「团队怎么共享技能？」

这些问题，这篇统一回答。

---

## 2. 安全最佳实践

### 权限控制

```bash
# 限制 Bash 工具的超时时间（默认 600 秒）
export BYOE_BASH_TIMEOUT=60

# AI 的工具调用需要用户确认
#   auto: 自动放行（速度快）
#   confirm: 每次确认（安全）
#   reject: 禁止（只用于观察）
```

生产环境建议先设置为 `confirm` 模式，观察 AI 的行为后再放宽。

### 文件保护

AI 可能误删文件。建议：
- 项目用 git 管理，AI 改了可以 revert
- 敏感文件（`.env`、`credentials.json`）放 `.gitignore` 并提醒 AI 不要碰
- 关键操作由 Crew 的 `verify` 阶段控制

### API Key 安全

```bash
# 不要写在代码里
api_key = os.environ["OPENAI_API_KEY"]  # ✅ 环境变量
api_key = "sk-xxx"                       # ❌ 别这么做
```

### 限速

多人使用 Web UI 时：

```bash
export BYOE_CHAT_RATE_LIMIT=30  # 每 IP 每分钟最多 30 次
```

---

## 3. 成本控制

### Token 估算

BYOE 默认模型 gpt-4o，每百万输入 token 约 $2.50：

```bash
# 查看当前对话费用
byoe chat → /cost

# 设置模型更便宜
export BYOE_MODEL=deepseek-chat  # ~$0.27/百万 token
```

### 上下文管理

长对话消耗大量 token。BYOE 自动在接近 128K token 时压缩上下文。

如果费用太高：
1. 用便宜的模型（DeepSeek、Qwen）做日常任务
2. 用 `/save` + `/load` 切分长对话，不要在一个会话里堆积太多
3. 定时任务用 `--max-runs` 限制执行次数

### Hooks 计费

```python
@on("llm.response")
def bill_client(model, input_tokens, output_tokens, **_):
    cost = estimate_cost(model, input_tokens, output_tokens)
    redis.incrbyfloat(f"usage:{client_id}:cost", cost)
```

适合 SaaS 场景按量计费。

---

## 4. 常见问题

### Q1: 安装后 `byoe` 命令找不到？

```bash
# 确认安装成功
pip list | grep byoe

# 可能是 PATH 问题
python -m byoe --version
```

### Q2: API 调用报错 401 / 403？

```bash
# 检查环境变量
echo $OPENAI_API_KEY  # macOS/Linux
echo %OPENAI_API_KEY%  # Windows

# 运行诊断
byoe doctor
```

### Q3: AI 回复太慢？

- 流式模式 `stream()` 比非流式 `chat()` 感觉更快（首字延迟更短）
- 换更快的模型（DeepSeek、GPT-4o-mini）
- 减少上下文长度（`/reset` 重置）
- 检查网络延迟（`byoe doctor`）

### Q4: AI 乱用工具 / 执行错误命令？

- 设置 `BYOE_BASH_TIMEOUT` 限制执行时间
- 用 Tool 的权限系统设为 `confirm` 模式
- 在 `system` prompt 中加入安全规则
- 定期 `byoe sober` 扫描代码质量

### Q5: 怎么让 AI 更懂我的项目？

1. 在项目目录下创建 `INSTRUCTIONS.md`（AI 自动加载）
2. 配置 `crew.yaml` 设置项目规范
3. 创建项目专属的技能（Skills）
4. 用 `/save` 保存好的对话示例

### Q6: 团队怎么共享技能和配置？

```bash
# 技能目录直接做 git 仓库
cd ~/.byoe/skills
git init
git remote add origin git@github.com:team/byoe-skills.git
git push

# 其他成员
git clone git@github.com:team/byoe-skills.git ~/.byoe/skills
```

### Q7: BYOE 和 Copilot / Cursor 怎么选？

| 场景 | 推荐工具 |
|------|---------|
| 日常写代码需要补全 | Copilot |
| 需要 IDE 深度集成 | Cursor |
| 自动化任务 / CI/CD | **BYOE** |
| 多人团队协作开发 | **BYOE Crew** |
| 定时任务 / 无人值守 | **BYOE Loop** |
| 自定义工作流 | **BYOE Python API** |

不是替代关系，可以同时使用。

---

## 5. 从 Demo 到生产的检查清单

```
□ 安全
  □ API Key 使用环境变量，不硬编码
  □ Bash 工具设置了超时（BYOE_BASH_TIMEOUT）
  □ 关键操作用 git 管理，可回滚
  □ 多人使用时开启限速（BYOE_CHAT_RATE_LIMIT）

□ 成本
  □ 选择了性价比合适的模型
  □ 长对话定期 /save + /reset
  □ 配置了 Hook 计费（可选）

□ 工程化
  □ 项目配置了 crew.yaml
  □ 团队 Skills 用 git 共享
  □ 重要项目配置了 INSTRUCTIONS.md
  □ CI/CD 集成了 byoe loop --once

□ 质量
  □ 定期运行 byoe sober 扫描
  □ Crew 的 verify 阶段有测试命令
  □ 重要变更经过 Crew 的 Plan → Run → Release 流程
```

---

## 6. 要点总结

- 安全第一：限时、限权、限速，git 兜底
- 成本控制：选对模型、及时清理上下文、Hooks 计费
- 团队协作：Skills 共享、crew.yaml 配置、INSTRUCTIONS.md 规范
- 生产化：PDEVI 流程、CI/CD 集成、sober 质量扫描
- BYOE 和 Copilot/Cursor 不是二选一，可以组合使用

---

📎 完整文档：[故障排查](../../docs/04-config/TROUBLESHOOTING-ZH.md)
📎 非研发场景：[PLAYBOOK-NONDEV-ZH.md](../../docs/04-config/PLAYBOOK-NONDEV-ZH.md)

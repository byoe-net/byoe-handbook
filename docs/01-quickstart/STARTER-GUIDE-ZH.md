# BYOE 新手上手指南（30 分钟）

> 适用版本：v0.8.0+

本指南目标：30 分钟内完成从安装到首次稳定运行，并体验 skills、crew、swarm、loop 的完整闭环。

---

## 1. 安装与环境检查（5 分钟）

```bash
pip install -U byoe
byoe --version
```

推荐最小环境变量（示例 DeepSeek 兼容 OpenAI 接口）：

```bash
# Linux/macOS
export OPENAI_API_KEY=sk-xxx
export OPENAI_BASE_URL=https://api.deepseek.com
export BYOE_MODEL=deepseek-chat

# Windows PowerShell
$env:OPENAI_API_KEY="sk-xxx"
$env:OPENAI_BASE_URL="https://api.deepseek.com"
$env:BYOE_MODEL="deepseek-chat"
```

可选：运行健康检查。

```bash
byoe doctor
```

---

## 2. 第一个可运行项目（8 分钟）

```bash
mkdir demo-byoe
cd demo-byoe
byoe init
```

创建变更计划并执行：

```bash
byoe plan first-change
byoe run
```

完成后查看进度：

```bash
byoe status
```

归档成果：

```bash
byoe release
```

---

## 3. Web 模式与统一调度（7 分钟）

启动 Web：

```bash
byoe web
```

建议在 Web 中完成以下操作：

1. 新建一条对话并执行一个文件修改任务
2. 打开 TaskPanel，新增一个 `interval:5m` 任务
3. 打开 Auto heartbeat，设置 300 秒
4. 在 TaskPanel 试用任务搜索、状态筛选、排序

你会看到：

- 任务状态由服务端统一管理
- `Auto` 与任务数与后端状态保持一致
- 调度失败会按重试策略退避

---

## 4. 体验 skills（4 分钟）

目标：让系统记住你团队常用执行风格。

在对话中执行：

```text
/skill mine
```

然后查看技能面板，确认是否出现新沉淀的技能。

建议新增一个手工技能：

- 名称：`review-strict`
- 说明：代码评审优先列问题，再给建议

激活技能后重复执行一次相同任务，比较输出风格差异。

---

## 5. 体验 swarm 与 loop（6 分钟）

### Swarm（并行协作）

当任务可拆分为多个子目标时，使用 swarm 协作流（参考 `SWARM-GUIDE-ZH.md`）：

- 需求拆解
- 并行执行
- 汇总交付

### Loop（时间驱动）

```bash
byoe loop -p "检查未处理事项并输出今日计划" --every 30m
```

一次性定时：

```bash
byoe loop -p "生成今日日报" --at 18:00 --max-runs 1
```

---

## 6. 你应该掌握的最小命令集

```text
byoe init
byoe plan <name>
byoe run
byoe status
byoe release
byoe web
byoe loop -p "..." --every 30m
byoe sessions
```

---

## 7. 下一步建议

1. 阅读完整手册：`USER-MANUAL-ZH.md`
2. 深入技能系统：`SKILLS-GUIDE-ZH.md`
3. 深入群智协作：`SWARM-GUIDE-ZH.md`
4. 非研发场景落地：`PLAYBOOK-NONDEV-ZH.md`
5. 遇到问题先查：`TROUBLESHOOTING-ZH.md`

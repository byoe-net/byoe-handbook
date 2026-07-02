# 技能系统：给 AI 注入专属经验

> 一句话摘要：Skills 是 BYOE 的「记忆」—— 让 AI 记住过去的经验，下次遇到同类问题自动复用。

---

## 1. 场景引入

你有没有这种体验：

让 AI 帮你写代码，每次都要重复交代：
> 「接口返回格式统一用 `{code, data, message}`」
> 「数据库字段要有 `id, created_at, updated_at`」
> 「测试覆盖率不能低于 80%」

AI 这次记住了，下次启动**又忘了**。

BYOE 的技能系统就是为了解决这个问题。

---

## 2. 两种技能形态

BYOE 的技能分为两种：

```
技能 (Skills)
├── 认知型 (JSON)   → 注入「思考规范」
└── 动作型 (Python) → 注入「执行能力」
```

### 认知型技能（Prompt Skills）

本质是一段 JSON，告诉 AI：「当你遇到 XX 场景时，按以下规范来。」

```json
{
  "name": "api-reviewer",
  "description": "RESTful API 设计审查专家",
  "trigger": "审查API",
  "instructions": "审查 API 设计时，必须检查：
    1. URL 使用名词复数，禁止动词
    2. 正确使用 HTTP 方法 (GET/POST/PUT/DELETE)
    3. 统一响应格式 {code, data, message}
    4. 分页参数标准化 (page, page_size)",
  "created_at": "2026-06-27T10:00:00Z"
}
```

保存到 `~/.byoe/skills/api-reviewer.json`，下次你说「审查API」时，AI 自动遵守这套规范。

### 动作型技能（Python Skills）

本质是一个 `.py` 文件，教 AI 做一件事情：

```python
# ~/.byoe/skills/desktop_notify.py
import platform, subprocess

def run(title: str = "BYOE 提醒", message: str = "", **kwargs) -> str:
    """发送桌面系统通知。"""
    # ... 跨平台实现
    return f"✅ 已发送通知：{title}"
```

AI 可以像调用内置工具一样调用它。

---

## 3. Trigger 自动注入

认知型技能的核心机制是 **trigger（触发词）**：

```
用户说 "帮我审查API接口设计"
                ↓
引擎扫描 ~/.byoe/skills/*.json
发现 api-reviewer.json 的 trigger = "审查API"
                ↓
api-reviewer.json 的 instructions 自动注入 AI 上下文
                ↓
AI 回复时自动遵循 RESTful 规范
```

> v0.7.2 起，Trigger 匹配是**确定性行为**，不再依赖 AI 自主感知。

当一个对话中命中多个技能时，多个 `instructions` **叠加注入**。对话结束后自动恢复原始 prompt，不影响下一轮。

---

## 4. 让 AI 自己沉淀技能

BYOE 最强大的特性：**AI 可以在工作中自己创造技能**。

### 场景：沉淀代码审查规范

你和 AI 经过多轮打磨，建立了一套数据库设计规范：

```
You: 请把我们刚才总结的数据库设计规范保存为技能，
     触发词设为 "设计新表"
```

AI 会自动：
1. 回顾聊天上下文，提取规范要点
2. 封装为 JSON 格式
3. 调用 `save_skill` 写入 `~/.byoe/skills/`
4. 下次遇到「设计新表」自动生效

### 场景：沉淀自动化脚本

AI 写了一段环境诊断脚本并跑通了：

```
You: 把这个环境自检流程封装成技能 project_doctor
```

AI 会自动：
1. 将散装代码重构为 `def run(**kwargs):` 格式
2. 写入 `~/.byoe/skills/project_doctor.py`
3. 以后你说「调用 project_doctor 排查」，直接可用

---

## 5. 管理与共享

所有技能保存在 `~/.byoe/skills/`：

```bash
# 查看已安装技能
ls ~/.byoe/skills/

# 团队共享：整个目录做成 git 仓库
cd ~/.byoe/skills
git init
git remote add origin git@github.com:team/skills.git
git push
```

Web UI 中也有可视化管理面板：

> 插入 Web UI Skills 面板截图

| 操作 | CLI | Web UI |
|------|-----|--------|
| 查看 | `ls ~/.byoe/skills/` | Skills 面板 |
| 激活 | `/skill api-reviewer` | 点击开关 |
| 导入 | 复制文件到目录 | 粘贴 JSON |
| 删除 | `rm ~/.byoe/skills/xxx.json` | 点击删除 |

### 自动淘汰机制

技能上限默认 50 个。超出时自动淘汰**最久未使用**的技能：

```json
{
  "name": "api-reviewer",
  "use_count": 23,
  "last_used": "2026-06-28T14:33:00Z"
}
```

高频使用的核心技能自然保留，低频的一次性技能自动清理。

---

## 6. 要点总结

- 两种技能：**JSON 认知型**（思考规范）+ **Python 动作型**（执行能力）
- Trigger 触发词自动注入：说到「审查API」→ 自动加载审查规范
- AI 可以**自己创造技能**：`把这个流程保存为技能`
- 上限 50 个，LRU 自动淘汰不常用的
- 团队共享：`~/.byoe/skills/` 直接做 git 仓库

## 下期预告

下一篇进入开发者专区：**Python API 编程** —— 把 BYOE 嵌入你自己的应用。

---

📎 完整参考：[SKILLS-GUIDE-ZH.md](../../docs/02-user-guide/SKILLS-GUIDE-ZH.md)
📎 动手教程：[SKILLS-TUTORIAL.md](../../tutorials/SKILLS-TUTORIAL.md)
📎 示例代码：[demos/02-skills/](../../demos/02-skills/)

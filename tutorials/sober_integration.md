# 结合 BYOE 与 Sober Coding 的最佳实践

在 AI "狂飙突进"式的编程（Vibe coding）之后，不可避免地会留下死代码、逻辑重复、上帝类等"坏味道代码"（Technical debt）。通过将 `BYOE`（全权执行管家）与 `Sober Coding`（AI 代码质量静态检测工具）结合，你可以打造一个闭环的 **"先开发 → 后自纠"自动化修复工作流**。

这里有三种由简到繁的结合方式：

---

## 方式零（推荐）：直接使用 BYOE 内置的 `sober_scan` 工具

**无需任何外部安装**。BYOE v0.8.0 已将 Sober 扫描能力作为原生工具 `sober_scan` 默认提供。只要你安装了 `byoe`，就拥有了它。

### 使用方式

在 `byoe chat` 或 `byoe web` 对话框中直接发令：

🗣：`"用 sober_scan 扫描当前项目，列出所有 High 和 Medium 级别问题，然后逐一修复它们。"`

🤖 **BYOE 将如何执行**：
1. 直接在进程内调用内置 `sober_scan` 工具（**无需 Shell、无需 node、无需网络**）；
2. 返回结构化隐患报告（`HIGH dead-code Unused Export src/utils.ts:16` 等格式）；
3. AI 读懂报告后，自动调用 `read_file` + `edit_file` 逐条清理。

### 将扫描固化为 Skill（一键触发）

告诉 AI："把刚才的扫描+修复流程保存为一个叫 `code-purify` 的技能，触发词设为'代码净化'。"

之后每次只需说「**代码净化**」，AI 便会自动触发完整流程。

> **与方式二相比**：方式零不依赖任何外部工具，适合纯 BYOE 环境；若你的项目使用 TypeScript/JavaScript 且已安装 Node.js，方式一可借助 sober CLI 获得更精细的 AST 级分析。



---

## 方式一：让 BYOE 调用外部 sober CLI 进行 AST 级深度扫描（Node.js 项目）

> 前提：你的机器已安装 Node.js，且项目以 TypeScript/JavaScript 为主。此方式可获得更精细的 AST 语法树分析，适合 TS 前端项目。

原方式不变，通过 Bash 调用 `sober scan . --ci` 并让 BYOE 读懂报告后自动修复。

## 方式一（兼容方案）：通过命令行调用 BYOE 内置 sober

如果你希望在脚本中显式触发扫描，可直接调用 BYOE 自带命令：

```bash
byoe sober . --format md --out .sober_report.md
```

然后让 BYOE 读取报告并自动修复 High/Medium 项。

---

## 方式二（进阶）：沉淀为 BYOE 的长效 "Code Review" 动作技能 (Skill 集成)

这是一种进阶做法——我们将这些“固定动作”固化为 BYOE 系统中的一个永久 Python Skill 工具，让这种代码净化能力能随时招之即来。

### 1. 编写与加载 `sober_purify.py` 技能
在你的 `~/.byoe/skills/` 目录下创建一个 `sober_purify.py`：

```python
import os
import subprocess
import json

def run(target_dir: str = ".", **kwargs) -> str:
    """
    自动对项目进行
    当用户要求做代码净化、或者是做提交前的大范围重构前，请先调用此方法拿到项目各个文件的隐患清单。
    这个工具会返回一份死代码和架构报错的精简分析表。
    """
    try:
        # 直接调用 byoe 内置 sober 子命令，无需额外安装 sober-coding 目录
        result = subprocess.run(
            ["byoe", "sober", target_dir, "--format", "md"], 
            capture_output=True, 
            text=True, 
            cwd=os.path.abspath(target_dir)
        )
    except FileNotFoundError:
         return "❌ 未检测到 byoe 命令，请先安装 byoe。"

    # 将格式化后的报告返回给大模型上下文
    report_text = result.stdout.strip()
    if not report_text:
        return "✅ 恭喜，所在工程当前没有发现典型的 AI 坏味道报错！代码非常干净！"
        
    return f"⚠️ 发现了以下 AI 坏味道债务，请分析此清单并针对性修复源文件：\n\n{report_text}"
```

### 2. 闭环体验
平时在敲完了几十个增删改代码后，在终端说：
🗣：`“执行全仓体检并修复。”`

AI 会自动触发 `skill_sober_purify` 工具，系统会在后台悄无声息跑完静态规则引擎检查，接着 AI 根据回传的隐患列表，精准去每个死文件里做截肢级清理。而且最重要的是，这一切几乎无需太多 LLM 推理（全依靠确定的正则检测找问题），省流又精确。
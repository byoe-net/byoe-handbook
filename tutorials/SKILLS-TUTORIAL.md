# BYOE 动态技能开发教学 (从入门到实战)

> 这是一份为新手准备的使用和开发 BYOE Python 动作技能 (Dynamic Skills) 的实战手册。
> 我们将以打通您本地体验极佳的 Markdown 编辑器 **MarkFlow** 为例，演示如何让大模型变成你手下的自动化管家。

---

## 🧐 1. 什么是动作型技能 (Python Tool Skills) 与 认知型技能 (JSON Prompt Skills)？

BYOE 极度追求“轻装上阵”，抛弃了复杂的多文件文件夹配置模式。无论是能力扩展还是思维方式配置，在 BYOE 体系中**只需要一个文件**即可搞定。它们按照类型主要分为两种：

1. **认知型技能 (JSON Prompt Skills)**：
   本质是一个设定了角色的“思维/规范模板”。当你在给定的任务里提到特定的词语，AI 就会加载这个 JSON 里规定好的经验法则和工作要求。
2. **动作型技能 (Python Tool Skills)**：
   通过一个 `.py` 脚本文件，依靠 Python 原生代码教 AI 怎么调用操作系统底层的能力（网络、GUI、工具控制等）。

---

## 🧠 2. 实战案例一：导入一个网上的 JSON 认知型技能

**场景痛点**：你想让 AI 在帮你写后端接口时，严格按照一套专业的 RESTful 规范来，避免它每次都随心所欲生成不同的数据包裹格式。

### 第一步：获取 JSON 配置文件

由于只需要单个文件，从别人那里下载或拷贝这个技能极其简单。
例如，你在社区拿到了一份（我们打包在这份教程同目录下的 `api_reviewer.json`），它的内容长这样：
```json
{
  "name": "api-reviewer",
  "description": "严格的 RESTful API 设计审查专家",
  "instructions": "当你负责审查或设计 API 接口时，请务必严格遵守以下企业级规范：\n1. 【动词禁用】URL 路径中绝对不能包含动词，必须使用名词复数...\n(省略后面的几千字规范)",
  "trigger": "审查API",
  "created_at": "2026-06-27T10:00:00Z",
  "builtin": false
}
```

### 第二步：如何安装并使用网上的 JSON 技能？

**方法一（终端界面 UI 导入）：**
启动通过浏览器访问带图形界面的 BYOE Dashboard -> 点击导航寻找 "Skills" -> 点击 "Import/新建" -> 将网上下载好的这段 JSON 文本完全复制粘贴进去 -> 保存！

**方法二（命令行手工拷贝法）：**
直接把 `api_reviewer.json` 复制扔进你的 `~/.byoe/skills/` 文件夹下。

### 第三步：见证它的使用效果

启动终端运行 `byoe chat`。
现在，当你的需求包含触发词 `"审查API"` 这个字眼时：
🗣 `“帮我审查API结构: 后端现在写了一个接口是 GET /getUserInfo?userId=123”`

🤖 AI 在内部会提取到触发词，系统底层瞬间抓取该规则文件的 `instructions` 并组装给大脑。
于是 AI 就会回复（大意）：
>`❌ 违规提醒：【动词禁用】发现动词 “getUserInfo”，按标准应该优化为 “GET /api/users/123”。`

至此，外部的架构经验彻底化为了你专属数字大脑的一部分。

---

## 🚀 3. 实战案例二：导入让 AI 把总结长文用 MarkFlow 打开的动作技能

**场景痛点**：AI 帮你生成了一篇非常优秀的项目技术架构总结，在黑乎乎的终端面板看体验很一般。你有一个前端非常优雅的 `MarkFlow` 页面，希望它完成生成后，直接把结果甩进这个编辑器里看。

### 第一步：编写技能代码

创建一个名为 `preview_markflow.py` 的脚本，放在系统的 `~/.byoe/skills/` 目录中。
（*在本次演示中，我们将代码打包在这份教学同目录下的 `preview_markflow.py` 中*）。

编写动态技能代码只需遵守一个核心约定：**必须提供一个入口函数 `def run(**kwargs) -> str:`**

代码如下：
```python
import os
import webbrowser
import subprocess
from pathlib import Path

#入口函数 `run` 将由 AI 调用，参数 `markdown_text` 就是模型智能填写的文本。
def run(markdown_text: str, **kwargs) -> str:
    """
    专门为 BYOE 编写的外挂技能。
    功能：接收生成的 Markdown 文本，并唤起本地的 MarkFlow 进行预览排版。
    """
    if not markdown_text:
        return "❌ 错误：缺少文本。"

    # 将内容利用终端命令写入剪贴板 (Windows 原生命令)
    subprocess.run(['clip'], input=markdown_text, text=True)
        
   # 定位本地的 Web 编辑器路径（优先读取环境变量）
   markflow_env = os.environ.get("BYOE_MARKFLOW_PATH", "").strip()
   markflow_path = Path(markflow_env) if markflow_env else Path("../MarkFlow/index.html")
   markflow_path = markflow_path.expanduser().resolve()
        
    # 唤起本地浏览器
    webbrowser.open(f"file:///{markflow_path.as_posix()}")
    
    # 必须返回字符串，AI 根据返回值确认操作是否成功。
    return "✅ 唤醒成功！已复制到剪贴板，可前往浏览器直接 Ctrl+V 粘贴啦！"
```

> 💡 **小贴士**：函数头部的 `"""docstring"""` (代码注释) 非常关键！它将被 BYOE 自动解析为参数说明书教大模型怎么用。所以请在这段注释里清楚描述这个技能的功能、以及参数是什么类型。

建议先配置环境变量，避免硬编码路径：

```bash
# Linux/macOS
export BYOE_MARKFLOW_PATH=/absolute/path/to/MarkFlow/index.html

# Windows PowerShell
$env:BYOE_MARKFLOW_PATH="D:\\tools\\MarkFlow\\index.html"
```

### 第二步：安装技能

要让这段代码生效，有三种方式：
1. **手工复制**：你把上述 `preview_markflow.py` 手动拷贝/移动到你系统用户的 `~/.byoe/skills/` 目录下。
2. **让它自己写（魔法般体验）**：如果你懒得复制，你可以把这段代码连同需求丢给控制台的大模型，说：`“请把这段代码保存为一个名为 preview_markflow 的 Python 技能并在本地注册生效”`。大模型将自己调用底层的 `create_skill` 完成自身强化！

### 第三步：见证奇迹时刻

完成第一、二步后，当你打开终端进入工作态（`byoe chat`）时：

1. **下达模糊命令**：
   🗣 `“帮我写一份教新手使用 BYOE 的文档大纲，写好以后，用 preview_markflow 在我的本地编辑器里打开。”`

2. **AI 理解与行动**：
   - 🤖 它首先会运用大语言能力构思写出了一份漂亮的大纲文本。
   - 🤖 然后，它去检查可用的工具列表，发现了一个动态工具 `skill_preview_markflow`。
   - 🤖 它将刚写好的文本作为 `markdown_text` 参数调用这个函数。
   - 💻 你的浏览器忽然**自动弹开**了 `MarkFlow` 编辑页面。
   - 🤖 AI 最后回复：`“我已经成功帮您打开。文档已经放在你的剪贴板中了，按下 Ctrl+V 就能获得排版极佳的效果！”`

这就是赋予系统动作型技能的魅力。

---

## 🎯 4. 开发进阶总结

在自己书写技能时，请谨记以下三点：
1. **单一职责原则**：不要写包含 1000 行包罗万象的脚本。建议像 Linux 哲学一样：发邮件专门一个，传图片专门一个。
2. **强健的异常拦截**：技能会在没有人工保护的后台被调用，务必写好 `try...except...`。如果成功了，你一定要在 `return` 里告诉模型：`"✅ 操作成功，拿到的结果是 XXX"`；如果失败了，告诉模型：`"❌ 报错拉，错误原因是 YYYY"`。
3. **第三方库依赖**：如果你技能里 `import pandas`，千万确信你当前启动 BYOE 的 Python 环境里已经 `pip install pandas`。

赶紧享受让专属 AI 越来越强大的乐趣吧！
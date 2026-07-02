# 5 分钟装好你的 AI 工程师

> 一句话摘要：`pip install byoe`，两行环境变量，你的 AI 工程师就上岗了。

---

## 1. 场景引入

你有没有遇到过这种情况：

想尝试一个新 AI 工具：
1. 打开官网 → 注册账号 → 等待审核 → 绑定信用卡
2. 下载客户端 → 安装依赖 → 配了半天跑不起来
3. 发现必须用他们的云服务，代码不能离网

BYOE 的安装流程恰好相反。

---

## 2. 安装

### 前提条件

- Python 3.10+
- 一个 OpenAI 兼容的 API Key（DeepSeek / OpenAI / Qwen / Ollama 均可）

### 安装命令

```bash
pip install byoe
```

没了。是的，就这么一句。

验证安装：

```bash
byoe --version
# 输出: byoe 1.0.0
```

```python
# 也可以从 Python 验证
python -c "import byoe; print(byoe.__version__)"
# 输出: 1.0.0
```

### 从本地安装

如果你下载了本仓库，也可以从本地 wheel 安装：

```bash
pip install wheel/byoe-1.0.0-py3-none-any.whl
```

适合内网环境或固定版本控制的场景。

---

## 3. 配置环境变量

BYOE 默认从环境变量读取配置。最少需要设置 API Key 和模型名：

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-xxx"
$env:OPENAI_BASE_URL = "https://api.deepseek.com"
$env:BYOE_MODEL = "deepseek-chat"

# macOS / Linux
export OPENAI_API_KEY=sk-xxx
export OPENAI_BASE_URL=https://api.deepseek.com
export BYOE_MODEL=deepseek-chat
```

### 常用 LLM 提供商配置

| 提供商 | `OPENAI_BASE_URL` | 推荐模型 |
|--------|-------------------|---------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen3-plus` |
| Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-128k` |
| Ollama（本地） | `http://localhost:11434/v1` | `qwen2.5-coder:32b` |

也可以写入 `~/.byoe/.env` 文件，BYOE 会自动加载：

```dotenv
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.deepseek.com
BYOE_MODEL=deepseek-chat
```

---

## 4. 运行健康检查

配置完成后，运行诊断命令验证一切正常：

```bash
byoe doctor
```

如果输出包含 `✅` 标识，说明安装成功。

---

## 5. 第一个对话

### 终端模式

```bash
byoe chat
```

你会看到一个交互式终端，输入 `你好`，AI 会回复你。

```
╭─ BYOE Chat ───────────────────────────────╮
│ 输入 /help 查看命令列表                      │
│ 输入 /exit 退出                            │
╰────────────────────────────────────────────╯
You: 用一句话解释什么是向量数据库
Assistant: 向量数据库是一种专门存储和检索高维向量数据的数据库...
```

### Python API 模式

```python
import byoe

agent = byoe.create_agent()
response = agent.chat("用 Python 写一个冒泡排序")
print(response)
```

### Web 界面

```bash
byoe web
```

浏览器打开 `http://localhost:7860`。

---

## 6. 要点总结

- 安装：`pip install byoe`
- 最少配置：`OPENAI_API_KEY` + `BYOE_MODEL`
- 支持所有 OpenAI 兼容的 LLM 提供商
- 三种使用方式：`byoe chat` / `byoe web` / `import byoe`
- 诊断命令：`byoe doctor`

## 下期预告

下一篇我们深入 CLI 模式：**如何用一句话让 AI 改代码、查文件、跑命令**。

---

📎 完整文档：[配置参考](../../docs/04-config/configuration.md)
📎 示例代码：[01_quickstart.py](../../demos/01-api/01_quickstart.py)

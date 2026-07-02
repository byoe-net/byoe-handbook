"""BYOE 结构化输出 (response_model)

通过 response_model= 参数让 Agent 返回 Pydantic 模型实例，
而不是原始字符串。

BYOE 会自动：
  1. 将 JSON Schema 注入本轮系统提示
  2. 剥离模型可能输出的 Markdown 代码块包裹
  3. 用 pydantic 验证并返回模型实例（验证失败时回退到 dict）

安装依赖：
    pip install byoe pydantic

运行：
    python 03_structured_output.py
"""

from pydantic import BaseModel, Field
import byoe

agent = byoe.create_agent()

# ── 示例 1：代码审查报告 ──────────────────────────────────────────────────────

class CodeReview(BaseModel):
    score: int = Field(description="代码质量评分 0-100")
    issues: list[str] = Field(description="发现的问题列表")
    suggestions: list[str] = Field(description="改进建议")
    verdict: str = Field(description="总体评价：pass / warn / fail")

code = """
def get_user(id):
    import sqlite3
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {id}")
    return cursor.fetchone()
"""

review: CodeReview = agent.chat(
    f"请审查以下 Python 代码：\n```python\n{code}\n```",
    response_model=CodeReview,
)

print(f"评分: {review.score}/100")
print(f"判定: {review.verdict}")
print("问题:")
for issue in review.issues:
    print(f"  • {issue}")
print("建议:")
for s in review.suggestions:
    print(f"  → {s}")

print()

# ── 示例 2：信息提取 ──────────────────────────────────────────────────────────

class ExtractedInfo(BaseModel):
    name: str
    role: str
    company: str
    technologies: list[str]

text = "我是李明，在字节跳动担任后端架构师，主要负责 Go 微服务和 Kafka 消息队列的设计。"

info: ExtractedInfo = agent.chat(
    f"从以下文本中提取结构化信息：{text}",
    response_model=ExtractedInfo,
)

print(f"姓名: {info.name}")
print(f"职位: {info.role} @ {info.company}")
print(f"技术栈: {', '.join(info.technologies)}")

print()

# ── 示例 3：stream() 也支持 response_model ───────────────────────────────────

class Summary(BaseModel):
    title: str
    key_points: list[str]
    word_count: int

stream = agent.stream(
    "总结向量数据库的三大核心优势",
    response_model=Summary,
)

# 流式打印 token（token 是未解析的 JSON 文本）
print("生成中: ", end="")
for tok in stream:
    print(".", end="", flush=True)
print()

# 迭代完成后 .result 是解析好的 Summary 实例
summary: Summary = stream.result
print(f"标题: {summary.title}")
print(f"要点: {summary.key_points}")

"""AI 应用模板 03：结构化数据提取器
========================================
用 byoe 的结构化输出（response_model）从非结构化文本中抽取数据。
支持：发票、简历、日程、会议纪要、产品信息等常见场景。

特点：
  - Pydantic v2 模型验证，类型安全
  - 批量处理：一次处理目录中的所有文本文件
  - 输出 JSON / CSV / stdout
  - 失败重试（LLM 幻觉自动修复）

运行：
    python apps/03_structured_extractor.py [--schema invoice] [--input file.txt]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    print("Warning: pydantic not installed. Install with: pip install 'byoe[structured]'")

import byoe


# ─── Pydantic 模型 ──────────────────────────────────────────────────────────

if HAS_PYDANTIC:
    class InvoiceModel(BaseModel):
        """发票信息"""
        invoice_number: str = Field(description="发票号")
        date: str = Field(description="开票日期 (YYYY-MM-DD)")
        vendor: str = Field(description="供应商名称")
        buyer: str = Field(description="买方名称")
        items: list[dict] = Field(default_factory=list, description="商品列表 [{name, qty, unit_price, amount}]")
        subtotal: float = Field(description="小计金额")
        tax: float = Field(default=0.0, description="税额")
        total: float = Field(description="合计金额")
        currency: str = Field(default="CNY", description="货币代码")

    class ResumeModel(BaseModel):
        """简历信息"""
        name: str
        email: Optional[str] = None
        phone: Optional[str] = None
        location: Optional[str] = None
        summary: Optional[str] = Field(None, description="个人简介")
        skills: list[str] = Field(default_factory=list)
        education: list[dict] = Field(default_factory=list, description="[{school, degree, field, year}]")
        experience: list[dict] = Field(default_factory=list, description="[{company, role, duration, highlights}]")
        languages: list[str] = Field(default_factory=list)

    class MeetingNotesModel(BaseModel):
        """会议纪要"""
        meeting_title: str
        date: str
        participants: list[str]
        agenda: list[str] = Field(default_factory=list)
        decisions: list[str] = Field(default_factory=list, description="已做出的决策")
        action_items: list[dict] = Field(default_factory=list, description="[{owner, task, deadline}]")
        next_meeting: Optional[str] = None

    SCHEMA_MAP = {
        "invoice": InvoiceModel,
        "resume": ResumeModel,
        "meeting": MeetingNotesModel,
    }
else:
    SCHEMA_MAP = {}


# ─── 提取函数 ────────────────────────────────────────────────────────────────

def extract(text: str, schema_name: str, retries: int = 2) -> dict:
    """Extract structured data from text using the specified schema.

    Args:
        text:        Raw text to parse.
        schema_name: One of: invoice, resume, meeting
        retries:     How many times to retry on validation failure.

    Returns:
        Extracted data as a dict.
    """
    if not HAS_PYDANTIC:
        raise RuntimeError("pydantic required: pip install 'byoe[structured]'")

    model_cls = SCHEMA_MAP.get(schema_name)
    if model_cls is None:
        raise ValueError(f"Unknown schema '{schema_name}'. Available: {list(SCHEMA_MAP)}")

    system = (
        "You are a precise data extraction engine. "
        "Extract all available information from the provided text into the requested schema. "
        "Use null/empty for missing fields. Do not hallucinate values."
    )
    agent = byoe.create_agent(system=system, tools=[])

    prompt = f"Extract {schema_name} data from this text:\n\n{text}"

    for attempt in range(retries + 1):
        try:
            result: BaseModel = agent.chat(prompt, response_model=model_cls)
            return result.model_dump()
        except Exception as e:
            if attempt == retries:
                raise
            # Reset agent state and retry with hint
            agent.reset()
            prompt = (
                f"Extract {schema_name} data. Previous attempt failed: {e}. "
                f"Be very strict about types and required fields.\n\n{text}"
            )

    raise RuntimeError("Extraction failed after all retries")


def batch_extract(input_dir: Path, schema_name: str) -> list[dict]:
    """Process all .txt files in a directory."""
    results = []
    for txt_file in sorted(input_dir.glob("*.txt")):
        print(f"  Processing {txt_file.name}…", end=" ", flush=True)
        try:
            text = txt_file.read_text(encoding="utf-8", errors="replace")
            data = extract(text, schema_name)
            data["_source_file"] = txt_file.name
            results.append(data)
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
            results.append({"_source_file": txt_file.name, "_error": str(e)})
    return results


# ─── demo data ───────────────────────────────────────────────────────────────

DEMO_INVOICE = """
Invoice #INV-2025-001
Date: March 15, 2025

From: Acme Technologies Ltd.
      123 Tech Street, Beijing 100000

To: Global Corp Inc.
    456 Business Ave, Shanghai 200000

Items:
  - Software License (Enterprise) × 1  ¥50,000.00
  - Support & Maintenance × 12 months  ¥24,000.00
  - Training Sessions × 3              ¥9,000.00

Subtotal: ¥83,000.00
VAT (13%): ¥10,790.00
Total Due: ¥93,790.00

Payment due: April 15, 2025
"""

DEMO_MEETING = """
Weekly Engineering Sync — 2025-03-20

Attendees: Alice (PM), Bob (Backend), Carol (Frontend), Dave (QA)

Agenda:
1. Sprint review
2. Production incident post-mortem
3. Q2 roadmap planning

Decisions:
- Roll back payment service to v2.1 until root cause is identified
- Freeze feature deployments until Friday
- Allocate 2 sprints for tech debt cleanup

Action Items:
- Bob: Write incident post-mortem by Wednesday
- Carol: Fix checkout flow bug (JIRA-1234) by EOD today
- Dave: Add integration tests for payment service by next Monday

Next meeting: March 27, 2025 at 10:00 AM
"""


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Structured data extractor powered by byoe")
    parser.add_argument("--schema", default="invoice", choices=list(SCHEMA_MAP or ["invoice"]),
                        help="Extraction schema")
    parser.add_argument("--input", default=None, help="Input text file (default: use demo data)")
    parser.add_argument("--batch-dir", default=None, help="Process all .txt files in a directory")
    parser.add_argument("--output", default="json", choices=["json", "csv"], help="Output format")
    args = parser.parse_args()

    if not HAS_PYDANTIC:
        print("Error: pydantic is required. Run: pip install 'byoe[structured]'")
        sys.exit(1)

    print(f"结构化提取器 · Schema: {args.schema}")

    if args.batch_dir:
        results = batch_extract(Path(args.batch_dir), args.schema)
        if args.output == "csv":
            import csv, io
            if results:
                buf = io.StringIO()
                w = csv.DictWriter(buf, fieldnames=results[0].keys())
                w.writeheader(); w.writerows(results)
                print(buf.getvalue())
        else:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    # Single file or demo
    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        print("(使用内置演示数据，传入 --input <file> 处理真实数据)")
        text = DEMO_INVOICE if args.schema == "invoice" else DEMO_MEETING

    result = extract(text, args.schema)
    print("\n提取结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

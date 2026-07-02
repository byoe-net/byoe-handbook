"""byoe skill: api_spec_gen
用途：从自然语言需求或现有代码生成 OpenAPI 3.1 规范 + Pydantic 模型。

安装：
    cp skills/api_spec_gen.py ~/.byoe/skills/api_spec_gen.py

Agent 内使用：
    load_skill("api_spec_gen")
    skill_api_spec_gen(args_json='{"source": "需求描述或 .py 文件路径", "output": "openapi"}')
"""

from __future__ import annotations

import sys
from pathlib import Path


def run(
    source: str,
    output: str = "openapi",     # "openapi" | "pydantic" | "both"
    title: str = "My API",
    version: str = "1.0.0",
    framework: str = "fastapi",  # "fastapi" | "flask" | "django"
) -> str:
    """Generate API specifications from a description or existing code.

    Args:
        source:    Natural language requirement string OR path to a .py file.
        output:    What to generate: openapi (YAML spec), pydantic (model code), both.
        title:     API title for the OpenAPI spec.
        version:   API version string.
        framework: Target framework for generated code snippets.

    Returns:
        Generated OpenAPI YAML and/or Pydantic model code as a string.
    """
    import byoe

    # Detect if source is a file path
    src_path = Path(source).expanduser()
    if src_path.exists() and src_path.suffix in (".py", ".txt", ".md"):
        source_text = src_path.read_text(encoding="utf-8")
        source_label = f"Existing code from {src_path.name}"
    else:
        source_text = source
        source_label = "Requirements description"

    output_instructions = {
        "openapi": (
            "Generate a complete OpenAPI 3.1 YAML specification. "
            "Include paths, request/response schemas, and examples."
        ),
        "pydantic": (
            f"Generate Python Pydantic v2 models and {framework} route handlers. "
            "Include request/response models with field validators."
        ),
        "both": (
            f"Generate BOTH:\n"
            f"1. A complete OpenAPI 3.1 YAML spec\n"
            f"2. Python Pydantic v2 models + {framework} route stubs"
        ),
    }

    system = (
        "You are an expert API designer. Produce clean, idiomatic, production-ready output. "
        "Follow REST best practices. Use snake_case for JSON fields."
    )
    prompt = (
        f"{source_label}:\n\n{source_text}\n\n"
        f"API Title: {title}  Version: {version}\n\n"
        f"{output_instructions.get(output, output_instructions['openapi'])}"
    )

    agent = byoe.create_agent(system=system, tools=[])
    return agent.chat(prompt)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python api_spec_gen.py <source_or_file> [output] [title] [version]")
        sys.exit(1)
    source = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "openapi"
    title = sys.argv[3] if len(sys.argv) > 3 else "My API"
    version = sys.argv[4] if len(sys.argv) > 4 else "1.0.0"
    print(run(source=source, output=output, title=title, version=version))

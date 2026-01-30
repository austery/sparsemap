from __future__ import annotations

import json
import logging
from typing import List

from google import genai
from google.genai import types
from pydantic import ValidationError

from sparsemap.core.config import get_settings
from sparsemap.domain.models import Graph


logger = logging.getLogger(__name__)


def build_prompt(contents: List[dict]) -> str:
    prompt = """你是一位资深的教学专家和知识架构师。请分析以下课程内容，提取逻辑骨架和知识依赖关系。

要求：
1. **识别主线逻辑**：课程的核心思想、步骤流程、关键主张（type: "main"）
2. **识别支线知识**：达成主线目标所需的技术工具、背景概念（type: "dependency"）
3. **最佳实践校验**：结合行业最佳实践，若文本遗漏关键步骤，请补充节点并标记 type 为 "suggested_best_practice"
4. **解释关系**：为每个依赖关系说明“为什么需要这个工具/概念”，节点提供 reason 字段

返回严格的 JSON 格式：
{
  "nodes": [
    {
      "id": "n1",
      "label": "节点名称",
      "type": "main" | "dependency" | "suggested_best_practice",
      "priority": "critical" | "optional",
      "reason": "节点出现的原因",
      "source": "url1" | "text1",
      "description": "节点描述"
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n2",
      "type": "depends_on" | "references" | "implements",
      "reason": "为什么需要这个依赖"
    }
  ],
  "summary": "整体课程逻辑的简要总结"
}

内容：
"""
    for content in contents:
        prompt += f"\n\n=== 来源 {content['source']} ===\n{content['text']}\n"
    return prompt


def _extract_json(payload: str) -> str:
    if "```json" in payload:
        return payload.split("```json")[1].split("```")[0].strip()
    if "```" in payload:
        parts = payload.split("```")
        if len(parts) >= 3:
            return parts[1].strip().lstrip("json").strip()
    return payload.strip()


def _fix_json(payload: str) -> str:
    return payload.replace(",]", "]").replace(",}", "}")


def analyze_contents(contents: List[dict]) -> Graph:
    settings = get_settings()
    client = genai.Client(api_key=settings.llm_api_key)
    
    prompt = build_prompt(contents)
    system_instruction = (
        "你是一位知识架构专家，擅长将复杂课程内容解构为清晰的逻辑骨架。"
        "返回纯 JSON，不要包含 markdown 代码块。"
    )

    last_error: Exception | None = None
    for attempt in range(settings.llm_max_retries + 1):
        try:
            response = client.models.generate_content(
                model=settings.llm_model,
                contents=f"{system_instruction}\n\n{prompt}",
                config=types.GenerateContentConfig(
                    temperature=settings.llm_temperature,
                    max_output_tokens=settings.llm_max_tokens,
                ),
            )
            content = response.text
            json_payload = _fix_json(_extract_json(content))
            data = json.loads(json_payload)
            return Graph.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            logger.warning("LLM response invalid on attempt %s: %s", attempt + 1, exc)
        except Exception as exc:
            last_error = exc
            logger.exception("LLM call failed on attempt %s", attempt + 1)
            break

    raise ValueError(f"LLM 返回结果无法通过校验: {last_error}")

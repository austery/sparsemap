"""Gemini Provider Implementation"""
from __future__ import annotations

import json
import logging
from typing import List

from google import genai
from google.genai import types
from pydantic import ValidationError

from sparsemap.domain.models import Graph, NodeDetails
from sparsemap.services.llm_provider import LLMProvider
from sparsemap.services.llm_utils import extract_json, fix_json, repair_json

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini Provider"""

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.2,
        max_tokens: int = 2000,
        max_retries: int = 2,
    ):
        if not api_key:
            raise ValueError("Gemini API key is required")

        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries

        http_options = types.HttpOptions(baseUrl=base_url) if base_url else None
        self.client = genai.Client(api_key=api_key, http_options=http_options)
        
        base_url_log = f", base_url: {base_url}" if base_url else ""
        logger.info(f"✓ GeminiProvider initialized (model: {model}{base_url_log})")

    def generate_graph(self, contents: List[dict], prompt: str) -> Graph:
        """Generate knowledge graph using Gemini API"""
        system_instruction = """你是一位知识架构专家，擅长将复杂的课程内容解构为清晰的逻辑骨架和知识依赖关系。

**重要：JSON 格式要求**
1. 所有字符串中的特殊字符（引号、换行符、反斜杠等）必须正确转义
2. 字符串中的双引号必须转义为 \\"
3. 不要在 JSON 字符串中使用未转义的引号
4. 不要在对象或数组的最后一个元素后添加逗号
5. 返回纯 JSON，不要包含 markdown 代码块标记

返回格式：
{
  "nodes": [{"id": "n1", "label": "节点", "type": "main", "priority": "critical", "reason": "原因", "source": "text1", "description": "描述"}],
  "edges": [{"source": "n1", "target": "n2", "type": "depends_on", "reason": "原因"}],
  "summary": "总结"
}"""

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=f"{system_instruction}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        temperature=self.temperature,
                        max_output_tokens=self.max_tokens,
                        response_mime_type="application/json",
                    ),
                )
                content = response.text
                
                # Use robust repair logic
                try:
                    data = repair_json(extract_json(content))
                    return Graph.model_validate(data)
                except ValueError as ve:
                    logger.error(f"JSON repair failed: {ve}")
                    logger.error(f"❌ Failed Raw Content (Length: {len(content)}):\n{content}")
                    
                    # Save debug files
                    with open("debug_gemini_prompt.txt", "w", encoding="utf-8") as f:
                        f.write(f"{system_instruction}\n\n{prompt}")
                    with open("debug_gemini_response.txt", "w", encoding="utf-8") as f:
                        f.write(content)
                    logger.info("Saved debug files: debug_gemini_prompt.txt, debug_gemini_response.txt")
                    
                    raise

            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
                logger.warning(f"Gemini response invalid on attempt {attempt + 1}: {exc}")

            except Exception as exc:
                last_error = exc
                logger.exception(f"Gemini API call failed on attempt {attempt + 1}")
                break

        raise ValueError(f"Gemini 返回结果无法通过校验: {last_error}")

    def generate_raw(self, prompt: str) -> str:
        """Generate raw text response from Gemini"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                ),
            )
            return response.text
        except Exception as exc:
            logger.exception("Gemini raw generation failed")
            raise ValueError(f"Gemini 生成失败: {exc}")
    def generate_node_details(self, node_label: str, context: str) -> NodeDetails:
        """Generate detailed explanation for a specific node"""
        system_instruction = """你是一位资深的教育专家。请为给定的知识点生成详细的解释卡片。
你需要返回严格的 JSON 格式，包含以下字段：
1. definition: 清晰、学术的定义
2. analogy: 一个通俗易懂的生活类比
3. importance: 为什么这个概念很重要（在上下文语境如AP课程或大纲中）
4. actionable_step: 一个具体的行动步骤或练习
5. keywords: 3-5个相关关键词列表

返回示例：
{
  "definition": "...",
  "analogy": "...",
  "importance": "...",
  "actionable_step": "...",
  "keywords": ["key1", "key2"]
}"""
        
        prompt = f"知识点：{node_label}\n\n上下文/来源内容：\n{context}"

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{system_instruction}\n\n{prompt}",
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                    response_mime_type="application/json",
                ),
            )
            content = response.text
            if not content:
                logger.warning(f"Gemini returned empty content for node: {node_label}. Response: {response}")
                # Fallback to avoid crash
                return NodeDetails(
                    definition="无法生成详细信息 (AI 响应为空)",
                    analogy="可能由于内容安全策略，无法显示。",
                    importance="请稍后重试。",
                    actionable_step="无",
                    keywords=[]
                )

            data = repair_json(extract_json(content))
            return NodeDetails.model_validate(data)
            
        except Exception as exc:
            logger.exception(f"Gemini node details generation failed for {node_label}")
            raise ValueError(f"Gemini 生成节点详情失败: {exc}")

"""DeepSeek Provider Implementation (OpenAI-compatible)"""
from __future__ import annotations

import json
import logging
from typing import List

from openai import OpenAI
from pydantic import ValidationError

from sparsemap.domain.models import Graph, NodeDetails
from sparsemap.services.llm_provider import LLMProvider
from sparsemap.services.llm_utils import extract_json, repair_json

logger = logging.getLogger(__name__)


class DeepSeekProvider(LLMProvider):
    """DeepSeek Provider (OpenAI-compatible API)"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://space.ai-builders.com/backend/v1",
        model: str = "deepseek",
        temperature: float = 0.2,
        max_tokens: int = 2000,
        max_retries: int = 2,
    ):
        if not api_key:
            raise ValueError("DeepSeek API key is required")

        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries

        self.client = OpenAI(
            base_url=base_url, 
            api_key=api_key,
            timeout=180.0,  # 3 minutes timeout for complex prompts
            max_retries=0,  # Disable OpenAI SDK retries (we handle it ourselves)
        )
        logger.info(f"✓ DeepSeekProvider initialized (model: {model}, base_url: {base_url})")

    def generate_graph(self, contents: List[dict], prompt: str) -> Graph:
        """Generate knowledge graph using DeepSeek API"""
        # Use exact same system prompt as linklog (proven to work)
        system_content = """你是一位知识架构专家，擅长将复杂的课程内容解构为清晰的逻辑骨架和知识依赖关系。

**重要：JSON 格式要求**
1. 所有字符串中的特殊字符（引号、换行符、反斜杠等）必须正确转义
2. 字符串中的双引号必须转义为 \\"
3. 不要在 JSON 字符串中使用未转义的引号
4. 不要在对象或数组的最后一个元素后添加逗号
5. 返回纯 JSON，不要包含 markdown 代码块标记

**边类型严格限制**：
- 只能使用以下四种边类型：depends_on, references, implements, supports
- 不要使用 extends, includes, contains 等其他类型

返回格式：
{
  "nodes": [{"id": "n1", "label": "节点", "type": "main", "priority": "critical", "reason": "原因", "source": "text1", "description": "描述"}],
  "edges": [{"source": "n1", "target": "n2", "type": "depends_on", "reason": "原因"}],
  "summary": "总结"
}"""

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,  # Same as linklog
                    max_tokens=self.max_tokens,
                )
                
                # Log token usage if available
                if hasattr(response, 'usage'):
                    usage = response.usage
                    logger.info(
                        f"DeepSeek tokens: prompt={usage.prompt_tokens}, "
                        f"completion={usage.completion_tokens}, total={usage.total_tokens}"
                    )
                
                content = response.choices[0].message.content or ""
                logger.info(f"Response length: {len(content)} chars")
                
                json_payload = extract_json(content)
                
                # Use aggressive repair for DeepSeek
                try:
                    data = repair_json(json_payload)
                except ValueError as ve:
                    logger.warning(f"JSON repair failed: {ve}")
                    # Log the problematic JSON for debugging
                    logger.debug(f"Failed JSON (first 500 chars): {json_payload[:500]}")
                    raise
                
                return Graph.model_validate(data)

            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
                logger.warning(f"DeepSeek response invalid on attempt {attempt + 1}: {exc}")

            except Exception as exc:
                last_error = exc
                logger.exception(f"DeepSeek API call failed on attempt {attempt + 1}")
                break

        raise ValueError(f"DeepSeek 返回结果无法通过校验: {last_error}")

    def generate_raw(self, prompt: str) -> str:
        """Generate raw text response from DeepSeek"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.exception("DeepSeek raw generation failed")
            raise ValueError(f"DeepSeek 生成失败: {exc}")

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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            content = response.choices[0].message.content or ""
            if not content:
                logger.warning(f"DeepSeek returned empty content for node: {node_label}")
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
            logger.exception(f"DeepSeek node details generation failed for {node_label}")
            raise ValueError(f"DeepSeek 生成节点详情失败: {exc}")

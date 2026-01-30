"""Gemini Provider Implementation"""
from __future__ import annotations

import json
import logging
from typing import List

from google import genai
from google.genai import types
from pydantic import ValidationError

from sparsemap.domain.models import Graph
from sparsemap.services.llm_provider import LLMProvider
from sparsemap.services.llm_utils import extract_json, fix_json

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini Provider"""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.2,
        max_tokens: int = 2000,
        max_retries: int = 2,
    ):
        if not api_key:
            raise ValueError("Gemini API key is required")

        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries

        self.client = genai.Client(api_key=api_key)
        logger.info(f"✓ GeminiProvider initialized (model: {model})")

    def generate_graph(self, contents: List[dict], prompt: str) -> Graph:
        """Generate knowledge graph using Gemini API"""
        system_instruction = (
            "你是一位知识架构专家，擅长将复杂课程内容解构为清晰的逻辑骨架。"
            "返回纯 JSON，不要包含 markdown 代码块。"
        )

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=f"{system_instruction}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        temperature=self.temperature,
                        max_output_tokens=self.max_tokens,
                    ),
                )
                content = response.text
                json_payload = fix_json(extract_json(content))
                data = json.loads(json_payload)
                return Graph.model_validate(data)

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

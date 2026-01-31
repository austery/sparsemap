"""
LLM Provider 抽象层

支持多个 LLM 提供商：
- Gemini (Google)
- DeepSeek (OpenAI-compatible)
- 其他 OpenAI-compatible APIs
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from sparsemap.domain.models import Graph, NodeDetails


class LLMProvider(ABC):
    """LLM 提供商抽象基类"""

    @abstractmethod
    def generate_graph(self, contents: List[dict], prompt: str) -> Graph:
        """
        生成知识图谱

        Args:
            contents: 内容列表，每个包含 source 和 text
            prompt: 提示词

        Returns:
            Graph: 解析后的知识图谱

        Raises:
            ValueError: 当生成失败或无法解析时
        """
        pass

    @abstractmethod
    def generate_raw(self, prompt: str) -> str:
        """
        生成原始文本响应（不解析为 Graph）

        Args:
            prompt: 提示词

        Returns:
            str: LLM 原始响应文本
        """
        pass

    @abstractmethod
    def generate_node_details(self, node_label: str, context: str) -> NodeDetails:
        """
        生成节点详细信息 (Deep Dive)

        Args:
            node_label: 节点名称
            context: 上下文或描述

        Returns:
            NodeDetails: 详细信息对象
        """
        pass

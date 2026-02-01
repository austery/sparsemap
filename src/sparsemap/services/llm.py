from __future__ import annotations

import logging
from typing import List

from sparsemap.core.config import get_settings
from sparsemap.domain.models import Graph, NodeDetails
from sparsemap.services.llm_provider import LLMProvider
from sparsemap.services.providers import DeepSeekProvider, GeminiProvider


logger = logging.getLogger(__name__)


def _get_provider() -> LLMProvider:
    """
    Get LLM provider based on configuration

    Returns:
        LLMProvider: Configured provider instance

    Raises:
        ValueError: If provider is not supported
    """
    settings = get_settings()
    provider_name = settings.llm_provider.lower()

    if provider_name == "gemini":
        return GeminiProvider(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            max_retries=settings.llm_max_retries,
        )
    elif provider_name == "deepseek":
        return DeepSeekProvider(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            max_retries=settings.llm_max_retries,
        )
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider_name}. "
            f"Supported providers: gemini, deepseek"
        )


def build_prompt(contents: List[dict]) -> str:
    prompt = """你是一位资深的教学专家和知识架构师。请分析以下课程内容，提取逻辑骨架和知识依赖关系。

要求：
1. **识别主线逻辑**：课程的核心思想、步骤流程、关键主张（type: "main"）
2. **识别支线知识**：达成主线目标所需的技术工具、背景概念（type: "dependency"）
3. **解释关系**：为每个依赖关系说明"为什么需要这个工具/概念"
4. **边类型限制**：edges.type 只能使用 depends_on, references, implements, supports 四种之一

返回严格的 JSON 格式：
{
  "nodes": [
    {
      "id": "n1",
      "label": "节点名称",
      "type": "main" | "dependency",
      "priority": "critical" | "optional",
      "reason": "节点出现的原因",
      "source": "text1",
      "description": "节点描述"
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n2",
      "type": "depends_on" | "references" | "implements" | "supports",
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


def analyze_contents(contents: List[dict]) -> Graph:
    """
    Analyze contents and generate knowledge graph using configured LLM provider

    Args:
        contents: List of content dictionaries with 'source' and 'text' keys

    Returns:
        Graph: Parsed knowledge graph

    Raises:
        ValueError: If generation or parsing fails
    """
    provider = _get_provider()
    prompt = build_prompt(contents)
    return provider.generate_graph(contents, prompt)


def generate_node_details(node_label: str, context: str) -> NodeDetails:
    """
    Generate detailed explanation for a node using configured LLM provider

    Args:
        node_label: Node label
        context: Context text

    Returns:
        NodeDetails: Detailed explanation
    """
    provider = _get_provider()
    return provider.generate_node_details(node_label, context)


def integrate_concept(new_concept: str, existing_nodes: List[dict]) -> dict:
    """
    Analyze how a new concept relates to existing graph nodes

    Args:
        new_concept: The new concept to integrate
        existing_nodes: List of existing nodes with id, label, description

    Returns:
        dict with 'node' and 'edges' representing the new concept and its relationships
    """
    provider = _get_provider()

    # Build the prompt for integration analysis
    nodes_text = "\n".join(
        [
            f"- {n['label']} (id: {n['id']}): {n.get('description', 'No description')}"
            for n in existing_nodes
        ]
    )

    prompt = f"""你是一位知识架构专家。用户想要将一个新概念关联到现有知识图谱中。

新概念: {new_concept}

现有图谱节点:
{nodes_text}

任务:
1. 分析新概念与现有节点的关系
2. 创建新节点表示这个概念
3. 建立适当的边连接到相关的现有节点

返回严格的 JSON 格式:
{{
  "node": {{
    "id": "linked_1",
    "label": "{new_concept}",
    "description": "对这个概念的简短描述",
    "reason": "为什么这个概念与图谱相关"
  }},
  "edges": [
    {{
      "source": "linked_1",
      "target": "现有节点id",
      "type": "relates_to",
      "reason": "关系说明"
    }}
  ]
}}

注意:
- source 应该是新节点 "linked_1"，target 是现有节点的 id
- 只连接真正相关的节点，不要强行建立关系
- 如果找不到明显相关的节点，edges 可以为空数组
- type 可以是: relates_to, depends_on, supports, implements
"""

    # Use the provider to generate integration
    import json

    result = provider.generate_raw(prompt)

    # Parse the JSON response
    try:
        # Clean up the response (remove markdown code fences if present)
        result = result.strip()
        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()

        data = json.loads(result)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse integration response: {e}")
        logger.error(f"Raw response: {result}")
        # Return a basic structure
        return {
            "node": {
                "id": "linked_1",
                "label": new_concept,
                "description": f"用户添加的概念: {new_concept}",
                "reason": "用户手动关联",
            },
            "edges": [],
        }


def expand_node(
    node_id: str,
    node_label: str,
    node_description: str | None,
    graph_context: str | None,
) -> dict:
    """
    Expand a node to reveal its sub-concepts and details.

    Args:
        node_id: ID of the node to expand
        node_label: Label of the node
        node_description: Optional description
        graph_context: Optional context about the current graph

    Returns:
        dict with 'child_nodes' and 'new_edges'
    """
    provider = _get_provider()

    context_text = ""
    if graph_context:
        context_text = f"\n当前图谱概述: {graph_context}\n"
    if node_description:
        context_text += f"\n节点描述: {node_description}\n"

    prompt = f"""你是一位知识架构专家。用户想要展开一个知识节点，查看其包含的子概念。

要展开的节点: {node_label} (id: {node_id})
{context_text}

任务:
1. 分析这个概念，找出其包含的 2-4 个核心子概念或组成部分
2. 为每个子概念创建节点
3. 建立从父节点到子节点的边

返回严格的 JSON 格式:
{{
  "child_nodes": [
    {{
      "id": "{node_id}_sub1",
      "label": "子概念名称",
      "type": "dependency",
      "priority": "critical" | "optional",
      "reason": "这个子概念的作用",
      "description": "简短描述",
      "level": 1,
      "expandable": false,
      "parent_id": "{node_id}"
    }}
  ],
  "new_edges": [
    {{
      "source": "{node_id}",
      "target": "{node_id}_sub1",
      "type": "implements" | "depends_on" | "supports",
      "reason": "父子关系说明"
    }}
  ]
}}

注意:
- 子节点数量控制在 2-4 个，不要太多
- 子节点的 id 格式为 父节点id_sub1, 父节点id_sub2 等
- 子节点的 level 应该是 1（表示次级节点）
- 子节点的 parent_id 应该是父节点的 id
- type 应该是 dependency
- expandable 设为 false（子节点通常不再可展开）
"""

    import json

    result = provider.generate_raw(prompt)

    try:
        # Clean up the response
        result = result.strip()
        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()

        data = json.loads(result)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse expand response: {e}")
        logger.error(f"Raw response: {result}")
        # Return empty structure on failure
        return {"child_nodes": [], "new_edges": []}

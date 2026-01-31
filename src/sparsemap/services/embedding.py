"""Embedding service for semantic similarity search using pgvector."""

from __future__ import annotations

from typing import List, Optional

from sqlmodel import Session, select, text

from sparsemap.core.config import get_settings
from sparsemap.domain.models import Graph, Node, NodeEmbedding, EMBEDDING_DIM


def _get_embedding_client():
    """Get the appropriate embedding client based on LLM provider."""
    settings = get_settings()

    if settings.llm_provider == "gemini":
        from google import genai

        client = genai.Client(api_key=settings.llm_api_key)
        return ("gemini", client)
    else:
        # Use OpenAI for other providers
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url
            if settings.llm_provider == "deepseek"
            else None,
        )
        return ("openai", client)


def generate_embedding(text: str) -> List[float]:
    """Generate embedding vector for given text.

    Args:
        text: Text to embed

    Returns:
        List of floats representing the embedding vector
    """
    provider, client = _get_embedding_client()

    if provider == "gemini":
        # Gemini embedding
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=text,
        )
        return list(result.embeddings[0].values)
    else:
        # OpenAI embedding
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            dimensions=EMBEDDING_DIM,
        )
        return response.data[0].embedding


def generate_node_text(node: Node) -> str:
    """Generate text representation of a node for embedding."""
    parts = [node.label]
    if node.description:
        parts.append(node.description)
    if node.reason:
        parts.append(node.reason)
    return " | ".join(parts)


def store_node_embeddings(
    session: Session, analysis_id: int, graph: Graph
) -> List[NodeEmbedding]:
    """Generate and store embeddings for all nodes in a graph.

    Args:
        session: Database session
        analysis_id: ID of the AnalysisResult
        graph: Graph containing nodes to embed

    Returns:
        List of created NodeEmbedding records
    """
    embeddings = []

    for node in graph.nodes:
        node_text = generate_node_text(node)
        embedding_vector = generate_embedding(node_text)

        node_embedding = NodeEmbedding(
            analysis_id=analysis_id,
            node_id=node.id,
            node_label=node.label,
            node_description=node.description,
            embedding=embedding_vector,
        )
        session.add(node_embedding)
        embeddings.append(node_embedding)

    session.commit()
    return embeddings


def search_similar_nodes(
    session: Session,
    query: str,
    top_k: int = 5,
    exclude_analysis_id: Optional[int] = None,
) -> List[dict]:
    """Search for nodes similar to the query text.

    Args:
        session: Database session
        query: Query text to search for
        top_k: Number of results to return
        exclude_analysis_id: Optionally exclude nodes from a specific analysis

    Returns:
        List of dicts with node info and similarity score
    """
    query_embedding = generate_embedding(query)

    # Use pgvector's <=> operator for cosine distance
    # Lower distance = more similar
    sql = text("""
        SELECT
            id,
            analysis_id,
            node_id,
            node_label,
            node_description,
            1 - (embedding <=> :query_embedding::vector) as similarity
        FROM node_embedding
        WHERE (:exclude_id IS NULL OR analysis_id != :exclude_id)
        ORDER BY embedding <=> :query_embedding::vector
        LIMIT :top_k
    """)

    result = session.execute(
        sql,
        {
            "query_embedding": str(query_embedding),
            "exclude_id": exclude_analysis_id,
            "top_k": top_k,
        },
    )

    return [
        {
            "id": row.id,
            "analysis_id": row.analysis_id,
            "node_id": row.node_id,
            "node_label": row.node_label,
            "node_description": row.node_description,
            "similarity": float(row.similarity),
        }
        for row in result
    ]


def get_embeddings_for_analysis(
    session: Session, analysis_id: int
) -> List[NodeEmbedding]:
    """Get all embeddings for an analysis."""
    return list(
        session.exec(
            select(NodeEmbedding).where(NodeEmbedding.analysis_id == analysis_id)
        ).all()
    )


def delete_embeddings_for_analysis(session: Session, analysis_id: int) -> int:
    """Delete all embeddings for an analysis.

    Returns:
        Number of deleted records
    """
    embeddings = get_embeddings_for_analysis(session, analysis_id)
    count = len(embeddings)
    for emb in embeddings:
        session.delete(emb)
    session.commit()
    return count


def has_embeddings(session: Session, analysis_id: int) -> bool:
    """Check if an analysis already has embeddings."""
    result = session.exec(
        select(NodeEmbedding).where(NodeEmbedding.analysis_id == analysis_id).limit(1)
    ).first()
    return result is not None

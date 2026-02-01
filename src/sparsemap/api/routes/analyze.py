from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlmodel import Session

from sparsemap.domain.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    Graph,
    Node,
    Edge,
    NodeType,
    Priority,
    EdgeType,
    NodeDetails,
    DetailsRequest,
    URLInput,
    HistoryListResponse,
    IntegrateConceptRequest,
    IntegrateConceptResponse,
    IntegrateConceptData,
    LinkedNode,
    LinkedEdge,
    ExpandNodeRequest,
    ExpandNodeResponse,
    ExpandedNodeData,
)
from sparsemap.infra.db import get_session
from sparsemap.services.extractor import fetch_url_content, hash_url
from sparsemap.services.exporter import ExportFormat, export_graph, get_mime_type
from sparsemap.services.llm import (
    analyze_contents,
    generate_node_details,
    integrate_concept,
    expand_node,
)
from sparsemap.services.repository import (
    get_analysis_by_hash,
    get_analysis_by_id,
    save_analysis,
    list_analyses,
    count_analyses,
    delete_analysis,
)
from sparsemap.services.embedding import (
    store_node_embeddings,
    search_similar_nodes,
    has_embeddings,
)


router = APIRouter()


# Response models for embedding endpoints
class SimilarNode(BaseModel):
    """A node similar to the query."""

    id: int
    analysis_id: int
    node_id: str
    node_label: str
    node_description: Optional[str] = None
    similarity: float


class RecallResponse(BaseModel):
    """Response for recall endpoint."""

    success: bool
    results: List[SimilarNode]


class EmbedResponse(BaseModel):
    """Response for embed endpoint."""

    success: bool
    message: str
    count: int


def _extract_title(url: str = None, text: str = None, graph: Graph = None) -> str:
    """Extract a meaningful title from URL, text, or graph summary"""
    if url:
        # Extract domain or path from URL
        from urllib.parse import urlparse

        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if path:
            # Use last path segment
            return path.split("/")[-1][:50] or parsed.netloc
        return parsed.netloc
    if graph and graph.summary:
        # Use first 50 chars of summary
        return graph.summary[:50] + ("..." if len(graph.summary) > 50 else "")
    if text:
        # Use first 50 chars of text
        clean = text.strip()[:50]
        return clean + ("..." if len(text) > 50 else "")
    return "Untitled"


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest, session: Session = Depends(get_session)
) -> AnalyzeResponse:
    contents = []
    sources = []

    if not request.urls and not request.texts:
        raise HTTPException(status_code=400, detail="至少提供一个 URL 或文本。")

    for idx, url in enumerate(request.urls, start=1):
        url_hash = hash_url(url)
        cached = get_analysis_by_hash(session, url_hash)
        if cached and len(request.urls) == 1 and not request.texts:
            graph = Graph.model_validate(cached.graph_data)
            return AnalyzeResponse(success=True, data=graph, sources=[f"url{idx}"])

        text, _ = await fetch_url_content(url)
        contents.append({"source": f"url{idx}", "text": text})
        sources.append(f"url{idx}")

    for idx, text in enumerate(request.texts, start=1):
        contents.append({"source": f"text{idx}", "text": text})
        sources.append(f"text{idx}")

    try:
        graph = analyze_contents(contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Save with metadata
    for url in request.urls:
        url_hash = hash_url(url)
        if not get_analysis_by_hash(session, url_hash):
            title = _extract_title(url=url, graph=graph)
            save_analysis(
                session,
                url_hash,
                graph,
                title=title,
                original_url=url,
                source_type="url",
            )

    for text in request.texts:
        text_hash = hash_url(text)
        if not get_analysis_by_hash(session, text_hash):
            title = _extract_title(text=text, graph=graph)
            save_analysis(session, text_hash, graph, title=title, source_type="text")

    return AnalyzeResponse(success=True, data=graph, sources=sources)


@router.post("/node-details", response_model=NodeDetails)
async def get_node_details(request: DetailsRequest) -> NodeDetails:
    try:
        context = request.node_context or request.node_description or request.node_label
        return generate_node_details(request.node_label, context)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/history", response_model=HistoryListResponse)
async def get_history(
    limit: int = 50, offset: int = 0, session: Session = Depends(get_session)
) -> HistoryListResponse:
    """Get analysis history, most recent first"""
    items = list_analyses(session, limit=limit, offset=offset)
    total = count_analyses(session)
    return HistoryListResponse(items=items, total=total)


@router.get("/history/{analysis_id}", response_model=AnalyzeResponse)
async def get_history_item(
    analysis_id: int, session: Session = Depends(get_session)
) -> AnalyzeResponse:
    """Get a specific analysis by ID"""
    record = get_analysis_by_id(session, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    graph = Graph.model_validate(record.graph_data)
    return AnalyzeResponse(success=True, data=graph, sources=[record.source_type])


@router.delete("/history/{analysis_id}")
async def delete_history_item(
    analysis_id: int, session: Session = Depends(get_session)
):
    """Delete an analysis by ID"""
    if delete_analysis(session, analysis_id):
        return {"success": True, "message": "Deleted"}
    raise HTTPException(status_code=404, detail="Analysis not found")


@router.post("/analyze-test", response_model=AnalyzeResponse)
async def analyze_test() -> AnalyzeResponse:
    """Test endpoint - returns fixed test data without calling AI."""
    test_data = Graph(
        nodes=[
            Node(
                id="n1",
                label="AI-first 架构思维",
                type=NodeType.main,
                priority=Priority.critical,
                reason="课程核心思想",
                source="text1",
                description="从传统性能/功能评估转向AI友好性评估",
            ),
            Node(
                id="n2",
                label="选择 FastAPI",
                type=NodeType.main,
                priority=Priority.critical,
                reason="AI友好框架选择",
                source="text1",
                description="选择 FastAPI 作为 AI 友好框架",
            ),
            Node(
                id="n3",
                label="自动文档生成",
                type=NodeType.dependency,
                priority=Priority.critical,
                reason="FastAPI特性",
                source="text1",
                description="FastAPI 的自动文档生成特性",
            ),
            Node(
                id="n4",
                label="严格数据契约",
                type=NodeType.dependency,
                priority=Priority.critical,
                reason="FastAPI特性",
                source="text1",
                description="FastAPI 的严格数据契约特性",
            ),
            Node(
                id="n5",
                label="Python 类型系统",
                type=NodeType.dependency,
                priority=Priority.optional,
                reason="技术依赖",
                source="text1",
                description="利用 Python 的类型系统",
            ),
            Node(
                id="n6",
                label="Cursor AI 编辑器",
                type=NodeType.dependency,
                priority=Priority.optional,
                reason="开发工具",
                source="text1",
                description="使用 Cursor AI 编辑器进行开发",
            ),
            Node(
                id="n7",
                label="创建第一个应用",
                type=NodeType.main,
                priority=Priority.critical,
                reason="实践步骤",
                source="text1",
                description="创建第一个 FastAPI 应用",
            ),
            Node(
                id="n8",
                label="定义路由",
                type=NodeType.main,
                priority=Priority.critical,
                reason="实践步骤",
                source="text1",
                description="定义 API 路由",
            ),
            Node(
                id="n9",
                label="数据验证",
                type=NodeType.main,
                priority=Priority.critical,
                reason="实践步骤",
                source="text1",
                description="使用 Pydantic 进行数据验证",
            ),
            Node(
                id="n10",
                label="Pydantic",
                type=NodeType.dependency,
                priority=Priority.critical,
                reason="技术依赖",
                source="text1",
                description="Pydantic 数据验证库",
            ),
        ],
        edges=[
            Edge(
                source="n1",
                target="n2",
                type=EdgeType.depends_on,
                reason="架构思维指导框架选择",
            ),
            Edge(
                source="n2",
                target="n3",
                type=EdgeType.implements,
                reason="FastAPI 提供自动文档生成",
            ),
            Edge(
                source="n2",
                target="n4",
                type=EdgeType.implements,
                reason="FastAPI 提供严格数据契约",
            ),
            Edge(
                source="n2",
                target="n5",
                type=EdgeType.depends_on,
                reason="基于 Python 类型系统",
            ),
            Edge(
                source="n2",
                target="n6",
                type=EdgeType.supports,
                reason="与 Cursor AI 编辑器配合",
            ),
            Edge(
                source="n1",
                target="n7",
                type=EdgeType.depends_on,
                reason="架构思维指导应用创建",
            ),
            Edge(
                source="n7",
                target="n8",
                type=EdgeType.depends_on,
                reason="应用需要定义路由",
            ),
            Edge(
                source="n8",
                target="n9",
                type=EdgeType.depends_on,
                reason="路由需要数据验证",
            ),
            Edge(
                source="n9",
                target="n10",
                type=EdgeType.depends_on,
                reason="使用 Pydantic 进行验证",
            ),
        ],
        summary="课程构建了一个完整的AI优先开发框架，核心逻辑是从传统开发思维转向AI-first架构思维。",
    )
    return AnalyzeResponse(success=True, data=test_data, sources=["test"])


@router.post("/add-url", response_model=AnalyzeResponse)
async def add_url(
    request: URLInput, session: Session = Depends(get_session)
) -> AnalyzeResponse:
    """Add a new URL to existing canvas."""
    try:
        text, _ = await fetch_url_content(request.url)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"无法抓取 URL 内容: {exc}"
        ) from exc

    contents = [{"source": "new_url", "text": text}]

    try:
        graph = analyze_contents(contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    url_hash = hash_url(request.url)
    if not get_analysis_by_hash(session, url_hash):
        title = _extract_title(url=request.url, graph=graph)
        save_analysis(
            session,
            url_hash,
            graph,
            title=title,
            original_url=request.url,
            source_type="url",
        )

    return AnalyzeResponse(success=True, data=graph, sources=["new_url"])


@router.post("/integrate-concept", response_model=IntegrateConceptResponse)
async def integrate_concept_endpoint(
    request: IntegrateConceptRequest,
) -> IntegrateConceptResponse:
    """
    Integrate a new concept into the existing knowledge graph.
    Uses AI to analyze relationships between the new concept and existing nodes.
    """
    if not request.new_concept.strip():
        raise HTTPException(status_code=400, detail="概念名称不能为空")

    if not request.existing_nodes:
        raise HTTPException(status_code=400, detail="需要至少一个现有节点")

    try:
        # Convert ExistingNode models to dicts for the LLM function
        existing_nodes_dicts = [
            {"id": node.id, "label": node.label, "description": node.description or ""}
            for node in request.existing_nodes
        ]

        # Call LLM to analyze relationships
        result = integrate_concept(request.new_concept.strip(), existing_nodes_dicts)

        # Parse and validate the result
        node_data = result.get("node", {})
        edges_data = result.get("edges", [])

        linked_node = LinkedNode(
            id=node_data.get("id", "linked_1"),
            label=node_data.get("label", request.new_concept),
            description=node_data.get("description"),
            reason=node_data.get("reason"),
        )

        linked_edges = [
            LinkedEdge(
                source=edge.get("source", "linked_1"),
                target=edge.get("target"),
                type=edge.get("type", "relates_to"),
                reason=edge.get("reason"),
            )
            for edge in edges_data
            if edge.get("target")  # Only include edges with valid targets
        ]

        data = IntegrateConceptData(node=linked_node, edges=linked_edges)
        return IntegrateConceptResponse(success=True, data=data)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"关联失败: {str(exc)}") from exc


@router.get("/export/{analysis_id}")
async def export_analysis(
    analysis_id: int,
    format: ExportFormat = Query(default=ExportFormat.MERMAID),
    session: Session = Depends(get_session),
) -> PlainTextResponse:
    """
    Export a graph analysis to various formats.

    Supported formats:
    - mermaid: Mermaid diagram syntax
    - d2: D2 diagram syntax
    - json: Full JSON export
    - markdown: Human-readable Markdown with tables
    """
    record = get_analysis_by_id(session, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    graph = Graph.model_validate(record.graph_data)
    content = export_graph(graph, format)
    mime_type = get_mime_type(format)

    return PlainTextResponse(content=content, media_type=mime_type)


@router.post("/embed/{analysis_id}", response_model=EmbedResponse)
async def embed_analysis(
    analysis_id: int,
    session: Session = Depends(get_session),
) -> EmbedResponse:
    """
    Generate embeddings for all nodes in an analysis.
    This enables semantic similarity search via the /recall endpoint.
    """
    record = get_analysis_by_id(session, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if has_embeddings(session, analysis_id):
        return EmbedResponse(
            success=True,
            message="Embeddings already exist for this analysis",
            count=0,
        )

    graph = Graph.model_validate(record.graph_data)

    try:
        embeddings = store_node_embeddings(session, analysis_id, graph)
        return EmbedResponse(
            success=True,
            message=f"Generated embeddings for {len(embeddings)} nodes",
            count=len(embeddings),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate embeddings: {str(exc)}"
        ) from exc


@router.get("/recall", response_model=RecallResponse)
async def recall_similar_nodes(
    query: str = Query(..., min_length=1, description="Search query text"),
    top_k: int = Query(default=5, ge=1, le=20, description="Number of results"),
    exclude_analysis_id: Optional[int] = Query(
        default=None, description="Exclude nodes from this analysis"
    ),
    session: Session = Depends(get_session),
) -> RecallResponse:
    """
    Search for semantically similar nodes across all analyses.
    Useful for finding related historical knowledge.
    """
    try:
        results = search_similar_nodes(
            session, query, top_k=top_k, exclude_analysis_id=exclude_analysis_id
        )
        return RecallResponse(
            success=True,
            results=[SimilarNode(**r) for r in results],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Search failed: {str(exc)}"
        ) from exc


@router.post("/expand-node", response_model=ExpandNodeResponse)
async def expand_node_endpoint(
    request: ExpandNodeRequest,
) -> ExpandNodeResponse:
    """
    Expand a node to reveal its sub-concepts.
    Uses AI to analyze and generate child nodes.
    """
    if not request.node_label.strip():
        raise HTTPException(status_code=400, detail="节点标签不能为空")

    try:
        result = expand_node(
            node_id=request.node_id,
            node_label=request.node_label.strip(),
            node_description=request.node_description,
            graph_context=request.graph_context,
        )

        # Parse child nodes into Node objects
        child_nodes = []
        for n in result.get("child_nodes", []):
            try:
                node = Node(
                    id=n.get("id", f"{request.node_id}_sub"),
                    label=n.get("label", "Unknown"),
                    type=NodeType(n.get("type", "dependency")),
                    priority=Priority(n.get("priority", "optional")),
                    reason=n.get("reason", ""),
                    description=n.get("description"),
                    level=n.get("level", 1),
                    expandable=n.get("expandable", False),
                    parent_id=n.get("parent_id", request.node_id),
                )
                child_nodes.append(node)
            except Exception:
                # Skip invalid nodes
                pass

        # Parse edges
        new_edges = []
        for e in result.get("new_edges", []):
            try:
                edge = Edge(
                    source=e.get("source", request.node_id),
                    target=e.get("target", ""),
                    type=EdgeType(e.get("type", "implements")),
                    reason=e.get("reason", ""),
                )
                if edge.target:  # Only add edges with valid targets
                    new_edges.append(edge)
            except Exception:
                # Skip invalid edges
                pass

        data = ExpandedNodeData(child_nodes=child_nodes, new_edges=new_edges)
        return ExpandNodeResponse(success=True, data=data)

    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"展开节点失败: {str(exc)}"
        ) from exc


@router.patch("/analysis/{analysis_id}")
async def update_analysis(
    analysis_id: int,
    graph_data: Graph,
    session: Session = Depends(get_session),
):
    """
    Update an analysis with edited graph data.
    Used for saving edits made in the graph editor.
    """
    record = get_analysis_by_id(session, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    record.graph_data = graph_data.model_dump()
    session.commit()

    return {"success": True, "message": "Analysis updated"}

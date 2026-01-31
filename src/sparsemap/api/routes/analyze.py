from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
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
)
from sparsemap.infra.db import get_session
from sparsemap.services.extractor import fetch_url_content, hash_url
from sparsemap.services.llm import (
    analyze_contents,
    generate_node_details,
    integrate_concept,
)
from sparsemap.services.repository import (
    get_analysis_by_hash,
    get_analysis_by_id,
    save_analysis,
    list_analyses,
    count_analyses,
    delete_analysis,
)


router = APIRouter()


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

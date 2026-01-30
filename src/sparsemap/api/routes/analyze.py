from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from sparsemap.domain.models import AnalyzeRequest, AnalyzeResponse, Graph, NodeDetails, DetailsRequest
from sparsemap.infra.db import get_session
from sparsemap.services.extractor import fetch_url_content, hash_url
from sparsemap.services.llm import analyze_contents, generate_node_details
from sparsemap.services.repository import get_analysis_by_hash, save_analysis


router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, session: Session = Depends(get_session)) -> AnalyzeResponse:
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

    for url in request.urls:
        url_hash = hash_url(url)
        if not get_analysis_by_hash(session, url_hash):
            save_analysis(session, url_hash, graph)

    for text in request.texts:
        # Use hash of text content as key
        text_hash = hash_url(text)
        if not get_analysis_by_hash(session, text_hash):
            save_analysis(session, text_hash, graph)

    return AnalyzeResponse(success=True, data=graph, sources=sources)


@router.post("/node-details", response_model=NodeDetails)
async def get_node_details(request: DetailsRequest) -> NodeDetails:
    try:
        # If context is not provided, use the label as context (minimal fallback)
        context = request.node_context or request.node_description or request.node_label
        return generate_node_details(request.node_label, context)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

from __future__ import annotations

from typing import List, Optional

from sqlmodel import Session, select, desc

from sparsemap.domain.models import AnalysisResult, Graph, HistoryItem


def get_analysis_by_hash(session: Session, url_hash: str) -> AnalysisResult | None:
    return session.exec(
        select(AnalysisResult).where(AnalysisResult.url_hash == url_hash)
    ).first()


def get_analysis_by_id(session: Session, analysis_id: int) -> AnalysisResult | None:
    return session.exec(
        select(AnalysisResult).where(AnalysisResult.id == analysis_id)
    ).first()


def save_analysis(
    session: Session,
    url_hash: str,
    graph: Graph,
    title: str = "Untitled",
    original_url: Optional[str] = None,
    source_type: str = "text",
) -> AnalysisResult:
    record = AnalysisResult(
        url_hash=url_hash,
        graph_data=graph.model_dump(),
        title=title,
        original_url=original_url,
        source_type=source_type,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_analyses(
    session: Session, limit: int = 50, offset: int = 0
) -> List[HistoryItem]:
    """List analysis history, most recent first"""
    results = session.exec(
        select(AnalysisResult)
        .order_by(desc(AnalysisResult.created_at))
        .offset(offset)
        .limit(limit)
    ).all()

    items = []
    for r in results:
        node_count = len(r.graph_data.get("nodes", [])) if r.graph_data else 0
        items.append(
            HistoryItem(
                id=r.id,
                title=r.title,
                source_type=r.source_type,
                original_url=r.original_url,
                node_count=node_count,
                created_at=r.created_at,
            )
        )
    return items


def count_analyses(session: Session) -> int:
    """Count total analyses"""
    from sqlalchemy import func

    return session.exec(select(func.count(AnalysisResult.id))).one()


def delete_analysis(session: Session, analysis_id: int) -> bool:
    """Delete an analysis by ID"""
    record = get_analysis_by_id(session, analysis_id)
    if record:
        session.delete(record)
        session.commit()
        return True
    return False

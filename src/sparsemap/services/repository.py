from __future__ import annotations

from sqlmodel import Session, select

from sparsemap.domain.models import AnalysisResult, Graph


def get_analysis_by_hash(session: Session, url_hash: str) -> AnalysisResult | None:
    return session.exec(select(AnalysisResult).where(AnalysisResult.url_hash == url_hash)).first()


def save_analysis(session: Session, url_hash: str, graph: Graph) -> AnalysisResult:
    record = AnalysisResult(url_hash=url_hash, graph_data=graph.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

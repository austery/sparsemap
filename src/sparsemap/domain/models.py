from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field as PydanticField
from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from sqlmodel import JSON as SQLModelJSON


class NodeType(str, Enum):
    main = "main"
    dependency = "dependency"
    suggested_best_practice = "suggested_best_practice"


class Priority(str, Enum):
    critical = "critical"
    optional = "optional"


class EdgeType(str, Enum):
    depends_on = "depends_on"
    references = "references"
    implements = "implements"
    supports = "supports"


class Node(BaseModel):
    id: str
    label: str
    type: NodeType
    priority: Priority = Priority.critical
    reason: str
    description: Optional[str] = None
    source: Optional[str] = None


class Edge(BaseModel):
    source: str
    target: str
    type: EdgeType
    reason: str


class Graph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    summary: Optional[str] = None


class AnalyzeRequest(BaseModel):
    urls: List[str] = PydanticField(default_factory=list)
    texts: List[str] = PydanticField(default_factory=list)


class AnalyzeResponse(BaseModel):
    success: bool
    data: Graph
    sources: List[str]


class AnalysisResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url_hash: str = Field(index=True, unique=True)
    graph_data: dict = Field(sa_column=Column(SQLModelJSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

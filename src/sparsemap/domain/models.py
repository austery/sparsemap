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


class SourceType(str, Enum):
    url = "url"
    text = "text"


class AnalysisResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url_hash: str = Field(index=True, unique=True)
    title: str = Field(default="Untitled")  # Display title
    original_url: Optional[str] = Field(default=None)  # Original URL if source is URL
    source_type: str = Field(default="text")  # "url" or "text"
    graph_data: dict = Field(sa_column=Column(SQLModelJSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HistoryItem(BaseModel):
    """History list item for API response"""
    id: int
    title: str
    source_type: str
    original_url: Optional[str] = None
    node_count: int
    created_at: datetime


class HistoryListResponse(BaseModel):
    """Response for /api/history"""
    items: List[HistoryItem]
    total: int


class NodeDetails(BaseModel):
    definition: str = PydanticField(..., description="The clear, academic definition of the concept")
    analogy: str = PydanticField(..., description="A real-world analogy to help explain the concept")
    importance: str = PydanticField(..., description="Why this concept is critical in the broader context")
    actionable_step: str = PydanticField(..., description="One concrete action to practice or apply this concept")
    keywords: List[str] = PydanticField(default_factory=list, description="Related keywords")


class DetailsRequest(BaseModel):
    node_label: str
    node_context: Optional[str] = None
    node_description: Optional[str] = None


class URLInput(BaseModel):
    """URL input for add-url endpoint"""
    url: str

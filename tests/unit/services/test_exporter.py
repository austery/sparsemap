"""Tests for graph export service."""

import json
import pytest

from sparsemap.domain.models import Graph, Node, Edge, NodeType, Priority, EdgeType
from sparsemap.services.exporter import (
    ExportFormat,
    export_graph,
    get_file_extension,
    get_mime_type,
)


@pytest.fixture
def sample_graph() -> Graph:
    """Create a sample graph for testing."""
    return Graph(
        nodes=[
            Node(
                id="n1",
                label="React",
                type=NodeType.main,
                priority=Priority.critical,
                reason="Core framework",
                description="A JavaScript library for building UIs",
            ),
            Node(
                id="n2",
                label="Virtual DOM",
                type=NodeType.dependency,
                priority=Priority.critical,
                reason="Core concept",
                description="In-memory representation of DOM",
            ),
            Node(
                id="n3",
                label="JSX",
                type=NodeType.dependency,
                priority=Priority.optional,
                reason="Syntax extension",
            ),
        ],
        edges=[
            Edge(
                source="n1",
                target="n2",
                type=EdgeType.implements,
                reason="React uses Virtual DOM",
            ),
            Edge(
                source="n1",
                target="n3",
                type=EdgeType.supports,
                reason="React supports JSX",
            ),
        ],
        summary="React framework overview",
    )


class TestMermaidExporter:
    def test_export_basic(self, sample_graph: Graph):
        result = export_graph(sample_graph, ExportFormat.MERMAID)

        assert result.startswith("graph TD")
        assert 'n1["React"]' in result
        assert 'n2["Virtual DOM"]' in result
        assert "n1 -->|implements| n2" in result
        assert "n1 -->|supports| n3" in result

    def test_export_sanitizes_labels(self):
        graph = Graph(
            nodes=[
                Node(
                    id="n1",
                    label='Test "Node" [1]',
                    type=NodeType.main,
                    priority=Priority.critical,
                    reason="test",
                )
            ],
            edges=[],
        )
        result = export_graph(graph, ExportFormat.MERMAID)

        # Should replace quotes and brackets
        assert "Test 'Node' (1)" in result


class TestD2Exporter:
    def test_export_basic(self, sample_graph: Graph):
        result = export_graph(sample_graph, ExportFormat.D2)

        assert 'n1: "React"' in result
        assert 'n2: "Virtual DOM"' in result
        assert "n1 -> n2: implements" in result
        assert "n1 -> n3: supports" in result


class TestJsonExporter:
    def test_export_basic(self, sample_graph: Graph):
        result = export_graph(sample_graph, ExportFormat.JSON)

        # Should be valid JSON
        data = json.loads(result)
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 2
        assert data["summary"] == "React framework overview"


class TestMarkdownExporter:
    def test_export_basic(self, sample_graph: Graph):
        result = export_graph(sample_graph, ExportFormat.MARKDOWN)

        assert "# Knowledge Graph Export" in result
        assert "## Summary" in result
        assert "React framework overview" in result
        assert "## Nodes" in result
        assert "🔴 React" in result  # Critical priority
        assert "🟡 JSX" in result  # Optional priority
        assert "## Relationships" in result
        assert "| React | Virtual DOM | implements |" in result


class TestExportHelpers:
    def test_get_file_extension(self):
        assert get_file_extension(ExportFormat.MERMAID) == "mmd"
        assert get_file_extension(ExportFormat.D2) == "d2"
        assert get_file_extension(ExportFormat.JSON) == "json"
        assert get_file_extension(ExportFormat.MARKDOWN) == "md"

    def test_get_mime_type(self):
        assert get_mime_type(ExportFormat.MERMAID) == "text/plain"
        assert get_mime_type(ExportFormat.JSON) == "application/json"
        assert get_mime_type(ExportFormat.MARKDOWN) == "text/markdown"

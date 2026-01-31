import pytest
from pydantic import ValidationError
from sparsemap.domain.models import Node, NodeType, Priority, Graph, Edge, EdgeType

class TestNode:
    def test_node_creation_valid(self):
        node = Node(
            id="1",
            label="Test Node",
            type=NodeType.main,
            priority=Priority.critical,
            reason="Because",
            description="A test node"
        )
        assert node.id == "1"
        assert node.type == NodeType.main
        assert node.priority == Priority.critical

    def test_node_defaults(self):
        node = Node(
            id="1",
            label="Test Node",
            type=NodeType.main,
            reason="Because"
        )
        assert node.priority == Priority.critical
        assert node.description is None

    def test_node_validation_missing_field(self):
        with pytest.raises(ValidationError):
            Node(id="1", label="Test Node") # Missing type, reason

class TestGraph:
    def test_graph_creation(self):
        node1 = Node(id="1", label="A", type=NodeType.main, reason="root")
        node2 = Node(id="2", label="B", type=NodeType.dependency, reason="dep")
        edge = Edge(source="1", target="2", type=EdgeType.depends_on, reason="A depends on B")

        graph = Graph(nodes=[node1, node2], edges=[edge])
        
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        assert graph.edges[0].type == EdgeType.depends_on

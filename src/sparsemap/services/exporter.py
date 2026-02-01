"""Graph export service supporting multiple formats."""

from __future__ import annotations

from enum import Enum
from typing import Protocol

from sparsemap.domain.models import Graph


class ExportFormat(str, Enum):
    MERMAID = "mermaid"
    D2 = "d2"
    JSON = "json"
    MARKDOWN = "markdown"


class GraphExporter(Protocol):
    """Protocol for graph exporters."""

    def export(self, graph: Graph) -> str:
        """Export graph to string format."""
        ...


def _sanitize_label(label: str) -> str:
    """Sanitize label for safe use in diagram languages."""
    # Replace characters that might break syntax
    return label.replace('"', "'").replace("[", "(").replace("]", ")")


def _mermaid_id(node_id: str) -> str:
    """Convert node ID to Mermaid-safe ID."""
    return node_id.replace("-", "_").replace(" ", "_")


class MermaidExporter:
    """Export graph to Mermaid diagram format."""

    def export(self, graph: Graph) -> str:
        lines = ["graph TD"]

        # Add nodes with labels
        for node in graph.nodes:
            safe_id = _mermaid_id(node.id)
            safe_label = _sanitize_label(node.label)
            lines.append(f'    {safe_id}["{safe_label}"]')

        # Add edges
        for edge in graph.edges:
            source = _mermaid_id(edge.source)
            target = _mermaid_id(edge.target)
            edge_label = edge.type.replace("_", " ")
            lines.append(f"    {source} -->|{edge_label}| {target}")

        return "\n".join(lines)


class D2Exporter:
    """Export graph to D2 diagram format."""

    def export(self, graph: Graph) -> str:
        lines = []

        # Define nodes with labels
        for node in graph.nodes:
            safe_label = _sanitize_label(node.label)
            lines.append(f'{node.id}: "{safe_label}"')

        lines.append("")  # Empty line separator

        # Add edges with labels
        for edge in graph.edges:
            edge_label = edge.type.replace("_", " ")
            lines.append(f"{edge.source} -> {edge.target}: {edge_label}")

        return "\n".join(lines)


class JsonExporter:
    """Export graph to JSON format."""

    def export(self, graph: Graph) -> str:
        return graph.model_dump_json(indent=2)


class MarkdownExporter:
    """Export graph to Markdown format with hierarchy and table."""

    def export(self, graph: Graph) -> str:
        lines = ["# Knowledge Graph Export", ""]

        # Summary
        if graph.summary:
            lines.extend(["## Summary", "", graph.summary, ""])

        # Nodes section
        lines.extend(["## Nodes", ""])
        for node in graph.nodes:
            priority_icon = "🔴" if node.priority.value == "critical" else "🟡"
            lines.append(f"### {priority_icon} {node.label}")
            lines.append("")
            if node.description:
                lines.append(f"**Description:** {node.description}")
                lines.append("")
            lines.append(f"- **Type:** {node.type.value}")
            lines.append(f"- **Priority:** {node.priority.value}")
            lines.append(f"- **Reason:** {node.reason}")
            if node.source:
                lines.append(f"- **Source:** {node.source}")
            lines.append("")

        # Relationships table
        lines.extend(["## Relationships", ""])
        lines.append("| From | To | Type | Reason |")
        lines.append("|------|-----|------|--------|")

        # Build node label map for readable table
        node_labels = {n.id: n.label for n in graph.nodes}

        for edge in graph.edges:
            source_label = node_labels.get(edge.source, edge.source)
            target_label = node_labels.get(edge.target, edge.target)
            lines.append(
                f"| {source_label} | {target_label} | {edge.type.value} | {edge.reason} |"
            )

        return "\n".join(lines)


# Exporter registry
_EXPORTERS: dict[ExportFormat, GraphExporter] = {
    ExportFormat.MERMAID: MermaidExporter(),
    ExportFormat.D2: D2Exporter(),
    ExportFormat.JSON: JsonExporter(),
    ExportFormat.MARKDOWN: MarkdownExporter(),
}


def export_graph(graph: Graph, format: ExportFormat) -> str:
    """Export graph to specified format.

    Args:
        graph: The graph to export
        format: Target export format

    Returns:
        Exported content as string

    Raises:
        ValueError: If format is not supported
    """
    exporter = _EXPORTERS.get(format)
    if not exporter:
        raise ValueError(f"Unsupported export format: {format}")
    return exporter.export(graph)


def get_file_extension(format: ExportFormat) -> str:
    """Get file extension for export format."""
    extensions = {
        ExportFormat.MERMAID: "mmd",
        ExportFormat.D2: "d2",
        ExportFormat.JSON: "json",
        ExportFormat.MARKDOWN: "md",
    }
    return extensions.get(format, "txt")


def get_mime_type(format: ExportFormat) -> str:
    """Get MIME type for export format."""
    mime_types = {
        ExportFormat.MERMAID: "text/plain",
        ExportFormat.D2: "text/plain",
        ExportFormat.JSON: "application/json",
        ExportFormat.MARKDOWN: "text/markdown",
    }
    return mime_types.get(format, "text/plain")

// static/js/exporter.js
// Local graph export utilities (mirrors backend exporter.py logic)

function sanitizeLabel(label) {
  return label.replace(/"/g, "'").replace(/\[/g, '(').replace(/\]/g, ')');
}

function mermaidId(nodeId) {
  return nodeId.replace(/-/g, '_').replace(/ /g, '_');
}

function exportToMermaid(graph) {
  const lines = ['graph TD'];

  for (const node of graph.nodes) {
    const safeId = mermaidId(node.id);
    const safeLabel = sanitizeLabel(node.label);
    lines.push(`    ${safeId}["${safeLabel}"]`);
  }

  for (const edge of graph.edges) {
    const source = mermaidId(edge.source);
    const target = mermaidId(edge.target);
    const edgeLabel = edge.type.replace(/_/g, ' ');
    lines.push(`    ${source} -->|${edgeLabel}| ${target}`);
  }

  return lines.join('\n');
}

function exportToD2(graph) {
  const lines = [];

  for (const node of graph.nodes) {
    const safeLabel = sanitizeLabel(node.label);
    lines.push(`${node.id}: "${safeLabel}"`);
  }

  lines.push('');

  for (const edge of graph.edges) {
    const edgeLabel = edge.type.replace(/_/g, ' ');
    lines.push(`${edge.source} -> ${edge.target}: ${edgeLabel}`);
  }

  return lines.join('\n');
}

function exportToJson(graph) {
  return JSON.stringify(graph, null, 2);
}

function exportToMarkdown(graph) {
  const lines = ['# Knowledge Graph Export', ''];

  if (graph.summary) {
    lines.push('## Summary', '', graph.summary, '');
  }

  lines.push('## Nodes', '');

  for (const node of graph.nodes) {
    const priorityIcon = node.priority === 'critical' ? '🔴' : '🟡';
    lines.push(`### ${priorityIcon} ${node.label}`);
    lines.push('');

    if (node.description) {
      lines.push(`**Description:** ${node.description}`);
      lines.push('');
    }

    lines.push(`- **Type:** ${node.type}`);
    lines.push(`- **Priority:** ${node.priority}`);
    lines.push(`- **Reason:** ${node.reason}`);

    if (node.source) {
      lines.push(`- **Source:** ${node.source}`);
    }

    lines.push('');
  }

  // Build node label map
  const nodeLabels = {};
  for (const n of graph.nodes) {
    nodeLabels[n.id] = n.label;
  }

  lines.push('## Relationships', '');
  lines.push('| From | To | Type | Reason |');
  lines.push('|------|-----|------|--------|');

  for (const edge of graph.edges) {
    const sourceLabel = nodeLabels[edge.source] || edge.source;
    const targetLabel = nodeLabels[edge.target] || edge.target;
    lines.push(`| ${sourceLabel} | ${targetLabel} | ${edge.type} | ${edge.reason} |`);
  }

  return lines.join('\n');
}

export function exportGraphLocally(graph, format) {
  switch (format) {
    case 'mermaid':
      return exportToMermaid(graph);
    case 'd2':
      return exportToD2(graph);
    case 'json':
      return exportToJson(graph);
    case 'markdown':
      return exportToMarkdown(graph);
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
}

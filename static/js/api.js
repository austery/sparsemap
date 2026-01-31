import { API_BASE } from './config.js';

// Simpler version that matches existing usage patterns (expects JSON almost always)
async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  let data;
  try {
    data = await response.json();
  } catch (_e) {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} ${response.statusText}`);
    }
    // If ok but not JSON (e.g. empty body 204), handle gracefully if needed,
    // but our API seems to return JSON.
    // For now, assume if it's 200 it should be JSON, otherwise error.
    throw new Error('Invalid JSON response');
  }

  if (!response.ok) {
    throw new Error(data.detail || data.error || `HTTP ${response.status} Error`);
  }
  return data;
}

export async function fetchHistory() {
  return fetchJson(`${API_BASE}/api/history`);
}

export async function fetchHistoryItem(id) {
  return fetchJson(`${API_BASE}/api/history/${encodeURIComponent(id)}`);
}

export async function deleteHistoryItem(id) {
  const response = await fetch(`${API_BASE}/api/history/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    let data;
    try {
      data = await response.json();
    } catch (_e) {
      throw new Error(`HTTP ${response.status} ${response.statusText}`);
    }
    throw new Error(data.detail || 'Failed to delete');
  }
  return true;
}

export async function analyze(payload) {
  // payload: { urls: [], texts: [] }
  return fetchJson(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

export async function addUrl(url) {
  return fetchJson(`${API_BASE}/api/add-url`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url: url }),
  });
}

export async function fetchNodeDetails(payload) {
  // payload: { node_label, node_description, node_context }
  return fetchJson(`${API_BASE}/api/node-details`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export async function integrateConcept(payload) {
  // payload: { new_concept: string, existing_nodes: array }
  return fetchJson(`${API_BASE}/api/integrate-concept`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export async function exportGraph(analysisId, format = 'mermaid') {
  // format: 'mermaid' | 'd2' | 'json' | 'markdown'
  const response = await fetch(
    `${API_BASE}/api/export/${encodeURIComponent(analysisId)}?format=${encodeURIComponent(format)}`
  );
  if (!response.ok) {
    let data;
    try {
      data = await response.json();
    } catch (_e) {
      throw new Error(`HTTP ${response.status} ${response.statusText}`);
    }
    throw new Error(data.detail || 'Export failed');
  }
  return response.text();
}

export async function embedAnalysis(analysisId) {
  return fetchJson(`${API_BASE}/api/embed/${encodeURIComponent(analysisId)}`, {
    method: 'POST',
  });
}

export async function recallSimilarNodes(query, topK = 5, excludeAnalysisId = null) {
  const params = new URLSearchParams({ query, top_k: topK });
  if (excludeAnalysisId) {
    params.append('exclude_analysis_id', excludeAnalysisId);
  }
  return fetchJson(`${API_BASE}/api/recall?${params.toString()}`);
}

export async function expandNode(nodeId, nodeLabel, nodeDescription = null, graphContext = null) {
  return fetchJson(`${API_BASE}/api/expand-node`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      node_id: nodeId,
      node_label: nodeLabel,
      node_description: nodeDescription,
      graph_context: graphContext,
    }),
  });
}

import { API_BASE } from './config.js';

export async function fetchHistory() {
    const response = await fetch(`${API_BASE}/api/history`);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Failed to load history');
    }
    return data;
}

export async function fetchHistoryItem(id) {
    const response = await fetch(`${API_BASE}/api/history/${id}`);
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.detail || 'Failed to load');
    }
    return result;
}

export async function deleteHistoryItem(id) {
    const response = await fetch(`${API_BASE}/api/history/${id}`, { method: 'DELETE' });
    if (!response.ok) {
         const data = await response.json();
         throw new Error(data.detail || 'Failed to delete');
    }
    return true;
}

export async function analyze(payload) {
    // payload: { urls: [], texts: [] }
    const response = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.detail || result.error || `HTTP ${response.status} Error`);
    }
    return result;
}

export async function addUrl(url) {
    const response = await fetch(`${API_BASE}/api/add-url`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    });
    const result = await response.json();
    if (!response.ok) {
         throw new Error(result.detail || result.error || `HTTP ${response.status} Error`);
    }
    return result;
}

export async function fetchNodeDetails(payload) {
    // payload: { node_label, node_description, node_context }
    const response = await fetch(`${API_BASE}/api/node-details`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.detail || 'Failed to fetch details');
    }
    return result;
}

export async function analyzeTest() {
    const response = await fetch(`${API_BASE}/api/analyze-test`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    });
    const result = await response.json();
    if (!response.ok) {
         throw new Error(result.detail || result.error || `HTTP ${response.status} Error`);
    }
    return result;
}

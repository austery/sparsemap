import * as API from './api.js';
import {
  addLinkedConcept,
  formatGraph,
  mergeGraphData,
  renderGraph,
  toggleLayoutDirection,
} from './graph.js';
import { setGraphData, state } from './state.js';
import * as UI from './ui.js';

document.addEventListener('DOMContentLoaded', () => {
  initEventListeners();
});

function initEventListeners() {
  // Tab switching
  document.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      UI.switchTab(tab);
      if (tab === 'history') {
        loadHistory();
      }
    });
  });

  // Analyze URL
  const analyzeBtn = document.getElementById('analyze-btn');
  const urlInput = document.getElementById('url-input');

  if (analyzeBtn) analyzeBtn.addEventListener('click', handleAnalyze);
  if (urlInput) {
    urlInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleAnalyze();
      }
    });
  }

  // Analyze Text
  const analyzeTextBtn = document.getElementById('analyze-text-btn');
  const textInput = document.getElementById('text-input');

  if (analyzeTextBtn) analyzeTextBtn.addEventListener('click', handleAnalyzeText);
  if (textInput) {
    textInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && e.metaKey) {
        // Cmd+Enter
        e.preventDefault();
        handleAnalyzeText();
      }
    });
  }

  // Canvas Screen Inputs
  const backBtn = document.getElementById('back-btn');
  const addUrlBtn = document.getElementById('add-url-btn');
  const closeInfoBtn = document.getElementById('close-info');

  if (backBtn) backBtn.addEventListener('click', () => UI.switchScreen('input'));
  if (addUrlBtn) addUrlBtn.addEventListener('click', () => UI.showAddUrlModal());
  if (closeInfoBtn) closeInfoBtn.addEventListener('click', () => UI.hideNodeInfo());

  // Modal
  const closeModalBtn = document.getElementById('close-modal');
  const cancelBtn = document.getElementById('cancel-btn');
  const backdrop = document.getElementById('modal-backdrop');
  const confirmAddBtn = document.getElementById('confirm-add-btn');
  const newUrlInput = document.getElementById('new-url-input');

  if (closeModalBtn) closeModalBtn.addEventListener('click', UI.hideAddUrlModal);
  if (cancelBtn) cancelBtn.addEventListener('click', UI.hideAddUrlModal);
  if (backdrop) backdrop.addEventListener('click', UI.hideAddUrlModal);
  if (confirmAddBtn) confirmAddBtn.addEventListener('click', handleAddUrl);
  if (newUrlInput) {
    newUrlInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleAddUrl();
    });
  }

  // Graph Control Buttons
  const toggleLayoutBtn = document.getElementById('toggle-layout-btn');
  const formatGraphBtn = document.getElementById('format-graph-btn');
  const linkConceptBtn = document.getElementById('link-concept-btn');

  if (toggleLayoutBtn) toggleLayoutBtn.addEventListener('click', handleToggleLayout);
  if (formatGraphBtn) formatGraphBtn.addEventListener('click', handleFormatGraph);
  if (linkConceptBtn) linkConceptBtn.addEventListener('click', showLinkConceptModal);

  // Link Concept Modal
  const closeLinkModalBtn = document.getElementById('close-link-modal');
  const cancelLinkBtn = document.getElementById('cancel-link-btn');
  const linkConceptBackdrop = document.getElementById('link-concept-backdrop');
  const confirmLinkBtn = document.getElementById('confirm-link-btn');
  const newConceptInput = document.getElementById('new-concept-input');

  if (closeLinkModalBtn) closeLinkModalBtn.addEventListener('click', hideLinkConceptModal);
  if (cancelLinkBtn) cancelLinkBtn.addEventListener('click', hideLinkConceptModal);
  if (linkConceptBackdrop) linkConceptBackdrop.addEventListener('click', hideLinkConceptModal);
  if (confirmLinkBtn) confirmLinkBtn.addEventListener('click', handleIntegrateConcept);
  if (newConceptInput) {
    newConceptInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleIntegrateConcept();
    });
  }

  // Delegate dynamic events (History load/delete, Deep Dive)
  document.body.addEventListener('click', handleDynamicEvents);
}

function handleDynamicEvents(e) {
  // History Load
  const loadBtn =
    e.target.closest('.load-history-btn') ||
    e.target.closest('.history-item-actions .btn-icon[title="打开"]');
  if (loadBtn) {
    const id = loadBtn.dataset.id || loadBtn.closest('.history-item')?.dataset.id;
    if (id) loadHistoryItem(id);
    return;
  }

  // History Delete
  const deleteBtn =
    e.target.closest('.delete-history-btn') || e.target.closest('.history-item-actions .delete');
  if (deleteBtn) {
    const id = deleteBtn.dataset.id || deleteBtn.closest('.history-item')?.dataset.id;
    if (id) deleteHistoryItem(id);
    return;
  }

  // Deep Dive
  const deepDiveBtn = e.target.closest('#deep-dive-btn');
  if (deepDiveBtn) {
    const label = deepDiveBtn.dataset.label;
    const desc = deepDiveBtn.dataset.desc;
    handleDeepDive(label, desc);
    return;
  }
}

async function handleAnalyze() {
  const urlInput = document.getElementById('url-input');
  const url = urlInput.value.trim();

  if (!url) {
    alert('请输入有效的 URL');
    return;
  }

  UI.setLoading('loading-indicator', true);
  UI.setButtonLoading('analyze-btn', true);

  try {
    const result = await API.analyze({ urls: [url], texts: [] });
    if (result.success) {
      setGraphData(result.data);
      UI.switchScreen('canvas');
      setTimeout(() => renderGraph(result.data), 100);
    } else {
      alert(`分析失败: ${result.error || result.detail || '未知错误'}`);
    }
  } catch (e) {
    console.error(e);
    alert(`系统错误: ${e.message}`);
  } finally {
    UI.setLoading('loading-indicator', false);
    UI.setButtonLoading('analyze-btn', false);
  }
}

async function handleAnalyzeText() {
  const textInput = document.getElementById('text-input');
  const text = textInput.value.trim();

  if (!text) {
    alert('请输入课程内容文本');
    return;
  }
  if (text.length < 50) {
    alert('文本内容太短，请输入至少 50 个字符的课程内容');
    return;
  }

  UI.setLoading('loading-indicator', true);
  UI.setButtonLoading('analyze-text-btn', true);

  try {
    const result = await API.analyze({ urls: [], texts: [text] });
    if (result.success) {
      setGraphData(result.data);
      UI.switchScreen('canvas');
      setTimeout(() => renderGraph(result.data), 100);
    } else {
      alert(`分析失败: ${result.error || result.detail || '未知错误'}`);
    }
  } catch (e) {
    console.error(e);
    alert(`系统错误: ${e.message}`);
  } finally {
    UI.setLoading('loading-indicator', false);
    UI.setButtonLoading('analyze-text-btn', false);
  }
}

async function loadHistory() {
  const historyList = document.getElementById('history-list');
  if (!historyList) return;

  historyList.innerHTML = '<div class="history-loading">加载中...</div>';

  try {
    const data = await API.fetchHistory();
    if (data.items) {
      UI.renderHistoryList(data.items);
    } else {
      historyList.innerHTML = '<div class="history-error">数据格式错误</div>';
    }
  } catch (e) {
    console.error(e);
    historyList.innerHTML = `<div class="history-error">加载失败: ${e.message}</div>`;
  }
}

async function loadHistoryItem(id) {
  UI.setLoading('loading-indicator', true);
  try {
    const result = await API.fetchHistoryItem(id);
    if (result.success) {
      setGraphData(result.data);
      UI.switchScreen('canvas');
      setTimeout(() => renderGraph(result.data), 100);
    }
  } catch (e) {
    console.error(e);
    alert(`加载失败: ${e.message}`);
  } finally {
    UI.setLoading('loading-indicator', false);
  }
}

async function deleteHistoryItem(id) {
  if (!confirm('确定要删除这条记录吗？')) return;
  try {
    await API.deleteHistoryItem(id);
    loadHistory();
  } catch (e) {
    console.error(e);
    alert(`删除失败: ${e.message}`);
  }
}

async function handleAddUrl() {
  const input = document.getElementById('new-url-input');
  const url = input.value.trim();

  if (!url) {
    alert('请输入有效的 URL');
    return;
  }

  UI.setLoading('modal-loading', true);
  UI.setButtonLoading('confirm-add-btn', true);

  try {
    const result = await API.addUrl(url);
    if (result.success) {
      mergeGraphData(result.data);
      UI.hideAddUrlModal();
    } else {
      alert(`添加失败: ${result.error || result.detail}`);
    }
  } catch (e) {
    console.error(e);
    alert(`添加失败: ${e.message}`);
  } finally {
    UI.setLoading('modal-loading', false);
    UI.setButtonLoading('confirm-add-btn', false);
  }
}

async function handleDeepDive(label, desc) {
  UI.setDeepDiveLoading();
  try {
    const result = await API.fetchNodeDetails({
      node_label: label,
      node_description: desc,
      node_context: desc,
    });
    UI.renderDeepDiveContent(result);
  } catch (e) {
    console.error(e);
    UI.renderDeepDiveError(e);
  }
}

// Graph Control Handlers
function handleToggleLayout() {
  const newDirection = toggleLayoutDirection();
  const btn = document.getElementById('toggle-layout-btn');
  if (btn) {
    const label = btn.querySelector('span');
    if (label) {
      label.textContent = newDirection === 'TB' ? '横向布局' : '纵向布局';
    }
  }
}

function handleFormatGraph() {
  formatGraph();
}

function showLinkConceptModal() {
  const modal = document.getElementById('link-concept-modal');
  const input = document.getElementById('new-concept-input');
  if (modal) {
    modal.classList.remove('hidden');
    if (input) {
      input.value = '';
      input.focus();
    }
  }
}

function hideLinkConceptModal() {
  const modal = document.getElementById('link-concept-modal');
  if (modal) {
    modal.classList.add('hidden');
  }
}

async function handleIntegrateConcept() {
  const input = document.getElementById('new-concept-input');
  const concept = input?.value.trim();

  if (!concept) {
    alert('请输入要关联的概念');
    return;
  }

  // Get existing nodes from current graph
  const existingNodes =
    state.currentGraphData?.nodes?.map((n) => ({
      id: n.id,
      label: n.label,
      description: n.description || '',
    })) || [];

  if (existingNodes.length === 0) {
    alert('当前图谱为空，请先分析一个内容');
    return;
  }

  UI.setLoading('link-modal-loading', true);
  UI.setButtonLoading('confirm-link-btn', true);

  try {
    const result = await API.integrateConcept({
      new_concept: concept,
      existing_nodes: existingNodes,
    });

    if (result.success && result.data) {
      addLinkedConcept(result.data);
      hideLinkConceptModal();
    } else {
      alert(`关联失败: ${result.error || result.detail || '未知错误'}`);
    }
  } catch (e) {
    console.error(e);
    alert(`关联失败: ${e.message}`);
  } finally {
    UI.setLoading('link-modal-loading', false);
    UI.setButtonLoading('confirm-link-btn', false);
  }
}

window.debugState = state;

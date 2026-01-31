// static/js/ui.js
import { state } from './state.js';

export function escapeHtml(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function formatDate(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins} 分钟前`;
  if (diffHours < 24) return `${diffHours} 小时前`;
  if (diffDays < 7) return `${diffDays} 天前`;
  return date.toLocaleDateString('zh-CN');
}

export function switchTab(tab) {
  const urlGroup = document.getElementById('url-input-group');
  const textGroup = document.getElementById('text-input-group');
  const historyGroup = document.getElementById('history-input-group');
  const urlInput = document.getElementById('url-input');
  const textInput = document.getElementById('text-input');
  const tabButtons = document.querySelectorAll('.tab-btn');

  if (!urlGroup || !textGroup || !historyGroup) return;

  tabButtons.forEach((btn) => {
    if (btn.dataset.tab === tab) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Hide all groups
  urlGroup.classList.add('hidden');
  textGroup.classList.add('hidden');
  historyGroup.classList.add('hidden');

  if (tab === 'url') {
    urlGroup.classList.remove('hidden');
    if (urlInput) setTimeout(() => urlInput.focus(), 100);
  } else if (tab === 'text') {
    textGroup.classList.remove('hidden');
    if (textInput) setTimeout(() => textInput.focus(), 100);
  } else if (tab === 'history') {
    historyGroup.classList.remove('hidden');
  }
}

export function switchScreen(screenName) {
  console.log(`🔄 切换屏幕到: ${screenName}`);

  const allScreens = document.querySelectorAll('.screen');

  // Remove active from all
  allScreens.forEach((screen) => {
    screen.classList.remove('active');
    screen.style.display = 'none';
    screen.style.visibility = 'hidden';
    screen.style.opacity = '0';
    screen.style.pointerEvents = 'none';
    screen.style.zIndex = '0';
  });

  const targetScreen = document.getElementById(`${screenName}-screen`);
  if (targetScreen) {
    targetScreen.classList.add('active');
    targetScreen.style.display = 'flex';
    targetScreen.style.visibility = 'visible';
    targetScreen.style.opacity = '1';
    targetScreen.style.pointerEvents = 'auto';
    targetScreen.style.zIndex = '10';
  } else {
    console.error(`❌ 找不到屏幕元素: ${screenName}-screen`);
  }
}

export function renderHistoryList(items) {
  const historyList = document.getElementById('history-list');
  if (!historyList) return;

  if (items.length === 0) {
    historyList.innerHTML = '<div class="history-empty">暂无历史记录</div>';
    return;
  }

  historyList.innerHTML = items
    .map((item) => {
      const sourceType =
        item.source_type === 'url' || item.source_type === 'text' ? item.source_type : 'text';
      const safeId = escapeHtml(String(item.id));
      return `
        <div class="history-item" data-id="${safeId}">
            <div class="history-item-info">
                <div class="history-item-title">${escapeHtml(item.title)}</div>
                <div class="history-item-meta">
                    <span class="history-type ${sourceType}">${sourceType === 'url' ? '🔗 URL' : '📝 文本'}</span>
                    <span class="history-nodes">${escapeHtml(String(item.node_count))} 节点</span>
                    <span class="history-date">${formatDate(item.created_at)}</span>
                </div>
            </div>
            <div class="history-item-actions">
                <button class="btn-icon load-history-btn" data-id="${safeId}" title="打开">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
                <button class="btn-icon delete-history-btn" data-id="${safeId}" title="删除">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
        </div>
    `;
    })
    .join('');
}

export function showNodeInfo(nodeData, currentGraphData) {
  const panel = document.getElementById('node-info-panel');
  const title = document.getElementById('node-title');
  const contentDiv = document.getElementById('node-details-content');
  const loading = document.getElementById('loading-details');

  if (!panel || !title || !contentDiv || !loading) return;

  title.textContent = nodeData.label;
  loading.classList.add('hidden');

  const hasMultipleSources =
    currentGraphData?.nodes &&
    new Set(currentGraphData.nodes.map((n) => n.source).filter(Boolean)).size > 1;

  let basicHtml = '';

  if (nodeData.description) {
    basicHtml += `
            <div class="detail-card">
                <div class="card-label">📝 Description</div>
                <div class="card-content">${escapeHtml(nodeData.description)}</div>
            </div>`;
  }

  if (nodeData.reason) {
    basicHtml += `
            <div class="detail-card">
                <div class="card-label">💡 Reason</div>
                <div class="card-content">${escapeHtml(nodeData.reason)}</div>
            </div>`;
  }

  if (nodeData.source && hasMultipleSources) {
    basicHtml += `
            <div class="detail-card">
                <div class="card-label">📚 Source</div>
                <div class="card-content">${escapeHtml(nodeData.source)}</div>
            </div>`;
  }

  if (nodeData.type === 'dependency') {
    basicHtml += `
            <div class="detail-card" style="border-color: #2dd4bf;">
                <div class="card-content">💡 这是一个技术依赖，你可以先了解其基本用途，不必深挖细节。</div>
            </div>`;
  }

  // Add Deep Dive button
  basicHtml += `
        <div style="margin-top: 16px; text-align: center;">
            <button id="deep-dive-btn" class="deep-dive-btn"
                data-label="${escapeHtml(nodeData.label)}"
                data-desc="${escapeHtml(nodeData.description || '')}">
                🔍 Deep Dive (AI 详解)
            </button>
        </div>
        <div id="deep-dive-content"></div>`;

  contentDiv.innerHTML = basicHtml || '<p>暂无详细信息</p>';
  panel.classList.add('visible');
}

export function renderDeepDiveContent(details) {
  const contentDiv = document.getElementById('deep-dive-content');
  const btn = document.getElementById('deep-dive-btn');

  if (!contentDiv) return;

  if (btn) btn.style.display = 'none';

  const html = `
        <div class="detail-card">
            <div class="card-label">📖 Definition</div>
            <div class="card-content">${escapeHtml(details.definition)}</div>
        </div>

        <div class="detail-card">
            <div class="card-label">💡 Analogy</div>
            <div class="card-content">${escapeHtml(details.analogy)}</div>
        </div>

        <div class="detail-card">
            <div class="card-label">⚡ Why It Matters</div>
            <div class="card-content">${escapeHtml(details.importance)}</div>
        </div>

        <div class="detail-card">
            <div class="card-label">🚀 Actionable Step</div>
            <div class="card-content">${escapeHtml(details.actionable_step)}</div>
        </div>

        <div class="detail-card">
            <div class="card-label">🏷️ Keywords</div>
            <div class="card-content">
                ${details.keywords.map((k) => `<span class="keyword-tag">${escapeHtml(k)}</span>`).join('')}
            </div>
        </div>
    `;
  contentDiv.innerHTML = html;
}

export function renderDeepDiveError(error) {
  const contentDiv = document.getElementById('deep-dive-content');
  const btn = document.getElementById('deep-dive-btn');

  if (!contentDiv) return;

  contentDiv.innerHTML = `<div class="detail-card" style="border-color: red;"><div class="card-content">Failed to load Deep Dive. ${escapeHtml(error.message)}</div></div>`;
  if (btn) {
    btn.disabled = false;
    btn.textContent = '🔍 Retry Deep Dive';
  }
}

export function setDeepDiveLoading() {
  const btn = document.getElementById('deep-dive-btn');
  const contentDiv = document.getElementById('deep-dive-content');

  if (btn) {
    btn.disabled = true;
    btn.textContent = '⏳ Loading...';
  }

  if (contentDiv) {
    contentDiv.innerHTML =
      '<div class="loading-spinner" style="text-align: center; padding: 20px;">AI 正在生成详解...</div>';
  }
}

export function hideNodeInfo() {
  const panel = document.getElementById('node-info-panel');
  if (panel) panel.classList.remove('visible');

  if (state.cy) {
    state.cy.elements().unselect();
  }
}

export function showAddUrlModal() {
  const modal = document.getElementById('add-url-modal');
  const input = document.getElementById('new-url-input');

  if (modal) modal.classList.remove('hidden');
  if (input) {
    input.value = '';
    input.focus();
  }
}

export function hideAddUrlModal() {
  const modal = document.getElementById('add-url-modal');
  const loading = document.getElementById('modal-loading');

  if (modal) modal.classList.add('hidden');
  if (loading) loading.classList.add('hidden');
}

export function setLoading(elementId, isLoading) {
  const el = document.getElementById(elementId);
  if (!el) return;
  if (isLoading) el.classList.remove('hidden');
  else el.classList.add('hidden');
}

export function setButtonLoading(btnId, isLoading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = isLoading;
}

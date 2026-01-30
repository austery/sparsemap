// Logic Linker - 前端核心逻辑

const API_BASE = '';

let cy = null;
let currentGraphData = null;

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
});

function initEventListeners() {
    // 标签页切换
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            switchTab(tab);
        });
    });

    // URL 输入界面
    const analyzeBtn = document.getElementById('analyze-btn');
    const urlInput = document.getElementById('url-input');

    analyzeBtn.addEventListener('click', handleAnalyze);
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleAnalyze();
        }
    });


    // 文本输入界面
    const analyzeTextBtn = document.getElementById('analyze-text-btn');
    const textInput = document.getElementById('text-input');

    analyzeTextBtn.addEventListener('click', handleAnalyzeText);
    textInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.metaKey) { // Cmd+Enter 提交
            e.preventDefault();
            handleAnalyzeText();
        }
    });

    // 画布界面
    const backBtn = document.getElementById('back-btn');
    const addUrlBtn = document.getElementById('add-url-btn');
    const closeInfoBtn = document.getElementById('close-info');

    backBtn.addEventListener('click', () => {
        switchScreen('input');
    });
    addUrlBtn.addEventListener('click', () => {
        showAddUrlModal();
    });
    closeInfoBtn.addEventListener('click', () => {
        hideNodeInfo();
    });

    // 模态框
    const modal = document.getElementById('add-url-modal');
    const modalBackdrop = document.getElementById('modal-backdrop');
    const closeModalBtn = document.getElementById('close-modal');
    const cancelBtn = document.getElementById('cancel-btn');
    const confirmAddBtn = document.getElementById('confirm-add-btn');
    const newUrlInput = document.getElementById('new-url-input');

    closeModalBtn.addEventListener('click', hideAddUrlModal);
    cancelBtn.addEventListener('click', hideAddUrlModal);
    modalBackdrop.addEventListener('click', hideAddUrlModal);
    confirmAddBtn.addEventListener('click', handleAddUrl);
    newUrlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleAddUrl();
        }
    });
}

// ==================== 标签页切换 ====================

function switchTab(tab) {
    const urlGroup = document.getElementById('url-input-group');
    const textGroup = document.getElementById('text-input-group');
    const historyGroup = document.getElementById('history-input-group');
    const urlInput = document.getElementById('url-input');
    const textInput = document.getElementById('text-input');
    const tabButtons = document.querySelectorAll('.tab-btn');

    tabButtons.forEach(btn => {
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
        setTimeout(() => urlInput.focus(), 100);
    } else if (tab === 'text') {
        textGroup.classList.remove('hidden');
        setTimeout(() => textInput.focus(), 100);
    } else if (tab === 'history') {
        historyGroup.classList.remove('hidden');
        loadHistory();
    }
}

// ==================== 历史记录 ====================

async function loadHistory() {
    const historyList = document.getElementById('history-list');
    historyList.innerHTML = '<div class="history-loading">加载中...</div>';

    try {
        const response = await fetch(`${API_BASE}/api/history`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to load history');
        }

        if (data.items.length === 0) {
            historyList.innerHTML = '<div class="history-empty">暂无历史记录</div>';
            return;
        }

        historyList.innerHTML = data.items.map(item => `
            <div class="history-item" data-id="${item.id}">
                <div class="history-item-info">
                    <div class="history-item-title">${escapeHtml(item.title)}</div>
                    <div class="history-item-meta">
                        <span class="history-type ${item.source_type}">${item.source_type === 'url' ? '🔗 URL' : '📝 文本'}</span>
                        <span class="history-nodes">${item.node_count} 节点</span>
                        <span class="history-date">${formatDate(item.created_at)}</span>
                    </div>
                </div>
                <div class="history-item-actions">
                    <button class="btn-icon" onclick="loadHistoryItem(${item.id})" title="打开">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                    <button class="btn-icon delete" onclick="deleteHistoryItem(${item.id})" title="删除">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Load history error:', error);
        historyList.innerHTML = `<div class="history-error">加载失败: ${error.message}</div>`;
    }
}

async function loadHistoryItem(id) {
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE}/api/history/${id}`);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Failed to load');
        }

        if (result.success) {
            currentGraphData = result.data;
            switchScreen('canvas');
            setTimeout(() => renderGraph(result.data), 100);
        }
    } catch (error) {
        console.error('Load history item error:', error);
        alert('加载失败: ' + error.message);
    } finally {
        loadingIndicator.classList.add('hidden');
    }
}

async function deleteHistoryItem(id) {
    if (!confirm('确定要删除这条记录吗？')) return;

    try {
        const response = await fetch(`${API_BASE}/api/history/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadHistory(); // Refresh list
        } else {
            const data = await response.json();
            alert('删除失败: ' + (data.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('删除失败: ' + error.message);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(isoString) {
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

// ==================== 屏幕切换 ====================

function switchScreen(screenName) {
    console.log(`🔄 切换屏幕到: ${screenName}`); // 调试日志

    // 获取所有屏幕元素
    const allScreens = document.querySelectorAll('.screen');
    console.log(`找到 ${allScreens.length} 个屏幕元素`);

    // 移除所有 active 类
    allScreens.forEach((screen, index) => {
        const hadActive = screen.classList.contains('active');
        screen.classList.remove('active');
        console.log(`  屏幕 ${index + 1} (${screen.id}): 移除 active${hadActive ? ' (之前是 active)' : ''}`);
    });

    // 找到目标屏幕
    const targetScreen = document.getElementById(`${screenName}-screen`);
    if (targetScreen) {
        targetScreen.classList.add('active');
        console.log(`✅ 屏幕 ${screenName} 已激活`);

        // 验证切换是否成功
        const isActive = targetScreen.classList.contains('active');
        const computedStyle = window.getComputedStyle(targetScreen);
        const display = computedStyle.display;
        const visibility = computedStyle.visibility;
        const opacity = computedStyle.opacity;
        console.log(`   检查结果: active=${isActive}, display=${display}, visibility=${visibility}, opacity=${opacity}`);

        // 检查所有屏幕的显示状态
        allScreens.forEach((screen, index) => {
            const screenStyle = window.getComputedStyle(screen);
            console.log(`   屏幕 ${screen.id}: display=${screenStyle.display}, visibility=${screenStyle.visibility}, hasActive=${screen.classList.contains('active')}`);
        });

        if (display === 'none' || visibility === 'hidden') {
            console.error(`⚠️  警告: 屏幕已激活但显示属性异常！`);
            console.log(`   尝试强制设置显示属性`);
            targetScreen.style.display = 'flex';
            targetScreen.style.visibility = 'visible';
            targetScreen.style.opacity = '1';
        }

        // 强制隐藏所有其他屏幕
        allScreens.forEach(screen => {
            if (screen !== targetScreen) {
                screen.classList.remove('active');
                screen.style.display = 'none';
                screen.style.visibility = 'hidden';
                screen.style.opacity = '0';
                screen.style.pointerEvents = 'none';
                screen.style.zIndex = '0';
                console.log(`   强制隐藏: ${screen.id}`);
            }
        });

        // 强制显示目标屏幕
        targetScreen.style.display = 'flex';
        targetScreen.style.visibility = 'visible';
        targetScreen.style.opacity = '1';
        targetScreen.style.pointerEvents = 'auto';
        targetScreen.style.zIndex = '10';
        console.log(`   强制显示: ${targetScreen.id}`);

        // 延迟验证，确保切换成功
        setTimeout(() => {
            const inputScreen = document.getElementById('input-screen');
            const canvasScreen = document.getElementById('canvas-screen');

            if (screenName === 'canvas' && inputScreen) {
                const inputStyle = window.getComputedStyle(inputScreen);
                if (inputStyle.display !== 'none') {
                    console.error(`❌ input-screen 仍然显示！再次强制隐藏...`);
                    inputScreen.style.cssText = 'display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important; z-index: 0 !important;';
                }
            }

            if (canvasScreen) {
                const canvasStyle = window.getComputedStyle(canvasScreen);
                console.log(`   最终验证 - canvas-screen: display=${canvasStyle.display}, visibility=${canvasStyle.visibility}, zIndex=${canvasStyle.zIndex}`);
            }
        }, 100);
    } else {
        console.error(`❌ 找不到屏幕元素: ${screenName}-screen`);
        console.log(`   当前页面中的屏幕元素:`, Array.from(allScreens).map(s => s.id));
    }

    if (screenName === 'canvas') {
        console.log('准备初始化 Cytoscape，当前 cy 状态:', cy ? '已初始化' : '未初始化');
        if (!cy) {
            console.log('初始化 Cytoscape...');
            initCytoscape();
        } else {
            console.log('Cytoscape 已存在，跳过初始化');
        }
    }
}

// ==================== 分析课程 ====================

async function handleAnalyze() {
    const urlInput = document.getElementById('url-input');
    const url = urlInput.value.trim();

    if (!url) {
        alert('请输入有效的 URL');
        return;
    }

    const loadingIndicator = document.getElementById('loading-indicator');
    const analyzeBtn = document.getElementById('analyze-btn');

    loadingIndicator.classList.remove('hidden');
    analyzeBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                urls: [url],
                texts: []
            })
        });

        const result = await response.json();

        if (!response.ok) {
            // HTTP 错误响应
            const errorMsg = result.detail || result.error || `HTTP ${response.status} 错误`;
            console.error('API 错误:', result);
            alert('分析失败：' + errorMsg);
            return;
        }

        if (result.success) {
            currentGraphData = result.data;
            switchScreen('canvas');
            renderGraph(result.data);
        } else {
            const errorMsg = result.error || result.detail || '未知错误';
            console.error('分析失败:', result);
            alert('分析失败：' + errorMsg);
        }
    } catch (error) {
        console.error('分析错误:', error);
        alert('分析失败：' + (error.message || '网络错误，请检查服务器是否正常运行'));
    } finally {
        loadingIndicator.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
}

// ==================== 分析文本内容 ====================

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

    const loadingIndicator = document.getElementById('loading-indicator');
    const analyzeTextBtn = document.getElementById('analyze-text-btn');

    loadingIndicator.classList.remove('hidden');
    analyzeTextBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                urls: [],
                texts: [text]
            })
        });

        const result = await response.json();

        console.log('API 响应:', result); // 调试日志

        if (!response.ok) {
            const errorMsg = result.detail || result.error || `HTTP ${response.status} 错误`;
            console.error('API 错误:', result);
            alert('分析失败：' + errorMsg);
            return;
        }

        if (result.success) {
            console.log('分析成功，准备跳转到画布');
            console.log('数据:', result.data);
            currentGraphData = result.data;
            switchScreen('canvas');
            // 等待一下确保画布初始化完成
            setTimeout(() => {
                renderGraph(result.data);
            }, 100);
        } else {
            const errorMsg = result.error || result.detail || '未知错误';
            console.error('分析失败:', result);
            alert('分析失败：' + errorMsg);
        }
    } catch (error) {
        console.error('分析错误:', error);
        alert('分析失败：' + (error.message || '网络错误，请检查服务器是否正常运行'));
    } finally {
        loadingIndicator.classList.add('hidden');
        analyzeTextBtn.disabled = false;
    }
}

// ==================== Cytoscape 初始化 ====================

function initCytoscape() {
    cy = cytoscape({
        container: document.getElementById('cy'),
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'width': 'label',
                    'height': 40,
                    'padding': '12px',
                    'shape': 'round-rectangle',
                    'background-color': '#4c1d95', /* Dark violet */
                    'background-opacity': 0.8,
                    'border-width': 2,
                    'border-color': '#8b5cf6',
                    'color': '#fff',
                    'font-size': '14px',
                    'font-weight': 'bold',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'shadow-blur': 15,
                    'shadow-color': '#8b5cf6',
                    'shadow-opacity': 0.5
                }
            },
            {
                selector: 'node[type="main"]',
                style: {
                    'background-color': '#4c1d95',
                    'border-color': '#8b5cf6',
                    'shadow-color': '#8b5cf6'
                }
            },
            {
                selector: 'node[type="dependency"]',
                style: {
                    'background-color': '#0f766e', /* Cyan/Teal */
                    'border-color': '#2dd4bf',
                    'shadow-color': '#2dd4bf',
                    'font-size': '12px'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#6366f1', /* Indigo */
                    'target-arrow-color': '#6366f1',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'arrow-scale': 1.2,
                    'opacity': 0.6
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-width': 3,
                    'border-color': '#ffffff',
                    'shadow-blur': 25,
                    'shadow-opacity': 1
                }
            }
        ],
        layout: {
            name: 'dagre',
            rankDir: 'TB',
            spacingFactor: 1.2,
            animate: true,
            animationDuration: 500,
            ranker: 'network-simplex'
        }
    });

    // 节点点击事件
    cy.on('tap', 'node', (evt) => {
        const node = evt.target;
        showNodeInfo(node.data());
    });

    // 画布点击事件（取消选择）
    cy.on('tap', (evt) => {
        if (evt.target === cy) {
            hideNodeInfo();
        }
    });

    console.log('✅ Cytoscape 初始化完成');
}

// ==================== 渲染图谱 ====================

function renderGraph(graphData) {
    console.log('开始渲染图谱，数据:', graphData); // 调试日志

    if (!cy) {
        console.log('Cytoscape 未初始化，正在初始化...');
        initCytoscape();
    }

    if (!cy) {
        console.error('Cytoscape 初始化失败！');
        alert('画布初始化失败，请刷新页面重试');
        return;
    }

    // 清空现有内容
    cy.elements().remove();

    // 添加节点
    if (graphData.nodes && graphData.nodes.length > 0) {
        console.log(`添加 ${graphData.nodes.length} 个节点`);
        graphData.nodes.forEach(node => {
            cy.add({
                group: 'nodes',
                data: {
                    id: node.id,
                    label: node.label,
                    type: node.type,
                    description: node.description || '',
                    reason: node.reason || '',
                    source: node.source || ''
                }
            });
        });
    } else {
        console.warn('没有节点数据或节点数组为空');
    }

    // 添加边
    if (graphData.edges && graphData.edges.length > 0) {
        console.log(`添加 ${graphData.edges.length} 条边`);
        graphData.edges.forEach(edge => {
            cy.add({
                group: 'edges',
                data: {
                    id: `e${edge.source}-${edge.target}`,
                    source: edge.source,
                    target: edge.target,
                    reason: edge.reason || '',
                    type: edge.type || 'depends_on'
                }
            });
        });
    } else {
        console.warn('没有边数据或边数组为空');
    }

    console.log('图谱元素添加完成，开始布局...');

    // 重新布局 - 使用兼容的布局算法
    try {
        // 优先尝试使用 dagre 布局
        cy.layout({
            name: 'dagre',
            rankDir: 'TB',
            spacingFactor: 1.2,
            padding: 30,
            animate: true,
            animationDuration: 500
        }).run();
        console.log('布局完成');
    } catch (e) {
        console.warn('布局算法失败，使用 grid 布局:', e);
        // 如果失败，使用最简单的 grid 布局
        const nodeCount = cy.nodes().length;
        cy.layout({
            name: 'grid',
            rows: nodeCount > 0 ? Math.ceil(Math.sqrt(nodeCount)) : 1,
            cols: nodeCount > 0 ? Math.ceil(Math.sqrt(nodeCount)) : 1,
            padding: 30
        }).run();
    }

    // 适应画布
    cy.fit(cy.elements(), 50);
    console.log('图谱渲染完成！');
}

// ==================== 节点信息显示 ====================

function showNodeInfo(nodeData) {
    const panel = document.getElementById('node-info-panel');
    const title = document.getElementById('node-title');
    const contentDiv = document.getElementById('node-details-content');
    const loading = document.getElementById('loading-details');

    // Reset and Show panel immediately with basic info
    title.textContent = nodeData.label;
    loading.classList.add('hidden');

    // Check if we have multiple sources in current graph
    const hasMultipleSources = currentGraphData && currentGraphData.nodes && 
        new Set(currentGraphData.nodes.map(n => n.source).filter(Boolean)).size > 1;

    // Build basic info HTML (instant, no API call)
    let basicHtml = '';
    
    if (nodeData.description) {
        basicHtml += `
            <div class="detail-card">
                <div class="card-label">📝 Description</div>
                <div class="card-content">${nodeData.description}</div>
            </div>`;
    }
    
    if (nodeData.reason) {
        basicHtml += `
            <div class="detail-card">
                <div class="card-label">💡 Reason</div>
                <div class="card-content">${nodeData.reason}</div>
            </div>`;
    }
    
    // Only show source if multiple sources exist
    if (nodeData.source && hasMultipleSources) {
        basicHtml += `
            <div class="detail-card">
                <div class="card-label">📚 Source</div>
                <div class="card-content">${nodeData.source}</div>
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
            <button id="deep-dive-btn" class="deep-dive-btn" onclick="loadDeepDive('${nodeData.label.replace(/'/g, "\\'")}', '${(nodeData.description || '').replace(/'/g, "\\'")}')">
                🔍 Deep Dive (AI 详解)
            </button>
        </div>
        <div id="deep-dive-content"></div>`;

    contentDiv.innerHTML = basicHtml || '<p>暂无详细信息</p>';
    panel.classList.add('visible');
}

async function loadDeepDive(nodeLabel, nodeDescription) {
    const btn = document.getElementById('deep-dive-btn');
    const contentDiv = document.getElementById('deep-dive-content');
    
    // Disable button and show loading
    btn.disabled = true;
    btn.textContent = '⏳ Loading...';
    contentDiv.innerHTML = '<div class="loading-spinner" style="text-align: center; padding: 20px;">AI 正在生成详解...</div>';

    try {
        const response = await fetch(`${API_BASE}/api/node-details`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                node_label: nodeLabel,
                node_description: nodeDescription,
                node_context: nodeDescription
            })
        });

        const details = await response.json();

        if (!response.ok) throw new Error(details.detail || 'Failed to fetch details');

        // Render Deep Dive Cards
        const html = `
            <div class="detail-card">
                <div class="card-label">📖 Definition</div>
                <div class="card-content">${details.definition}</div>
            </div>
            
            <div class="detail-card">
                <div class="card-label">💡 Analogy</div>
                <div class="card-content">${details.analogy}</div>
            </div>
            
            <div class="detail-card">
                <div class="card-label">⚡ Why It Matters</div>
                <div class="card-content">${details.importance}</div>
            </div>
            
            <div class="detail-card">
                <div class="card-label">🚀 Actionable Step</div>
                <div class="card-content">${details.actionable_step}</div>
            </div>
            
            <div class="detail-card">
                <div class="card-label">🏷️ Keywords</div>
                <div class="card-content">
                    ${details.keywords.map(k => `<span class="keyword-tag">${k}</span>`).join('')}
                </div>
            </div>
        `;

        contentDiv.innerHTML = html;
        btn.style.display = 'none'; // Hide button after success

    } catch (error) {
        console.error("Deep Dive error:", error);
        contentDiv.innerHTML = `<div class="detail-card" style="border-color: red;"><div class="card-content">Failed to load Deep Dive. ${error.message}</div></div>`;
        btn.disabled = false;
        btn.textContent = '🔍 Retry Deep Dive';
    }
}

function hideNodeInfo() {
    document.getElementById('node-info-panel').classList.remove('visible');
    if (cy) {
        cy.elements().unselect();
    }
}


// ==================== 添加 URL 模态框 ====================

function showAddUrlModal() {
    const modal = document.getElementById('add-url-modal');
    const input = document.getElementById('new-url-input');
    modal.classList.remove('hidden');
    input.value = '';
    input.focus();
}

function hideAddUrlModal() {
    document.getElementById('add-url-modal').classList.add('hidden');
    document.getElementById('modal-loading').classList.add('hidden');
}

async function handleAddUrl() {
    const input = document.getElementById('new-url-input');
    const url = input.value.trim();

    if (!url) {
        alert('请输入有效的 URL');
        return;
    }

    const modalLoading = document.getElementById('modal-loading');
    const confirmBtn = document.getElementById('confirm-add-btn');

    modalLoading.classList.remove('hidden');
    confirmBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/api/add-url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url
            })
        });

        const result = await response.json();

        if (!response.ok) {
            const errorMsg = result.detail || result.error || `HTTP ${response.status} 错误`;
            console.error('API 错误:', result);
            alert('添加失败：' + errorMsg);
            return;
        }

        if (result.success) {
            // 合并新数据到现有图谱
            mergeGraphData(result.data);
            hideAddUrlModal();
        } else {
            const errorMsg = result.error || result.detail || '未知错误';
            console.error('添加失败:', result);
            alert('添加失败：' + errorMsg);
        }
    } catch (error) {
        console.error('添加 URL 错误:', error);
        alert('添加失败：' + (error.message || '网络错误'));
    } finally {
        modalLoading.classList.add('hidden');
        confirmBtn.disabled = false;
    }
}

// ==================== 合并图谱数据 ====================

function mergeGraphData(newData) {
    if (!currentGraphData) {
        currentGraphData = newData;
        renderGraph(newData);
        return;
    }

    // 合并节点（避免重复）
    const existingNodeIds = new Set(currentGraphData.nodes.map(n => n.id));
    newData.nodes.forEach(node => {
        if (!existingNodeIds.has(node.id)) {
            currentGraphData.nodes.push(node);
        }
    });

    // 合并边
    const existingEdgeIds = new Set(
        currentGraphData.edges.map(e => `${e.source}-${e.target}`)
    );
    newData.edges.forEach(edge => {
        const edgeId = `${edge.source}-${edge.target}`;
        if (!existingEdgeIds.has(edgeId)) {
            currentGraphData.edges.push(edge);
        }
    });

    // 重新渲染
    renderGraph(currentGraphData);
}


// ==================== 测试函数 ====================

async function handleTest() {
    console.log('🧪 测试模式：使用固定数据，不调用 AI');

    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.classList.remove('hidden');
    }

    try {
        const response = await fetch(`${API_BASE}/api/analyze-test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const result = await response.json();

        console.log('测试 API 响应:', result);

        if (!response.ok) {
            const errorMsg = result.detail || result.error || `HTTP ${response.status} 错误`;
            console.error('测试 API 错误:', result);
            alert('测试失败：' + errorMsg);
            return;
        }

        if (result.success) {
            console.log('✅ 测试数据接收成功，准备跳转到画布');
            console.log('数据:', result.data);
            currentGraphData = result.data;
            switchScreen('canvas');
            setTimeout(() => {
                renderGraph(result.data);
            }, 100);
        } else {
            console.error('测试失败:', result);
            alert('测试失败：' + (result.error || '未知错误'));
        }
    } catch (error) {
        console.error('测试错误:', error);
        alert('测试失败：' + (error.message || '网络错误'));
    } finally {
        if (loadingIndicator) {
            loadingIndicator.classList.add('hidden');
        }
    }
}

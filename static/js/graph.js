// static/js/graph.js
import { state, setCy, setGraphData } from './state.js';
import { showNodeInfo, hideNodeInfo } from './ui.js';

export function initCytoscape() {
    const container = document.getElementById('cy');
    if (!container) {
        console.error('Cytoscape initialization failed: container element with id "cy" not found.');
        return;
    }

    if (state.cy) {
        console.log('Cytoscape already initialized');
        return;
    }

    const cyInstance = cytoscape({
        container: container,
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
    cyInstance.on('tap', 'node', (evt) => {
        const node = evt.target;
        showNodeInfo(node.data(), state.currentGraphData);
    });

    // 画布点击事件（取消选择）
    cyInstance.on('tap', (evt) => {
        if (evt.target === cyInstance) {
            hideNodeInfo();
        }
    });

    setCy(cyInstance);
    console.log('✅ Cytoscape 初始化完成');
}

export function renderGraph(graphData) {
    console.log('开始渲染图谱，数据:', graphData);

    if (!state.cy) {
        initCytoscape();
    }

    const cy = state.cy;
    if (!cy) {
        console.error('Cytoscape 初始化失败！');
        alert('画布初始化失败，请刷新页面重试');
        return;
    }

    // Clear existing
    cy.elements().remove();

    // Add nodes
    if (graphData.nodes && graphData.nodes.length > 0) {
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
    }

    // Add edges
    if (graphData.edges && graphData.edges.length > 0) {
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
    }

    // Layout
    try {
        cy.layout({
            name: 'dagre',
            rankDir: 'TB',
            spacingFactor: 1.2,
            padding: 30,
            animate: true,
            animationDuration: 500
        }).run();
    } catch (e) {
        console.warn('布局算法失败，使用 grid 布局:', e);
        const nodeCount = cy.nodes().length;
        cy.layout({
            name: 'grid',
            rows: nodeCount > 0 ? Math.ceil(Math.sqrt(nodeCount)) : 1,
            cols: nodeCount > 0 ? Math.ceil(Math.sqrt(nodeCount)) : 1,
            padding: 30
        }).run();
    }

    cy.fit(cy.elements(), 50);
}

export function mergeGraphData(newData) {
    if (!state.currentGraphData) {
        setGraphData(newData);
        renderGraph(newData);
        return;
    }

    const currentGraphData = state.currentGraphData;

    // Merge nodes
    const existingNodeIds = new Set(currentGraphData.nodes.map(n => n.id));
    newData.nodes.forEach(node => {
        if (!existingNodeIds.has(node.id)) {
            currentGraphData.nodes.push(node);
        }
    });

    // Merge edges
    const existingEdgeIds = new Set(
        currentGraphData.edges.map(e => `${e.source}-${e.target}`)
    );
    newData.edges.forEach(edge => {
        const edgeId = `${edge.source}-${edge.target}`;
        if (!existingEdgeIds.has(edgeId)) {
            currentGraphData.edges.push(edge);
        }
    });

    renderGraph(currentGraphData);
}

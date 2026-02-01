// static/js/graph.js
import { markDirty, setCy, setGraphData, state } from './state.js';
import { hideNodeInfo, showNodeInfo } from './ui.js';

// Layout direction state: 'TB' (top-bottom) or 'LR' (left-right)
let layoutDirection = 'TB';

export function getLayoutDirection() {
  return layoutDirection;
}

export function toggleLayoutDirection() {
  layoutDirection = layoutDirection === 'TB' ? 'LR' : 'TB';
  if (state.cy && state.cy.nodes().length > 0) {
    runLayout();
  }
  return layoutDirection;
}

export function formatGraph() {
  if (state.cy && state.cy.nodes().length > 0) {
    runLayout();
  }
}

function runLayout() {
  const cy = state.cy;
  if (!cy) return;

  try {
    cy.layout({
      name: 'dagre',
      rankDir: layoutDirection,
      spacingFactor: 1.2,
      padding: 30,
      animate: true,
      animationDuration: 500,
    }).run();

    setTimeout(() => cy.fit(cy.elements(), 50), 550);
  } catch (e) {
    console.warn('布局算法失败，使用 grid 布局:', e);
    const nodeCount = cy.nodes().length;
    cy.layout({
      name: 'grid',
      rows: nodeCount > 0 ? Math.ceil(Math.sqrt(nodeCount)) : 1,
      cols: nodeCount > 0 ? Math.ceil(Math.sqrt(nodeCount)) : 1,
      padding: 30,
    }).run();
  }
}

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
          label: 'data(label)',
          width: 'label',
          height: 40,
          padding: '12px',
          shape: 'round-rectangle',
          'background-color': '#4c1d95' /* Dark violet */,
          'background-opacity': 0.8,
          'border-width': 2,
          'border-color': '#8b5cf6',
          color: '#fff',
          'font-size': '14px',
          'font-weight': 'bold',
          'text-valign': 'center',
          'text-halign': 'center',
          'shadow-blur': 15,
          'shadow-color': '#8b5cf6',
          'shadow-opacity': 0.5,
        },
      },
      {
        selector: 'node[type="main"]',
        style: {
          'background-color': '#4c1d95',
          'border-color': '#8b5cf6',
          'shadow-color': '#8b5cf6',
        },
      },
      {
        selector: 'node[type="dependency"]',
        style: {
          'background-color': '#0f766e' /* Cyan/Teal */,
          'border-color': '#2dd4bf',
          'shadow-color': '#2dd4bf',
          'font-size': '12px',
        },
      },
      {
        selector: 'node[type="linked"]',
        style: {
          'background-color': '#854d0e' /* Amber/Brown */,
          'border-color': '#fbbf24',
          'border-style': 'dashed',
          'border-width': 3,
          'shadow-color': '#fbbf24',
          'font-size': '13px',
        },
      },
      {
        selector: 'edge',
        style: {
          width: 2,
          'line-color': '#6366f1' /* Indigo */,
          'target-arrow-color': '#6366f1',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'arrow-scale': 1.2,
          opacity: 0.6,
        },
      },
      {
        selector: 'node:selected',
        style: {
          'border-width': 3,
          'border-color': '#ffffff',
          'shadow-blur': 25,
          'shadow-opacity': 1,
        },
      },
    ],
    layout: {
      name: 'dagre',
      rankDir: 'TB',
      spacingFactor: 1.2,
      animate: true,
      animationDuration: 500,
      ranker: 'network-simplex',
    },
  });

  // 节点点击事件
  cyInstance.on('tap', 'node', (evt) => {
    const node = evt.target;
    showNodeInfo(node.data(), state.currentGraphData);
  });

  // 节点双击事件 - 进入编辑模式
  cyInstance.on('dbltap', 'node', (evt) => {
    const node = evt.target;
    showEditNodeModal(node.data());
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
    graphData.nodes.forEach((node) => {
      cy.add({
        group: 'nodes',
        data: {
          id: node.id,
          label: node.label,
          type: node.type,
          description: node.description || '',
          reason: node.reason || '',
          source: node.source || '',
        },
      });
    });
  }

  // Add edges
  if (graphData.edges && graphData.edges.length > 0) {
    graphData.edges.forEach((edge) => {
      cy.add({
        group: 'edges',
        data: {
          id: `e${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target,
          reason: edge.reason || '',
          type: edge.type || 'depends_on',
        },
      });
    });
  }

  // Layout
  try {
    cy.layout({
      name: 'dagre',
      rankDir: layoutDirection,
      spacingFactor: 1.2,
      padding: 30,
      animate: true,
      animationDuration: 500,
    }).run();
  } catch (e) {
    console.warn('布局算法失败，使用 grid 布局:', e);
    const nodeCount = cy.nodes().length;
    cy.layout({
      name: 'grid',
      rows: nodeCount > 0 ? Math.ceil(Math.sqrt(nodeCount)) : 1,
      cols: nodeCount > 0 ? Math.ceil(Math.sqrt(nodeCount)) : 1,
      padding: 30,
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
  const existingNodeIds = new Set(currentGraphData.nodes.map((n) => n.id));
  newData.nodes.forEach((node) => {
    if (!existingNodeIds.has(node.id)) {
      currentGraphData.nodes.push(node);
    }
  });

  // Merge edges
  const existingEdgeIds = new Set(currentGraphData.edges.map((e) => `${e.source}-${e.target}`));
  newData.edges.forEach((edge) => {
    const edgeId = `${edge.source}-${edge.target}`;
    if (!existingEdgeIds.has(edgeId)) {
      currentGraphData.edges.push(edge);
    }
  });

  renderGraph(currentGraphData);
}

export function addLinkedConcept(conceptData) {
  // conceptData: { node: {...}, edges: [...] }
  if (!state.cy || !state.currentGraphData) {
    console.error('Cannot add linked concept: graph not initialized');
    return;
  }

  const cy = state.cy;
  const graphData = state.currentGraphData;

  // Add node with special "linked" type for styling
  const newNode = {
    ...conceptData.node,
    type: 'linked',
  };

  // Check if node already exists
  if (!graphData.nodes.find((n) => n.id === newNode.id)) {
    graphData.nodes.push(newNode);
    cy.add({
      group: 'nodes',
      data: {
        id: newNode.id,
        label: newNode.label,
        type: 'linked',
        description: newNode.description || '',
        reason: newNode.reason || '',
        source: 'linked',
      },
    });
  }

  // Add edges
  const existingEdgeIds = new Set(graphData.edges.map((e) => `${e.source}-${e.target}`));

  conceptData.edges.forEach((edge) => {
    const edgeId = `${edge.source}-${edge.target}`;
    if (!existingEdgeIds.has(edgeId)) {
      graphData.edges.push(edge);
      cy.add({
        group: 'edges',
        data: {
          id: `e${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target,
          reason: edge.reason || '',
          type: edge.type || 'relates_to',
        },
      });
    }
  });

  // Re-run layout
  runLayout();
}

export function addExpandedNodes(expandedData, parentNodeId) {
  // expandedData: { child_nodes: [...], new_edges: [...] }
  if (!state.cy || !state.currentGraphData) {
    console.error('Cannot add expanded nodes: graph not initialized');
    return;
  }

  const cy = state.cy;
  const graphData = state.currentGraphData;

  // Mark parent as expanded
  const parentNode = cy.getElementById(parentNodeId);
  if (parentNode) {
    parentNode.data('expanded', true);
  }

  // Add child nodes
  const existingNodeIds = new Set(graphData.nodes.map((n) => n.id));
  expandedData.child_nodes.forEach((node) => {
    if (!existingNodeIds.has(node.id)) {
      graphData.nodes.push(node);
      cy.add({
        group: 'nodes',
        data: {
          id: node.id,
          label: node.label,
          type: node.type || 'dependency',
          description: node.description || '',
          reason: node.reason || '',
          source: node.source || '',
          level: node.level || 1,
          expandable: node.expandable || false,
          parentId: node.parent_id || parentNodeId,
        },
      });
    }
  });

  // Add edges
  const existingEdgeIds = new Set(graphData.edges.map((e) => `${e.source}-${e.target}`));
  expandedData.new_edges.forEach((edge) => {
    const edgeId = `${edge.source}-${edge.target}`;
    if (!existingEdgeIds.has(edgeId)) {
      graphData.edges.push(edge);
      cy.add({
        group: 'edges',
        data: {
          id: `e${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target,
          reason: edge.reason || '',
          type: edge.type || 'implements',
        },
      });
    }
  });

  // Re-run layout
  runLayout();
}

// Edit node modal functions
function showEditNodeModal(nodeData) {
  const modal = document.getElementById('edit-node-modal');
  if (!modal) return;

  document.getElementById('edit-node-id').value = nodeData.id;
  document.getElementById('edit-node-label').value = nodeData.label || '';
  document.getElementById('edit-node-description').value = nodeData.description || '';
  document.getElementById('edit-node-reason').value = nodeData.reason || '';
  document.getElementById('edit-node-type').value = nodeData.type || 'main';
  document.getElementById('edit-node-priority').value = nodeData.priority || 'critical';

  modal.classList.remove('hidden');
}

export function hideEditNodeModal() {
  const modal = document.getElementById('edit-node-modal');
  if (modal) modal.classList.add('hidden');
}

export function updateNodeInGraph(nodeId, updates) {
  if (!state.cy || !state.currentGraphData) return false;

  const cy = state.cy;
  const graphData = state.currentGraphData;

  // Update in Cytoscape
  const cyNode = cy.getElementById(nodeId);
  if (cyNode) {
    cyNode.data(updates);
  }

  // Update in graph data
  const nodeIndex = graphData.nodes.findIndex((n) => n.id === nodeId);
  if (nodeIndex !== -1) {
    Object.assign(graphData.nodes[nodeIndex], updates);
  }

  markDirty();
  return true;
}

export function deleteNodeFromGraph(nodeId) {
  if (!state.cy || !state.currentGraphData) return false;

  const cy = state.cy;
  const graphData = state.currentGraphData;

  // Remove from Cytoscape (this also removes connected edges)
  const cyNode = cy.getElementById(nodeId);
  if (cyNode) {
    cyNode.remove();
  }

  // Remove from graph data
  graphData.nodes = graphData.nodes.filter((n) => n.id !== nodeId);
  graphData.edges = graphData.edges.filter((e) => e.source !== nodeId && e.target !== nodeId);

  markDirty();
  return true;
}

export function addNodeToGraph(nodeData) {
  if (!state.cy || !state.currentGraphData) return false;

  const cy = state.cy;
  const graphData = state.currentGraphData;

  // Generate unique ID
  const existingIds = new Set(graphData.nodes.map((n) => n.id));
  let newId = `n${graphData.nodes.length + 1}`;
  while (existingIds.has(newId)) {
    newId = `n${Date.now()}`;
  }

  const newNode = {
    id: newId,
    label: nodeData.label,
    description: nodeData.description || '',
    reason: nodeData.reason || 'User added',
    type: nodeData.type || 'main',
    priority: nodeData.priority || 'critical',
  };

  // Add to graph data
  graphData.nodes.push(newNode);

  // Add to Cytoscape
  cy.add({
    group: 'nodes',
    data: {
      id: newNode.id,
      label: newNode.label,
      type: newNode.type,
      description: newNode.description,
      reason: newNode.reason,
    },
  });

  markDirty();
  runLayout();
  return newNode;
}

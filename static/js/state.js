export const state = {
  cy: null,
  currentGraphData: null,
  currentAnalysisId: null,  // Track current analysis ID for export
  isDirty: false,  // Track if graph has unsaved changes
};

export function setCy(instance) {
  state.cy = instance;
}

export function setGraphData(data, analysisId = null) {
  state.currentGraphData = data;
  state.currentAnalysisId = analysisId;
  state.isDirty = false;
}

export function markDirty() {
  state.isDirty = true;
}

export function markClean() {
  state.isDirty = false;
}

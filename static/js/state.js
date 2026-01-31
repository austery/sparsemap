export const state = {
  cy: null,
  currentGraphData: null,
  currentAnalysisId: null,  // Track current analysis ID for export
};

export function setCy(instance) {
  state.cy = instance;
}

export function setGraphData(data, analysisId = null) {
  state.currentGraphData = data;
  state.currentAnalysisId = analysisId;
}

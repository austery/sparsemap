export const state = {
  cy: null,
  currentGraphData: null,
};

export function setCy(instance) {
  state.cy = instance;
}

export function setGraphData(data) {
  state.currentGraphData = data;
}

import { describe, it, expect, beforeEach } from 'bun:test';
import { state, setCy, setGraphData } from '../../static/js/state.js';

describe('State Management', () => {
    beforeEach(() => {
        // Reset state manually since it's a singleton
        state.cy = null;
        state.currentGraphData = null;
        state.currentAnalysisId = null;
    });

    it('should initialize with null values', () => {
        expect(state.cy).toBeNull();
        expect(state.currentGraphData).toBeNull();
        expect(state.currentAnalysisId).toBeNull();
    });

    it('should set cy instance', () => {
        const mockCy = { id: 'mockCy' };
        setCy(mockCy);
        expect(state.cy).toEqual(mockCy);
    });

    it('should set graph data', () => {
        const mockData = { nodes: [], edges: [] };
        setGraphData(mockData);
        expect(state.currentGraphData).toEqual(mockData);
    });

    it('should set graph data with analysis id', () => {
        const mockData = { nodes: [], edges: [] };
        setGraphData(mockData, 123);
        expect(state.currentGraphData).toEqual(mockData);
        expect(state.currentAnalysisId).toBe(123);
    });
});

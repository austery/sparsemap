import { describe, it, expect, beforeEach } from 'bun:test';
import { state, setCy, setGraphData, markDirty, markClean } from '../../static/js/state.js';

describe('State Management', () => {
    beforeEach(() => {
        // Reset state manually since it's a singleton
        state.cy = null;
        state.currentGraphData = null;
        state.currentAnalysisId = null;
        state.isDirty = false;
    });

    it('should initialize with null values', () => {
        expect(state.cy).toBeNull();
        expect(state.currentGraphData).toBeNull();
        expect(state.currentAnalysisId).toBeNull();
        expect(state.isDirty).toBe(false);
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
        expect(state.isDirty).toBe(false);
    });

    it('should track dirty state', () => {
        expect(state.isDirty).toBe(false);
        markDirty();
        expect(state.isDirty).toBe(true);
        markClean();
        expect(state.isDirty).toBe(false);
    });
});

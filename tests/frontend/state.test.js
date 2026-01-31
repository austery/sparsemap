import { describe, it, expect, beforeEach } from 'bun:test';
import { state, setCy, setGraphData } from '../../static/js/state.js';

describe('State Management', () => {
    beforeEach(() => {
        // Reset state manually since it's a singleton
        state.cy = null;
        state.currentGraphData = null;
    });

    it('should initialize with null values', () => {
        expect(state.cy).toBeNull();
        expect(state.currentGraphData).toBeNull();
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
});

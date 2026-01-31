import { describe, it, expect } from 'bun:test';
import { exportGraphLocally } from '../../static/js/exporter.js';

const sampleGraph = {
    nodes: [
        { id: 'n1', label: 'React', type: 'main', priority: 'critical', reason: 'Core', description: 'A library' },
        { id: 'n2', label: 'Virtual DOM', type: 'dependency', priority: 'critical', reason: 'Core concept' },
        { id: 'n3', label: 'JSX', type: 'dependency', priority: 'optional', reason: 'Syntax' },
    ],
    edges: [
        { source: 'n1', target: 'n2', type: 'implements', reason: 'Uses VDOM' },
        { source: 'n1', target: 'n3', type: 'supports', reason: 'Supports JSX' },
    ],
    summary: 'React overview',
};

describe('Graph Exporter', () => {
    describe('Mermaid Export', () => {
        it('should export valid mermaid syntax', () => {
            const result = exportGraphLocally(sampleGraph, 'mermaid');
            expect(result).toContain('graph TD');
            expect(result).toContain('n1["React"]');
            expect(result).toContain('n1 -->|implements| n2');
        });
    });

    describe('D2 Export', () => {
        it('should export valid D2 syntax', () => {
            const result = exportGraphLocally(sampleGraph, 'd2');
            expect(result).toContain('n1: "React"');
            expect(result).toContain('n1 -> n2: implements');
        });
    });

    describe('JSON Export', () => {
        it('should export valid JSON', () => {
            const result = exportGraphLocally(sampleGraph, 'json');
            const parsed = JSON.parse(result);
            expect(parsed.nodes.length).toBe(3);
            expect(parsed.edges.length).toBe(2);
        });
    });

    describe('Markdown Export', () => {
        it('should export markdown with headers and tables', () => {
            const result = exportGraphLocally(sampleGraph, 'markdown');
            expect(result).toContain('# Knowledge Graph Export');
            expect(result).toContain('## Summary');
            expect(result).toContain('React overview');
            expect(result).toContain('## Nodes');
            expect(result).toContain('🔴 React');
            expect(result).toContain('🟡 JSX');
            expect(result).toContain('## Relationships');
            expect(result).toContain('| React | Virtual DOM | implements |');
        });
    });

    describe('Error handling', () => {
        it('should throw for unsupported format', () => {
            expect(() => exportGraphLocally(sampleGraph, 'invalid')).toThrow();
        });
    });
});

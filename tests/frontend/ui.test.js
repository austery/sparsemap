import { describe, it, expect } from 'bun:test';
import { escapeHtml, formatDate } from '../../static/js/ui.js';

describe('UI Utilities', () => {
    describe('escapeHtml', () => {
        it('should escape special characters', () => {
            const input = '<script>alert("xss")</script>';
            const expected = '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;';
            expect(escapeHtml(input)).toBe(expected);
        });

        it('should handle ampersands', () => {
            const input = 'Tom & Jerry';
            const expected = 'Tom &amp; Jerry';
            expect(escapeHtml(input)).toBe(expected);
        });

        it('should return empty string for null/undefined', () => {
            expect(escapeHtml(null)).toBe('');
            expect(escapeHtml(undefined)).toBe('');
        });
    });

    describe('formatDate', () => {
        it('should format recent time as "刚刚"', () => {
            const now = new Date();
            const iso = now.toISOString();
            expect(formatDate(iso)).toBe('刚刚');
        });

        it('should format minutes ago', () => {
            const date = new Date(Date.now() - 5 * 60 * 1000); // 5 mins ago
            const iso = date.toISOString();
            expect(formatDate(iso)).toBe('5 分钟前');
        });

        it('should format hours ago', () => {
            const date = new Date(Date.now() - 2 * 3600 * 1000); // 2 hours ago
            const iso = date.toISOString();
            expect(formatDate(iso)).toBe('2 小时前');
        });

        it('should format days ago', () => {
            const date = new Date(Date.now() - 3 * 24 * 3600 * 1000); // 3 days ago
            const iso = date.toISOString();
            expect(formatDate(iso)).toBe('3 天前');
        });
    });
});

import { describe, expect, it } from 'vite-plus/test';
import { layoutLabels, type LabelInput } from './labels';

const boxOf = (l: LabelInput, p: { dx: number; dy: number }) => ({
	x0: l.x + p.dx,
	y0: l.y + p.dy,
	x1: l.x + p.dx + l.w,
	y1: l.y + p.dy + l.h
});

describe('layoutLabels', () => {
	it('puts a lone label to the right of its dot', () => {
		const [p] = layoutLabels([{ x: 100, y: 100, w: 80, h: 12 }]);
		expect(p!.dx).toBeGreaterThan(0);
		expect(p!.dy).toBe(-6);
	});

	it('moves a label that would overlap another', () => {
		// Kamasu Complex and Bagmulgwan: dots a few pixels apart.
		const labels = [
			{ x: 100, y: 100, w: 100, h: 12 },
			{ x: 106, y: 104, w: 70, h: 12 }
		];
		const [a, b] = layoutLabels(labels);
		expect(a).not.toBeNull();
		expect(b).not.toBeNull();
		const A = boxOf(labels[0], a!);
		const B = boxOf(labels[1], b!);
		expect(A.x0 < B.x1 && B.x0 < A.x1 && A.y0 < B.y1 && B.y0 < A.y1).toBe(false);
	});

	it('never covers another pin’s dot', () => {
		const labels = [
			{ x: 100, y: 100, w: 100, h: 12 },
			{ x: 140, y: 100, w: 60, h: 12 }
		];
		const [a] = layoutLabels(labels);
		const A = boxOf(labels[0], a!);
		expect(A.x0 < 144 && 136 < A.x1 && A.y0 < 104 && 96 < A.y1).toBe(false);
	});

	it('hides a label with nowhere to go', () => {
		const crowd = Array.from({ length: 9 }, (_, i) => ({
			x: 100 + (i % 3) * 3,
			y: 100 + Math.floor(i / 3) * 3,
			w: 90,
			h: 12
		}));
		const placed = layoutLabels(crowd);
		expect(placed[0]).not.toBeNull();
		expect(placed.some((p) => p === null)).toBe(true);
	});
});

import { describe, expect, it } from 'vitest';
import { latLonToVector, shapePoint } from './geo';

const close = (a: number[], b: number[]) => a.forEach((v, i) => expect(v).toBeCloseTo(b[i], 6));

describe('latLonToVector', () => {
	it('puts the equator at y = 0 and the poles on the y axis', () => {
		close(latLonToVector(90, 37), [0, 1, 0]);
		close(latLonToVector(-90, -120), [0, -1, 0]);
		expect(latLonToVector(0, 45)[1]).toBeCloseTo(0, 6);
	});

	it('matches three.js SphereGeometry UVs: 0° at +x, 90° W at +z, 180° at -x', () => {
		close(latLonToVector(0, 0), [1, 0, 0]);
		close(latLonToVector(0, -90), [0, 0, 1]);
		close(latLonToVector(0, 90), [0, 0, -1]);
		close(latLonToVector(0, 180, 2), [-2, 0, 0]);
	});
});

describe('shapePoint', () => {
	it('leaves the sphere alone with no stretch or indent', () => {
		const p = latLonToVector(20, 40);
		const q = shapePoint(p, { stretch: 1, indent: 0, indentLon: 180 });
		q.forEach((c, i) => expect(c).toBeCloseTo(p[i]));
	});
	it('stretches the poles and presses in the hollow side only', () => {
		const shape = { stretch: 1.45, indent: 0.15, indentLon: 180 };
		const pole = shapePoint(latLonToVector(90, 0), shape);
		const hollow = shapePoint(latLonToVector(0, 180), shape);
		const back = shapePoint(latLonToVector(0, 0), shape);
		const len = (v: number[]) => Math.hypot(...v);
		expect(len(pole)).toBeGreaterThan(len(back));
		expect(len(hollow)).toBeLessThan(len(back) - 0.1);
	});
});

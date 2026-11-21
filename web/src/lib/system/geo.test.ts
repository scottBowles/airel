import { describe, expect, it } from 'vitest';
import { latLonToVector } from './geo';

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

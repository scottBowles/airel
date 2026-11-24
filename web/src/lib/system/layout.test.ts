import { describe, expect, it } from 'vitest';
import { D, figureEight, period } from './layout';

describe('figureEight', () => {
	it('crosses between the suns and turns round each one', () => {
		expect(Math.hypot(...figureEight(Math.PI / 2))).toBeCloseTo(0, 6);
		const [x0] = figureEight(0);
		const [x1] = figureEight(Math.PI);
		// The lobes reach past each sun (at ±D/2).
		expect(x0).toBeGreaterThan(D / 2);
		expect(x1).toBeLessThan(-D / 2);
	});
});

describe('period', () => {
	it('follows Kepler: four times the distance, eight times the year', () => {
		expect(period(0.4) / period(0.1)).toBeCloseTo(8, 6);
	});
});

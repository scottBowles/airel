import { describe, expect, it } from 'vitest';
import { decodeJwt, formatGameDate, sortEdgesByUpdatedDesc } from './utils';

function encodeBase64Url(value: string): string {
	return Buffer.from(value)
		.toString('base64')
		.replace(/\+/g, '-')
		.replace(/\//g, '_')
		.replace(/=+$/u, '');
}

describe('decodeJwt', () => {
	it('decodes nested payload claims and normalizes exp', () => {
		const payload = {
			payload: JSON.stringify({
				sub: 'user-123',
				exp: '2026-03-21T12:34:56.000Z'
			})
		};
		const token = `header.${encodeBase64Url(JSON.stringify(payload))}.signature`;

		expect(decodeJwt(token)).toEqual({
			sub: 'user-123',
			exp: Math.floor(Date.parse('2026-03-21T12:34:56.000Z') / 1000)
		});
	});

	it('returns null for malformed tokens', () => {
		expect(decodeJwt('not-a-token')).toBeNull();
	});
});

describe('formatGameDate', () => {
	it('formats ISO-compatible dates as yyyy-mm-dd', () => {
		expect(formatGameDate('2026-03-21T12:34:56.000Z')).toBe('2026-03-21');
	});

	it('returns the fallback label for missing dates', () => {
		expect(formatGameDate(null)).toBe('UNKNOWN DATE');
	});
});

describe('sortEdgesByUpdatedDesc', () => {
	it('sorts edges descending and pushes invalid dates last', () => {
		const edges = [
			{ node: { updated: '2026-03-20T00:00:00.000Z' } },
			{ node: { updated: 'invalid-date' } },
			{ node: { updated: '2026-03-21T00:00:00.000Z' } }
		];

		expect(sortEdgesByUpdatedDesc(edges)).toEqual([
			{ node: { updated: '2026-03-21T00:00:00.000Z' } },
			{ node: { updated: '2026-03-20T00:00:00.000Z' } },
			{ node: { updated: 'invalid-date' } }
		]);
	});
});

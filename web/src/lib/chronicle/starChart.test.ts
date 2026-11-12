import { describe, expect, it } from 'vite-plus/test';
import { buildPlaceTree, toChronicle } from './model';
import { buildRoutes, labelPosition, layoutChart, starsOf, type ChartPoint } from './starChart';

/** Sessions from raw logs, as the Chronicle page builds them. */
const sessionsOf = (edges: Parameters<typeof toChronicle>[0]) => toChronicle(edges).sessions;

type Place = { id: string; name: string; placeType: string | null; parent?: Place | null };

const yellow: Place = { id: 'yellow', name: 'The Yellow Sun', placeType: 'STAR' };
const red: Place = { id: 'red', name: 'The Red Sun', placeType: 'STAR' };
const planet = (id: string, sun: Place): Place => ({
	id,
	name: id.toUpperCase(),
	placeType: 'PLANET',
	parent: sun
});
const place = (id: string, parent: Place): Place => ({
	id,
	name: `A place called ${id}`,
	placeType: 'LOCATION',
	parent
});

const magmus = planet('magmus', yellow);
const hyang = planet('hyangwan', yellow);
const janus = planet('janus', red);
const space: Place = { id: 'space', name: 'Space', placeType: 'REGION' };
const stops = [
	magmus,
	place('ember', magmus),
	place('forge', place('ymir', magmus)),
	hyang,
	place('kamasu', hyang),
	janus,
	place('mezzolux', janus),
	space
];

const sessions = sessionsOf(
	stops.map((stop, i) => ({
		node: {
			id: `log-${i}`,
			title: `Log ${i}`,
			gameDate: `2020-01-${String(i + 1).padStart(2, '0')}`,
			url: `https://example.invalid/${i}`,
			placesSetIn: { edges: [{ node: stop }] }
		}
	}))
);

describe('layoutChart', () => {
	const tree = buildPlaceTree(sessions);
	const chart = layoutChart(tree.roots, starsOf(sessions));

	it('places every place', () => {
		expect([...chart.points.keys()].sort()).toEqual([...tree.byId.keys()].sort());
	});

	it('groups worlds by the sun they orbit, sunless worlds last', () => {
		expect(chart.groups.map((g) => [g.star, g.worlds.map((w) => w.id)])).toEqual([
			['The Yellow Sun', ['magmus', 'hyangwan']],
			['The Red Sun', ['janus']],
			[null, ['space']]
		]);
	});

	it('keeps every place on the canvas', () => {
		for (const point of chart.points.values()) {
			expect(point.x).toBeGreaterThanOrEqual(0);
			expect(point.y).toBeGreaterThanOrEqual(0);
			expect(point.x).toBeLessThanOrEqual(chart.width);
			expect(point.y).toBeLessThanOrEqual(chart.height);
		}
	});

	it('keeps groups apart', () => {
		const extent = (group: (typeof chart.groups)[number]) => {
			const pts = [...chart.points.values()].filter((p) =>
				group.worlds.some((w) => w.id === p.worldId)
			);
			const xs = pts.map((p) => p.x);
			const ys = pts.map((p) => p.y);
			return {
				left: Math.min(...xs),
				right: Math.max(...xs),
				top: Math.min(...ys),
				bottom: Math.max(...ys)
			};
		};
		const boxes = chart.groups.map(extent);
		for (let i = 0; i < boxes.length; i++) {
			for (let j = i + 1; j < boxes.length; j++) {
				const a = boxes[i];
				const b = boxes[j];
				const overlap =
					a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
				expect(overlap).toBe(false);
			}
		}
	});

	it('puts a world on its sun’s ring', () => {
		const group = chart.groups[0];
		const world = chart.points.get('magmus') as ChartPoint;
		expect(Math.hypot(world.x - group.x, world.y - group.y)).toBeCloseTo(group.ring, 5);
	});
});

describe('labelPosition', () => {
	it('keeps a label inside the chart, shortening or moving it near an edge', () => {
		const node = buildPlaceTree(sessions).byId.get('ember')!;
		// A place near the left edge whose label would naturally go left.
		const point = { node, x: 30, y: 100, cx: 80, cy: 100 };
		const label = labelPosition(point, 400);
		const width = (Math.min(node.name.length, label.maxChars) + 4) * 7.2;
		const left = label.anchor === 'end' ? label.x - width : label.x;
		expect(left).toBeGreaterThanOrEqual(0);
	});
});

describe('buildRoutes', () => {
	it('merges flights between the same two places in either direction and skips stays', () => {
		const routes = buildRoutes(['a', 'b', 'b', 'a', 'c', 'a']);
		expect(routes.map((r) => [r.key, r.legs])).toEqual([
			['a|b', [1, 3]],
			['a|c', [4, 5]]
		]);
	});
});

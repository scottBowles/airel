import { describe, expect, it } from 'vite-plus/test';
import {
	buildArcs,
	buildPlaceTree,
	buildThreads,
	MINOR,
	primaryStop,
	roman,
	sessionWorld,
	stripSessionPrefix,
	toChronicle,
	wherePath,
	worldColours
} from './model';

/** Sessions from raw logs, as the Chronicle page builds them. */
const sessionsOf = (edges: Parameters<typeof toChronicle>[0]) => toChronicle(edges).sessions;

type Place = { id: string; name: string; placeType: string | null; parent?: Place | null };

const sun: Place = { id: 'sun', name: 'The Yellow Sun', placeType: 'STAR' };
const magmus: Place = { id: 'magmus', name: 'Magmus', placeType: 'PLANET', parent: sun };
const emberPit: Place = { id: 'ember', name: 'Ember Pit', placeType: 'LOCATION', parent: magmus };
const janus: Place = {
	id: 'janus',
	name: 'Janus',
	placeType: 'PLANET',
	parent: { id: 'red', name: 'The Red Sun', placeType: 'STAR' }
};
const space: Place = { id: 'space', name: 'Space', placeType: 'REGION' };

let seq = 0;
function log(date: string | null, places: Place[] = [], extra: Record<string, unknown> = {}) {
	seq += 1;
	return {
		node: {
			id: `log-${seq}`,
			title: `Log ${seq}`,
			brief: '',
			synopsis: '',
			gameDate: date,
			url: `https://example.invalid/${seq}`,
			placesSetIn: { edges: places.map((node) => ({ node })) },
			characters: { edges: [] },
			associations: { edges: [] },
			items: { edges: [] },
			artifacts: { edges: [] },
			...extra
		}
	};
}

describe('toChronicle', () => {
	it('splits off logs before the first one set anywhere as an unnumbered prologue', () => {
		const { sessions, prologue } = toChronicle([
			log('2018-08-13', [magmus]),
			log('2013-01-01'),
			log('2018-08-06', [emberPit])
		]);
		expect(prologue.map((p) => p.n)).toEqual([0]);
		expect(prologue[0].date?.getUTCFullYear()).toBe(2013);
		expect(sessions.map((s) => s.n)).toEqual([1, 2]);
		expect(sessions.map((s) => s.date?.toISOString().slice(0, 10))).toEqual([
			'2018-08-06',
			'2018-08-13'
		]);
	});

	it('keeps every log as a session when no log records a place', () => {
		const { sessions, prologue } = toChronicle([log('2020-01-01'), log('2020-01-08')]);
		expect(prologue).toEqual([]);
		expect(sessions.map((s) => s.n)).toEqual([1, 2]);
	});

	it('puts undated logs last', () => {
		const sessions = sessionsOf([log(null, [magmus]), log('2020-01-01', [magmus])]);
		expect(sessions.map((s) => s.date)).toEqual([new Date('2020-01-01'), null]);
	});
});

describe('places', () => {
	it('starts a path at the world and keeps the sun as a label', () => {
		const [session] = sessionsOf([log('2020-01-01', [emberPit])]);
		const stop = session.stops[0];
		expect(stop.path.map((p) => p.name)).toEqual(['Magmus', 'Ember Pit']);
		expect(stop.star).toBe('The Yellow Sun');
		expect(wherePath(stop)).toBe('Ember Pit · Magmus · The Yellow Sun');
	});

	it('treats a place with nothing above it as its own world', () => {
		const [session] = sessionsOf([log('2020-01-01', [space])]);
		expect(session.stops[0].path.map((p) => p.name)).toEqual(['Space']);
		expect(session.stops[0].star).toBeNull();
	});

	it('takes the most specific stop as where a session is mainly set', () => {
		const [session] = sessionsOf([log('2020-01-01', [magmus, emberPit])]);
		expect(primaryStop(session)?.name).toBe('Ember Pit');
		expect(sessionWorld(session)?.name).toBe('Magmus');
	});

	it('builds a tree of worlds and the places within them', () => {
		const sessions = sessionsOf([log('2020-01-01', [emberPit]), log('2020-01-08', [janus])]);
		const tree = buildPlaceTree(sessions);
		expect(tree.roots.map((r) => r.name)).toEqual(['Magmus', 'Janus']);
		expect(tree.byId.get('magmus')?.allSessions).toHaveLength(1);
		expect(tree.byId.get('ember')?.sessions).toHaveLength(1);
	});
});

describe('buildArcs', () => {
	it('groups consecutive sessions on the same world, whatever place on it', () => {
		const sessions = sessionsOf([
			log('2020-01-01', [magmus]),
			log('2020-01-08', [emberPit]),
			log('2020-01-15', [space]),
			log('2020-01-22', [janus]),
			log('2020-01-29', [magmus])
		]);
		const arcs = buildArcs(sessions);
		expect(arcs.map((a) => [a.world?.name, a.sessions.length, a.start])).toEqual([
			['Magmus', 2, 0],
			['Space', 1, 2],
			['Janus', 1, 3],
			['Magmus', 1, 4]
		]);
		expect(arcs.map((a) => a.n)).toEqual([1, 2, 3, 4]);
	});

	it('keeps a session with no recorded place in the arc it falls in', () => {
		const sessions = sessionsOf([
			log('2020-01-01', [magmus]),
			log('2020-01-08'),
			log('2020-01-15', [magmus])
		]);
		const arcs = buildArcs(sessions);
		expect(arcs).toHaveLength(1);
		expect(arcs[0].sessions).toHaveLength(3);
	});
});

describe('worldColours', () => {
	it('gives the most-visited worlds distinct colours and the rest a shared muted tone', () => {
		const worlds = Array.from({ length: 10 }, (_, i) => ({
			id: `w${i}`,
			name: `World ${i}`,
			placeType: 'PLANET'
		}));
		// World i is visited 10 - i times, so worlds 8 and 9 are the two least visited.
		const logs = worlds.flatMap((world, i) =>
			Array.from({ length: 10 - i }, (_, k) =>
				log(`2020-${String(i + 1).padStart(2, '0')}-${String(k + 1).padStart(2, '0')}`, [world])
			)
		);
		const colours = worldColours(sessionsOf(logs));
		const major = worlds.slice(0, 8).map((w) => colours.get(w.id));
		expect(new Set(major).size).toBe(8);
		expect(major).not.toContain(MINOR);
		expect(colours.get('w8')).toBe(MINOR);
		expect(colours.get('w9')).toBe(MINOR);
		// The first world visited gets the house amber.
		expect(colours.get('w0')).toBe('#ffb000');
	});
});

describe('buildThreads', () => {
	it('records which sessions an entity appears in, and its first and last', () => {
		const ego = { id: 'ego', name: 'Ego' };
		const sessions = sessionsOf([
			log('2020-01-01', [magmus], { characters: { edges: [{ node: ego }] } }),
			log('2020-01-08', [magmus]),
			log('2020-01-15', [magmus], { characters: { edges: [{ node: ego }] } })
		]);
		const [thread] = buildThreads(sessions, (s) => s.characters);
		expect(thread.ref.name).toBe('Ego');
		expect([...thread.hits]).toEqual([0, 2]);
		expect([thread.first, thread.last, thread.count]).toEqual([0, 2, 2]);
	});
});

describe('helpers', () => {
	it('drops a "Session N:" prefix from titles', () => {
		expect(stripSessionPrefix('Session 12: Archive of Echoes')).toBe('Archive of Echoes');
		expect(stripSessionPrefix('Ashes of Defiance')).toBe('Ashes of Defiance');
	});

	it('writes part numbers in roman numerals', () => {
		expect([1, 4, 9, 14, 15, 40].map(roman)).toEqual(['I', 'IV', 'IX', 'XIV', 'XV', 'XL']);
	});
});

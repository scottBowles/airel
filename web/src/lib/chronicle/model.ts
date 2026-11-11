// Shared shape for the Chronicle journey views, built once from the ChronicleJourney query.

export type Ref = { id: string; name: string };

export type PlaceStop = Ref & {
	type: string | null;
	/** From the world (the planet, or a place with nothing above it) down to this place. */
	path: Array<Ref & { type: string | null }>;
	/** The star the world orbits, when it has one. */
	star: string | null;
};

export type Session = {
	id: string;
	/** 1-based position in play order. */
	n: number;
	title: string;
	brief: string;
	synopsis: string;
	date: Date | null;
	url: string;
	/** Places the session is set in, most specific last-visited first as stored. */
	stops: PlaceStop[];
	characters: Ref[];
	associations: Ref[];
	items: Ref[];
	artifacts: Ref[];
};

type Connection<T> = { edges: ReadonlyArray<{ node: T }> } | null | undefined;

type RawPlace = {
	id: string;
	name: string;
	placeType?: string | null;
	parent?: RawPlace | null;
};

type RawLog = {
	id: string;
	title?: string | null;
	brief?: string | null;
	synopsis?: string | null;
	gameDate?: Date | string | null;
	url: string;
	placesSetIn?: Connection<RawPlace>;
	characters?: Connection<Ref>;
	associations?: Connection<Ref>;
	items?: Connection<Ref>;
	artifacts?: Connection<Ref>;
};

const nodes = <T>(connection: Connection<T>): T[] => connection?.edges.map((e) => e.node) ?? [];
const refs = (connection: Connection<Ref>): Ref[] =>
	nodes(connection).map(({ id, name }) => ({ id, name }));

function toStop(place: RawPlace): PlaceStop {
	const path: PlaceStop['path'] = [];
	for (let p: RawPlace | null | undefined = place; p; p = p.parent) {
		path.unshift({ id: p.id, name: p.name, type: p.placeType ?? null });
	}
	// The campaign moves world to world, so a path starts at the world (the planet, or a
	// place with nothing above it). The star above a world is kept only as a label.
	let star: string | null = null;
	if (path.length > 1 && path[0].type === 'STAR') {
		star = path[0].name;
		path.shift();
	}
	return { id: place.id, name: place.name, type: place.placeType ?? null, path, star };
}

function toSession(log: RawLog, n: number): Session {
	return {
		id: log.id,
		n,
		title: stripSessionPrefix(log.title) || 'Untitled log',
		brief: log.brief ?? '',
		synopsis: log.synopsis ?? '',
		date: log.gameDate ? new Date(log.gameDate) : null,
		url: log.url,
		stops: nodes(log.placesSetIn).map(toStop),
		characters: refs(log.characters),
		associations: refs(log.associations),
		items: refs(log.items),
		artifacts: refs(log.artifacts)
	};
}

/** The logs as a voyage: numbered sessions, and whatever came before the crew set out. */
export type Chronicle = {
	/** Sessions in play order (oldest first; undated logs last), numbered from 1. */
	sessions: Session[];
	/**
	 * Logs before the first one set anywhere, such as a world primer dated before play began.
	 * They are not sessions: they have `n` 0 and only the story views show them.
	 */
	prologue: Session[];
};

export function toChronicle(edges: ReadonlyArray<{ node: RawLog }> | null | undefined): Chronicle {
	const time = (log: RawLog) => (log.gameDate ? new Date(log.gameDate).getTime() : Infinity);
	const logs = (edges ?? []).map((e) => e.node).sort((a, b) => time(a) - time(b));
	// The voyage starts at the first log with a recorded place. When no log has one, the
	// campaign doesn't tag places at all, and every log is a session.
	const first = logs.findIndex((log) => nodes(log.placesSetIn).length > 0);
	const start = Math.max(0, first);
	return {
		prologue: logs.slice(0, start).map((log) => toSession(log, 0)),
		sessions: logs.slice(start).map((log, i) => toSession(log, i + 1))
	};
}

/** "Session 12: Archive of Echoes" -> "Archive of Echoes". Views show the number themselves. */
export function stripSessionPrefix(title: string | null | undefined): string {
	return (title ?? '').replace(/^\s*session\s*\d+\s*[:.\-–—]\s*/i, '').trim();
}

export const pad = (n: number, width = 2) => String(n).padStart(width, '0');

const MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];

/** "24 JAN 2026", in UTC so server and browser agree. */
export function shortDate(date: Date | null): string {
	if (!date) return 'UNDATED';
	return `${pad(date.getUTCDate())} ${MONTHS[date.getUTCMonth()]} ${date.getUTCFullYear()}`;
}

export function monthLabel(date: Date): string {
	return `${MONTHS[date.getUTCMonth()]} ${date.getUTCFullYear()}`;
}

export function daysBetween(a: Date | null, b: Date | null): number | null {
	if (!a || !b) return null;
	return Math.round((b.getTime() - a.getTime()) / 86_400_000);
}

/** "Port Veil · Calder · Ostra": the place, then what it is inside. */
export function wherePath(stop: PlaceStop): string {
	const names = [...stop.path].reverse().map((p) => p.name);
	if (stop.star) names.push(stop.star);
	return names.join(' · ');
}

/** The place a session is mainly set in: its most specific stop. */
export function primaryStop(session: Session): PlaceStop | null {
	if (!session.stops.length) return null;
	return [...session.stops].sort((a, b) => b.path.length - a.path.length)[0];
}

/** Stops in visiting order: broader places first, so "Lumen Spire" precedes its archive. */
export function orderedStops(session: Session): PlaceStop[] {
	return [...session.stops].sort((a, b) => a.path.length - b.path.length);
}

export type PlaceNode = Ref & {
	type: string | null;
	depth: number;
	parentId: string | null;
	children: PlaceNode[];
	/** Sessions set at this exact place. */
	sessions: Session[];
	/** Sessions set here or anywhere inside it. */
	allSessions: Session[];
};

/** The tree of every place the crew has been set in, plus the places that contain them. */
export function buildPlaceTree(sessions: Session[]): {
	roots: PlaceNode[];
	byId: Map<string, PlaceNode>;
} {
	const byId = new Map<string, PlaceNode>();
	const roots: PlaceNode[] = [];
	for (const session of sessions) {
		for (const stop of session.stops) {
			let parent: PlaceNode | null = null;
			stop.path.forEach((step, depth) => {
				let node = byId.get(step.id);
				if (!node) {
					node = {
						id: step.id,
						name: step.name,
						type: step.type,
						depth,
						parentId: parent?.id ?? null,
						children: [],
						sessions: [],
						allSessions: []
					};
					byId.set(step.id, node);
					if (parent) parent.children.push(node);
					else roots.push(node);
				}
				if (!node.allSessions.includes(session)) node.allSessions.push(session);
				parent = node;
			});
			const self = byId.get(stop.id);
			if (self && !self.sessions.includes(session)) self.sessions.push(session);
		}
	}
	return { roots, byId };
}

/** One leg of the journey: the crew's primary stop for a session. */
export type Leg = { session: Session; stop: PlaceStop };

export function journeyLegs(sessions: Session[]): Leg[] {
	const legs: Leg[] = [];
	for (const session of sessions) {
		const stop = primaryStop(session);
		if (stop) legs.push({ session, stop });
	}
	return legs;
}

const HUES = [
	'#ffb000',
	'#4de8e0',
	'#c084fc',
	'#39ff14',
	'#ff7a45',
	'#7aa8ff',
	'#ff5c8a',
	'#e8e04d'
];

/** Colour for places with no world of their own, and for sessions with no recorded place. */
export const NEUTRAL = '#8a7e60';
/** Colour for worlds visited too rarely to get one of the distinct hues. */
export const MINOR = '#a8997a';

/** The world a session is mainly set on: the top of its main stop's path. */
export function sessionWorld(session: Session): (Ref & { type: string | null }) | null {
	return primaryStop(session)?.path[0] ?? null;
}

/**
 * One colour per world. The most-visited worlds get the distinct hues, in order of first
 * visit, so the house amber goes to where the voyage began; worlds visited once or twice
 * share a muted tone instead of repeating a hue the main worlds already use.
 */
export function worldColours(sessions: Session[]): Map<string, string> {
	const visits = new Map<string, number>();
	const firstSeen: string[] = [];
	for (const session of sessions) {
		const main = sessionWorld(session)?.id;
		for (const stop of session.stops) {
			const id = stop.path[0].id;
			if (!visits.has(id)) {
				visits.set(id, 0);
				firstSeen.push(id);
			}
		}
		if (main) visits.set(main, (visits.get(main) ?? 0) + 1);
	}
	const major = new Set(
		[...visits.entries()]
			.filter(([, count]) => count > 0)
			.sort((a, b) => b[1] - a[1])
			.slice(0, HUES.length)
			.map(([id]) => id)
	);
	const colours = new Map<string, string>();
	for (const id of firstSeen) {
		colours.set(
			id,
			major.has(id) ? HUES[[...colours.values()].filter((c) => c !== MINOR).length] : MINOR
		);
	}
	return colours;
}

/** How many sessions are mainly set on each world. */
export function worldSessionCounts(sessions: Session[]): Map<string, number> {
	const counts = new Map<string, number>();
	for (const session of sessions) {
		const world = sessionWorld(session);
		if (world) counts.set(world.id, (counts.get(world.id) ?? 0) + 1);
	}
	return counts;
}

/** A session's colour: that of the world it is mainly set on. */
export function sessionColour(session: Session, colours: Map<string, string>): string {
	const world = sessionWorld(session);
	return world ? (colours.get(world.id) ?? NEUTRAL) : NEUTRAL;
}

/** A stay on one world: a run of consecutive sessions mainly set there. */
export type Arc = {
	/** 1-based position among the arcs. */
	n: number;
	/** The world, or null for a run of sessions with no recorded place. */
	world: (Ref & { type: string | null }) | null;
	sessions: Session[];
	/** Index of the arc's first session in the full list. */
	start: number;
	colour: string;
};

/**
 * The voyage as stays on worlds: a new arc starts each time the main world changes. A session
 * with no recorded place stays in the arc it falls in, since nothing says the crew moved.
 */
export function buildArcs(sessions: Session[], colours = worldColours(sessions)): Arc[] {
	const arcs: Arc[] = [];
	sessions.forEach((session, i) => {
		const world = sessionWorld(session);
		const last = arcs.at(-1);
		if (last && (!world || last.world?.id === world.id)) {
			last.sessions.push(session);
			return;
		}
		if (last && !last.world && world) {
			// A leading run with no place joins the first world the crew is seen on.
			last.world = world;
			last.colour = colours.get(world.id) ?? NEUTRAL;
			last.sessions.push(session);
			return;
		}
		arcs.push({
			n: arcs.length + 1,
			world,
			sessions: [session],
			start: i,
			colour: world ? (colours.get(world.id) ?? NEUTRAL) : NEUTRAL
		});
	});
	return arcs;
}

/** Arc lookup by session id. */
export function arcBySession(arcs: Arc[]): Map<string, Arc> {
	const map = new Map<string, Arc>();
	for (const arc of arcs) for (const session of arc.sessions) map.set(session.id, arc);
	return map;
}

const ROMAN: Array<[number, string]> = [
	[1000, 'M'],
	[900, 'CM'],
	[500, 'D'],
	[400, 'CD'],
	[100, 'C'],
	[90, 'XC'],
	[50, 'L'],
	[40, 'XL'],
	[10, 'X'],
	[9, 'IX'],
	[5, 'V'],
	[4, 'IV'],
	[1, 'I']
];

/** 14 -> "XIV", for part numbers. */
export function roman(n: number): string {
	let out = '';
	for (const [value, numeral] of ROMAN) {
		while (n >= value) {
			out += numeral;
			n -= value;
		}
	}
	return out;
}

/** One row of the Threads matrix: an entity and the sessions (by index) it appears in. */
export type Thread = { ref: Ref; hits: Set<number>; first: number; last: number; count: number };

export function buildThreads(sessions: Session[], pick: (session: Session) => Ref[]): Thread[] {
	const map = new Map<string, { ref: Ref; hits: Set<number> }>();
	sessions.forEach((session, i) => {
		for (const ref of pick(session)) {
			let thread = map.get(ref.id);
			if (!thread) map.set(ref.id, (thread = { ref, hits: new Set() }));
			thread.hits.add(i);
		}
	});
	return [...map.values()].map((t) => {
		const order = [...t.hits].sort((a, b) => a - b);
		return { ...t, first: order[0], last: order.at(-1) ?? order[0], count: order.length };
	});
}

export const dayKey = (y: number, m: number, d: number) => `${y}-${m}-${d}`;

/** Sessions keyed by the UTC day they were played. */
export function sessionsByDay(sessions: Session[]): Map<string, Session[]> {
	const map = new Map<string, Session[]>();
	for (const s of sessions) {
		if (!s.date) continue;
		const k = dayKey(s.date.getUTCFullYear(), s.date.getUTCMonth(), s.date.getUTCDate());
		map.set(k, [...(map.get(k) ?? []), s]);
	}
	return map;
}

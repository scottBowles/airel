// Shared shape for the Chronicle journey views, built once from the ChronicleJourney query.

export type Ref = { id: string; name: string };

export type PlaceStop = Ref & {
	type: string | null;
	/** Ancestors from the outermost place (a star, usually) down to this place, inclusive. */
	path: Array<Ref & { type: string | null }>;
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
	return { id: place.id, name: place.name, type: place.placeType ?? null, path };
}

/** Sessions in play order (oldest first; undated logs last), numbered from 1. */
export function toSessions(edges: ReadonlyArray<{ node: RawLog }> | null | undefined): Session[] {
	const logs = (edges ?? []).map((e) => e.node);
	const time = (log: RawLog) => (log.gameDate ? new Date(log.gameDate).getTime() : Infinity);
	return [...logs]
		.sort((a, b) => time(a) - time(b))
		.map((log, i) => ({
			id: log.id,
			n: i + 1,
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
		}));
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
	return [...stop.path]
		.reverse()
		.map((p) => p.name)
		.join(' · ');
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

/** A stable accent colour for a name, e.g. one per star system. */
export function hueFor(key: string): string {
	let hash = 0;
	for (let i = 0; i < key.length; i++) hash = (hash * 31 + key.charCodeAt(i)) >>> 0;
	return HUES[hash % HUES.length];
}

/** Colours assigned in order of appearance, so the first systems get the house colours. */
export function colourByOrder(keys: string[]): Map<string, string> {
	const map = new Map<string, string>();
	for (const key of keys) if (!map.has(key)) map.set(key, HUES[map.size % HUES.length]);
	return map;
}

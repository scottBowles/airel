// Layout for the Chronicle star chart: each sun with its worlds on an orbit ring, each world's
// places fanned out around it, and the crew's flights between places. Pure, so it is tested.
import type { PlaceNode, Session } from './model';

/** A place on the chart. `cx, cy` is what it orbits: its parent place, or a world's sun. */
export type ChartPoint = {
	node: PlaceNode;
	x: number;
	y: number;
	cx: number;
	cy: number;
	/** The world (a root of the place tree) this place belongs to. */
	worldId: string;
};

/** A sun and the worlds that orbit it, or the worlds with no sun recorded (`star` null). */
export type ChartGroup = {
	star: string | null;
	x: number;
	y: number;
	/** Radius of the ring the group's worlds sit on; 0 for a lone world with no sun. */
	ring: number;
	worlds: PlaceNode[];
};

export type ChartLayout = {
	points: Map<string, ChartPoint>;
	groups: ChartGroup[];
	width: number;
	height: number;
};

/** Distance from a place to its children, by the place's depth (0 is a world). */
export const ORBIT = [66, 44, 30, 20, 14];
const RING_GAP = 36;
const SUN_CLEARANCE = 80;
const MIN_RING = 130;
const GROUP_GAP = 36;
/** Room around the outermost places for their labels. */
const PAD_X = 14;
const PAD_Y = 44;
/** The panel the chart sits in is wider than tall; pick the arrangement closest to this. */
const TARGET_ASPECT = 1.45;

type Local = { node: PlaceNode; x: number; y: number; cx: number; cy: number };

/** Glyph radius for a place: worlds largest, then planets and moons, then everything else. */
export function glyphSize(type: string | null, depth: number): number {
	return depth === 0 ? 8 : type === 'PLANET' ? 6 : type === 'MOON' ? 4.5 : 4;
}

/** Longest label drawn; longer names are cut with an ellipsis (the full name is in the tooltip). */
export const LABEL_MAX = 24;

export function shortName(name: string, max = LABEL_MAX): string {
	return name.length > max ? `${name.slice(0, max - 1)}…` : name;
}

type Placed = { node: PlaceNode; x: number; y: number; cx: number; cy: number };

/**
 * Where a place's label goes. A world's sits above it. Any other label sits on the far side of
 * the place from what it orbits, so it points away from the crowd: beside it when that is
 * mostly sideways, above or below otherwise.
 */
export function labelPosition(
	point: Placed,
	/** The chart's width: labels are kept inside it. */
	chartWidth = Infinity
): { x: number; y: number; anchor: 'start' | 'middle' | 'end'; maxChars: number } {
	const size = glyphSize(point.node.type, point.node.depth);
	const width = labelWidth(point.node);
	const fit = (x: number) => Math.min(Math.max(x, width / 2 + 4), chartWidth - width / 2 - 4);
	if (point.node.depth === 0) {
		return { x: fit(point.x), y: point.y - size - 9, anchor: 'middle', maxChars: LABEL_MAX };
	}
	const side = naturalSide(point);
	if (side === 'below-or-above') {
		const below = point.y > point.cy;
		const y = point.y + (below ? size + 14 : -size - 6);
		return { x: fit(point.x), y, anchor: 'middle', maxChars: LABEL_MAX };
	}
	// Beside the place, away from what it orbits. Near an edge the label is shortened to the
	// room there; it moves to the other side only when there is hardly any room at all.
	const gap = size + 6;
	const room = (right: boolean) => (right ? chartWidth - point.x - gap - 4 : point.x - gap - 4);
	const charsIn = (px: number) => Math.floor(px / CHAR_W) - 4;
	let right = side === 'right';
	if (charsIn(room(right)) < 10 && room(!right) > room(right)) right = !right;
	return {
		x: point.x + (right ? gap : -gap),
		y: point.y + 4,
		anchor: right ? 'start' : 'end',
		maxChars: Math.max(6, Math.min(LABEL_MAX, charsIn(room(right))))
	};
}

/** Width of one character of a place label (11px mono with letter spacing). */
const CHAR_W = 7.2;

/** Roughly how wide a place's label is drawn, with room for a visit count. */
function labelWidth(node: PlaceNode): number {
	return (Math.min(node.name.length, LABEL_MAX) + 4) * (node.depth === 0 ? 11 : CHAR_W);
}

/**
 * The horizontal span a place needs, label included. A world's label is always drawn. Other
 * labels show only for the world the ship is at; room is kept for most of one on its natural
 * side, and a longer one that would still run off the chart flips inwards.
 */
function labelSpan(point: Placed): [number, number] {
	if (point.node.depth === 0) {
		const width = labelWidth(point.node);
		return [point.x - width / 2, point.x + width / 2];
	}
	const width = Math.min(labelWidth(point.node), 120);
	const side = naturalSide(point);
	if (side === 'right') return [point.x - 8, point.x + 10 + width];
	if (side === 'left') return [point.x - 10 - width, point.x + 8];
	return [point.x - width / 2, point.x + width / 2];
}

/** Which side of a place its label belongs on: away from what the place orbits. */
function naturalSide(point: Placed): 'left' | 'right' | 'below-or-above' {
	const cos = Math.cos(Math.atan2(point.y - point.cy, point.x - point.cx));
	return Math.abs(cos) < 0.45 ? 'below-or-above' : cos > 0 ? 'right' : 'left';
}

/** A world's places fanned out around it, facing away from its sun, relative to the world. */
function layoutWorld(world: PlaceNode, facing: number): Local[] {
	const out: Local[] = [{ node: world, x: 0, y: 0, cx: 0, cy: 0 }];
	const place = (node: PlaceNode, px: number, py: number, towards: number) => {
		const count = node.children.length;
		if (!count) return;
		const radius = ORBIT[Math.min(node.depth, ORBIT.length - 1)];
		// A world's own places may wrap most of the way round it; deeper ones fan narrowly.
		const spread = node.depth === 0 ? Math.PI * 1.5 : Math.PI * 0.85;
		const step = count > 1 ? Math.min(node.depth === 0 ? 1.0 : 0.65, spread / (count - 1)) : 0;
		node.children.forEach((child, k) => {
			const angle = towards + (k - (count - 1) / 2) * step;
			const x = px + Math.cos(angle) * radius;
			const y = py + Math.sin(angle) * radius;
			out.push({ node: child, x, y, cx: px, cy: py });
			place(child, x, y, angle);
		});
	};
	place(world, 0, 0, facing);
	return out;
}

/** How far a world's places reach from it, whichever way they face. */
function reach(world: PlaceNode): number {
	return Math.max(0, ...layoutWorld(world, 0).map((p) => Math.hypot(p.x, p.y))) + 22;
}

function layoutGroup(star: string | null, worlds: PlaceNode[]) {
	const radii = worlds.map(reach);
	const shares = radii.map((r) => 2 * r + RING_GAP);
	const total = shares.reduce((sum, share) => sum + share, 0);
	const lone = !star && worlds.length === 1;
	const ring = lone
		? 0
		: // Places fan out away from the sun, so a world needs only part of its reach as clearance.
			Math.max(
				MIN_RING,
				(total / (2 * Math.PI)) * 1.15,
				(star ? SUN_CLEARANCE : 0) + 0.65 * Math.max(...radii)
			);

	const local: Array<Local & { worldId: string }> = [];
	let along = 0;
	worlds.forEach((world, i) => {
		// Each world gets a share of the ring in proportion to the room its places need.
		const angle = -Math.PI / 2 + ((along + shares[i] / 2) / total) * Math.PI * 2;
		along += shares[i];
		const wx = Math.cos(angle) * ring;
		const wy = Math.sin(angle) * ring;
		for (const p of layoutWorld(world, lone ? -Math.PI / 2 : angle)) {
			const isWorld = p.node.id === world.id;
			local.push({
				node: p.node,
				x: p.x + wx,
				y: p.y + wy,
				cx: isWorld ? 0 : p.cx + wx,
				cy: isWorld ? 0 : p.cy + wy,
				worldId: world.id
			});
		}
	});

	const spans = local.map(labelSpan);
	const ys = local.map((p) => p.y);
	return {
		star,
		ring,
		worlds,
		local,
		minX: Math.min(-ring, ...spans.map(([left]) => left)) - PAD_X,
		maxX: Math.max(ring, ...spans.map(([, right]) => right)) + PAD_X,
		minY: Math.min(-ring, ...ys) - PAD_Y,
		maxY: Math.max(ring, ...ys) + PAD_Y
	};
}

type Group = ReturnType<typeof layoutGroup>;

/** Groups left to right, wrapping into rows `rowWidth` wide. */
function pack(groups: Group[], rowWidth: number) {
	const placed: Array<{ group: Group; dx: number; dy: number }> = [];
	let x = 0;
	let y = 0;
	let rowHeight = 0;
	let width = 0;
	for (const group of groups) {
		const w = group.maxX - group.minX;
		const h = group.maxY - group.minY;
		if (x > 0 && x + w > rowWidth) {
			x = 0;
			y += rowHeight + GROUP_GAP;
			rowHeight = 0;
		}
		placed.push({ group, dx: x - group.minX, dy: y - group.minY });
		x += w + GROUP_GAP;
		width = Math.max(width, x - GROUP_GAP);
		rowHeight = Math.max(rowHeight, h);
	}
	return { placed, width, height: y + rowHeight };
}

/**
 * Suns are laid out as groups: the sun in the middle, its worlds on a ring sized so their
 * places don't collide, each world's places fanned out away from the sun. Worlds with no sun
 * recorded form one more group. Groups are then arranged in the rows that best fit the panel.
 */
export function layoutChart(roots: PlaceNode[], starOf: Map<string, string | null>): ChartLayout {
	const byStar = new Map<string | null, PlaceNode[]>();
	for (const world of roots) {
		const star = starOf.get(world.id) ?? null;
		byStar.set(star, [...(byStar.get(star) ?? []), world]);
	}
	const sessionsIn = (worlds: PlaceNode[]) => worlds.reduce((n, w) => n + w.allSessions.length, 0);
	const groups = [...byStar.entries()]
		// Suns with the most play first; worlds with no sun last.
		.sort(
			([a, wa], [b, wb]) =>
				(a === null ? 1 : 0) - (b === null ? 1 : 0) || sessionsIn(wb) - sessionsIn(wa)
		)
		.map(([star, worlds]) => layoutGroup(star, worlds));

	// Try each row width that ends a row exactly after one of the groups, and keep the
	// arrangement whose shape is closest to the panel's.
	const fit = (p: ReturnType<typeof pack>) =>
		Math.abs(Math.log(p.width / Math.max(1, p.height) / TARGET_ASPECT));
	let best = pack(groups, Infinity);
	let rowWidth = 0;
	for (const group of groups) {
		rowWidth += group.maxX - group.minX + (rowWidth ? GROUP_GAP : 0);
		const candidate = pack(groups, rowWidth + 1);
		if (fit(candidate) < fit(best)) best = candidate;
	}

	const points = new Map<string, ChartPoint>();
	const placedGroups: ChartGroup[] = [];
	for (const { group, dx, dy } of best.placed) {
		placedGroups.push({ star: group.star, x: dx, y: dy, ring: group.ring, worlds: group.worlds });
		for (const p of group.local) {
			const isWorld = p.node.depth === 0;
			points.set(p.node.id, {
				node: p.node,
				x: p.x + dx,
				y: p.y + dy,
				cx: (isWorld ? 0 : p.cx) + dx,
				cy: (isWorld ? 0 : p.cy) + dy,
				worldId: p.worldId
			});
		}
	}
	return {
		points,
		groups: placedGroups,
		width: Math.max(best.width, 480),
		height: Math.max(best.height, 320)
	};
}

/** The sun each world orbits, as recorded on the places the crew visited there. */
export function starsOf(sessions: Session[]): Map<string, string | null> {
	const map = new Map<string, string | null>();
	for (const session of sessions) {
		for (const stop of session.stops) {
			const world = stop.path[0].id;
			if (!map.get(world)) map.set(world, stop.star);
		}
	}
	return map;
}

/** Every flight between the same two places, in either direction, as one route. */
export type Route = {
	key: string;
	/** The two places, in a fixed order so the route always draws the same way. */
	a: string;
	b: string;
	/** Indices of the legs that flew this route, in order. */
	legs: number[];
};

/** Routes from the places visited in order: one per pair of places the crew moved between. */
export function buildRoutes(stopIds: string[]): Route[] {
	const routes = new Map<string, Route>();
	stopIds.forEach((to, i) => {
		const from = stopIds[i - 1];
		if (i === 0 || from === to) return;
		const [a, b] = from < to ? [from, to] : [to, from];
		const key = `${a}|${b}`;
		const route = routes.get(key) ?? { key, a, b, legs: [] };
		route.legs.push(i);
		routes.set(key, route);
	});
	return [...routes.values()];
}

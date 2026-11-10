// Layout for the Chronicle star chart: where each place sits on the canvas.
import type { PlaceNode } from './model';

/** A place on the chart, with the position of what it orbits (its parent, or itself). */
export type ChartPoint = {
	node: PlaceNode;
	x: number;
	y: number;
	rootId: string;
	cx: number;
	cy: number;
};

/** Orbit radius by depth: worlds around a star, then what is inside each world. */
export const ORBIT = [0, 104, 66, 42, 26];
const PAD_X = 20;
const PAD_Y = 52;

const seed = (text: string) => {
	let hash = 7;
	for (let i = 0; i < text.length; i++) hash = (hash * 31 + text.charCodeAt(i)) >>> 0;
	return hash;
};

/**
 * Each system is laid out around its own star: worlds ring the star, and what is inside a
 * world fans out beyond it. Systems are then packed side by side by their real extents,
 * wrapping to a new row when a row is full, so nothing is clipped or overlaps.
 */
export function layoutChart(roots: PlaceNode[]): {
	points: Map<string, ChartPoint>;
	width: number;
	height: number;
} {
	const systems = roots.map((root) => {
		const local: ChartPoint[] = [{ node: root, x: 0, y: 0, rootId: root.id, cx: 0, cy: 0 }];
		const start = ((seed(root.name) % 360) * Math.PI) / 180;
		const place = (node: PlaceNode, px: number, py: number, facing: number, full: boolean) => {
			const count = node.children.length;
			const radius = ORBIT[Math.min(node.depth + 1, ORBIT.length - 1)];
			const step = full ? (Math.PI * 2) / count : Math.min(1.15, 2.7 / Math.max(1, count - 1));
			node.children.forEach((child, k) => {
				const angle = full ? start + k * step : facing + (k - (count - 1) / 2) * step;
				const x = px + Math.cos(angle) * radius;
				const y = py + Math.sin(angle) * radius;
				local.push({ node: child, x, y, rootId: root.id, cx: px, cy: py });
				place(child, x, y, angle, false);
			});
		};
		place(root, 0, 0, start, true);
		// Extents include each label, which sits on the far side of a place from its parent.
		const reach = root.children.length ? ORBIT[1] : 0;
		let minX = -reach;
		let maxX = reach;
		for (const p of local) {
			const text = (p.node.name.length + 3) * (p.node.depth === 0 ? 12 : 8.7);
			const cos = Math.cos(Math.atan2(p.y - p.cy, p.x - p.cx));
			const sideways = p.node.depth > 0 && Math.abs(cos) >= 0.45;
			minX = Math.min(minX, sideways ? (cos < 0 ? p.x - text - 16 : p.x) : p.x - text / 2);
			maxX = Math.max(maxX, sideways ? (cos > 0 ? p.x + text + 16 : p.x) : p.x + text / 2);
		}
		const ys = local.map((p) => p.y);
		return {
			local,
			minX: minX - PAD_X,
			maxX: maxX + PAD_X,
			minY: Math.min(-reach, ...ys) - PAD_Y,
			maxY: Math.max(reach, ...ys) + PAD_Y
		};
	});

	// Aim for a wide chart: one row until the systems would make it far wider than tall.
	const total = systems.reduce((sum, s) => sum + (s.maxX - s.minX), 0);
	const tallest = Math.max(1, ...systems.map((s) => s.maxY - s.minY));
	const rowCount = Math.max(1, Math.round(Math.sqrt(total / (tallest * 2.2))));
	const ROW_WIDTH = total / rowCount + 1;

	const points = new Map<string, ChartPoint>();
	let x = 0;
	let y = 0;
	let rowHeight = 0;
	let width = 0;
	for (const system of systems) {
		const w = system.maxX - system.minX;
		const h = system.maxY - system.minY;
		if (x > 0 && x + w > ROW_WIDTH) {
			x = 0;
			y += rowHeight;
			rowHeight = 0;
		}
		for (const p of system.local) {
			const dx = x - system.minX;
			const dy = y - system.minY;
			points.set(p.node.id, { ...p, x: p.x + dx, y: p.y + dy, cx: p.cx + dx, cy: p.cy + dy });
		}
		x += w;
		width = Math.max(width, x);
		rowHeight = Math.max(rowHeight, h);
	}
	return { points, width: Math.max(width, 480), height: Math.max(y + rowHeight, 320) };
}

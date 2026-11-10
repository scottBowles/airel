// Procedural "postcard" art for a session: a small landscape drawn from the place it is set in.
// Deterministic, so the same session always gets the same card on server and client.

function mulberry32(seed: number) {
	return () => {
		seed = (seed + 0x6d2b79f5) | 0;
		let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
		t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}

function hash(text: string): number {
	let h = 2166136261;
	for (let i = 0; i < text.length; i++) h = Math.imul(h ^ text.charCodeAt(i), 16777619);
	return h >>> 0;
}

export type Postcard = {
	stars: Array<{ x: number; y: number; r: number; o: number }>;
	/** The sun, moon or world hanging in the sky. */
	orb: { x: number; y: number; r: number; ringed: boolean };
	/** Far and near ground silhouettes as SVG path data, in a 200x120 box. */
	far: string;
	near: string;
};

export const CARD_W = 200;
export const CARD_H = 120;

/** `placeKey` decides the landscape (so a place looks the same each visit); `type` its style. */
export function postcard(placeKey: string, type: string | null, variant: number): Postcard {
	const place = mulberry32(hash(placeKey));
	const sky = mulberry32(hash(`${placeKey}#${variant}`));

	const stars = Array.from({ length: 22 }, () => ({
		x: sky() * CARD_W,
		y: sky() * CARD_H * 0.7,
		r: sky() > 0.85 ? 1.1 : 0.6,
		o: 0.25 + sky() * 0.6
	}));

	const big = type === 'PLANET' || type === 'STAR' || type === 'MOON';
	const orb = {
		x: 40 + place() * 120,
		y: 22 + place() * 30,
		r: big ? 20 + place() * 16 : 8 + place() * 10,
		ringed: place() > 0.6
	};

	// Built-up places get a skyline; everywhere else gets hills or crags.
	const built = type === 'TOWN' || type === 'DISTRICT';
	const ridge = (base: number, height: number, steps: number, blocky: boolean) => {
		let d = `M0,${CARD_H} `;
		const step = CARD_W / steps;
		for (let i = 0; i <= steps; i++) {
			const y = base - place() * height;
			d += blocky ? `L${i * step},${y} L${(i + 1) * step},${y} ` : `L${i * step},${y} `;
		}
		return `${d}L${CARD_W},${CARD_H} Z`;
	};

	return {
		stars,
		orb,
		far: ridge(86, built ? 34 : 22, built ? 16 : 9, built),
		near: ridge(104, built ? 16 : 14, built ? 11 : 6, built && place() > 0.3)
	};
}

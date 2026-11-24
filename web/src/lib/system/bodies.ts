import type { Shape } from './geo';
// Render settings for each body, keyed by the folder its textures live in (web/static/system/<slug>,
// made by tools/planets). Which bodies exist and what they orbit will come from the DB; how they
// look stays here with the textures. Sizes and orbits are for the display, not to scale.

import type { AtmosphereLook } from './atmosphere';

export type BodyLook = {
	name: string;
	radius: number;
	/** Emissive multiplier (lava, city lights, the giant's ember). */
	glow?: number;
	/** See Planet's `metalness`. */
	metalness?: number;
	flicker?: number;
	clouds?: {
		color?: [number, number, number];
		opacity?: number;
		drift?: number;
		near?: number;
		normal?: boolean;
		glow?: number;
		lightning?: number;
	};
	atmosphere?: AtmosphereLook;
	/** Dusk light past the terminator (see Planet's `twilight`). */
	twilight?: { strength: number; color?: [number, number, number] };
	/** For a moon: distance from its planet's centre and seconds per orbit. */
	orbit?: { distance: number; period: number; phase: number; tilt?: number };
};

export const GONHIRRIM: BodyLook = {
	name: 'Gonhirrim',
	radius: 4,
	glow: 1,
	flicker: 0.5,
	atmosphere: { color: [0.9, 0.62, 0.42], strength: 0.45 }
};

// The moons are broadly alike (dwarven mining moons with thin air and weather), each styled by
// its god. Durinfol, the capital moon, is a little larger. Periods are minutes, so they're easy
// to click; tidally locked, with lon 0 facing Gonhirrim. Their glow is settlement lights, shown only
// on the night side, so it can be bright.
export const GONHIRRIM_MOONS: Record<string, BodyLook> = {
	broadbeam: {
		name: 'Broadbeam',
		radius: 0.42,
		glow: 3,
		clouds: { color: [0.92, 0.95, 1], opacity: 0.85 },
		atmosphere: { color: [0.55, 0.7, 1], strength: 0.9 },
		orbit: { distance: 7.2, period: 240, phase: 0.3, tilt: 2 }
	},
	firebeard: {
		name: 'Firebeard',
		radius: 0.4,
		glow: 3,
		clouds: { color: [0.9, 0.82, 1], opacity: 0.7 },
		atmosphere: { color: [0.7, 0.45, 1], strength: 0.8 },
		orbit: { distance: 8.6, period: 300, phase: 1.4, tilt: -3 }
	},
	durinfol: {
		name: 'Durinfol',
		radius: 0.5,
		glow: 3.5,
		clouds: { opacity: 0.8 },
		atmosphere: { color: [0.4, 0.65, 1], strength: 1 },
		orbit: { distance: 10.2, period: 360, phase: 2.6, tilt: 1 }
	},
	ironfist: {
		name: 'Ironfist',
		radius: 0.44,
		glow: 3.5,
		clouds: { color: [1, 0.93, 0.88], opacity: 0.7 },
		atmosphere: { color: [1, 0.6, 0.45], strength: 0.7 },
		orbit: { distance: 11.8, period: 420, phase: 3.9, tilt: -1.5 }
	},
	blacklock: {
		name: 'Blacklock',
		radius: 0.4,
		glow: 4.5,
		clouds: { color: [0.95, 0.92, 0.88], opacity: 0.7 },
		atmosphere: { color: [1, 0.72, 0.45], strength: 0.6 },
		orbit: { distance: 13.4, period: 480, phase: 5.0, tilt: 2.5 }
	},
	stiffbeard: {
		name: 'Stiffbeard',
		radius: 0.42,
		glow: 3,
		clouds: { opacity: 0.75 },
		atmosphere: { color: [0.75, 0.8, 0.95], strength: 0.7 },
		orbit: { distance: 15.0, period: 540, phase: 0.9, tilt: -2 }
	},
	stonefoot: {
		name: 'Stonefoot',
		radius: 0.44,
		glow: 3,
		clouds: { color: [1, 0.96, 0.9], opacity: 0.6 },
		atmosphere: { color: [0.85, 0.72, 0.55], strength: 0.5 },
		orbit: { distance: 16.6, period: 600, phase: 4.4, tilt: 1.5 }
	}
};

// The rain world: islands under a heavy grey deck, city lights showing through the gaps at night.
export const HYANG_WAN: BodyLook = {
	name: 'Hyang Wan',
	radius: 1.4,
	glow: 7,
	clouds: { color: [0.52, 0.55, 0.58], opacity: 0.82, drift: 0.003, normal: true },
	atmosphere: { color: [0.55, 0.7, 0.85], strength: 0.85 }
};

/** Humid jungle world of the fey: white cumulus over the canopy, a faint green-blue haze. */
export const FELUCIA: BodyLook = {
	name: 'Felucia',
	radius: 1.2,
	glow: 5,
	clouds: { color: [0.9, 0.92, 0.93], opacity: 0.9, drift: 0.003, normal: true },
	atmosphere: { color: [0.55, 0.78, 0.9], strength: 0.9 }
};

/** The planet-wide metropolis: grey city by day, the brightest night side in the system. */
export const TERRAN: BodyLook = {
	name: 'Terran',
	radius: 1.4,
	glow: 3,
	clouds: { color: [0.9, 0.92, 0.94], opacity: 0.85, drift: 0.003, normal: true },
	atmosphere: { color: [0.5, 0.68, 0.95], strength: 0.85 }
};

/** The pink Dagobah: wine and rose swamp under a broken pink mist deck that fills the lowlands. */
export const MYSTRA: BodyLook = {
	name: 'Mystra',
	radius: 1.15,
	glow: 3,
	// The mist sits in the basins and breaks over the uplands, so it doesn't drift.
	clouds: { color: [0.62, 0.4, 0.5], opacity: 0.9, drift: 0, normal: true, glow: 0.5 },
	atmosphere: { color: [0.95, 0.55, 0.72], strength: 0.75 }
};

/**
 * Chromium, the dark planet of the dragons: near-black basalt under a dark storm deck, ember
 * rifts glowing dull red up through the cloud at night, lightning in the storms, and a faint
 * cool sheen at the rim. The deck doesn't drift, as the ember glow is mapped on it.
 */
export const CHROMIUM: BodyLook = {
	name: 'Chromium',
	radius: 1.1,
	glow: 1.6,
	flicker: 0.6,
	clouds: {
		color: [0.07, 0.07, 0.08],
		opacity: 0.95,
		drift: 0,
		normal: true,
		glow: 0.4,
		lightning: 0.8,
		near: 0.55
	},
	atmosphere: { color: [0.5, 0.48, 0.8], strength: 0.22 }
};

/**
 * Didymus, one small planet broken in two long ago: Prime, the larger, kidney-bean shaped and
 * home to every known place; and its smaller, rounder, more charred twin. Each keeps its worn
 * break face (lon 180) toward the other. Thin red-brown dust haze, no clouds.
 */
export const DIDYMUS_PRIME: BodyLook & { shape: Shape } = {
	name: 'Didymus Prime',
	radius: 0.6,
	glow: 4,
	atmosphere: { color: [1.0, 0.66, 0.42], strength: 0.3, height: 1.015 },
	shape: { stretch: 1.45, indent: 0.24, indentLon: 180 }
};
export const DIDYMUS: BodyLook = {
	name: 'Didymus',
	radius: 0.4,
	glow: 4,
	atmosphere: { color: [1.0, 0.66, 0.42], strength: 0.25, height: 1.015 }
};

/**
 * "Nega-Terran", the Vegas of planets: a grimy rust-and-soot city by day under brown smog, and
 * at night four quadrants of different light (G2's neon blaze, G4's broken sodium orange).
 */
export const GENUSSA: BodyLook = {
	name: 'Genussa',
	radius: 1.3,
	glow: 3,
	// Glass and metal: with the roughness map, the cores and G3 catch a broad sun highlight.
	metalness: 0.15,
	clouds: { color: [0.62, 0.56, 0.5], opacity: 0.75, drift: 0.003, normal: true },
	atmosphere: { color: [0.82, 0.58, 0.42], strength: 0.85 }
};

/**
 * Tidally locked to the Red Sun: one half always in its light, one always dark, the Mezzolux
 * between. Its clouds stay put over the dark side (steam from the geysers), so they don't drift.
 */
export const JANUS: BodyLook = {
	name: 'Janus',
	radius: 1.1,
	glow: 2.5,
	clouds: { color: [0.86, 0.86, 0.87], opacity: 0.85, drift: 0, normal: true },
	atmosphere: { color: [0.95, 0.62, 0.42], strength: 0.6 },
	// The Mezzolux is the penumbra: dusk under the Red Sun's disc, half above the horizon.
	twilight: { strength: 0.8, color: [1.0, 0.55, 0.38] }
};

/** Two logs see it set over Mulgogi. Airless grey rock. */
export const HYANG_WAN_MOON: BodyLook = {
	name: "Hyang Wan's Moon",
	radius: 0.3,
	orbit: { distance: 4.6, period: 300, phase: 2.2, tilt: 4 }
};

// Where everything sits in the whole-system view. Distances are fractions of D, the distance
// between the two suns, measured from the user's sketch (see .ideas/projects/solar-system-3d/
// bodies/system.md, "Proposed layout"); the user says not to read much into it. Nothing is to
// scale: planets are drawn far bigger than their orbits would allow, or they'd be invisible.

import {
	DIDYMUS_PRIME,
	FELUCIA,
	GENUSSA,
	GONHIRRIM,
	HYANG_WAN,
	JANUS,
	MAGMUS,
	MYSTRA,
	TERRAN,
	type BodyLook
} from './bodies';

export type Vec3 = [number, number, number];

/** Distance between the suns, in scene units. */
export const D = 240;
export const YELLOW_AT: Vec3 = [-D / 2, 0, 0];
export const RED_AT: Vec3 = [D / 2, 0, 0];
export const SUN_RADIUS = 6;
/** Planets are drawn this many times their size in the lab (Gonhirrim and its moons at 1). */
export const SIZE = 1.5;

export type Orbiter = {
	slug: string;
	look: BodyLook;
	sun: 'yellow' | 'red';
	/** Orbit radius, as a fraction of D. */
	distance: number;
	/** Starting angle and orbit tilt, degrees. */
	phase: number;
	tilt: number;
	/** City lights: glow only on the night side. */
	nightLights?: boolean;
	/** Keeps one face to its sun (Janus): it doesn't spin, and `face` is set for that. */
	tidal?: boolean;
};

// The sketch numbers the planets 1–10 from the Yellow Sun outward, through the belt, then in to
// the Red Sun. Hyang Wan isn't on it; it's put between Terran and Gonhirrim. Felucia and Terran
// are drawn at the same distance; they're spread apart here.
export const PLANETS: Orbiter[] = [
	{ slug: 'magmus', look: MAGMUS, sun: 'yellow', distance: 0.1, phase: 40, tilt: 1.5 },
	{
		slug: 'felucia',
		look: FELUCIA,
		sun: 'yellow',
		distance: 0.17,
		phase: 200,
		tilt: -1,
		nightLights: true
	},
	{
		slug: 'terran',
		look: TERRAN,
		sun: 'yellow',
		distance: 0.22,
		phase: 120,
		tilt: 2,
		nightLights: true
	},
	{
		slug: 'hyang-wan',
		look: HYANG_WAN,
		sun: 'yellow',
		distance: 0.27,
		phase: 300,
		tilt: -2,
		nightLights: true
	},
	{ slug: 'gonhirrim', look: GONHIRRIM, sun: 'yellow', distance: 0.35, phase: 150, tilt: 1 },
	{
		slug: 'didymus',
		look: DIDYMUS_PRIME,
		sun: 'red',
		distance: 0.14,
		phase: 250,
		tilt: -2.5,
		nightLights: true
	},
	{
		slug: 'janus',
		look: JANUS,
		sun: 'red',
		distance: 0.22,
		phase: 20,
		tilt: 1,
		nightLights: true,
		tidal: true
	},
	{
		slug: 'genussa',
		look: GENUSSA,
		sun: 'red',
		distance: 0.36,
		phase: 100,
		tilt: -1.5,
		nightLights: true
	},
	{
		slug: 'mystra',
		look: MYSTRA,
		sun: 'red',
		distance: 0.43,
		phase: 190,
		tilt: 2,
		nightLights: true
	}
];

/** Seconds per orbit at normal speed: Magmus takes a minute, the rest follow Kepler (T ∝ r^1.5). */
export function period(distance: number): number {
	return 60 * (distance / 0.1) ** 1.5;
}

/**
 * The belt: an arc of rocks between the suns, a little nearer the Yellow Sun (DM), curving round
 * it. It orbits nothing. Angles are measured in the x–z plane from +x (toward the Red Sun) to -z.
 */
export const BELT = {
	radius: 0.47 * D,
	arc: [-0.55, 0.55] as [number, number],
	width: 5,
	thickness: 1.2
};
/** Hielo, the belt's largest body, a little off the line between the suns. */
const HIELO_ANGLE = 0.12;
export const HIELO_AT: Vec3 = [
	YELLOW_AT[0] + BELT.radius * Math.cos(HIELO_ANGLE),
	0,
	YELLOW_AT[2] - BELT.radius * Math.sin(HIELO_ANGLE)
];

/**
 * Chromium's figure-eight round both suns: a lemniscate of Bernoulli with the suns at its foci,
 * crossing between them. `s` runs 0..2π once round; the path tilts a few degrees out of the
 * plane, so it passes over and under the other orbits rather than through them.
 */
export const CHROMIUM_PERIOD = 900;
const LOBE = D / Math.SQRT2;
const TILT = (4 * Math.PI) / 180;
export function figureEight(s: number): Vec3 {
	const k = 1 + Math.sin(s) ** 2;
	const x = (LOBE * Math.cos(s)) / k;
	const z = (LOBE * Math.sin(s) * Math.cos(s)) / k;
	return [x, z * Math.sin(TILT), z * Math.cos(TILT)];
}

// Latitude/longitude on a planet, matching the equirectangular textures from tools/planets
// (left edge = 180° W, right edge = 180° E, top = north) as three.js's SphereGeometry maps them.

export type Pin = {
	name: string;
	lat: number;
	lon: number;
	/** lore: the logs fix the spot; layout: the logs give the area; guess: no lore yet. */
	confidence: 'lore' | 'layout' | 'guess';
};

/** Point on a sphere of the given radius at a latitude/longitude in degrees. */
export function latLonToVector(lat: number, lon: number, radius = 1): [number, number, number] {
	const phi = ((lon + 180) / 360) * Math.PI * 2;
	const la = (lat * Math.PI) / 180;
	return [
		-Math.cos(phi) * Math.cos(la) * radius,
		Math.sin(la) * radius,
		Math.sin(phi) * Math.cos(la) * radius
	];
}

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

/**
 * A non-spherical body: stretched along the polar axis, and pressed in on one side (a kidney
 * bean's hollow). `stretch` is the polar length over the equatorial width; `indent` how deep the
 * hollow is (a fraction of the radius); `indentLon` the longitude the hollow faces. The volume
 * stays about that of the unit sphere.
 */
export type Shape = { stretch: number; indent: number; indentLon: number };

/** Where a point of the unit sphere (three.js coordinates, y up) moves to on the shaped body. */
export function shapePoint(p: [number, number, number], shape: Shape): [number, number, number] {
	const k = 1 / Math.cbrt(shape.stretch);
	const y = p[1] * shape.stretch * k;
	const d = latLonToVector(0, shape.indentLon);
	const toward = p[0] * d[0] + p[2] * d[2]; // 1 at the hollow's centre, on the equator
	// Pushed in most at the middle of that side, easing off toward the poles and the sides.
	const push = shape.indent * Math.max(0, toward) ** 1.5 * Math.exp(-((p[1] / 0.55) ** 2));
	return [p[0] * k - d[0] * push, y, p[2] * k - d[2] * push];
}

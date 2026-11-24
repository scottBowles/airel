<script lang="ts">
	// The asteroid belt: thousands of rocks along an arc, as a few instanced meshes (one per rock
	// shape). The belt orbits nothing (DM, Nov 2026), so the rocks stay put; each tumbles slowly.
	import { T, useTask } from '@threlte/core';
	import { onDestroy } from 'svelte';
	import * as THREE from 'three';
	import { mergeVertices } from 'three/examples/jsm/utils/BufferGeometryUtils.js';

	type Props = {
		/** Centre of the circle the arc lies on. */
		centre?: [number, number, number];
		/** Radius of that circle. */
		radius: number;
		/** The arc: start and end angle, radians, measured in the x–z plane from +x toward -z. */
		arc: [number, number];
		/** Spread across the belt (standard deviation, in the plane) and through it (vertical). */
		width: number;
		thickness: number;
		count: number;
		/** Rock sizes: smallest and largest radius. Sizes follow a power law, many more small. */
		size: [number, number];
		/** Share of pale icy rocks among the grey and brown. */
		icy?: number;
		/** Keep rocks away from these points (a body sitting in the belt, the camera). */
		clear?: { at: [number, number, number]; radius: number }[];
		/** Crowd rocks toward a point: they're this many times denser near it. */
		crowd?: { at: [number, number, number]; radius: number; factor: number };
		seed?: number;
	};
	let { centre = [0, 0, 0], radius, arc, width, thickness, count, size, icy = 0.2, clear, crowd, seed = 7 }: Props = $props();

	/** Small seeded PRNG (mulberry32), so the belt is the same on every load. */
	function rng(s: number) {
		return () => {
			s |= 0;
			s = (s + 0x6d2b79f5) | 0;
			let t = Math.imul(s ^ (s >>> 15), 1 | s);
			t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
			return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
		};
	}
	const gauss = (r: () => number) => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * Math.PI * r());

	/** A lumpy rock: an icosphere pushed in and out by a few random bumps, then squashed. */
	function rock(r: () => number) {
		const g = mergeVertices(new THREE.IcosahedronGeometry(1, 3));
		const pos = g.attributes.position;
		// Broad lobes, then a few craters: narrow dents with a slight raised rim.
		const bumps = [
			...Array.from({ length: 7 }, () => ({
				d: new THREE.Vector3(gauss(r), gauss(r), gauss(r)).normalize(),
				k: (r() - 0.45) * 0.5,
				w: 2 + r() * 5
			})),
			...Array.from({ length: 6 }, () => ({
				d: new THREE.Vector3(gauss(r), gauss(r), gauss(r)).normalize(),
				k: -0.06 - 0.08 * r(),
				w: 25 + r() * 60
			}))
		];
		const v = new THREE.Vector3();
		for (let i = 0; i < pos.count; i++) {
			v.fromBufferAttribute(pos, i);
			let s = 1;
			for (const b of bumps) s += b.k * Math.exp(-b.w * (1 - v.dot(b.d)));
			// Fine roughness, so a rock isn't smooth as a pebble.
			s += 0.05 * Math.sin(v.x * 7 + 1.7) * Math.sin(v.y * 9 + 0.3) * Math.sin(v.z * 6 + 2.1);
			s += 0.025 * Math.sin(v.x * 19 + 0.4) * Math.sin(v.y * 23 + 2.2) * Math.sin(v.z * 17 + 1.1);
			v.multiplyScalar(s);
			pos.setXYZ(i, v.x, v.y, v.z);
		}
		g.scale(1, 0.6 + 0.4 * r(), 0.7 + 0.3 * r());
		g.computeVertexNormals();
		return g;
	}

	// Fixed for the belt's lifetime.
	// svelte-ignore state_referenced_locally
	const r = rng(seed);
	const SHAPES = 6;
	const geometries = Array.from({ length: SHAPES }, () => rock(r));
	const material = new THREE.MeshStandardMaterial({ roughness: 0.95, metalness: 0, flatShading: true });

	type Rock = { pos: THREE.Vector3; scale: number; quat: THREE.Quaternion; axis: THREE.Vector3; spin: number };
	const rocks: Rock[][] = Array.from({ length: SHAPES }, () => []);
	const colours: THREE.Color[][] = Array.from({ length: SHAPES }, () => []);
	// svelte-ignore state_referenced_locally
	{
		const c = new THREE.Vector3(...centre);
		const holes = (clear ?? []).map((h) => ({ at: new THREE.Vector3(...h.at), radius: h.radius }));
		const dense = crowd && new THREE.Vector3(...crowd.at);
		const p = new THREE.Vector3();
		let placed = 0;
		for (let tries = 0; placed < count && tries < count * 20; tries++) {
			const a = arc[0] + (arc[1] - arc[0]) * r();
			const rr = radius + gauss(r) * width;
			p.set(c.x + rr * Math.cos(a), c.y + gauss(r) * thickness, c.z - rr * Math.sin(a));
			if (holes.some((h) => p.distanceTo(h.at) < h.radius)) continue;
			// Thin out away from the crowd point (rejection sampling), and toward the arc's ends.
			let keep = 1;
			if (dense) keep = (1 + (crowd!.factor - 1) * Math.exp(-((p.distanceTo(dense) / crowd!.radius) ** 2))) / crowd!.factor;
			const along = (a - arc[0]) / (arc[1] - arc[0]);
			keep *= Math.min(1, 6 * Math.min(along, 1 - along));
			if (r() > keep) continue;
			const u = r();
			const scale = Math.min(size[1], size[0] * (1 - u) ** -0.55);
			const shape = Math.floor(r() * SHAPES);
			rocks[shape].push({
				pos: p.clone(),
				scale,
				quat: new THREE.Quaternion().setFromEuler(new THREE.Euler(r() * 6.3, r() * 6.3, r() * 6.3)),
				axis: new THREE.Vector3(gauss(r), gauss(r), gauss(r)).normalize(),
				spin: (r() - 0.5) * 0.4
			});
			// Grey and brown rock, some pale icy bodies; darker small ones (dust-coated).
			const ice = r() < icy;
			// Asteroids are dark (most reflect 5–20% of light); the icy ones a pale blue-grey, not snow.
			const l = ice ? 0.36 + 0.14 * r() : 0.12 + 0.14 * r();
			const warm = ice ? -0.03 : 0.04 * r();
			colours[shape].push(new THREE.Color(l + warm, l, l - warm + (ice ? 0.05 : 0)));
			placed++;
		}
	}

	const meshes = geometries.map((g, i) => {
		const m = new THREE.InstancedMesh(g, material, Math.max(rocks[i].length, 1));
		m.count = rocks[i].length;
		colours[i].forEach((col, j) => m.setColorAt(j, col));
		m.frustumCulled = false;
		return m;
	});
	const matrix = new THREE.Matrix4();
	const turn = new THREE.Quaternion();
	const scl = new THREE.Vector3();
	function update(delta: number) {
		meshes.forEach((m, i) => {
			rocks[i].forEach((k, j) => {
				turn.setFromAxisAngle(k.axis, k.spin * delta);
				k.quat.premultiply(turn);
				matrix.compose(k.pos, k.quat, scl.setScalar(k.scale));
				m.setMatrixAt(j, matrix);
			});
			m.instanceMatrix.needsUpdate = true;
		});
	}
	update(0);
	useTask((delta) => update(delta));

	onDestroy(() => {
		meshes.forEach((m) => m.dispose());
		geometries.forEach((g) => g.dispose());
		material.dispose();
	});
</script>

{#each meshes as mesh, i (i)}
	<T is={mesh} />
{/each}

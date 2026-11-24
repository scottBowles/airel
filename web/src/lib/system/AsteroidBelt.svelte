<script lang="ts">
	// The asteroid belt: thousands of rocks along an arc, as a few instanced meshes (one per rock
	// shape). The belt orbits nothing (DM, Nov 2026), so the rocks stay put; each tumbles slowly.
	import { T, useTask, useThrelte } from '@threlte/core';
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
		/** Keep rocks away from these points (a body sitting in the belt, the camera). With
		 * `shield`, rocks between the camera and the point also shrink away, so none hides it. */
		clear?: { at: [number, number, number]; radius: number; shield?: boolean }[];
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

	/** Smooth 3D value noise, -1..1, and a few octaves of it: for a big rock's rough surface. */
	function hash(x: number, y: number, z: number) {
		const h = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453;
		return h - Math.floor(h);
	}
	function noise(x: number, y: number, z: number) {
		const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
		const f = (t: number) => t * t * (3 - 2 * t);
		const u = f(x - xi), v = f(y - yi), w = f(z - zi);
		const l = (a: number, b: number, t: number) => a + (b - a) * t;
		const c = (dx: number, dy: number, dz: number) => hash(xi + dx, yi + dy, zi + dz);
		return (
			2 *
				l(
					l(l(c(0, 0, 0), c(1, 0, 0), u), l(c(0, 1, 0), c(1, 1, 0), u), v),
					l(l(c(0, 0, 1), c(1, 0, 1), u), l(c(0, 1, 1), c(1, 1, 1), u), v),
					w
				) -
			1
		);
	}
	function fbm(x: number, y: number, z: number, octaves: number, gain = 0.5) {
		let sum = 0;
		let amp = 0.5;
		for (let o = 0; o < octaves; o++) {
			sum += amp * noise(x, y, z);
			x *= 2.1;
			y *= 2.1;
			z *= 2.1;
			amp *= gain;
		}
		return sum;
	}

	/**
	 * A rock shape, as real small asteroids are (Eros, Ida, Itokawa): lumpy potatoes with broad
	 * flattened sides and craters. Three tiers by size, because nearly every rock is a few pixels
	 * across and only a few are ever seen up close:
	 * - big (round 1): rounder, as larger bodies are; a fine mesh with rough noise at several
	 *   scales and many rimmed craters, so it isn't smooth up close;
	 * - mid: a medium mesh, lumpier;
	 * - small: a coarse mesh (a few hundred faces); they're specks.
	 */
	function rock(r: () => number, tier: 'big' | 'mid' | 'small') {
		const round = tier === 'big' ? 1 : 0;
		const g = mergeVertices(new THREE.IcosahedronGeometry(1, tier === 'big' ? 5 : tier === 'mid' ? 3 : 2));
		const pos = g.attributes.position;
		const dir = () => new THREE.Vector3(gauss(r), gauss(r), gauss(r)).normalize();
		const lobes = Array.from({ length: 7 }, () => ({ d: dir(), k: (r() - 0.45) * 1.1 * (1 - 0.6 * round), w: 2 + r() * 5 }));
		// Craters: a bowl and a raised rim, a few large and many small.
		const craters = Array.from({ length: tier === 'big' ? 40 : 12 }, (_, i) => ({
			d: dir(),
			k: -(0.03 + 0.06 * r()) * (i < 4 ? 1.6 : 1),
			w: i < 4 ? 6 + 8 * r() : 20 + r() * 90
		}));
		const cuts = Array.from({ length: (tier === 'big' ? 2 : 3) + Math.floor(r() * 3 * (1 - round)) }, () => ({ n: dir(), d: 0.65 + 0.25 * r() }));
		const off = r() * 100;
		const v = new THREE.Vector3();
		for (let i = 0; i < pos.count; i++) {
			v.fromBufferAttribute(pos, i);
			let s = 1;
			for (const b of lobes) s += b.k * Math.exp(-b.w * (1 - v.dot(b.d)));
			for (const c of craters) {
				const t = (1 - v.dot(c.d)) * c.w;
				s += c.k * (Math.exp(-t * 1.5) - 0.4 * Math.exp(-((t - 1.3) ** 2) * 2));
			}
			// Rough at every scale the mesh can hold: broad swells to fine grit.
			// Big rocks keep more of the fine octaves (higher gain), or they read smooth up close.
			s += (tier === 'big' ? 0.14 : 0.12) * fbm(v.x * 2.5 + off, v.y * 2.5, v.z * 2.5, tier === 'big' ? 7 : tier === 'mid' ? 4 : 2, tier === 'big' ? 0.68 : 0.5);
			v.multiplyScalar(s);
			// Broad flattened sides: planes press the rock most of the way flat. (Without them every
			// rock was a smooth egg; cut fully flat, with many planes, they were gravel chips.)
			for (const c of cuts) {
				const over = v.dot(c.n) - c.d;
				if (over > 0) v.addScaledVector(c.n, -over * 0.7);
			}
			pos.setXYZ(i, v.x, v.y, v.z);
		}
		// Squashed and stretched; now and then a long one or a peanut (two lobes touching).
		// Long ones are rarer among the small: a field of them read as scattered seeds.
		const kind = round > 0 ? 1 : r() * (tier === 'small' ? 1.6 : 1);
		if (kind < 0.2) g.scale(1.8, 0.6 + 0.3 * r(), 0.7 + 0.2 * r());
		else if (kind < 0.3) {
			for (let i = 0; i < pos.count; i++) {
				const x = pos.getX(i);
				pos.setX(i, x * 1.5);
				const pinch = 1 - 0.35 * Math.exp(-(x * x) * 6);
				pos.setY(i, pos.getY(i) * pinch);
				pos.setZ(i, pos.getZ(i) * pinch);
			}
		} else if (round > 0) g.scale(1, 0.8 + 0.15 * r(), 0.85 + 0.15 * r());
		else g.scale(1, (tier === 'small' ? 0.7 : 0.6) + 0.3 * r(), 0.75 + 0.25 * r());
		g.computeVertexNormals();
		return g;
	}

	// Fixed for the belt's lifetime.
	// svelte-ignore state_referenced_locally
	const r = rng(seed);
	// Shapes per tier. A rock's tier follows its size: big above half the largest size (a few
	// dozen rocks), mid above a sixth (a few hundred), small for the rest (thousands). With 12,000
	// rocks that's ~3M vertices a frame, against ~30M when every rock used the fine mesh.
	const TIERS = { big: 4, mid: 6, small: 4 } as const;
	const tierOf: ('big' | 'mid' | 'small')[] = (['big', 'mid', 'small'] as const).flatMap((t) => Array(TIERS[t]).fill(t));
	const SHAPES = tierOf.length;
	const first = { big: 0, mid: TIERS.big, small: TIERS.big + TIERS.mid };
	const geometries = tierOf.map((t) => rock(r, t));
	/** A tiling noise texture for a bump map: grit, knobs and small pits finer than any rock's mesh
	 * can hold, at no cost in vertices. Octaves of value noise on a periodic lattice, so it tiles. */
	function grit(size = 256) {
		const data = new Uint8Array(size * size * 4);
		const lattice = (n: number) => Array.from({ length: n * n }, () => r());
		const octaves = [8, 16, 32, 64].map((n) => ({ n, v: lattice(n) }));
		for (let y = 0; y < size; y++)
			for (let x = 0; x < size; x++) {
				let h = 0;
				let amp = 0.5;
				for (const { n, v } of octaves) {
					const fx = (x / size) * n, fy = (y / size) * n;
					const x0 = Math.floor(fx), y0 = Math.floor(fy);
					const tx = fx - x0, ty = fy - y0;
					const sx = tx * tx * (3 - 2 * tx), sy = ty * ty * (3 - 2 * ty);
					const at = (i: number, j: number) => v[((j + n) % n) * n + ((i + n) % n)];
					const a = at(x0, y0) + (at(x0 + 1, y0) - at(x0, y0)) * sx;
					const b = at(x0, y0 + 1) + (at(x0 + 1, y0 + 1) - at(x0, y0 + 1)) * sx;
					h += amp * (a + (b - a) * sy);
					amp *= 0.6;
				}
				const k = Math.round(Math.min(Math.max(h / 1.1, 0), 1) * 255);
				data.set([k, k, k, 255], (y * size + x) * 4);
			}
		const t = new THREE.DataTexture(data, size, size);
		t.wrapS = t.wrapT = THREE.RepeatWrapping;
		t.repeat.set(2, 1);
		t.magFilter = THREE.LinearFilter;
		t.minFilter = THREE.LinearMipmapLinearFilter;
		t.generateMipmaps = true;
		t.needsUpdate = true;
		return t;
	}
	const bump = grit();
	const material = new THREE.MeshStandardMaterial({ roughness: 0.95, metalness: 0, bumpMap: bump, bumpScale: 3 });

	// svelte-ignore state_referenced_locally
	const holes = (clear ?? []).map((h) => ({ at: new THREE.Vector3(...h.at), radius: h.radius, shield: !!h.shield }));
	type Rock = { pos: THREE.Vector3; scale: number; quat: THREE.Quaternion; axis: THREE.Vector3; spin: number };
	const rocks: Rock[][] = Array.from({ length: SHAPES }, () => []);
	const colours: THREE.Color[][] = Array.from({ length: SHAPES }, () => []);
	// svelte-ignore state_referenced_locally
	{
		const c = new THREE.Vector3(...centre);
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
			const tier = scale > 0.5 * size[1] ? 'big' : scale > size[1] / 6 ? 'mid' : 'small';
			const shape = first[tier] + Math.floor(r() * TIERS[tier]);
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
			// One range, cool dark grey to grey-brown; icy ones only a little paler and bluer.
			const l = ice ? 0.1 + 0.05 * r() : 0.04 + 0.09 * r();
			// Slightly cool, as the warm sun tints neutral grey toward tan.
			const warm = ice ? -0.012 : -0.012 + 0.015 * r();
			colours[shape].push(new THREE.Color(l + warm, l, l - warm + (ice ? 0.015 : 0)));
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
	const { camera } = useThrelte();
	const matrix = new THREE.Matrix4();
	const world = new THREE.Vector3();
	const toBody = new THREE.Vector3();
	const toRock = new THREE.Vector3();
	const turn = new THREE.Quaternion();
	const scl = new THREE.Vector3();
	function update(delta: number) {
		meshes.forEach((m, i) => {
			rocks[i].forEach((k, j) => {
				turn.setFromAxisAngle(k.axis, k.spin * delta);
				k.quat.premultiply(turn);
				// Rocks shrink away as the camera comes close, so none ever fills the view.
				world.copy(k.pos);
				let near = Math.min(Math.max((camera.current.position.distanceTo(world) - 0.6) / 1.2, 0), 1);
				// And rocks between the camera and a body in the belt, so none hides it.
				for (const h of holes) {
					if (!h.shield) continue;
					toBody.copy(h.at).sub(camera.current.position);
					const len = toBody.length();
					toBody.divideScalar(len);
					toRock.copy(world).sub(camera.current.position);
					const t = toRock.dot(toBody);
					if (t > 0 && t < len) {
						const off = toRock.addScaledVector(toBody, -t).length() / (h.radius * (t / len));
						near = Math.min(near, Math.min(Math.max((off - 0.9) / 0.3, 0), 1));
					}
				}
				matrix.compose(k.pos, k.quat, scl.setScalar(k.scale * near * near * (3 - 2 * near)));
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
		bump.dispose();
	});
</script>

{#each meshes as mesh, i (i)}
	<T is={mesh} />
{/each}

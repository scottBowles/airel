<script lang="ts">
	import { T, useTask, useThrelte } from '@threlte/core';
	import { HTML } from '@threlte/extras';
	import { onDestroy } from 'svelte';
	import * as THREE from 'three';
	import { atmosphereMaterial, type AtmosphereLook } from './atmosphere';
	import { addEmissiveFlicker } from './emissiveFlicker';
	import { latLonToVector, shapePoint, type Pin, type Shape } from './geo';
	import { layoutLabels, type Placement } from './labels';

	type Props = {
		/** Folder under /system/ holding albedo, normal, roughness, emissive (from tools/planets). */
		slug: string;
		radius?: number;
		position?: [number, number, number];
		/** Multiplier for the emissive map (lava, city lights). */
		glow?: number;
		/**
		 * Metalness, 0..1 (default 0). A little makes glossy parts of the roughness map shine with
		 * a broad sun highlight (glass and metal in a city), which plain dielectric barely shows.
		 */
		metalness?: number;
		/** Turns per second about the planet's axis. */
		spin?: number;
		/** Longitude (degrees) that starts out facing +z, towards the default camera. */
		face?: number;
		/** How much the glow pulses and shimmers, 0 (steady) … 1 (lava). */
		flicker?: number;
		pins?: Pin[];
		onpin?: (pin: Pin) => void;
		/**
		 * A cloud layer from clouds.webp (white where cloudy), drifting slowly over the ground. It
		 * thins as the camera comes close, to `near` × its opacity, so places can be seen.
		 */
		clouds?: {
			color?: [number, number, number];
			opacity?: number;
			drift?: number;
			near?: number;
			/** Shade the cloud tops with clouds-normal.webp. */
			normal?: boolean;
			/** How dark the clouds' shadows on the ground are, 0..1 (default 0.6). */
			shadow?: number;
			/**
			 * Lights glowing up through the cloud at night, from clouds-glow.webp (the ground's
			 * lights blurred, as fog scatters them): its brightness. Only for a layer that doesn't
			 * drift, as the glow is mapped on the cloud mesh.
			 */
			glow?: number;
			/** Lightning flashing inside thick cloud: its brightness (0 or unset for none). */
			lightning?: number;
		};
		/** A glow around the rim, lit from `sun`. */
		atmosphere?: AtmosphereLook;
		/** World position of the light that lights the atmosphere. */
		sun?: [number, number, number];
		/** The glow is city lights: show it only on the night side (away from `sun`). */
		nightLights?: boolean;
		/** 0..1: up close, break the glow into points of light finer than the map (cities). */
		detail?: number;
		/** Dusk light spilling past the terminator: strength (0 for none) and colour. */
		twilight?: { strength: number; color?: [number, number, number] };
		/** A non-spherical body (Didymus Prime's kidney bean). */
		shape?: Shape;
		/** Load the small maps (made by tools/planets/far_maps.py): for a body seen from afar. */
		far?: boolean;
	};
	let {
		slug,
		radius = 1,
		position = [0, 0, 0],
		glow = 1.5,
		metalness = 0,
		spin = 0,
		face = -90,
		flicker = 0,
		pins = [],
		onpin,
		clouds,
		atmosphere,
		sun = [0, 0, 0],
		nightLights = false,
		detail = 0,
		twilight,
		shape,
		far = false
	}: Props = $props();

	/** A unit sphere, or the shaped body, with normals worked out from the shape itself (not
	 * from the mesh, which would leave a seam where the sphere's texture wraps). */
	function body(segments: number, rings: number, grow = 1) {
		const g = new THREE.SphereGeometry(1, segments, rings);
		if (!shape) return g;
		const pos = g.attributes.position;
		const nrm = g.attributes.normal;
		const at = (v: THREE.Vector3) => new THREE.Vector3(...shapePoint([v.x, v.y, v.z], shape)).multiplyScalar(grow);
		const u = new THREE.Vector3();
		const e = new THREE.Vector3();
		const n = new THREE.Vector3();
		const eps = 1e-3;
		for (let i = 0; i < pos.count; i++) {
			u.fromBufferAttribute(pos, i).normalize();
			const p = at(u);
			pos.setXYZ(i, p.x, p.y, p.z);
			// Tangents east and north of the point, through the shape.
			e.set(-u.z, 0, u.x);
			if (e.lengthSq() < 1e-8) {
				nrm.setXYZ(i, 0, Math.sign(u.y), 0);
				continue;
			}
			e.normalize();
			n.crossVectors(u, e).normalize();
			const de = at(u.clone().addScaledVector(e, eps).normalize()).sub(at(u.clone().addScaledVector(e, -eps).normalize()));
			const dn = at(u.clone().addScaledVector(n, eps).normalize()).sub(at(u.clone().addScaledVector(n, -eps).normalize()));
			const out = new THREE.Vector3().crossVectors(de, dn).normalize();
			if (out.dot(p) < 0) out.negate();
			nrm.setXYZ(i, out.x, out.y, out.z);
		}
		pos.needsUpdate = true;
		nrm.needsUpdate = true;
		return g;
	}
	/** Where a place sits on the surface (local coordinates, before `radius`). */
	function surface(lat: number, lon: number): [number, number, number] {
		const p = latLonToVector(lat, lon);
		return shape ? shapePoint(p, shape) : p;
	}
	// svelte-ignore state_referenced_locally
	const groundGeometry = body(128, 64);
	// svelte-ignore state_referenced_locally
	const cloudGeometry = body(128, 64);
	// svelte-ignore state_referenced_locally
	const airGeometry = body(96, 48);

	const loader = new THREE.TextureLoader();
	// The maps are fixed for the planet's lifetime: to switch to or from the small ones, re-create it.
	function load(file: string, srgb: boolean) {
		const tex = loader.load(`/system/${slug}/${far ? 'far/' : ''}${file}`);
		tex.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
		tex.anisotropy = 8;
		return tex;
	}
	// The planet's textures don't change while it's shown, so they load once.
	// svelte-ignore state_referenced_locally
	const material = new THREE.MeshStandardMaterial({
		map: load('albedo.webp', true),
		normalMap: load('normal.webp', false),
		roughnessMap: load('roughness.webp', false),
		emissiveMap: load('emissive.webp', true),
		emissive: new THREE.Color(1, 1, 1),
		metalness
	});
	// svelte-ignore state_referenced_locally
	const live = addEmissiveFlicker(material, flicker);
	$effect(() => {
		material.emissiveIntensity = glow;
		live.uniforms.uAmount.value = flicker;
		live.uniforms.uNightOnly.value = nightLights ? 1 : 0;
		live.uniforms.uDetail.value = detail;
		live.uniforms.uTwilight.value = twilight?.strength ?? 0;
		if (twilight?.color) live.uniforms.uTwilightColor.value.setRGB(...twilight.color);
		live.uniforms.uSun.value.set(...sun);
	});

	// Optional layers, also fixed for the planet's lifetime.
	// svelte-ignore state_referenced_locally
	const cloudMaterial = clouds
		? new THREE.MeshStandardMaterial({
				color: new THREE.Color(...(clouds.color ?? [1, 1, 1])),
				alphaMap: load('clouds.webp', false),
				normalMap: clouds.normal ? load('clouds-normal.webp', false) : null,
				transparent: true,
				opacity: clouds.opacity ?? 0.9,
				depthWrite: false,
				roughness: 1,
				metalness: 0,
				...(clouds.glow
					? { emissiveMap: load('clouds-glow.webp', true), emissive: new THREE.Color(1, 0.78, 0.55), emissiveIntensity: clouds.glow }
					: {})
			})
		: null;
	if (cloudMaterial) live.uniforms.uCloudMap.value = cloudMaterial.alphaMap;
	// The glow through the cloud shows on the night side only, as the lights below do.
	const cloudLive = cloudMaterial && (clouds?.glow || clouds?.lightning) ? addEmissiveFlicker(cloudMaterial, 0) : null;
	if (cloudLive) {
		cloudLive.uniforms.uLightning.value = clouds?.lightning ?? 0;
		cloudLive.uniforms.uNightOnly.value = 1;
		// Lit mist outshines the glow from below: it comes on only well past the terminator.
		cloudLive.uniforms.uDusk.value = 0.15;
	}
	$effect(() => {
		cloudLive?.uniforms.uSun.value.set(...sun);
	});
	const sunPosition = new THREE.Vector3();
	// svelte-ignore state_referenced_locally
	const airMaterial = atmosphere ? atmosphereMaterial(atmosphere, sunPosition) : null;
	$effect(() => {
		sunPosition.set(...sun);
	});

	let group = $state<THREE.Group>();
	let cloudMesh = $state<THREE.Mesh>();
	let ground = $state<THREE.Mesh>();
	const { camera, size } = useThrelte();

	// A pin shows only while it's on the side of the planet facing the camera, and its label sits
	// wherever on screen it overlaps no other label or dot (or hides, until its dot is hovered).
	let facing = $state<boolean[]>([]);
	let placements = $state<Placement[]>([]);
	let widths = $state<number[]>([]);
	const LABEL_H = 13;
	const screen = new THREE.Vector3();
	const labelOf = (pin: Pin) => pin.name.split(' — ')[0].split(',')[0];
	const world = new THREE.Vector3();
	const normal = new THREE.Vector3();
	const toCamera = new THREE.Vector3();
	const centre = new THREE.Vector3();
	useTask((delta) => {
		if (!group) return;
		group.rotation.y += spin * Math.PI * 2 * delta;
		if (cloudMesh && cloudMaterial) {
			cloudMesh.rotation.y += (clouds?.drift ?? 0.002) * Math.PI * 2 * delta;
			// Full cover from afar (5 radii out), thinning to `near` close in (2 radii).
			group.getWorldPosition(centre);
			const d = camera.current.position.distanceTo(centre) / radius;
			const t = Math.min(Math.max((d - 2) / 3, 0), 1);
			const near = clouds?.near ?? 0.4;
			cloudMaterial.opacity = (clouds?.opacity ?? 0.9) * (near + (1 - near) * t * t * (3 - 2 * t));
			// Shadows on the ground, from where the sun is now and how far the clouds have drifted.
			if (ground) {
				live.uniforms.uSunLocal.value.copy(sunPosition);
				ground.worldToLocal(live.uniforms.uSunLocal.value);
				live.uniforms.uCloudTurn.value = cloudMesh.rotation.y;
				// Full strength even when the clouds thin close in: the shadows then show where they are.
					live.uniforms.uShadow.value = (clouds?.shadow ?? 0.6) * (clouds?.opacity ?? 0.9);
			}
		}
		live.uniforms.uTime.value += delta;
		if (cloudLive) cloudLive.uniforms.uTime.value += delta;
		if (!pins.length) return;
		const { width, height } = size.current;
		const at = pins.map((pin) => {
			normal.set(...latLonToVector(pin.lat, pin.lon));
			world.set(...surface(pin.lat, pin.lon)).multiplyScalar(radius * 1.01);
			group!.localToWorld(world);
			normal.transformDirection(group!.matrixWorld);
			toCamera.copy(camera.current.position).sub(world).normalize();
			screen.copy(world).project(camera.current);
			return {
				facing: normal.dot(toCamera) > 0.3,
				x: ((screen.x + 1) / 2) * width,
				y: ((1 - screen.y) / 2) * height
			};
		});
		const next = at.map((a) => a.facing);
		if (next.some((v, i) => v !== facing[i])) facing = next;
		const shown = pins.map((_, i) => i).filter((i) => next[i]);
		const laid = layoutLabels(
			shown.map((i) => ({ x: at[i].x, y: at[i].y, w: widths[i] || labelOf(pins[i]).length * 7, h: LABEL_H }))
		);
		const all: Placement[] = pins.map(() => null);
		shown.forEach((i, k) => (all[i] = laid[k]));
		const same = (a: Placement, b: Placement | undefined) => (a && b ? a.dx === b.dx && a.dy === b.dy : a === b);
		if (all.length !== placements.length || all.some((p, i) => !same(p, placements[i]))) placements = all;
	});

	onDestroy(() => {
		for (const t of [material.map, material.normalMap, material.roughnessMap, material.emissiveMap])
			t?.dispose();
		material.dispose();
		cloudMaterial?.alphaMap?.dispose();
		cloudMaterial?.normalMap?.dispose();
		cloudMaterial?.emissiveMap?.dispose();
		cloudMaterial?.dispose();
		airMaterial?.dispose();
		groundGeometry.dispose();
		cloudGeometry.dispose();
		airGeometry.dispose();
	});
</script>

<T.Group bind:ref={group} {position} rotation.y={(-(face + 90) * Math.PI) / 180}>
	<T.Mesh bind:ref={ground} scale={radius} {material} geometry={groundGeometry} />
	{#if cloudMaterial}
		<T.Mesh bind:ref={cloudMesh} scale={radius * 1.006} material={cloudMaterial} geometry={cloudGeometry} />
	{/if}
	{#if airMaterial}
		<T.Mesh scale={radius * (atmosphere?.height ?? 1.035)} material={airMaterial} geometry={airGeometry} />
	{/if}
	{#each pins as pin, i (pin.name)}
		{#if facing[i]}
			<HTML position={surface(pin.lat, pin.lon).map((c) => c * radius * 1.01) as [number, number, number]} center zIndexRange={[10, 0]}>
				<div class="pin pin-{pin.confidence}">
					<button class="dot" aria-label={labelOf(pin)} onclick={() => onpin?.(pin)}></button>
					<button
						class="label"
						class:hidden={!placements[i]}
						style:left="{placements[i]?.dx ?? 9}px"
						style:top="{placements[i]?.dy ?? -LABEL_H / 2}px"
						bind:clientWidth={widths[i]}
						onclick={() => onpin?.(pin)}>{labelOf(pin)}</button
					>
				</div>
			</HTML>
		{/if}
	{/each}
</T.Group>

<style>
	.pin {
		position: relative;
		width: 7px;
		height: 7px;
		font: 500 11px/13px var(--font-mono, ui-monospace, monospace);
		color: #ffe9c7;
		text-shadow: 0 0 3px #000, 0 0 6px #000;
	}
	.pin button {
		background: none;
		border: 0;
		padding: 0;
		font: inherit;
		color: inherit;
		text-shadow: inherit;
		cursor: pointer;
	}
	.pin .dot {
		display: block;
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: currentColor;
		box-shadow: 0 0 0 1.5px #000;
	}
	.label {
		position: absolute;
		white-space: nowrap;
		height: 13px;
	}
	/* No room beside its dot: hidden (but still measured) until the dot is hovered. */
	.label.hidden {
		visibility: hidden;
	}
	.pin:hover .label {
		visibility: visible;
		z-index: 1;
	}
	.pin-lore {
		color: #9dffb0;
	}
	.pin-layout {
		color: #ffe07a;
	}
	.pin-guess {
		color: #ff9ee0;
	}
	.pin:hover {
		color: #fff;
	}
</style>

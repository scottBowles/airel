<script lang="ts">
	// The whole system: both suns, the planets on their orbits, the belt with Hielo, Chromium on
	// its figure-eight. Each body has a label to click; clicking flies the camera to it and follows
	// it round its orbit. Layout and speeds are in layout.ts.
	import { T, useTask } from '@threlte/core';
	import { HTML, OrbitControls, Stars } from '@threlte/extras';
	import { onDestroy } from 'svelte';
	import * as THREE from 'three';
	import type { OrbitControls as Controls } from 'three/examples/jsm/controls/OrbitControls.js';
	import AsteroidBelt from './AsteroidBelt.svelte';
	import { CHROMIUM, DIDYMUS, DIDYMUS_PRIME, GONHIRRIM_MOONS, HIELO, HYANG_WAN_MOON, type BodyLook } from './bodies';
	import type { Pin } from './geo';
	import {
		BELT,
		CHROMIUM_PERIOD,
		figureEight,
		HIELO_AT,
		PLANETS,
		period,
		D,
		RED_AT,
		SIZE,
		SUN_RADIUS,
		YELLOW_AT,
		type Vec3
	} from './layout';
	import Orbit from './Orbit.svelte';
	import Planet from './Planet.svelte';
	import Sun from './Sun.svelte';
	import { RED_SUN, YELLOW_SUN } from './sunShader';

	type Props = {
		/** How fast time runs: 1 normal, 0 paused. */
		rate?: number;
		/** The body the camera follows (its slug), or null for the overview. */
		focus?: string | null;
		showPins?: boolean;
		onpin?: (pin: Pin) => void;
	};
	let { rate = 1, focus = $bindable(null), showPins = true, onpin }: Props = $props();

	const MOONS = Object.entries(GONHIRRIM_MOONS);
	const SUN_REACH = 0.7 * D;
	const sunAt = (s: 'yellow' | 'red') => (s === 'yellow' ? YELLOW_AT : RED_AT);

	/** Planet props from a body's look, at the system view's size. */
	const looks = (l: BodyLook, size = SIZE) => ({
		radius: l.radius * size,
		glow: l.glow ?? 1,
		flicker: l.flicker ?? 0,
		metalness: l.metalness ?? 0,
		clouds: l.clouds,
		atmosphere: l.atmosphere,
		twilight: l.twilight
	});

	/** How big each focusable body is, for how close the camera comes. */
	const RADIUS: Record<string, number> = {
		yellow: SUN_RADIUS,
		red: SUN_RADIUS,
		chromium: CHROMIUM.radius * SIZE,
		hielo: HIELO.radius * SIZE,
		didymus: 2.2 * SIZE,
		gonhirrim: 4,
		'hyang-wan-moon': HYANG_WAN_MOON.radius * SIZE,
		...Object.fromEntries(PLANETS.map((p) => [p.slug, p.look.radius * (p.slug === 'gonhirrim' ? 1 : SIZE)])),
		...Object.fromEntries(MOONS.map(([slug, m]) => [slug, m.radius]))
	};
	/** Moons get labels only while their planet (or one of them) is in focus. */
	const inGonhirrim = $derived(focus === 'gonhirrim' || MOONS.some(([s]) => s === focus));

	// Each focusable body's group, to follow it.
	const refs: Record<string, THREE.Group | undefined> = $state({});

	// Places on the body in focus (Didymus: Prime's).
	let pins = $state<Pin[]>([]);
	$effect(() => {
		pins = [];
		const slug = focus === 'didymus' ? 'didymus-prime' : focus;
		if (!slug || slug === 'yellow' || slug === 'red') return;
		fetch(`/system/${slug}/pins.json`)
			.then((r) => (r.ok ? r.json() : { pins: [] }))
			.then((d) => {
				const now = focus === 'didymus' ? 'didymus-prime' : focus;
				if (slug === now) pins = d.pins;
			});
	});
	const pinsFor = (slug: string) => (showPins && (focus === slug || (focus === 'didymus' && slug === 'didymus-prime')) ? pins : []);
	const far = (slug: string) => focus !== slug && !(focus === 'didymus' && slug === 'didymus-prime');

	// Chromium runs its figure-eight; its "sun" (for the night side) is whichever is nearer.
	let chromium = $state<THREE.Group>();
	let chromiumSun = $state<Vec3>(YELLOW_AT);
	let s = 0.4;
	const chromiumPath = (() => {
		const pts: THREE.Vector3[] = [];
		for (let i = 0; i <= 400; i++) pts.push(new THREE.Vector3(...figureEight((i / 400) * Math.PI * 2)));
		return new THREE.BufferGeometry().setFromPoints(pts);
	})();
	const circle = (r: number) => {
		const pts: THREE.Vector3[] = [];
		for (let i = 0; i < 256; i++) pts.push(new THREE.Vector3(r * Math.cos((i / 256) * Math.PI * 2), 0, r * Math.sin((i / 256) * Math.PI * 2)));
		return new THREE.BufferGeometry().setFromPoints(pts);
	};
	const rings = PLANETS.map((p) => circle(p.distance * D));
	const line = (color: number, opacity: number) =>
		new THREE.LineBasicMaterial({ color, transparent: true, opacity, depthWrite: false });
	const yellowLine = line(0xe8c070, 0.2);
	const redLine = line(0xe07060, 0.2);
	const chromiumLine = line(0x9a90d0, 0.16);

	// --- Camera: an overview, or flying to and following a body ---------------------------
	const HOME_CAM = new THREE.Vector3(0, 230, 300);
	const HOME_TARGET = new THREE.Vector3(0, 0, 0);
	let controls = $state<Controls>();
	let camera = $state<THREE.PerspectiveCamera>();
	let blend = 1;
	const startCam = new THREE.Vector3();
	const startTarget = new THREE.Vector3();
	const goal = new THREE.Vector3();
	const last = new THREE.Vector3();
	const goalCam = new THREE.Vector3();
	$effect(() => {
		void focus;
		if (!camera || !controls) return;
		startCam.copy(camera.position);
		startTarget.copy(controls.target);
		blend = 0;
	});
	useTask((delta) => {
		s += ((Math.PI * 2) / CHROMIUM_PERIOD) * delta * rate;
		if (chromium) {
			chromium.position.set(...figureEight(s));
			const nearer = chromium.position.x < 0 ? YELLOW_AT : RED_AT;
			if (nearer !== chromiumSun) chromiumSun = nearer;
		}
		if (!camera || !controls) return;
		const body = focus ? refs[focus] : null;
		if (body) body.getWorldPosition(goal);
		else goal.copy(HOME_TARGET);
		if (blend < 1) {
			blend = Math.min(1, blend + delta / 1.8);
			const e = blend * blend * (3 - 2 * blend);
			if (body) {
				// Come in from where we are, to a few radii out.
				goalCam.copy(startCam).sub(goal).normalize().multiplyScalar(RADIUS[focus!] * 5).add(goal);
			} else goalCam.copy(HOME_CAM);
			camera.position.lerpVectors(startCam, goalCam, e);
			controls.target.lerpVectors(startTarget, goal, e);
		} else if (body) {
			// Ride along: move with the body, keeping whatever angle the user has turned to.
			camera.position.add(last.clone().sub(goal).negate());
			controls.target.copy(goal);
		}
		last.copy(goal);
		hideLabels();
	});

	// Labels hidden: the followed body's own (it's in plain view) and any behind it.
	let hidden = $state<string[]>([]);
	const labelAt = new THREE.Vector3();
	const toLabel = new THREE.Vector3();
	const toGoal = new THREE.Vector3();
	function hideLabels() {
		if (!camera) return;
		const next: string[] = [];
		if (focus && refs[focus]) {
			next.push(focus);
			toGoal.copy(goal).sub(camera.position);
			const dist = toGoal.length();
			toGoal.divideScalar(dist);
			for (const [slug, obj] of Object.entries(refs)) {
				if (!obj || slug === focus) continue;
				obj.getWorldPosition(labelAt);
				toLabel.copy(labelAt).sub(camera.position);
				const along = toLabel.dot(toGoal);
				if (along < dist) continue;
				// Behind the body: inside its disc as seen from the camera.
				const off = toLabel.addScaledVector(toGoal, -along).length() * (dist / along);
				if (off < RADIUS[focus] * 1.1) next.push(slug);
			}
		}
		if (next.join() !== hidden.join()) hidden = next;
	}

	function onkeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') focus = null;
	}

	onDestroy(() => {
		chromiumPath.dispose();
		rings.forEach((r) => r.dispose());
		[yellowLine, redLine, chromiumLine].forEach((m) => m.dispose());
	});
</script>

<svelte:window {onkeydown} />

{#snippet label(slug: string, name: string, kind = 'planet')}
	<HTML center zIndexRange={[20, 0]}>
		<button class="tag tag-{kind}" class:on={focus === slug} class:gone={hidden.includes(slug)} onclick={() => (focus = slug)}>
			<span class="ring"></span><span class="name">{name}</span>
		</button>
	</HTML>
{/snippet}

<T.PerspectiveCamera bind:ref={camera} makeDefault position={HOME_CAM.toArray()} fov={45} near={0.05} far={8000}>
	<OrbitControls
		bind:ref={controls}
		enableDamping
		minDistance={focus ? RADIUS[focus] * 1.3 : 20}
		maxDistance={1200}
	/>
</T.PerspectiveCamera>
<Stars count={6000} radius={2500} depth={400} />
<T.AmbientLight intensity={0.05} />

<!-- The suns: each light fades out before it reaches the other sun's inner planets, so a planet
     is lit mostly by its own sun; those between the suns catch some of both. -->
<T.Group bind:ref={refs.yellow} position={YELLOW_AT}>
	<Sun look={YELLOW_SUN} radius={SUN_RADIUS} intensity={1.6} reach={SUN_REACH} />
	{@render label('yellow', 'The Yellow Sun', 'sun')}
</T.Group>
<T.Group bind:ref={refs.red} position={RED_AT}>
	<Sun look={RED_SUN} radius={SUN_RADIUS} intensity={1.6} reach={SUN_REACH} />
	{@render label('red', 'The Red Sun', 'sun')}
</T.Group>

{#each PLANETS as p, i (p.slug)}
	{@const sun = sunAt(p.sun)}
	<Orbit position={sun} period={period(p.distance)} phase={(p.phase * Math.PI) / 180} tilt={p.tilt} {rate}>
		<T.LineLoop geometry={rings[i]} material={p.sun === 'yellow' ? yellowLine : redLine} />
		<T.Group bind:ref={refs[p.slug]} position={[p.distance * D, 0, 0]}>
			{#if p.slug === 'didymus'}
				<!-- The twins circle each other, each keeping its break face to the other. -->
				<Orbit period={200} {rate}>
					{#key far('didymus-prime')}
						<Planet
							slug="didymus-prime"
							far={far('didymus-prime')}
							position={[-0.75 * SIZE, 0, 0]}
							{...looks(DIDYMUS_PRIME)}
							shape={DIDYMUS_PRIME.shape}
							nightLights
							{sun}
							face={90}
							pins={pinsFor('didymus-prime')}
							{onpin}
						/>
					{/key}
					{#key far('didymus')}
						<Planet slug="didymus" far={far('didymus')} position={[1.05 * SIZE, 0, 0]} {...looks(DIDYMUS)} nightLights {sun} face={-90} />
					{/key}
				</Orbit>
			{:else if p.slug === 'gonhirrim'}
				{#key far('gonhirrim')}
					<Planet slug="gonhirrim" far={far('gonhirrim')} {...looks(p.look, 1)} {sun} face={40} spin={0.006} />
				{/key}
				{#each MOONS as [slug, m] (slug)}
					<Orbit period={m.orbit!.period} phase={m.orbit!.phase} tilt={m.orbit!.tilt} {rate}>
						<T.Group bind:ref={refs[slug]} position={[m.orbit!.distance, 0, 0]}>
							{#key far(slug)}
								<Planet {slug} far={far(slug)} {...looks(m, 1)} nightLights {sun} face={90} pins={pinsFor(slug)} {onpin} />
							{/key}
							{#if inGonhirrim}{@render label(slug, m.name, 'moon')}{/if}
						</T.Group>
					</Orbit>
				{/each}
			{:else}
				{#key far(p.slug)}
					<Planet
						slug={p.slug}
						far={far(p.slug)}
						{...looks(p.look)}
						nightLights={p.nightLights}
						detail={focus === p.slug && (p.slug === 'terran' || p.slug === 'genussa') ? 1 : 0}
						{sun}
						face={p.tidal ? 90 : 0}
						spin={p.tidal ? 0 : 0.003}
						pins={pinsFor(p.slug)}
						{onpin}
					/>
				{/key}
				{#if p.slug === 'hyang-wan'}
					<Orbit period={HYANG_WAN_MOON.orbit!.period} phase={HYANG_WAN_MOON.orbit!.phase} tilt={HYANG_WAN_MOON.orbit!.tilt} {rate}>
						<T.Group bind:ref={refs['hyang-wan-moon']} position={[HYANG_WAN_MOON.orbit!.distance * SIZE, 0, 0]}>
							<Planet slug="hyang-wan-moon" far {...looks(HYANG_WAN_MOON)} face={90} {sun} />
						</T.Group>
					</Orbit>
				{/if}
			{/if}
			{@render label(p.slug, p.slug === 'didymus' ? 'Didymus' : p.look.name)}
		</T.Group>
	</Orbit>
{/each}

<!-- Chromium, the dark planet, on its figure-eight round both suns. -->
<T.LineLoop geometry={chromiumPath} material={chromiumLine} />
<T.Group bind:ref={chromium}>
	<T.Group bind:ref={refs.chromium}>
		{#key far('chromium')}
			<Planet slug="chromium" far={far('chromium')} {...looks(CHROMIUM)} sun={chromiumSun} spin={0.003} />
		{/key}
		{@render label('chromium', 'Chromium')}
	</T.Group>
</T.Group>

<!-- The belt, between the suns and nearer the Yellow one, with Hielo in it. It orbits nothing. -->
<T.Group bind:ref={refs.hielo} position={HIELO_AT}>
	{#key far('hielo')}
		<Planet slug="hielo" far={far('hielo')} {...looks(HIELO)} nightLights sun={YELLOW_AT} face={-160} spin={0.002} />
	{/key}
	{@render label('hielo', 'Hielo')}
</T.Group>
<AsteroidBelt
	centre={YELLOW_AT}
	radius={BELT.radius}
	arc={BELT.arc}
	width={BELT.width}
	thickness={BELT.thickness}
	count={9000}
	size={[0.02, 0.3]}
	dust={5000}
	clear={[{ at: HIELO_AT, radius: 3, shield: true }]}
	crowd={{ at: HIELO_AT, radius: 20, factor: 2 }}
/>

<style>
	.tag {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 0;
		border: 0;
		background: none;
		color: #e8e4d8;
		font: 500 11px/1 var(--font-mono, ui-monospace, monospace);
		text-shadow: 0 0 3px #000, 0 0 6px #000;
		cursor: pointer;
		white-space: nowrap;
		/* The ring sits on the body; the name hangs to its right. */
		transform: translateX(calc(50% - 9px));
		opacity: 0.85;
	}
	.tag:hover,
	.tag.on {
		opacity: 1;
		color: #ffd58a;
	}
	.ring {
		width: 18px;
		height: 18px;
		border-radius: 50%;
		border: 1px solid currentColor;
		opacity: 0.55;
		flex: none;
	}
	.tag-sun .ring {
		width: 18px;
		opacity: 0;
	}
	.tag-moon {
		font-size: 10px;
		opacity: 0.7;
	}
	.tag-moon .ring {
		width: 10px;
		height: 10px;
	}
	.tag.on .ring {
		opacity: 0;
	}
	.tag.gone {
		visibility: hidden;
	}
</style>

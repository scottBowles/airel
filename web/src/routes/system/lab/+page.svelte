<script lang="ts">
	// A workbench for the solar-system models: look at each sun and planet on its own.
	import { Canvas, T } from '@threlte/core';
	import { NeutralToneMapping } from 'three';
	import { OrbitControls, Stars } from '@threlte/extras';
	import { GONHIRRIM, GONHIRRIM_MOONS, HYANG_WAN, HYANG_WAN_MOON } from '$lib/system/bodies';
	import Orbit from '$lib/system/Orbit.svelte';
	import Planet from '$lib/system/Planet.svelte';
	import Sun from '$lib/system/Sun.svelte';
	import type { Pin } from '$lib/system/geo';
	import { RED_SUN, YELLOW_SUN } from '$lib/system/sunShader';

	const VIEWS = [
		{ id: 'suns', label: 'Both suns' },
		{ id: 'yellow', label: 'The Yellow Sun' },
		{ id: 'red', label: 'The Red Sun' },
		{ id: 'magmus', label: 'Magmus' },
		{ id: 'hyang-wan', label: 'Hyang Wan' },
		{ id: 'gonhirrim', label: 'Gonhirrim' }
	];
	const MOONS = Object.entries(GONHIRRIM_MOONS);

	let view = $state('hyang-wan');
	let showPins = $state(true);
	let selected = $state<Pin | null>(null);
	let pins = $state<Pin[]>([]);

	/** The body whose places can be pinned in this view, if any. */
	const focus = $derived(
		view === 'magmus' || view === 'hyang-wan' ? view : view.startsWith('moon:') ? view.slice(5) : null
	);
	const moon = $derived(focus && view.startsWith('moon:') ? GONHIRRIM_MOONS[focus] : null);
	const focusName = $derived(moon ? moon.name : view === 'hyang-wan' ? HYANG_WAN.name : 'Magmus');
	const inGonhirrim = $derived(view === 'gonhirrim' || view.startsWith('moon:'));

	$effect(() => {
		pins = [];
		const slug = focus;
		if (!slug) return;
		fetch(`/system/${slug}/pins.json`)
			.then((r) => r.json())
			.then((d) => {
				if (slug === focus) pins = d.pins;
			});
	});

	const camera = $derived(
		view === 'suns'
			? { at: [0, 2, 14], min: 1.3 }
			: view === 'gonhirrim'
				? { at: [0, 7, 30], min: 5 }
				: view === 'hyang-wan'
					? { at: [0, 0.8, 5.4], min: 1.9 }
				: moon
					? { at: [0, 0.25, moon.radius * 3.6], min: moon.radius * 1.3 }
					: { at: [0, 0.6, 3.4], min: 1.3 }
	);

	// The Yellow Sun, off to the side of whatever we're looking at.
	const SUN_AT: [number, number, number] = [-26, 3, 14];
	const GONHIRRIM_SUN: [number, number, number] = [-80, 8, 45];

	function pick(id: string) {
		view = id;
		selected = null;
	}
</script>

<svelte:head><title>System lab</title></svelte:head>

<div class="lab">
	<Canvas toneMapping={NeutralToneMapping}>
		{#key view}
			<T.PerspectiveCamera makeDefault position={camera.at as [number, number, number]} fov={45}>
				<OrbitControls enableDamping minDistance={camera.min} maxDistance={90} />
			</T.PerspectiveCamera>
		{/key}
		<Stars count={4000} radius={150} />
		{#if view === 'suns'}
			<Sun look={YELLOW_SUN} position={[-3, 0, 0]} />
			<Sun look={RED_SUN} position={[3, 0, 0]} />
		{:else if view === 'yellow'}
			<Sun look={YELLOW_SUN} />
		{:else if view === 'red'}
			<Sun look={RED_SUN} />
		{:else if view === 'magmus'}
			<T.AmbientLight intensity={0.08} />
			<Sun look={YELLOW_SUN} radius={1.2} position={SUN_AT} intensity={1.2} />
			<Planet
				slug="magmus"
				glow={1.0}
				face={0}
				flicker={1}
				spin={0.004}
				pins={showPins ? pins : []}
				onpin={(p) => (selected = p)}
			/>
		{:else if view === 'hyang-wan'}
			<T.AmbientLight intensity={0.06} />
			<Sun look={YELLOW_SUN} radius={1.2} position={SUN_AT} intensity={1.6} />
			<Planet
				slug="hyang-wan"
				radius={HYANG_WAN.radius}
				glow={HYANG_WAN.glow}
				clouds={HYANG_WAN.clouds}
				atmosphere={HYANG_WAN.atmosphere}
				nightLights
				sun={SUN_AT}
				face={-24}
				spin={0.003}
				pins={showPins ? pins : []}
				onpin={(p) => (selected = p)}
			/>
			<Orbit period={HYANG_WAN_MOON.orbit!.period} phase={HYANG_WAN_MOON.orbit!.phase} tilt={HYANG_WAN_MOON.orbit!.tilt}>
				<Planet
					slug="hyang-wan-moon"
					radius={HYANG_WAN_MOON.radius}
					position={[HYANG_WAN_MOON.orbit!.distance, 0, 0]}
					face={90}
					sun={SUN_AT}
				/>
			</Orbit>
		{:else if view === 'gonhirrim'}
			<T.AmbientLight intensity={0.05} />
			<Sun look={YELLOW_SUN} radius={3} position={GONHIRRIM_SUN} intensity={1.6} />
			<Planet
				slug="gonhirrim"
				radius={GONHIRRIM.radius}
				glow={GONHIRRIM.glow}
				flicker={GONHIRRIM.flicker}
				atmosphere={GONHIRRIM.atmosphere}
				sun={GONHIRRIM_SUN}
				face={40}
				spin={0.006}
			/>
			{#each MOONS as [slug, m] (slug)}
				<Orbit period={m.orbit!.period} phase={m.orbit!.phase} tilt={m.orbit!.tilt}>
					<Planet
						{slug}
						radius={m.radius}
						position={[m.orbit!.distance, 0, 0]}
						face={90}
						glow={m.glow ?? 1}
						clouds={m.clouds}
						atmosphere={m.atmosphere}
						nightLights
						sun={GONHIRRIM_SUN}
					/>
				</Orbit>
			{/each}
		{:else if moon}
			<T.AmbientLight intensity={0.06} />
			<Sun look={YELLOW_SUN} radius={1.2} position={SUN_AT} intensity={1.6} />
			<!-- A planet loads its textures once, so switching moons needs a fresh one. -->
			{#key focus}
				<Planet
				slug={focus!}
				radius={moon.radius}
				glow={moon.glow ?? 1}
				clouds={moon.clouds}
				atmosphere={moon.atmosphere}
					nightLights
				sun={SUN_AT}
				face={pins[0]?.lon ?? 0}
				spin={0.003}
				pins={showPins ? pins : []}
				onpin={(p) => (selected = p)}
			/>
			{/key}
		{/if}
	</Canvas>

	<nav class="panel">
		{#each VIEWS as v (v.id)}
			<button class:active={view === v.id} onclick={() => pick(v.id)}>{v.label}</button>
		{/each}
		{#if focus}
			<label><input type="checkbox" bind:checked={showPins} /> Places</label>
		{/if}
		{#if inGonhirrim}
			<div class="moons">
				{#each MOONS as [slug, m] (slug)}
					<button class:active={view === `moon:${slug}`} onclick={() => pick(`moon:${slug}`)}>{m.name}</button>
				{/each}
			</div>
		{/if}
	</nav>

	{#if selected}
		<aside class="readout">
			<div class="kicker">{focusName} · {selected.lat.toFixed(1)}°, {selected.lon.toFixed(1)}°</div>
			<h2>{selected.name}</h2>
			<p>
				Position: <strong>{selected.confidence}</strong>
				{#if selected.confidence === 'lore'}(fixed by the session logs){:else if selected.confidence === 'layout'}(area from the logs){:else}(not in the lore yet){/if}
			</p>
			<button onclick={() => (selected = null)}>Close</button>
		</aside>
	{/if}
</div>

<style>
	.lab {
		position: relative;
		flex: 1;
		min-height: 0;
		background: radial-gradient(ellipse at center, #0b0d18 0%, #03040a 70%);
		color: #e8e4d8;
	}
	.panel {
		position: absolute;
		top: 12px;
		left: 12px;
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		align-items: center;
		max-width: calc(100% - 24px);
	}
	.panel button,
	.panel label,
	.readout button {
		font: 500 12px/1 ui-monospace, monospace;
		padding: 7px 10px;
		border: 1px solid #3a3d52;
		border-radius: 4px;
		background: #0d0f1ccc;
		color: inherit;
		cursor: pointer;
	}
	.moons {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		flex-basis: 100%;
	}
	.panel button.active {
		border-color: #e8b45a;
		color: #ffd58a;
	}
	.readout {
		position: absolute;
		right: 12px;
		bottom: 12px;
		width: min(320px, calc(100% - 24px));
		padding: 14px 16px;
		border: 1px solid #e8b45a66;
		border-radius: 6px;
		background: #0a0c16e6;
		font: 13px/1.45 ui-monospace, monospace;
		overflow: hidden;
	}
	/* The ship's computer keeps its screen look; the view of space behind it stays clear. */
	.readout::after {
		content: '';
		position: absolute;
		inset: 0;
		pointer-events: none;
		background: repeating-linear-gradient(0deg, transparent 0 2px, rgba(0, 0, 0, 0.22) 2px 4px);
	}
	.readout .kicker {
		font-size: 11px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #e8b45a;
	}
	.readout h2 {
		margin: 4px 0 8px;
		font-size: 17px;
	}
</style>

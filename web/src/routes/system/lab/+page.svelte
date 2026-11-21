<script lang="ts">
	// A workbench for the solar-system models: look at each sun and planet on its own.
	import { Canvas, T } from '@threlte/core';
	import { ACESFilmicToneMapping } from 'three';
	import { OrbitControls, Stars } from '@threlte/extras';
	import Planet from '$lib/system/Planet.svelte';
	import Sun from '$lib/system/Sun.svelte';
	import type { Pin } from '$lib/system/geo';
	import { RED_SUN, YELLOW_SUN } from '$lib/system/sunShader';

	const VIEWS = [
		{ id: 'suns', label: 'Both suns' },
		{ id: 'yellow', label: 'The Yellow Sun' },
		{ id: 'red', label: 'The Red Sun' },
		{ id: 'magmus', label: 'Magmus' }
	] as const;
	type ViewId = (typeof VIEWS)[number]['id'];

	let view = $state<ViewId>('magmus');
	let showPins = $state(true);
	let selected = $state<Pin | null>(null);
	let pins = $state<Pin[]>([]);

	$effect(() => {
		fetch('/system/magmus/pins.json')
			.then((r) => r.json())
			.then((d) => (pins = d.pins));
	});
</script>

<svelte:head><title>System lab</title></svelte:head>

<div class="lab">
	<Canvas toneMapping={ACESFilmicToneMapping}>
		{#key view}
			<T.PerspectiveCamera makeDefault position={view === 'suns' ? [0, 2, 14] : [0, 0.6, 3.4]} fov={45}>
				<OrbitControls enableDamping minDistance={1.3} maxDistance={40} />
			</T.PerspectiveCamera>
		{/key}
		<Stars count={4000} radius={80} />
		{#if view === 'suns'}
			<Sun look={YELLOW_SUN} position={[-3, 0, 0]} />
			<Sun look={RED_SUN} position={[3, 0, 0]} />
		{:else if view === 'yellow'}
			<Sun look={YELLOW_SUN} />
		{:else if view === 'red'}
			<Sun look={RED_SUN} />
		{:else}
			<T.AmbientLight intensity={0.08} />
			<Sun look={YELLOW_SUN} radius={1.2} position={[-26, 3, 14]} intensity={2.6} />
			<Planet
				slug="magmus"
				glow={1.2}
				face={0}
				spin={0.004}
				pins={showPins ? pins : []}
				onpin={(p) => (selected = p)}
			/>
		{/if}
	</Canvas>

	<nav class="panel">
		{#each VIEWS as v (v.id)}
			<button class:active={view === v.id} onclick={() => ((view = v.id), (selected = null))}>
				{v.label}
			</button>
		{/each}
		{#if view === 'magmus'}
			<label><input type="checkbox" bind:checked={showPins} /> Places</label>
		{/if}
	</nav>

	{#if selected}
		<aside class="readout">
			<div class="kicker">Magmus · {selected.lat.toFixed(1)}°, {selected.lon.toFixed(1)}°</div>
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

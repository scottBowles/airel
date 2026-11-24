<script lang="ts">
	// The whole system as a page: the 3D view, plus controls that work on a phone. A bar along
	// the bottom (time, overview, places), a menu of every body, and a readout for a tapped
	// place. The controls fold away to leave just the view. On a phone it loads smaller maps
	// and fewer belt rocks, as the full set can run the phone out of GPU memory.
	import { Canvas } from '@threlte/core';
	import { NeutralToneMapping } from 'three';
	import type { MapSize } from './assets';
	import { GONHIRRIM_MOONS } from './bodies';
	import type { Pin } from './geo';
	import SystemView from './SystemView.svelte';

	type Props = {
		/** Map size for the body in focus. By default full, or mid on a phone. */
		focusMaps?: MapSize;
	};
	let { focusMaps }: Props = $props();

	// A phone or small tablet: a touch screen, or a narrow window.
	const phone = typeof matchMedia !== 'undefined' && matchMedia('(pointer: coarse), (max-width: 760px)').matches;
	const mapsInFocus = $derived(focusMaps ?? (phone ? 'mid' : 'full'));

	const GROUPS: { name: string; bodies: { id: string; name: string }[] }[] = [
		{
			name: 'Yellow Sun',
			bodies: [
				{ id: 'yellow', name: 'The Yellow Sun' },
				{ id: 'magmus', name: 'Magmus' },
				{ id: 'felucia', name: 'Felucia' },
				{ id: 'terran', name: 'Terran' },
				{ id: 'hyang-wan', name: 'Hyang Wan' },
				{ id: 'gonhirrim', name: 'Gonhirrim' }
			]
		},
		{ name: 'Moons of Gonhirrim', bodies: Object.entries(GONHIRRIM_MOONS).map(([id, m]) => ({ id, name: m.name })) },
		{
			name: 'Between the suns',
			bodies: [
				{ id: 'hielo', name: 'Hielo' },
				{ id: 'chromium', name: 'Chromium' }
			]
		},
		{
			name: 'Red Sun',
			bodies: [
				{ id: 'red', name: 'The Red Sun' },
				{ id: 'didymus', name: 'Didymus' },
				{ id: 'janus', name: 'Janus' },
				{ id: 'genussa', name: 'Genussa' },
				{ id: 'mystra', name: 'Mystra' }
			]
		}
	];
	const ALL = GROUPS.flatMap((g) => g.bodies.map((b) => ({ ...b, group: g.name })));
	const RATES = [
		{ rate: 0, label: 'Pause' },
		{ rate: 1, label: '1×' },
		{ rate: 10, label: '10×' },
		{ rate: 60, label: '60×' }
	];

	let rate = $state(1);
	let focus = $state<string | null>(null);
	let showPins = $state(true);
	let selected = $state<Pin | null>(null);
	let menu = $state(false);
	let folded = $state(false);
	const current = $derived(ALL.find((b) => b.id === focus));

	function go(id: string | null) {
		focus = id;
		selected = null;
		menu = false;
	}
	// Tapping a label in the view changes the focus too: close any readout from the last body.
	$effect(() => {
		void focus;
		selected = null;
	});
</script>

<div class="explorer">
	<Canvas toneMapping={NeutralToneMapping} dpr={[1, phone ? 1.5 : 2]}>
		<SystemView {rate} bind:focus {showPins} focusMaps={mapsInFocus} lite={phone} onpin={(p) => (selected = p)} />
	</Canvas>

	<header class="title">
		<div class="kicker">{current ? current.group : 'The Airel system'}</div>
		<div class="name">{current ? current.name : 'Overview'}</div>
	</header>

	<!-- Everything along the bottom stacks upward, whatever height the bar wraps to. -->
	<div class="dock">
	{#if menu}
		<div class="sheet" role="dialog" aria-label="Bodies">
			<div class="sheet-head">
				<span>Go to</span>
				<button type="button" class="btn" onclick={() => (menu = false)}>Close</button>
			</div>
			<button type="button" class="btn wide" class:on={focus === null} onclick={() => go(null)}>Overview of the system</button>
			{#each GROUPS as g (g.name)}
				<div class="group">{g.name}</div>
				<div class="grid">
					{#each g.bodies as b (b.id)}
						<button type="button" class="btn" class:on={focus === b.id} onclick={() => go(b.id)}>{b.name}</button>
					{/each}
				</div>
			{/each}
		</div>
	{/if}

	{#if selected}
		<aside class="readout">
			<div class="kicker">{current?.name} · {selected.lat.toFixed(1)}°, {selected.lon.toFixed(1)}°</div>
			<h2>{selected.name}</h2>
			<p>
				Position: <strong>{selected.confidence}</strong>
				{#if selected.confidence === 'lore'}(fixed by the session logs){:else if selected.confidence === 'layout'}(area from the logs){:else}(not in the lore yet){/if}
			</p>
			<button type="button" class="btn" onclick={() => (selected = null)}>Close</button>
		</aside>
	{/if}

	{#if folded}
		<button type="button" class="btn unfold" onclick={() => (folded = false)} aria-label="Show controls">Controls</button>
	{:else}
		<nav class="bar" aria-label="Controls">
			<button type="button" class="btn primary" onclick={() => (menu = !menu)} aria-expanded={menu}>Go to…</button>
			{#if focus}
				<button type="button" class="btn" onclick={() => go(null)}>Overview</button>
			{/if}
			<div class="rates" role="group" aria-label="Speed of time">
				{#each RATES as r (r.rate)}
					<button type="button" class="btn" class:on={rate === r.rate} onclick={() => (rate = r.rate)}>{r.label}</button>
				{/each}
			</div>
			<label class="btn check"><input type="checkbox" bind:checked={showPins} /> Places</label>
			<button type="button" class="btn" onclick={() => ((folded = true), (menu = false))} aria-label="Hide controls">Hide</button>
		</nav>
	{/if}
	</div>
</div>

<style>
	.explorer {
		--ink: #e8e4d8;
		--dim: #9b97a8;
		--amber: #e8b45a;
		--amber-hi: #ffd58a;
		--panel: #0b0d18e0;
		--line: #3a3d52;
		position: relative;
		height: 100%;
		min-height: 0;
		flex: 1;
		overflow: hidden;
		background: radial-gradient(ellipse at center, #0b0d18 0%, #03040a 70%);
		color: var(--ink);
		font: 13px/1.4 var(--font-mono, ui-monospace, 'SFMono-Regular', Menlo, monospace);
		-webkit-tap-highlight-color: transparent;
	}
	.btn {
		font: 500 13px/1 inherit;
		font-family: inherit;
		min-height: 40px;
		padding: 0 12px;
		border: 1px solid var(--line);
		border-radius: 6px;
		background: var(--panel);
		color: inherit;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 6px;
		white-space: nowrap;
	}
	.btn.on {
		border-color: var(--amber);
		color: var(--amber-hi);
	}
	.btn.primary {
		border-color: var(--amber);
		color: var(--amber-hi);
	}
	.btn:focus-visible {
		outline: 2px solid var(--amber-hi);
		outline-offset: 1px;
	}
	.check input {
		accent-color: var(--amber);
		margin: 0;
	}
	/* Above the planets' labels (drawn in the view at z-index up to 20). */
	.title,
	.dock {
		z-index: 30;
	}
	.title {
		position: absolute;
		top: max(12px, env(safe-area-inset-top, 0px));
		left: max(14px, env(safe-area-inset-left, 0px));
		pointer-events: none;
		text-shadow: 0 0 4px #000;
	}
	.kicker {
		font-size: 10.5px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--amber);
	}
	.name {
		font-size: 18px;
		font-weight: 600;
		letter-spacing: 0.02em;
	}
	.dock {
		position: absolute;
		left: max(12px, env(safe-area-inset-left, 0px));
		right: max(12px, env(safe-area-inset-right, 0px));
		bottom: max(12px, env(safe-area-inset-bottom, 0px));
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
		pointer-events: none;
	}
	.dock > :global(*) {
		pointer-events: auto;
	}
	.bar {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 6px;
	}
	.rates {
		display: flex;
		gap: 3px;
	}
	.rates .btn {
		padding: 0 10px;
	}
	.unfold {
		align-self: flex-end;
		opacity: 0.75;
	}
	.sheet {
		width: min(520px, 100%);
		max-height: 60vh;
		overflow-y: auto;
		padding: 12px;
		border: 1px solid var(--line);
		border-radius: 8px;
		background: #0a0c16f2;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}
	.sheet-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		color: var(--amber);
		font-size: 11px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}
	.group {
		margin-top: 6px;
		color: var(--dim);
		font-size: 10.5px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}
	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
		gap: 5px;
	}
	.grid .btn,
	.wide {
		justify-content: flex-start;
	}
	.readout {
		width: min(340px, 100%);
		padding: 14px 16px;
		border: 1px solid #e8b45a66;
		border-radius: 8px;
		background: #0a0c16eb;
	}
	.readout h2 {
		margin: 4px 0 8px;
		font-size: 17px;
	}
	.readout p {
		margin: 0 0 10px;
	}
</style>

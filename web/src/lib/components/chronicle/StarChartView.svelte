<script lang="ts">
	// Star Chart: places drawn as systems with their worlds and ports in orbit, and the crew's
	// route plotted across them. Scrub or play the voyage; the itinerary lists every leg.
	import Play from '@lucide/svelte/icons/play';
	import Pause from '@lucide/svelte/icons/pause';
	import SkipBack from '@lucide/svelte/icons/skip-back';
	import SkipForward from '@lucide/svelte/icons/skip-forward';
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import { layoutChart, ORBIT, type ChartPoint } from '$lib/chronicle/starChart';
	import {
		buildPlaceTree,
		colourByOrder,
		journeyLegs,
		pad,
		shortDate,
		wherePath,
		type Session
	} from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	/** The chart never shrinks below this scale, so labels stay readable; it scrolls instead. */
	const MIN_SCALE = 0.68;

	type Point = ChartPoint;

	let tree = $derived(buildPlaceTree(sessions));
	let colours = $derived(colourByOrder(tree.roots.map((r) => r.id)));
	let legs = $derived(journeyLegs(sessions));

	let chart = $derived(layoutChart(tree.roots));
	let points = $derived(chart.points);
	let width = $derived(chart.width);
	let height = $derived(chart.height);

	// Curved segments between consecutive stops at different places.
	let segments = $derived(
		legs.flatMap((leg, i) => {
			if (i === 0) return [];
			const a = points.get(legs[i - 1].stop.id);
			const b = points.get(leg.stop.id);
			if (!a || !b || a === b) return [];
			const dx = b.x - a.x;
			const dy = b.y - a.y;
			const bend = (i % 2 ? 1 : -1) * 0.16;
			const mx = (a.x + b.x) / 2 - dy * bend;
			const my = (a.y + b.y) / 2 + dx * bend;
			// Point and heading at the curve's midpoint, for the direction arrow.
			const ax = 0.25 * a.x + 0.5 * mx + 0.25 * b.x;
			const ay = 0.25 * a.y + 0.5 * my + 0.25 * b.y;
			return [{ at: i, d: `M${a.x},${a.y} Q${mx},${my} ${b.x},${b.y}`, ax, ay, heading: (Math.atan2(dy, dx) * 180) / Math.PI }];
		})
	);

	const stars = Array.from({ length: 140 }, (_, i) => {
		const a = Math.sin(i * 127.1) * 43758.5453;
		const b = Math.sin(i * 311.7) * 24634.6345;
		return { x: a - Math.floor(a), y: b - Math.floor(b), r: (i % 5 === 0 ? 1.2 : 0.6) };
	});

	let cursor = $state(-1);
	let at = $derived(cursor < 0 ? legs.length - 1 : Math.min(cursor, legs.length - 1));
	let current = $derived(legs[at] ?? null);
	let here = $derived(current ? points.get(current.stop.id) : undefined);
	let visitedIds = $derived(new Set(legs.slice(0, at + 1).map((leg) => leg.stop.id)));

	let playing = $state(false);
	$effect(() => {
		if (!playing) return;
		const timer = setInterval(() => {
			if (at >= legs.length - 1) playing = false;
			else cursor = at + 1;
		}, 1500);
		return () => clearInterval(timer);
	});

	function togglePlay() {
		if (!playing && at >= legs.length - 1) cursor = 0;
		playing = !playing;
	}

	function step(delta: number) {
		playing = false;
		cursor = Math.max(0, Math.min(legs.length - 1, at + delta));
	}

	// Clicking a place jumps to the crew's next visit there (wrapping to the first).
	function visit(placeId: string) {
		const later = legs.findIndex((leg, i) => i > at && leg.stop.id === placeId);
		const index = later >= 0 ? later : legs.findIndex((leg) => leg.stop.id === placeId);
		if (index >= 0) {
			playing = false;
			cursor = index;
		}
	}

	// Keep the ship in view when the chart is larger than its viewport.
	let viewport: HTMLElement | undefined = $state();
	$effect(() => {
		if (!viewport || !here) return;
		const scale = viewport.scrollWidth / width;
		viewport.scrollTo({
			left: here.x * scale - viewport.clientWidth / 2,
			top: here.y * scale - viewport.clientHeight / 2,
			behavior: 'smooth'
		});
	});

	let itinerary: HTMLElement | undefined = $state();
	$effect(() => {
		const row = itinerary?.querySelector<HTMLElement>(`[data-leg="${at}"]`);
		if (row && itinerary) itinerary.scrollTop = row.offsetTop - itinerary.clientHeight / 2 + row.clientHeight / 2;
	});

	// Labels sit on the far side of a place from what it orbits, so they point away from the
	// crowded centre: beside it when that is mostly sideways, above or below otherwise.
	function labelAt(point: Point, size: number): { x: number; y: number; anchor: 'start' | 'middle' | 'end' } {
		if (point.node.depth === 0) return { x: point.x, y: point.y - size - 12, anchor: 'middle' };
		const angle = Math.atan2(point.y - point.cy, point.x - point.cx);
		const cos = Math.cos(angle);
		if (Math.abs(cos) >= 0.45) {
			return { x: point.x + Math.sign(cos) * (size + 8), y: point.y + 4, anchor: cos > 0 ? 'start' : 'end' };
		}
		return { x: point.x, y: point.y + (Math.sin(angle) > 0 ? size + 16 : -size - 8), anchor: 'middle' };
	}

	const colourOf = (rootId: string) => colours.get(rootId) ?? 'var(--color-text-muted)';
	const glyphSize = (type: string | null, depth: number) =>
		type === 'STAR' ? 9 : type === 'PLANET' ? 6.5 : type === 'MOON' ? 4.5 : depth === 0 ? 8 : 4.5;
</script>

<div class="grid grid-cols-1 gap-3 lg:grid-cols-[minmax(0,1fr)_300px]">
	<div class="min-w-0 border border-border-dim bg-hull">
		<div class="flex flex-wrap items-center justify-between gap-2 border-b border-border-dim px-3 py-1.5">
			<span class="machine-text text-[9px] text-text-muted">NAV-03 // STAR CHART</span>
			<span class="machine-text text-[9px] text-text-muted">
				{tree.roots.length} SYSTEMS · {tree.byId.size} PLACES · LEG {pad(at + 1)}/{pad(legs.length)}
			</span>
		</div>

		<div class="max-h-[70vh] overflow-auto" bind:this={viewport}>
			<svg viewBox="0 0 {width} {height}" class="block w-full" style:min-width="{width * MIN_SCALE}px" role="img" aria-label="Chart of the places the crew has visited, with their route">
				<defs>
					<radialGradient id="chart-glow">
						<stop offset="0%" stop-color="#fff" stop-opacity="0.9" />
						<stop offset="100%" stop-color="#fff" stop-opacity="0" />
					</radialGradient>
				</defs>
				<rect {width} {height} fill="#040407" />
				{#each stars as star, i (i)}
					<circle cx={star.x * width} cy={star.y * height} r={star.r} fill="#d4c5a0" opacity={0.12 + (i % 4) * 0.08} />
				{/each}

				<!-- Orbits and tethers -->
				{#each [...points.values()] as point (point.node.id)}
					{#if point.node.depth === 0 && point.node.children.length}
						<circle cx={point.x} cy={point.y} r={ORBIT[1]} fill="none" stroke={colourOf(point.rootId)} stroke-opacity="0.16" stroke-dasharray="2 5" />
					{:else if point.node.depth > 1}
						<line x1={point.cx} y1={point.cy} x2={point.x} y2={point.y} stroke={colourOf(point.rootId)} stroke-opacity="0.22" />
					{/if}
				{/each}

				<!-- Route: faint ahead of the cursor, lit behind it -->
				{#each segments as segment (segment.at)}
					{@const flown = segment.at <= at}
					<path d={segment.d} fill="none"
						stroke={flown ? 'var(--color-accent-amber)' : 'var(--color-text-faint)'}
						stroke-width={segment.at === at ? 2.5 : flown ? 1.6 : 1}
						stroke-opacity={segment.at === at ? 1 : flown ? 0.55 : 0.25}
						stroke-dasharray={flown ? undefined : '3 5'} />
					{#if flown}
						<path d="M-5,-3.5 L4,0 L-5,3.5 Z" fill="var(--color-accent-amber)" opacity={segment.at === at ? 1 : 0.6}
							transform="translate({segment.ax} {segment.ay}) rotate({segment.heading})" />
					{/if}
				{/each}

				<!-- Places -->
				{#each [...points.values()] as point (point.node.id)}
					{@const node = point.node}
					{@const colour = colourOf(point.rootId)}
					{@const size = glyphSize(node.type, node.depth)}
					{@const seen = visitedIds.has(node.id)}
					{@const visits = node.sessions.length}
					{@const label = labelAt(point, size)}
					{#snippet glyph()}
						{#if node.type === 'STAR' || node.depth === 0}
							<circle cx={point.x} cy={point.y} r={size * 3} fill="url(#chart-glow)" opacity="0.18" />
							<circle cx={point.x} cy={point.y} r={size} fill={colour} />
						{:else if node.type === 'PLANET' || node.type === 'MOON'}
							<circle cx={point.x} cy={point.y} r={size} fill={seen ? colour : '#0c0c0f'} stroke={colour} stroke-width="1.5" opacity={visits || seen ? 1 : 0.7} />
						{:else if node.type === 'REGION'}
							<circle cx={point.x} cy={point.y} r={size + 2} fill="none" stroke={colour} stroke-width="1.2" stroke-dasharray="2 2" />
							<circle cx={point.x} cy={point.y} r="1.6" fill={colour} />
						{:else}
							<rect x={point.x - size} y={point.y - size} width={size * 2} height={size * 2}
								transform="rotate(45 {point.x} {point.y})"
								fill={seen ? colour : '#0c0c0f'} stroke={colour} stroke-width="1.5" />
						{/if}
						<text
							x={label.x}
							y={label.y}
							text-anchor={label.anchor}
							font-size={node.depth === 0 ? 16 : 12}
							letter-spacing="1.2"
							font-family={node.depth === 0 ? 'var(--font-display)' : 'var(--font-mono)'}
							fill={node.depth === 0 ? colour : seen ? '#d4c5a0' : '#8a7e60'}
							paint-order="stroke" stroke="#040407" stroke-width="3"
						>
							{node.name.toUpperCase()}{visits > 1 ? ` ×${visits}` : ''}
						</text>
					{/snippet}
					{#if visits}
						<g
							class="cursor-pointer"
							role="button"
							tabindex="0"
							aria-label="{node.name}, {visits} sessions"
							onclick={() => visit(node.id)}
							onkeydown={(e) => e.key === 'Enter' && visit(node.id)}
						>
							{@render glyph()}
						</g>
					{:else}
						<g>{@render glyph()}</g>
					{/if}
				{/each}

				<!-- The ship -->
				{#if here}
					<g class="ship" style:transform="translate({here.x}px, {here.y}px)">
						<circle r="15" fill="none" stroke="var(--color-accent-amber)" stroke-width="1.5" />
						<circle r="21" fill="none" stroke="var(--color-accent-amber)" stroke-opacity="0.4" class="animate-pulse-glow" />
						<path d="M-21,0 h-7 M21,0 h7 M0,-21 v-7 M0,21 v7" stroke="var(--color-accent-amber)" stroke-width="1.5" />
					</g>
				{/if}
			</svg>
		</div>

		<!-- Transport -->
		<div class="flex items-center gap-2 border-t border-border-dim px-3 py-2">
			<button type="button" class="ctl" aria-label="Previous leg" onclick={() => step(-1)}><SkipBack class="h-3.5 w-3.5" /></button>
			<button type="button" class="ctl ctl-main" aria-label={playing ? 'Pause' : 'Play the voyage'} onclick={togglePlay}>
				{#if playing}<Pause class="h-3.5 w-3.5" />{:else}<Play class="h-3.5 w-3.5" />{/if}
			</button>
			<button type="button" class="ctl" aria-label="Next leg" onclick={() => step(1)}><SkipForward class="h-3.5 w-3.5" /></button>
			<input
				type="range" min="0" max={Math.max(0, legs.length - 1)} value={at}
				aria-label="Position in the voyage"
				class="scrub min-w-0 flex-1"
				oninput={(e) => { playing = false; cursor = Number(e.currentTarget.value); }}
			/>
			<span class="machine-text w-24 text-right text-[10px] text-text-muted">{shortDate(current?.session.date ?? null)}</span>
		</div>
	</div>

	<!-- Current stop and itinerary -->
	<div class="flex min-h-0 min-w-0 flex-col gap-3">
		{#if current}
			<div class="border border-accent-amber/25 bg-panel px-3 py-3">
				<p class="machine-text text-[9px] text-text-muted">CURRENT POSITION</p>
				<p class="mt-1 font-display text-sm uppercase tracking-widest" style:color={colourOf(current.stop.path[0].id)}>{current.stop.name}</p>
				<p class="text-[10px] uppercase tracking-wider text-text-muted">{wherePath(current.stop)}</p>
				<div class="trace-line my-2"></div>
				<p class="font-display text-[10px] text-accent-amber">SESSION {pad(current.session.n)} · {shortDate(current.session.date)}</p>
				<h2 class="mt-0.5 text-xs font-bold uppercase tracking-wider text-text-primary">{current.session.title}</h2>
				{#if current.session.brief}
					<p class="mt-1 text-xs leading-relaxed text-text-secondary">{current.session.brief}</p>
				{/if}
				<a href="/chronicle/{current.session.id}" class="mt-2 inline-flex items-center gap-1 machine-text text-[10px] text-accent-amber hover:underline">
					OPEN LOG <ArrowRight class="h-3 w-3" />
				</a>
			</div>
		{/if}

		<div class="flex min-h-0 flex-1 flex-col border border-border-dim bg-hull">
			<p class="border-b border-border-dim px-3 py-1.5 machine-text text-[9px] text-text-muted">ITINERARY</p>
			<ol bind:this={itinerary} class="relative max-h-72 overflow-y-auto lg:max-h-[26rem]">
				{#each legs as leg, i (leg.session.id)}
					{@const moved = i === 0 || legs[i - 1].stop.id !== leg.stop.id}
					<li data-leg={i}>
						<button
							type="button"
							class="flex w-full items-baseline gap-2 px-3 py-1.5 text-left text-[11px] transition-colors {i === at
								? 'bg-accent-amber/10 text-accent-amber'
								: i < at
									? 'text-text-secondary hover:bg-panel-hover'
									: 'text-text-faint hover:bg-panel-hover'}"
							onclick={() => { playing = false; cursor = i; }}
						>
							<span class="machine-text w-5 shrink-0 text-[10px]">{pad(leg.session.n)}</span>
							<span class="status-dot shrink-0 self-center" style:color={colourOf(leg.stop.path[0].id)} style:opacity={moved ? 1 : 0.35}></span>
							<span class="min-w-0 flex-1 truncate uppercase tracking-wider">{moved ? leg.stop.name : '· stays'}</span>
							<span class="max-w-[45%] truncate text-[10px] normal-case text-text-muted">{leg.session.title}</span>
						</button>
					</li>
				{/each}
			</ol>
		</div>
	</div>
</div>

<style>
	.ship {
		transition: transform 0.7s cubic-bezier(0.45, 0, 0.2, 1);
	}
	.ctl {
		display: flex;
		height: 2rem;
		width: 2rem;
		flex-shrink: 0;
		align-items: center;
		justify-content: center;
		border: 1px solid var(--color-border-subtle);
		color: var(--color-text-secondary);
	}
	.ctl:hover {
		border-color: var(--color-accent-amber);
		color: var(--color-accent-amber);
	}
	.ctl-main {
		background: var(--color-accent-amber-dim);
		color: var(--color-accent-amber);
	}
	.scrub {
		accent-color: var(--color-accent-amber);
	}
	@media (prefers-reduced-motion: reduce) {
		.ship {
			transition: none;
		}
	}
</style>

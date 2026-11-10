<script lang="ts">
	// Star Chart: each sun with its worlds in orbit and each world's places around it, with the
	// crew's flights plotted between them. Repeated flights share one line that thickens with use
	// and fades with age. Scrub or play the voyage; the itinerary lists it arc by arc.
	import Play from '@lucide/svelte/icons/play';
	import Pause from '@lucide/svelte/icons/pause';
	import SkipBack from '@lucide/svelte/icons/skip-back';
	import SkipForward from '@lucide/svelte/icons/skip-forward';
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import {
		buildRoutes,
		glyphSize,
		labelPosition,
		layoutChart,
		shortName,
		starsOf,
		type ChartPoint
	} from '$lib/chronicle/starChart';
	import {
		arcBySession,
		buildArcs,
		buildPlaceTree,
		journeyLegs,
		NEUTRAL,
		pad,
		shortDate,
		wherePath,
		worldColours,
		worldSessionCounts,
		type Session
	} from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	/** The chart never shrinks below this scale, so labels stay readable; it scrolls instead. */
	const MIN_SCALE = 0.62;
	/** How many legs it takes an old route to fade most of the way out. */
	const FADE_LEGS = 30;

	let tree = $derived(buildPlaceTree(sessions));
	let colours = $derived(worldColours(sessions));
	let legs = $derived(journeyLegs(sessions));
	let arcs = $derived(buildArcs(sessions, colours));
	let arcOf = $derived(arcBySession(arcs));

	let chart = $derived(layoutChart(tree.roots, starsOf(sessions)));
	let points = $derived(chart.points);
	let width = $derived(chart.width);
	let height = $derived(chart.height);
	let routes = $derived(buildRoutes(legs.map((leg) => leg.stop.id)));

	/** Sessions mainly set on each world, for the world labels. */
	let worldVisits = $derived(worldSessionCounts(sessions));

	const starfield = Array.from({ length: 160 }, (_, i) => {
		const a = Math.sin(i * 127.1) * 43758.5453;
		const b = Math.sin(i * 311.7) * 24634.6345;
		return { x: a - Math.floor(a), y: b - Math.floor(b), r: i % 5 === 0 ? 1.2 : 0.6 };
	});

	let cursor = $state(-1);
	let at = $derived(cursor < 0 ? legs.length - 1 : Math.min(cursor, legs.length - 1));
	let current = $derived(legs[at] ?? null);
	let here = $derived(current ? points.get(current.stop.id) : undefined);
	let hereWorld = $derived(current?.stop.path[0].id ?? null);
	let currentArc = $derived(current ? arcOf.get(current.session.id) : undefined);
	let visitedIds = $derived(new Set(legs.slice(0, at + 1).flatMap((leg) => leg.stop.path.map((p) => p.id))));
	let currentKey = $derived.by(() => {
		const from = legs[at - 1]?.stop.id;
		const to = legs[at]?.stop.id;
		if (!from || !to || from === to) return null;
		return from < to ? `${from}|${to}` : `${to}|${from}`;
	});

	// Each route as a curve, with how recently (as of the cursor) it was flown.
	let drawn = $derived(
		routes.flatMap((route) => {
			const a = points.get(route.a);
			const b = points.get(route.b);
			if (!a || !b) return [];
			const flown = route.legs.filter((i) => i <= at);
			const dx = b.x - a.x;
			const dy = b.y - a.y;
			const local = a.worldId === b.worldId;
			const bend = local ? 0.12 : 0.22;
			const mx = (a.x + b.x) / 2 - dy * bend;
			const my = (a.y + b.y) / 2 + dx * bend;
			return [
				{
					route,
					a,
					b,
					mx,
					my,
					local,
					count: flown.length,
					age: flown.length ? at - flown[flown.length - 1] : Infinity
				}
			];
		})
	);

	let playing = $state(false);
	$effect(() => {
		if (!playing) return;
		const timer = setInterval(() => {
			if (at >= legs.length - 1) playing = false;
			else cursor = at + 1;
		}, 1100);
		return () => clearInterval(timer);
	});

	function togglePlay() {
		if (!playing && at >= legs.length - 1) cursor = 0;
		playing = !playing;
	}

	function go(index: number) {
		playing = false;
		cursor = Math.max(0, Math.min(legs.length - 1, index));
	}

	// Clicking a place jumps to the crew's next time there (wrapping to the first). For a world,
	// any session on that world counts.
	function visit(point: ChartPoint) {
		const matches = (i: number) =>
			point.node.depth === 0 ? legs[i].stop.path[0].id === point.node.id : legs[i].stop.id === point.node.id;
		const later = legs.findIndex((_, i) => i > at && matches(i));
		const index = later >= 0 ? later : legs.findIndex((_, i) => matches(i));
		if (index >= 0) go(index);
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

	const colourOf = (worldId: string) => colours.get(worldId) ?? NEUTRAL;
	const visitsOf = (point: ChartPoint) =>
		point.node.depth === 0 ? (worldVisits.get(point.node.id) ?? 0) : point.node.sessions.length;
	let labelled = $derived(
		[...points.values()]
			.filter((point) => point.node.depth === 0 || point.worldId === hereWorld)
			.sort((a, b) => b.node.depth - a.node.depth)
	);
	/** A sun's colour, from its name when it says ("The Red Sun"), else a pale gold. */
	const sunColour = (name: string) =>
		/red/i.test(name) ? '#ff6a3d' : /blue/i.test(name) ? '#7aa8ff' : /white/i.test(name) ? '#f2f0e6' : '#ffd34d';
</script>

<div class="grid grid-cols-1 gap-3 2xl:grid-cols-[minmax(0,1fr)_320px]">
	<div class="min-w-0 border border-border-dim bg-hull">
		<div class="flex flex-wrap items-center justify-between gap-2 border-b border-border-dim px-3 py-1.5">
			<span class="machine-text text-[9px] text-text-muted">NAV-03 // STAR CHART</span>
			<span class="machine-text text-[9px] text-text-muted">
				{tree.roots.length} WORLDS · {tree.byId.size} PLACES · {routes.length} ROUTES · LEG {pad(at + 1)}/{pad(legs.length)}
			</span>
		</div>

		<div class="max-h-[72vh] overflow-auto" bind:this={viewport}>
			<svg
				viewBox="0 0 {width} {height}"
				class="block w-full"
				style:min-width="{width * MIN_SCALE}px"
				role="img"
				aria-label="Chart of the suns, worlds and places the crew has visited, with the routes they flew"
			>
				<defs>
					<radialGradient id="sun-glow">
						<stop offset="0%" stop-color="#fff" stop-opacity="0.85" />
						<stop offset="35%" stop-color="#fff" stop-opacity="0.25" />
						<stop offset="100%" stop-color="#fff" stop-opacity="0" />
					</radialGradient>
				</defs>
				<rect {width} {height} fill="#040407" />
				{#each starfield as dot, i (i)}
					<circle cx={dot.x * width} cy={dot.y * height} r={dot.r} fill="#d4c5a0" opacity={0.1 + (i % 4) * 0.07} />
				{/each}

				<!-- Suns and their orbit rings -->
				{#each chart.groups as group (group.star ?? '—')}
					{#if group.ring}
						<circle cx={group.x} cy={group.y} r={group.ring} fill="none" stroke="#d4c5a0" stroke-opacity="0.12" stroke-dasharray="2 6" />
					{/if}
					{#if group.star}
						{@const tone = sunColour(group.star)}
						<circle cx={group.x} cy={group.y} r="46" fill="url(#sun-glow)" opacity="0.35" />
						<circle cx={group.x} cy={group.y} r="46" fill={tone} opacity="0.08" />
						<circle cx={group.x} cy={group.y} r="13" fill={tone} />
						<text x={group.x} y={group.y + 34} text-anchor="middle" font-size="15" letter-spacing="2"
							font-family="var(--font-display)" fill={tone} paint-order="stroke" stroke="#040407" stroke-width="4">
							{group.star.toUpperCase()}
						</text>
					{:else if group.ring}
						<text x={group.x} y={group.y + 4} text-anchor="middle" font-size="11" letter-spacing="2"
							font-family="var(--font-mono)" fill="#6b634a">NO SUN RECORDED</text>
					{/if}
				{/each}

				<!-- Tethers from each place to what it is inside -->
				{#each [...points.values()] as point (point.node.id)}
					{#if point.node.depth > 0}
						<line x1={point.cx} y1={point.cy} x2={point.x} y2={point.y} stroke={colourOf(point.worldId)} stroke-opacity="0.2" />
					{/if}
				{/each}

				<!-- Routes: flown ones lit and fading with age, ones still ahead of the cursor faint -->
				{#each drawn as line (line.route.key)}
					{@const isCurrent = line.route.key === currentKey}
					{@const lit = line.count > 0}
					{@const tone = isCurrent ? 'var(--color-accent-amber)' : line.local ? colourOf(line.a.worldId) : 'var(--color-accent-amber)'}
					<path
						d="M{line.a.x},{line.a.y} Q{line.mx},{line.my} {line.b.x},{line.b.y}"
						fill="none"
						stroke={lit ? tone : 'var(--color-text-faint)'}
						stroke-width={isCurrent ? 3 : lit ? 1 + Math.log2(line.count) * 0.9 : 1}
						stroke-opacity={isCurrent ? 1 : lit ? 0.18 + 0.62 * Math.exp(-line.age / FADE_LEGS) : 0.14}
						stroke-dasharray={lit ? undefined : '3 5'}
					>
						<title>{line.a.node.name} ↔ {line.b.node.name}: flown {line.route.legs.length}×</title>
					</path>
				{/each}
				{#if currentKey}
					{@const line = drawn.find((d) => d.route.key === currentKey)}
					{#if line}
						{@const forward = legs[at].stop.id === line.route.b}
						{@const ax = 0.25 * line.a.x + 0.5 * line.mx + 0.25 * line.b.x}
						{@const ay = 0.25 * line.a.y + 0.5 * line.my + 0.25 * line.b.y}
						{@const heading = (Math.atan2(line.b.y - line.a.y, line.b.x - line.a.x) * 180) / Math.PI + (forward ? 0 : 180)}
						<path d="M-7,-5 L6,0 L-7,5 Z" fill="var(--color-accent-amber)" transform="translate({ax} {ay}) rotate({heading})" />
					{/if}
				{/if}

				<!-- Places -->
				{#each [...points.values()] as point (point.node.id)}
					{@const node = point.node}
					{@const colour = colourOf(point.worldId)}
					{@const size = glyphSize(node.type, node.depth)}
					{@const seen = visitedIds.has(node.id)}
					{@const visits = visitsOf(point)}
					{#snippet glyph()}
						<title>{node.name}{visits ? ` · ${visits} session${visits > 1 ? 's' : ''}` : ''}</title>
						{#if node.depth === 0}
							<circle cx={point.x} cy={point.y} r={size + 7} fill={colour} opacity={seen ? 0.12 : 0.05} />
							<circle cx={point.x} cy={point.y} r={size} fill={seen ? colour : '#0c0c0f'} stroke={colour} stroke-width="2" />
						{:else if node.type === 'PLANET' || node.type === 'MOON'}
							<circle cx={point.x} cy={point.y} r={size} fill={seen ? colour : '#0c0c0f'} stroke={colour} stroke-width="1.5" />
						{:else if node.type === 'REGION'}
							<circle cx={point.x} cy={point.y} r={size + 2} fill="none" stroke={colour} stroke-width="1.2" stroke-dasharray="2 2" />
							<circle cx={point.x} cy={point.y} r="1.6" fill={colour} />
						{:else}
							<rect x={point.x - size} y={point.y - size} width={size * 2} height={size * 2}
								transform="rotate(45 {point.x} {point.y})"
								fill={seen ? colour : '#0c0c0f'} stroke={colour} stroke-width="1.3" />
						{/if}
					{/snippet}
					{#if visits}
						<g
							class="cursor-pointer"
							role="button"
							tabindex="0"
							aria-label="{node.name}, {visits} sessions"
							onclick={() => visit(point)}
							onkeydown={(e) => e.key === 'Enter' && visit(point)}
						>
							{@render glyph()}
						</g>
					{:else}
						<g>{@render glyph()}</g>
					{/if}
				{/each}

				<!-- Labels on top: every world's name, and the places of the world the ship is at.
				     World names go last, so a crowded world's places never cover its name. -->
				{#each labelled as point (point.node.id)}
					{@const node = point.node}
					{@const label = labelPosition(point, width)}
					{@const visits = visitsOf(point)}
					<text
						x={label.x}
						y={label.y}
						text-anchor={label.anchor}
						font-size={node.depth === 0 ? 15 : 11}
						letter-spacing="1.1"
						font-family={node.depth === 0 ? 'var(--font-display)' : 'var(--font-mono)'}
						fill={node.depth === 0 ? colourOf(point.worldId) : visitedIds.has(node.id) ? '#d4c5a0' : '#8a7e60'}
						paint-order="stroke"
						stroke="#040407"
						stroke-width="3.5"
						pointer-events="none"
					>
						{shortName(node.name, label.maxChars).toUpperCase()}{visits > 1 ? ` ×${visits}` : ''}
					</text>
				{/each}

				<!-- The ship -->
				{#if here}
					<g class="ship" style:transform="translate({here.x}px, {here.y}px)">
						<circle r="14" fill="none" stroke="var(--color-accent-amber)" stroke-width="1.5" />
						<circle r="20" fill="none" stroke="var(--color-accent-amber)" stroke-opacity="0.4" class="animate-pulse-glow" />
						<path d="M-20,0 h-7 M20,0 h7 M0,-20 v-7 M0,20 v7" stroke="var(--color-accent-amber)" stroke-width="1.5" />
					</g>
				{/if}
			</svg>
		</div>

		<!-- Transport -->
		<div class="flex items-center gap-2 border-t border-border-dim px-3 py-2">
			<button type="button" class="ctl" aria-label="Previous leg" onclick={() => go(at - 1)}><SkipBack class="h-3.5 w-3.5" /></button>
			<button type="button" class="ctl ctl-main" aria-label={playing ? 'Pause' : 'Play the voyage'} onclick={togglePlay}>
				{#if playing}<Pause class="h-3.5 w-3.5" />{:else}<Play class="h-3.5 w-3.5" />{/if}
			</button>
			<button type="button" class="ctl" aria-label="Next leg" onclick={() => go(at + 1)}><SkipForward class="h-3.5 w-3.5" /></button>
			<input
				type="range"
				min="0"
				max={Math.max(0, legs.length - 1)}
				value={at}
				aria-label="Position in the voyage"
				class="scrub min-w-0 flex-1"
				oninput={(e) => go(Number(e.currentTarget.value))}
			/>
			<span class="machine-text w-24 text-right text-[10px] text-text-muted">{shortDate(current?.session.date ?? null)}</span>
		</div>
	</div>

	<!-- Current stop and itinerary -->
	<div class="grid min-h-0 min-w-0 content-start gap-3 md:grid-cols-2 2xl:grid-cols-1">
		{#if current}
			<div class="border border-accent-amber/25 bg-panel px-3 py-3">
				<p class="machine-text text-[9px] text-text-muted">CURRENT POSITION</p>
				<p class="mt-1 font-display text-sm uppercase tracking-widest" style:color={colourOf(current.stop.path[0].id)}>{current.stop.name}</p>
				<p class="text-[10px] uppercase tracking-wider text-text-muted">{wherePath(current.stop)}</p>
				{#if currentArc}
					<p class="mt-1 machine-text text-[9px] text-text-faint">
						ARC {currentArc.n} · SESSION {currentArc.sessions.indexOf(current.session) + 1} OF {currentArc.sessions.length} ON {(currentArc.world?.name ?? 'UNRECORDED').toUpperCase()}
					</p>
				{/if}
				<div class="trace-line my-2"></div>
				<p class="font-display text-[10px] text-accent-amber">SESSION {pad(current.session.n)} · {shortDate(current.session.date)}</p>
				<h2 class="mt-0.5 text-xs font-bold uppercase tracking-wider text-text-primary">{current.session.title}</h2>
				{#if current.session.brief}
					<p class="mt-1 line-clamp-6 text-xs leading-relaxed text-text-secondary">{current.session.brief}</p>
				{/if}
				<a href="/chronicle/{current.session.id}" class="mt-2 inline-flex items-center gap-1 machine-text text-[10px] text-accent-amber hover:underline">
					OPEN LOG <ArrowRight class="h-3 w-3" />
				</a>
			</div>
		{/if}

		<div class="flex min-h-0 flex-1 flex-col border border-border-dim bg-hull">
			<p class="border-b border-border-dim px-3 py-1.5 machine-text text-[9px] text-text-muted">ITINERARY · {arcs.length} ARCS</p>
			<ol bind:this={itinerary} class="relative max-h-80 overflow-y-auto 2xl:max-h-[30rem]">
				{#each legs as leg, i (leg.session.id)}
					{@const arc = arcOf.get(leg.session.id)}
					{@const opensArc = arc?.sessions[0] === leg.session}
					{@const moved = i === 0 || legs[i - 1].stop.id !== leg.stop.id}
					{#if opensArc && arc}
						<li class="sticky top-0 z-10">
							<button
								type="button"
								class="flex w-full items-baseline gap-2 border-y border-border-dim bg-hull px-3 py-1 text-left font-display text-[10px] uppercase tracking-widest"
								style:color={arc.colour}
								onclick={() => go(i)}
							>
								<span class="min-w-0 flex-1 truncate">{arc.world?.name ?? 'Unrecorded'}</span>
								<span class="shrink-0 machine-text text-[9px] text-text-muted">{arc.sessions.length} · {shortDate(arc.sessions[0].date).slice(3)}</span>
							</button>
						</li>
					{/if}
					<li data-leg={i}>
						<button
							type="button"
							class="flex w-full items-baseline gap-2 px-3 py-1 text-left text-[11px] transition-colors {i === at
								? 'bg-accent-amber/10 text-accent-amber'
								: i < at
									? 'text-text-secondary hover:bg-panel-hover'
									: 'text-text-faint hover:bg-panel-hover'}"
							onclick={() => go(i)}
						>
							<span class="machine-text w-6 shrink-0 text-[10px]">{pad(leg.session.n)}</span>
							<span class="min-w-0 flex-1 truncate uppercase tracking-wider" class:opacity-50={!moved}>{moved ? leg.stop.name : '· stays'}</span>
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

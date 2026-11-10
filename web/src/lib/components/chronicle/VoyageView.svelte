<script lang="ts">
	// Flight Path: a lane per place, a column per session, and one line tracing the journey.
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import {
		buildPlaceTree,
		worldColours,
		monthLabel,
		orderedStops,
		pad,
		primaryStop,
		shortDate,
		wherePath,
		type PlaceNode,
		type Session
	} from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	const ROW = 30;
	const MIN_COL = 16;
	const UNCHARTED = '__uncharted__';

	type Lane = { id: string; name: string; type: string | null; depth: number; rootId: string; visits: number };

	let tree = $derived(buildPlaceTree(sessions));
	let colours = $derived(worldColours(sessions));

	// Lanes are the place tree flattened depth-first, so a town sits under its world.
	let lanes = $derived.by(() => {
		const out: Lane[] = [];
		const walk = (node: PlaceNode, rootId: string) => {
			out.push({ id: node.id, name: node.name, type: node.type, depth: node.depth, rootId, visits: node.sessions.length });
			node.children.forEach((child) => walk(child, rootId));
		};
		tree.roots.forEach((root) => walk(root, root.id));
		if (sessions.some((s) => !s.stops.length)) {
			out.push({ id: UNCHARTED, name: 'Location not recorded', type: null, depth: 0, rootId: UNCHARTED, visits: 0 });
		}
		return out;
	});
	let laneIndex = $derived(new Map(lanes.map((lane, i) => [lane.id, i])));

	let chartWidth = $state(0);
	let col = $derived(Math.max(MIN_COL, sessions.length ? chartWidth / sessions.length : MIN_COL));
	let width = $derived(col * sessions.length);
	let height = $derived(lanes.length * ROW);

	const x = (i: number) => col * i + col / 2;
	const y = (laneId: string) => (laneIndex.get(laneId) ?? 0) * ROW + ROW / 2;
	const colourOf = (rootId: string) => colours.get(rootId) ?? 'var(--color-text-faint)';

	// Each session's marks, and the lane its journey line passes through.
	let columns = $derived(
		sessions.map((session, i) => {
			const stops = orderedStops(session);
			const main = primaryStop(session);
			return {
				session,
				x: x(i),
				mainY: y(main?.id ?? UNCHARTED),
				rootId: main?.path[0]?.id ?? UNCHARTED,
				marks: stops.length
					? stops.map((stop) => ({ y: y(stop.id), rootId: stop.path[0]?.id ?? UNCHARTED, main: stop.id === main?.id }))
					: [{ y: y(UNCHARTED), rootId: UNCHARTED, main: true }]
			};
		})
	);

	// The journey: an S-curve from each session's main stop to the next.
	let legs = $derived(
		columns.slice(1).map((to, i) => {
			const from = columns[i];
			const mid = (from.x + to.x) / 2;
			return {
				d: `M${from.x},${from.mainY} C${mid},${from.mainY} ${mid},${to.mainY} ${to.x},${to.mainY}`,
				moved: from.mainY !== to.mainY,
				jump: from.rootId !== to.rootId,
				colour: colourOf(to.rootId)
			};
		})
	);

	let monthTicks = $derived(
		sessions.flatMap((session, i) => {
			if (!session.date) return [];
			const prev = sessions[i - 1]?.date;
			const changed = !prev || monthLabel(prev) !== monthLabel(session.date);
			return changed ? [{ x: col * i, label: monthLabel(session.date) }] : [];
		})
	);

	let selectedId = $state<string | null>(null);
	let selected = $derived(sessions.find((s) => s.id === selectedId) ?? sessions.at(-1) ?? null);
	let selectedIndex = $derived(selected ? sessions.indexOf(selected) : -1);
	let jumps = $derived(legs.filter((leg) => leg.jump).length);
</script>

<div class="border border-border-dim bg-hull">
	<div class="flex flex-wrap items-center justify-between gap-2 border-b border-border-dim px-3 py-1.5">
		<span class="machine-text text-[9px] text-text-muted">NAV-02 // FLIGHT PATH</span>
		<span class="machine-text text-[9px] text-text-muted">
			{sessions.length} SESSIONS · {tree.byId.size} PLACES · {jumps} WORLD CHANGES
		</span>
	</div>

	<div class="flex">
		<!-- Place lanes -->
		<div class="w-36 shrink-0 border-r border-border-dim sm:w-52">
			<div class="h-7 border-b border-border-dim px-3 machine-text text-[9px] leading-7 text-text-faint">PLACE</div>
			{#each lanes as lane (lane.id)}
				<div
					class="flex items-center gap-1.5 overflow-hidden whitespace-nowrap px-3 text-[11px]"
					style:height="{ROW}px"
					style:padding-left="{10 + lane.depth * 8}px"
				>
					<span class="status-dot shrink-0" style:color={colourOf(lane.rootId)} style:opacity={lane.depth === 0 ? 1 : 0.45}></span>
					{#if lane.id === UNCHARTED}
						<span class="truncate italic text-text-faint">{lane.name}</span>
					{:else}
						<a
							href="/database/places/{lane.id}"
							class="truncate uppercase tracking-wider hover:text-accent-amber {lane.depth === 0
								? 'font-display text-[10px] text-text-primary'
								: lane.visits
									? 'text-text-secondary'
									: 'text-text-faint'}"
						>
							{lane.name}
						</a>
						{#if lane.visits}
							<span class="ml-auto shrink-0 machine-text text-[9px] text-text-faint">×{lane.visits}</span>
						{/if}
					{/if}
				</div>
			{/each}
			<div class="h-6 border-t border-border-dim"></div>
		</div>

		<!-- Chart -->
		<div class="min-w-0 flex-1 overflow-x-auto" bind:clientWidth={chartWidth}>
			<div style:width="{width}px">
				<div class="flex h-7 border-b border-border-dim">
					{#each sessions as session (session.id)}
						<button
							type="button"
							class="machine-text text-[10px] leading-7 transition-colors {session.id === selected?.id
								? 'bg-accent-amber/15 text-accent-amber'
								: 'text-text-muted hover:text-accent-amber'}"
							style:width="{col}px"
							aria-label="Session {session.n}: {session.title}"
							onclick={() => (selectedId = session.id)}
							onmouseenter={() => (selectedId = session.id)}
							onfocus={() => (selectedId = session.id)}
						>
							{pad(session.n)}
						</button>
					{/each}
				</div>

				<svg {width} {height} class="block" role="img" aria-label="The crew's journey between places, session by session">
					{#each lanes as lane, i (lane.id)}
						<line x1="0" x2={width} y1={i * ROW + ROW / 2} y2={i * ROW + ROW / 2}
							stroke={colourOf(lane.rootId)} stroke-opacity={lane.depth === 0 ? 0.22 : 0.09}
							stroke-dasharray={lane.visits ? undefined : '2 6'} />
					{/each}
					{#if selectedIndex >= 0}
						<rect x={col * selectedIndex} y="0" width={col} {height} fill="var(--color-accent-amber)" fill-opacity="0.06" />
					{/if}
					{#each legs as leg, i (i)}
						<path d={leg.d} fill="none" stroke={leg.colour} stroke-width={leg.moved ? 2 : 1.5}
							stroke-opacity={leg.moved ? 0.85 : 0.45} stroke-dasharray={leg.jump ? '5 4' : undefined} />
					{/each}
					{#each columns as column (column.session.id)}
						{@const ys = column.marks.map((m) => m.y)}
						{#if ys.length > 1}
							<line x1={column.x} x2={column.x} y1={Math.min(...ys)} y2={Math.max(...ys)}
								stroke={colourOf(column.rootId)} stroke-opacity="0.5" />
						{/if}
						{#each column.marks as mark, j (j)}
							<circle cx={column.x} cy={mark.y} r={mark.main ? 5 : 3.5}
								fill={mark.main ? colourOf(mark.rootId) : 'var(--color-hull)'}
								stroke={colourOf(mark.rootId)} stroke-width="1.5" />
						{/each}
						{#if column.session.id === selected?.id}
							<circle cx={column.x} cy={column.mainY} r="10" fill="none" stroke="var(--color-accent-amber)" stroke-width="1.5" />
						{/if}
						<rect x={column.x - col / 2} y="0" width={col} {height} fill="transparent" class="cursor-pointer"
							role="presentation"
							onmouseenter={() => (selectedId = column.session.id)}
							onclick={() => (selectedId = column.session.id)} />
					{/each}
				</svg>

				<div class="relative h-6 border-t border-border-dim">
					{#each monthTicks as tick (tick.x)}
						<span class="absolute top-0 h-full border-l border-border-subtle pl-1 machine-text text-[9px] leading-6 text-text-muted whitespace-nowrap" style:left="{tick.x}px">
							{tick.label}
						</span>
					{/each}
				</div>
			</div>
		</div>
	</div>

	<div class="flex flex-wrap gap-x-4 gap-y-1 border-t border-border-dim px-3 py-1.5 machine-text text-[9px] text-text-muted">
		<span>● MAIN SETTING</span>
		<span>○ ALSO VISITED</span>
		<span>┄ TRAVEL BETWEEN WORLDS</span>
	</div>
</div>

<!-- Selected session -->
{#if selected}
	{@const main = primaryStop(selected)}
	<div class="border border-accent-amber/25 bg-panel px-4 py-3">
		<div class="flex flex-wrap items-baseline gap-x-3 gap-y-1">
			<span class="font-display text-xs text-accent-amber">SESSION {pad(selected.n)}</span>
			<span class="machine-text text-[10px] text-text-muted">{shortDate(selected.date)}</span>
			{#if main}
				<span class="text-[11px] uppercase tracking-wider text-accent-cyan">{wherePath(main)}</span>
			{/if}
		</div>
		<h2 class="mt-1 text-sm font-bold uppercase tracking-wider text-text-primary">{selected.title}</h2>
		{#if selected.brief}
			<p class="mt-1 max-w-3xl text-xs leading-relaxed text-text-secondary">{selected.brief}</p>
		{/if}
		<div class="mt-2 flex flex-wrap items-center gap-1.5">
			{#each selected.characters as character (character.id)}
				<span class="border border-border-subtle px-1.5 py-0.5 text-[10px] uppercase tracking-wider text-text-muted">{character.name}</span>
			{/each}
			<a href="/chronicle/{selected.id}" class="ml-auto flex items-center gap-1 machine-text text-[10px] text-accent-amber hover:underline">
				OPEN LOG <ArrowRight class="h-3 w-3" />
			</a>
		</div>
	</div>
{/if}

<script lang="ts">
	// Threads: who and what appears in which session. A row per character, place, item or
	// faction; a column per session; a line from first appearance to last.
	import { buildThreads, pad, shortDate, type Ref, type Session } from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	const KINDS = [
		{ id: 'cast', label: 'Cast', route: 'characters', colour: 'var(--color-accent-amber)', pick: (s: Session): Ref[] => s.characters },
		{ id: 'places', label: 'Places', route: 'places', colour: 'var(--color-accent-cyan)', pick: (s: Session): Ref[] => s.stops },
		{ id: 'items', label: 'Items', route: 'items', colour: 'var(--color-accent-green)', pick: (s: Session): Ref[] => s.items },
		{ id: 'artifacts', label: 'Artifacts', route: 'artifacts', colour: 'var(--color-accent-purple)', pick: (s: Session): Ref[] => s.artifacts },
		{ id: 'factions', label: 'Factions', route: 'associations', colour: '#ff7a45', pick: (s: Session): Ref[] => s.associations }
	] as const;

	const MIN_CELL = 30;

	let kindId = $state<(typeof KINDS)[number]['id']>('cast');
	let kind = $derived(KINDS.find((k) => k.id === kindId) ?? KINDS[0]);
	let byCount = $state(true);
	// Long campaigns have hundreds of threads: show the top ones until asked for all.
	const TOP = 40;
	let showAll = $state(false);

	let threads = $derived.by(() => {
		const list = buildThreads(sessions, kind.pick);
		// Order of first appearance reads like a cast list; by count shows who matters most.
		return list.sort((a, b) => (byCount ? b.count - a.count || a.first - b.first : a.first - b.first || b.count - a.count));
	});

	let hoverCol = $state<number | null>(null);
	let hoverRow = $state<string | null>(null);
	let focus = $derived(hoverCol !== null ? sessions[hoverCol] : null);
	// Cells widen to fill the panel when there are few sessions.
	let panelWidth = $state(0);
	// A narrower name column on phones leaves room for the marks.
	let LABEL_W = $derived(panelWidth && panelWidth < 520 ? 132 : 200);
	let CELL = $derived(Math.max(sessions.length > 60 ? 8 : MIN_CELL, sessions.length ? Math.floor((panelWidth - LABEL_W) / sessions.length) : MIN_CELL));
	let width = $derived(sessions.length * CELL);
</script>

<div class="border border-border-dim bg-hull">
	<div class="flex flex-wrap items-center justify-between gap-2 border-b border-border-dim px-3 py-1.5">
		<span class="machine-text text-[9px] text-text-muted">DAT-06 // THREADS</span>
		<button type="button" class="machine-text text-[10px] text-accent-amber hover:underline" onclick={() => (byCount = !byCount)}>
			SORT: {byCount ? 'MOST APPEARANCES' : 'FIRST APPEARANCE'}
		</button>
	</div>
	<div class="flex overflow-x-auto border-b border-border-dim">
		{#each KINDS as option (option.id)}
			<button
				type="button"
				class="shrink-0 border-r border-border-dim px-3 py-2 text-[11px] uppercase tracking-wider transition-colors {option.id === kindId ? 'bg-panel-light' : 'text-text-muted hover:text-text-primary'}"
				style:color={option.id === kindId ? option.colour : undefined}
				aria-pressed={option.id === kindId}
				onclick={() => (kindId = option.id)}
			>
				{option.label}
			</button>
		{/each}
	</div>

	{#if threads.length}
		<div class="overflow-x-auto" role="presentation" bind:clientWidth={panelWidth} onmouseleave={() => { hoverCol = null; hoverRow = null; }}>
			<div style:width="{LABEL_W + width}px">
				<!-- Session numbers -->
				<div class="flex border-b border-border-dim">
					<div class="sticky left-0 z-10 shrink-0 bg-hull px-3 machine-text text-[9px] leading-7 text-text-faint" style:width="{LABEL_W}px">
						{threads.length} {kind.label.toUpperCase()}
					</div>
					{#each sessions as session, i (session.id)}
						<a
							href="/chronicle/{session.id}"
							class="shrink-0 text-center machine-text text-[10px] leading-7 {hoverCol === i ? 'bg-accent-amber/15 text-accent-amber' : 'text-text-muted'}"
							style:width="{CELL}px"
							title="{session.title} · {shortDate(session.date)}"
							onmouseenter={() => (hoverCol = i)}
						>
							{CELL >= 20 || session.n % 10 === 0 ? pad(session.n) : ''}
						</a>
					{/each}
				</div>

				{#each showAll ? threads : threads.slice(0, TOP) as thread (thread.ref.id)}
					<div class="flex {hoverRow === thread.ref.id ? 'bg-panel-hover' : ''}" role="presentation" onmouseenter={() => (hoverRow = thread.ref.id)}>
						<div class="sticky left-0 z-10 flex shrink-0 items-center gap-2 border-r border-border-dim px-3 {hoverRow === thread.ref.id ? 'bg-panel-hover' : 'bg-hull'}" style:width="{LABEL_W}px" style:height="{MIN_CELL}px">
							<a href="/database/{kind.route}/{thread.ref.id}" class="min-w-0 flex-1 truncate text-[11px] uppercase tracking-wider text-text-secondary hover:text-accent-amber">
								{thread.ref.name}
							</a>
							<span class="machine-text text-[9px] text-text-faint">{thread.count}</span>
						</div>
						<div class="relative flex" style:height="{MIN_CELL}px">
							<!-- The thread: first appearance to last -->
							<span class="absolute top-1/2 h-px" style:background={kind.colour} style:opacity="0.35"
								style:left="{thread.first * CELL + CELL / 2}px" style:width="{(thread.last - thread.first) * CELL}px"></span>
							{#each sessions as session, i (session.id)}
								<div class="relative flex shrink-0 items-center justify-center {hoverCol === i ? 'bg-accent-amber/[0.07]' : ''}" style:width="{CELL}px" role="presentation" onmouseenter={() => (hoverCol = i)}>
									{#if thread.hits.has(i)}
										<a href="/chronicle/{session.id}" class="block h-3 transition-transform hover:scale-150" style:width="{Math.min(12, CELL - 2)}px" style:background={kind.colour}
											style:box-shadow="0 0 6px {kind.colour}" aria-label="{thread.ref.name} in session {session.n}: {session.title}"></a>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		</div>
		{#if threads.length > TOP}
			<button type="button" class="w-full border-t border-border-dim px-3 py-2 text-left machine-text text-[10px] text-accent-amber hover:bg-panel-hover" onclick={() => (showAll = !showAll)}>
				{showAll ? `SHOW TOP ${TOP}` : `SHOW ALL ${threads.length}`}
			</button>
		{/if}
	{:else}
		<p class="px-4 py-8 text-center machine-text text-text-muted">NO {kind.label.toUpperCase()} LINKED TO ANY SESSION YET</p>
	{/if}

	<div class="min-h-[2.75rem] border-t border-border-dim px-3 py-2 text-xs">
		{#if focus}
			<span class="font-display text-[10px] text-accent-amber">SESSION {pad(focus.n)}</span>
			<span class="ml-2 uppercase tracking-wider text-text-primary">{focus.title}</span>
			<span class="ml-2 text-text-muted">{focus.brief}</span>
		{:else}
			<span class="machine-text text-[10px] text-text-faint">HOVER A COLUMN TO READ THE SESSION · CLICK A MARK TO OPEN ITS LOG</span>
		{/if}
	</div>
</div>

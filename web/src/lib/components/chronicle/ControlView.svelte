<script lang="ts">
	// Mission Control: several Chronicle views combined on one screen. Where the crew is now,
	// the course so far, who is aboard, what they carry, and which threads have gone quiet.
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import { viewHref } from '$lib/chronicle/views';
	import {
		buildPlaceTree,
		buildThreads,
		worldColours,
		daysBetween,
		pad,
		primaryStop,
		shortDate,
		wherePath,
		type Session
	} from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	let tree = $derived(buildPlaceTree(sessions));
	let colours = $derived(worldColours(sessions));
	let latest = $derived(sessions.at(-1) ?? null);
	let latestStop = $derived(latest ? primaryStop(latest) : null);
	let count = $derived(sessions.length);

	const toneOf = (session: Session) => {
		const stop = primaryStop(session);
		return stop ? (colours.get(stop.path[0].id) ?? '#8a7e60') : '#8a7e60';
	};

	// Course strip: one lane per system, one tick per session.
	const STRIP_H = 22;
	let systemIndex = $derived(new Map(tree.roots.map((root, i) => [root.id, i])));
	let course = $derived(
		sessions.map((session, i) => {
			const stop = primaryStop(session);
			const lane = stop ? (systemIndex.get(stop.path[0].id) ?? 0) : 0;
			return { session, x: ((i + 0.5) / count) * 100, y: lane * STRIP_H + STRIP_H / 2, tone: toneOf(session) };
		})
	);

	let cast = $derived(buildThreads(sessions, (s) => s.characters).sort((a, b) => b.count - a.count));
	let crew = $derived(cast.slice(0, 6));
	// Characters who mattered (two or more sessions) but have not been seen for a while.
	let quiet = $derived(
		cast
			.filter((t) => t.count >= 2 && count - 1 - t.last >= 2)
			.sort((a, b) => a.last - b.last)
			.slice(0, 5)
	);
	let cargo = $derived(
		[
			...buildThreads(sessions, (s) => s.artifacts).map((t) => ({ ...t, relic: true })),
			...buildThreads(sessions, (s) => s.items).map((t) => ({ ...t, relic: false }))
		].sort((a, b) => a.first - b.first)
	);
	let ports = $derived(
		[...tree.byId.values()]
			.filter((n) => n.sessions.length)
			.sort((a, b) => b.sessions.length - a.sessions.length)
			.slice(0, 6)
	);
	let span = $derived(daysBetween(sessions[0]?.date ?? null, latest?.date ?? null));
</script>

{#snippet more(view: Parameters<typeof viewHref>[0], label: string)}
	<a href={viewHref(view)} class="flex items-center gap-1 machine-text text-[9px] text-accent-cyan hover:underline">
		{label} <ArrowRight class="h-3 w-3" />
	</a>
{/snippet}

<div class="grid grid-cols-1 gap-3 lg:grid-cols-3">
	<!-- Where the story stands -->
	{#if latest}
		<section class="relative overflow-hidden border border-accent-amber/25 bg-panel p-4 lg:col-span-2">
			<div class="flex items-center justify-between">
				<p class="machine-text text-[9px] text-text-muted">LAST TRANSMISSION · SESSION {pad(latest.n)} · {shortDate(latest.date)}</p>
				{@render more('replay', 'REPLAY THE VOYAGE')}
			</div>
			{#if latestStop}
				<p class="mt-3 text-[11px] uppercase tracking-[0.2em]" style:color={toneOf(latest)}>▸ {wherePath(latestStop)}</p>
			{/if}
			<h2 class="mt-1 font-display text-2xl uppercase leading-tight text-text-primary text-glow-amber">{latest.title}</h2>
			<p class="mt-2 max-w-2xl text-sm leading-relaxed text-text-secondary">{latest.brief}</p>
			<div class="mt-3 flex flex-wrap items-center gap-1.5">
				{#each latest.characters as character (character.id)}
					<span class="border border-border-subtle px-1.5 py-0.5 text-[10px] uppercase tracking-wider text-text-muted">{character.name}</span>
				{/each}
				<a href="/chronicle/{latest.id}" class="ml-auto flex items-center gap-1 machine-text text-[10px] text-accent-amber hover:underline">
					OPEN LOG <ArrowRight class="h-3 w-3" />
				</a>
			</div>
		</section>
	{/if}

	<section class="grid grid-cols-2 gap-px border border-border-dim bg-border-dim">
		{#each [['SESSIONS', count], ['WORLDS', tree.roots.length], ['PLACES', tree.byId.size], ['CAST', cast.length], ['DAYS UNDER WAY', span ?? '—'], ['RELICS & ITEMS', cargo.length]] as [label, value] (label)}
			<div class="bg-hull px-3 py-2.5">
				<p class="machine-text text-[9px] text-text-muted">{label}</p>
				<p class="mt-0.5 font-display text-lg text-accent-amber">{value}</p>
			</div>
		{/each}
	</section>

	<!-- Course so far -->
	<section class="border border-border-dim bg-hull lg:col-span-3">
		<header class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<p class="machine-text text-[9px] text-text-muted">COURSE SO FAR</p>
			<div class="flex gap-4">{@render more('voyage', 'FLIGHT PATH')}{@render more('starchart', 'STAR CHART')}</div>
		</header>
		<div class="flex">
			<div class="shrink-0 border-r border-border-dim py-2">
				{#each tree.roots as root (root.id)}
					<p class="flex items-center gap-1.5 px-3 font-display text-[10px] uppercase tracking-wider" style:height="{STRIP_H}px" style:color={colours.get(root.id)}>
						<span class="status-dot"></span>{root.name}
					</p>
				{/each}
			</div>
			<div class="relative min-w-0 flex-1 py-2">
				<svg viewBox="0 0 100 {tree.roots.length * STRIP_H}" preserveAspectRatio="none" class="absolute inset-x-0 top-2 w-full" style:height="{tree.roots.length * STRIP_H}px" aria-hidden="true">
					{#each tree.roots as root, i (root.id)}
						<line x1="0" x2="100" y1={i * STRIP_H + STRIP_H / 2} y2={i * STRIP_H + STRIP_H / 2} stroke={colours.get(root.id)} stroke-opacity="0.15" vector-effect="non-scaling-stroke" />
					{/each}
					<polyline points={course.map((c) => `${c.x},${c.y}`).join(' ')} fill="none" stroke="var(--color-accent-amber)" stroke-opacity="0.6" stroke-width="1.5" vector-effect="non-scaling-stroke" />
				</svg>
				<div class="relative" style:height="{tree.roots.length * STRIP_H}px">
					{#each course as stop (stop.session.id)}
						<a
							href="/chronicle/{stop.session.id}"
							class="absolute h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 transition-transform hover:scale-150"
							style:left="{stop.x}%" style:top="{stop.y}px" style:background={stop.tone} style:box-shadow="0 0 6px {stop.tone}"
							title="Session {stop.session.n}: {stop.session.title}"
							aria-label="Session {stop.session.n}: {stop.session.title}"
						></a>
					{/each}
				</div>
			</div>
		</div>
	</section>

	<!-- Crew -->
	<section class="border border-border-dim bg-hull">
		<header class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<p class="machine-text text-[9px] text-text-muted">CREW MANIFEST</p>
			{@render more('threads', 'THREADS')}
		</header>
		<ul class="space-y-2 p-3">
			{#each crew as member (member.ref.id)}
				<li>
					<div class="flex items-baseline justify-between gap-2 text-[11px]">
						<a href="/database/characters/{member.ref.id}" class="truncate uppercase tracking-wider text-text-primary hover:text-accent-amber">{member.ref.name}</a>
						<span class="shrink-0 machine-text text-[9px] text-text-muted">{member.count}/{count}</span>
					</div>
					<div class="mt-1 flex gap-px">
						{#each sessions as session, i (session.id)}
							<span class="h-1.5 flex-1 {member.hits.has(i) ? 'bg-accent-amber' : 'bg-panel-light'}"></span>
						{/each}
					</div>
				</li>
			{/each}
		</ul>
	</section>

	<!-- Cargo -->
	<section class="border border-border-dim bg-hull">
		<header class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<p class="machine-text text-[9px] text-text-muted">CARGO & RELICS</p>
			{@render more('timeline', 'TIMELINE')}
		</header>
		<ul class="p-3 text-[11px]">
			{#each cargo as thing (thing.ref.id)}
				<li class="flex items-baseline gap-2 py-1">
					<span class="status-dot shrink-0 self-center {thing.relic ? 'text-accent-purple' : 'text-accent-green'}"></span>
					<a href="/database/{thing.relic ? 'artifacts' : 'items'}/{thing.ref.id}" class="truncate uppercase tracking-wider hover:text-accent-amber {thing.relic ? 'text-accent-purple' : 'text-text-primary'}">{thing.ref.name}</a>
					<a href="/chronicle/{sessions[thing.first].id}" class="ml-auto shrink-0 machine-text text-[9px] text-text-muted hover:text-accent-amber">FIRST SEEN S{pad(sessions[thing.first].n)}</a>
				</li>
			{:else}
				<li class="machine-text text-[10px] text-text-faint">NOTHING IN THE HOLD YET</li>
			{/each}
		</ul>
	</section>

	<!-- Ports and quiet threads -->
	<div class="flex flex-col gap-3">
		<section class="border border-border-dim bg-hull">
			<header class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
				<p class="machine-text text-[9px] text-text-muted">PORTS OF CALL</p>
				{@render more('atlas', 'ATLAS')}
			</header>
			<ul class="p-3 text-[11px]">
				{#each ports as port (port.id)}
					<li class="flex items-baseline gap-2 py-0.5">
						<a href="/database/places/{port.id}" class="truncate uppercase tracking-wider text-text-primary hover:text-accent-amber">{port.name}</a>
						<span class="ml-auto shrink-0 machine-text text-[9px] text-text-muted">×{port.sessions.length} · LAST S{pad(port.sessions.at(-1)?.n ?? 0)}</span>
					</li>
				{/each}
			</ul>
		</section>
		{#if quiet.length}
			<section class="border border-border-dim bg-hull">
				<header class="border-b border-border-dim px-3 py-1.5">
					<p class="machine-text text-[9px] text-text-muted">GONE QUIET</p>
				</header>
				<ul class="p-3 text-[11px]">
					{#each quiet as thread (thread.ref.id)}
						<li class="flex items-baseline gap-2 py-0.5">
							<a href="/database/characters/{thread.ref.id}" class="truncate uppercase tracking-wider text-text-secondary hover:text-accent-amber">{thread.ref.name}</a>
							<a href="/chronicle/{sessions[thread.last].id}" class="ml-auto shrink-0 machine-text text-[9px] text-accent-red/80 hover:text-accent-amber">
								NOT SEEN SINCE S{pad(sessions[thread.last].n)}
							</a>
						</li>
					{/each}
				</ul>
			</section>
		{/if}
	</div>
</div>

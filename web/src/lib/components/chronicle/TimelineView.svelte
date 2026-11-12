<script lang="ts">
	// Timeline: sessions along a spine of time. Each change of world opens an arc with a banner;
	// moves within a world, long breaks between game nights and new years are marked on the
	// spine. "Arcs only" folds the story down to its stays, and a banner opens its arc.
	import Rocket from '@lucide/svelte/icons/rocket';
	import MapPin from '@lucide/svelte/icons/map-pin';
	import Users from '@lucide/svelte/icons/users';
	import Gem from '@lucide/svelte/icons/gem';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import {
		buildArcs,
		daysBetween,
		pad,
		primaryStop,
		roman,
		shortDate,
		worldColours,
		type Arc,
		type Session
	} from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	/** Breaks between game nights longer than this are called out. */
	const LONG_BREAK_DAYS = 60;

	let newestFirst = $state(false);
	let arcsOnly = $state(false);
	/** Arcs opened by hand while "arcs only" is on. */
	let opened = $state<number[]>([]);

	let colours = $derived(worldColours(sessions));
	let arcs = $derived(buildArcs(sessions, colours));

	const starOf = (arc: Arc) =>
		arc.sessions.flatMap((s) => s.stops).find((stop) => stop.path[0].id === arc.world?.id)?.star ?? null;

	type Row =
		| { kind: 'arc'; key: string; arc: Arc; days: number | null; travel: boolean }
		| { kind: 'year'; key: string; year: number }
		| { kind: 'break'; key: string; days: number }
		| { kind: 'move'; key: string; place: string; colour: string }
		| { kind: 'session'; key: string; session: Session; arc: Arc; side: number };

	// The spine as a list of rows, built oldest first and reversed for newest first.
	let rows = $derived.by(() => {
		const out: Row[] = [];
		let side = 0;
		let lastYear: number | null = null;
		arcs.forEach((arc, a) => {
			const prevArc = arcs[a - 1];
			const expanded = !arcsOnly || opened.includes(arc.n);
			const arcRows: Row[] = [];
			arc.sessions.forEach((session, i) => {
				const prev = i > 0 ? arc.sessions[i - 1] : prevArc?.sessions.at(-1);
				const year = session.date?.getUTCFullYear() ?? null;
				if (expanded && year !== null && year !== lastYear) {
					arcRows.push({ kind: 'year', key: `y${year}-${session.id}`, year });
				}
				if (year !== null) lastYear = year;
				if (!expanded) return;
				const gap = prev ? daysBetween(prev.date, session.date) : null;
				if (i > 0 && gap !== null && gap > LONG_BREAK_DAYS) arcRows.push({ kind: 'break', key: `b${session.id}`, days: gap });
				const stop = primaryStop(session);
				const prevStop = i > 0 ? primaryStop(arc.sessions[i - 1]) : null;
				if (stop && prevStop && stop.id !== prevStop.id) {
					arcRows.push({ kind: 'move', key: `m${session.id}`, place: stop.name, colour: arc.colour });
				}
				arcRows.push({ kind: 'session', key: session.id, session, arc, side: side++ });
			});
			const days = prevArc ? daysBetween(prevArc.sessions.at(-1)?.date ?? null, arc.sessions[0].date) : null;
			const travel = !!prevArc;
			out.push({ kind: 'arc', key: `a${arc.n}`, arc, days, travel }, ...arcRows);
		});
		if (!newestFirst) return out;
		// Newest first: arcs in reverse, each still opening with its banner.
		const groups: Row[][] = [];
		for (const row of out) {
			if (row.kind === 'arc') groups.push([row]);
			else groups.at(-1)?.push(row);
		}
		return groups.reverse().flatMap(([banner, ...rest]) => [banner, ...rest.reverse()]);
	});

	function toggleArc(n: number) {
		opened = opened.includes(n) ? opened.filter((x) => x !== n) : [...opened, n];
	}

	const months = (days: number) => (days >= 60 ? `${Math.round(days / 30)} months` : `${days} days`);
</script>

<div class="flex flex-wrap items-center justify-between gap-2 border border-border-dim bg-hull px-3 py-1.5">
	<span class="machine-text text-[9px] text-text-muted">LOG-04 // TIMELINE · {arcs.length} ARCS · {sessions.length} SESSIONS</span>
	<div class="flex gap-4">
		<button type="button" class="machine-text text-[10px] text-accent-amber hover:underline" aria-pressed={arcsOnly} onclick={() => { arcsOnly = !arcsOnly; opened = []; }}>
			{arcsOnly ? 'SHOW ALL SESSIONS' : 'ARCS ONLY'}
		</button>
		<button type="button" class="machine-text text-[10px] text-accent-amber hover:underline" onclick={() => (newestFirst = !newestFirst)}>
			{newestFirst ? 'NEWEST FIRST ↓' : 'OLDEST FIRST ↓'}
		</button>
	</div>
</div>

<div>
	{#each rows as row (row.key)}
		{#if row.kind === 'arc'}
			{@const arc = row.arc}
			{@const star = starOf(arc)}
			{@const open = !arcsOnly || opened.includes(arc.n)}
			<div class="tl-row">
				<div class="tl-spine"><span class="tl-line"></span></div>
				<div class="col-start-2 row-start-1 py-3 md:col-span-3 md:col-start-1">
					{#if row.travel}
						<p class="mb-2 flex items-center justify-center gap-1.5 text-[10px] uppercase tracking-wider text-text-muted">
							<Rocket class="h-3 w-3" style="color: {arc.colour}" />
							Course set for {arc.world?.name ?? 'parts unrecorded'}{row.days ? ` · ${months(row.days)} later` : ''}
						</p>
					{/if}
					<button
						type="button"
						class="banner relative mx-auto flex w-full max-w-2xl items-center gap-3 border bg-void px-4 py-2.5 text-left transition-colors md:w-auto md:min-w-[26rem]"
						style:--tone={arc.colour}
						disabled={!arcsOnly}
						aria-expanded={arcsOnly ? open : undefined}
						onclick={() => toggleArc(arc.n)}
					>
						<span class="font-display text-[11px] tracking-[0.3em] text-text-muted">{roman(arc.n)}</span>
						<span class="min-w-0 flex-1">
							<span class="block truncate font-display text-base uppercase tracking-[0.15em]" style:color={arc.colour}>{arc.world?.name ?? 'Unrecorded'}</span>
							<span class="block machine-text text-[9px] text-text-muted">
								{star ? `${star} · ` : ''}{arc.sessions.length} session{arc.sessions.length > 1 ? 's' : ''} · {shortDate(arc.sessions[0].date)}{arc.sessions.length > 1 ? ` – ${shortDate(arc.sessions.at(-1)?.date ?? null)}` : ''}
							</span>
						</span>
						{#if arcsOnly}
							<ChevronDown class="h-4 w-4 shrink-0 text-text-muted transition-transform {open ? 'rotate-180' : ''}" />
						{/if}
					</button>
				</div>
			</div>
		{:else if row.kind === 'year'}
			<div class="tl-row">
				<div class="tl-spine"><span class="tl-line"></span></div>
				<div class="col-start-2 row-start-1 py-2 md:col-span-3 md:col-start-1 md:text-center">
					<span class="relative border border-border-subtle bg-void px-2 py-0.5 font-display text-[11px] tracking-widest text-text-secondary">{row.year}</span>
				</div>
			</div>
		{:else if row.kind === 'break'}
			<div class="tl-row">
				<div class="tl-spine"><span class="tl-line tl-line-dashed"></span></div>
				<p class="col-start-2 row-start-1 py-2 text-[10px] uppercase tracking-wider text-text-faint md:col-span-3 md:col-start-1 md:text-center">
					<span class="relative bg-void px-2">{months(row.days)} between sessions</span>
				</p>
			</div>
		{:else if row.kind === 'move'}
			<div class="tl-row">
				<div class="tl-spine"><span class="tl-line"></span></div>
				<p class="col-start-2 row-start-1 py-1 text-[10px] uppercase tracking-wider md:col-span-3 md:col-start-1 md:text-center" style:color={row.colour}>
					<span class="relative bg-void px-2">→ {row.place}</span>
				</p>
			</div>
		{:else}
			{@const session = row.session}
			{@const stop = primaryStop(session)}
			{@const treasures = [...session.artifacts, ...session.items]}
			{@const left = row.side % 2 === 0}
			<div class="tl-row">
				<div class="tl-spine">
					<span class="tl-line"></span>
					<span class="tl-node" style:border-color={row.arc.colour} style:color={row.arc.colour}>{pad(session.n)}</span>
				</div>
				<a
					href="/chronicle/{session.id}"
					class="group col-start-2 row-start-1 my-2 block border border-border-dim bg-panel p-3 transition-all hover:border-accent-amber/40 hover:bg-panel-hover {left
						? 'md:col-start-1'
						: 'md:col-start-3'}"
					style:border-left-color={row.arc.colour}
					style:border-left-width="2px"
				>
					<div class="flex flex-wrap items-baseline justify-between gap-x-3">
						<span class="machine-text text-[10px] text-accent-amber">{shortDate(session.date)}</span>
						{#if stop}
							<span class="flex items-center gap-1 text-[10px] uppercase tracking-wider" style:color={row.arc.colour}>
								<MapPin class="h-3 w-3" />{stop.name}
							</span>
						{/if}
					</div>
					<h2 class="mt-1 text-sm font-bold uppercase tracking-wider text-text-primary transition-colors group-hover:text-accent-amber">
						{session.title}
					</h2>
					{#if session.brief}
						<p class="mt-1 line-clamp-4 text-xs leading-relaxed text-text-secondary">{session.brief}</p>
					{/if}
					{#if session.characters.length || treasures.length}
						<div class="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[10px] uppercase tracking-wider text-text-muted">
							{#if session.characters.length}
								<span class="flex items-center gap-1">
									<Users class="h-3 w-3 shrink-0" />
									{session.characters.slice(0, 3).map((c) => c.name).join(', ')}{session.characters.length > 3 ? ` +${session.characters.length - 3}` : ''}
								</span>
							{/if}
							{#if treasures.length}
								<span class="flex items-center gap-1 text-accent-purple">
									<Gem class="h-3 w-3 shrink-0" />{treasures.slice(0, 3).map((t) => t.name).join(', ')}{treasures.length > 3 ? ` +${treasures.length - 3}` : ''}
								</span>
							{/if}
						</div>
					{/if}
				</a>
			</div>
		{/if}
	{/each}
</div>

<style>
	.tl-row {
		display: grid;
		grid-template-columns: 2.75rem minmax(0, 1fr);
		column-gap: 0.75rem;
	}
	.tl-spine {
		position: relative;
		grid-column-start: 1;
		grid-row-start: 1;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.tl-line {
		position: absolute;
		top: 0;
		bottom: 0;
		left: 50%;
		width: 1px;
		background: var(--color-border-accent);
	}
	.tl-line-dashed {
		background: repeating-linear-gradient(to bottom, var(--color-border-accent) 0 3px, transparent 3px 7px);
	}
	.tl-node {
		position: relative;
		display: flex;
		height: 2rem;
		width: 2rem;
		align-items: center;
		justify-content: center;
		border: 1px solid;
		background: var(--color-void);
		font-family: var(--font-display);
		font-size: 10px;
		box-shadow: 0 0 8px currentColor;
	}
	.banner {
		border-color: color-mix(in srgb, var(--tone) 45%, transparent);
		box-shadow: inset 3px 0 0 var(--tone);
	}
	.banner:not(:disabled):hover {
		border-color: var(--tone);
	}
	@media (min-width: 48rem) {
		.tl-row {
			grid-template-columns: minmax(0, 1fr) 2.75rem minmax(0, 1fr);
		}
		.tl-spine {
			grid-column-start: 2;
		}
	}
</style>

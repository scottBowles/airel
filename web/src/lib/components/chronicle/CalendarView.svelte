<script lang="ts">
	// Calendar: when the group played. One strip per year, a column per week and a row per
	// weekday, with each game night lit in the colour of the world it was set on. Hovering a
	// night reads the session; clicking opens its log.
	import {
		dayKey,
		daysBetween,
		pad,
		sessionColour,
		sessionsByDay,
		sessionWorld,
		shortDate,
		worldColours,
		type Session
	} from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	const CELL = 12;
	const GAP = 2;
	const STEP = CELL + GAP;
	const MONTHS = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'];

	let dated = $derived(sessions.filter((s): s is Session & { date: Date } => !!s.date));
	let colours = $derived(worldColours(sessions));
	let byDay = $derived(sessionsByDay(dated));

	type Night = { session: Session; col: number; row: number };

	// Every year from the first game night to the last, with each night placed on its week.
	let years = $derived.by(() => {
		if (!dated.length) return [];
		const first = dated[0].date.getUTCFullYear();
		const last = dated.at(-1)!.date.getUTCFullYear();
		const out = [];
		for (let year = first; year <= last; year++) {
			const jan1 = Date.UTC(year, 0, 1);
			const offset = new Date(jan1).getUTCDay();
			const days = (Date.UTC(year + 1, 0, 1) - jan1) / 86_400_000;
			const nights: Night[] = [];
			for (let d = 0; d < days; d++) {
				const date = new Date(jan1 + d * 86_400_000);
				const found = byDay.get(dayKey(year, date.getUTCMonth(), date.getUTCDate()));
				if (found) nights.push({ session: found[0], col: Math.floor((d + offset) / 7), row: (d + offset) % 7 });
			}
			const months = MONTHS.map((label, m) => ({
				label,
				col: Math.floor(((Date.UTC(year, m, 1) - jan1) / 86_400_000 + offset) / 7)
			}));
			const worldsThisYear = [
				...new Map(
					nights
						.map((n) => sessionWorld(n.session))
						.filter((w) => !!w)
						.map((w) => [w.id, w] as const)
				).values()
			];
			out.push({ year, nights, months, weeks: Math.ceil((days + offset) / 7), worlds: worldsThisYear });
		}
		return out;
	});

	let gaps = $derived(
		dated.slice(1).map((s, i) => ({ days: daysBetween(dated[i].date, s.date) ?? 0, before: s }))
	);
	let longest = $derived(gaps.reduce<(typeof gaps)[number] | null>((max, g) => (!max || g.days > max.days ? g : max), null));
	let usual = $derived.by(() => {
		const sorted = gaps.map((g) => g.days).sort((a, b) => a - b);
		return sorted.length ? sorted[Math.floor(sorted.length / 2)] : 0;
	});
	let busiest = $derived(years.reduce<(typeof years)[number] | null>((max, y) => (!max || y.nights.length > max.nights.length ? y : max), null));

	let focus = $state<Session | null>(null);
	const months = (days: number) => (days >= 60 ? `${Math.round(days / 30)} MONTHS` : `${days} DAYS`);
</script>

<div class="grid grid-cols-2 gap-px border border-border-dim bg-border-dim lg:grid-cols-4">
	{#each [['GAME NIGHTS', String(dated.length)], ['USUAL GAP', `${usual} DAYS`], ['LONGEST BREAK', longest ? months(longest.days) : '—'], ['BUSIEST YEAR', busiest ? `${busiest.year} · ${busiest.nights.length}` : '—']] as [label, value] (label)}
		<div class="bg-hull px-3 py-2.5">
			<p class="machine-text text-[9px] text-text-muted">{label}</p>
			<p class="mt-0.5 font-display text-sm text-accent-amber">{value}</p>
		</div>
	{/each}
</div>

<div class="border border-border-dim bg-hull">
	<div class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
		<span class="machine-text text-[9px] text-text-muted">CAL-08 // GAME NIGHTS</span>
		<span class="machine-text text-[9px] text-text-muted">SQUARES ARE COLOURED BY WORLD</span>
	</div>

	<div class="divide-y divide-border-dim" role="presentation" onmouseleave={() => (focus = null)}>
		{#each years as year (year.year)}
			<section class="flex flex-col gap-3 px-3 py-3 xl:flex-row xl:items-start">
				<header class="w-full shrink-0 xl:w-44">
					<h2 class="font-display text-base tracking-widest text-text-primary">{year.year}</h2>
					<p class="machine-text text-[9px] text-text-muted">{year.nights.length ? `${year.nights.length} SESSIONS` : 'NO SESSIONS'}</p>
					<div class="mt-1 flex flex-wrap gap-x-2 gap-y-0.5">
						{#each year.worlds as world (world.id)}
							<span class="flex items-center gap-1 text-[10px] uppercase tracking-wider" style:color={colours.get(world.id)}>
								<span class="status-dot"></span>{world.name}
							</span>
						{/each}
					</div>
				</header>
				<div class="min-w-0 overflow-x-auto">
					<svg width={year.weeks * STEP + 16} height={7 * STEP + 16} class="block" role="img" aria-label="Game nights in {year.year}">
						{#each year.months as month, m (m)}
							<text x={month.col * STEP} y="9" font-size="9" font-family="var(--font-mono)" fill="#6b634a">{month.label}</text>
						{/each}
						<g transform="translate(0 14)">
							{#each { length: year.weeks } as _, col (col)}
								{#each { length: 7 } as __, row (row)}
									<rect x={col * STEP} y={row * STEP} width={CELL} height={CELL} fill="#16161b" />
								{/each}
							{/each}
							{#each year.nights as night (night.session.id)}
								{@const tone = sessionColour(night.session, colours)}
								<a href="/chronicle/{night.session.id}" aria-label="Session {night.session.n}: {night.session.title}">
									<rect
										x={night.col * STEP}
										y={night.row * STEP}
										width={CELL}
										height={CELL}
										fill={tone}
										stroke={focus === night.session ? '#fff' : 'none'}
										role="presentation"
										onmouseenter={() => (focus = night.session)}
										onfocus={() => (focus = night.session)}
									>
										<title>{pad(night.session.n)} · {night.session.title} · {shortDate(night.session.date)}</title>
									</rect>
								</a>
							{/each}
						</g>
					</svg>
				</div>
			</section>
		{/each}
	</div>

	<div class="min-h-[2.75rem] border-t border-border-dim px-3 py-2 text-xs">
		{#if focus}
			<span class="font-display text-[10px]" style:color={sessionColour(focus, colours)}>SESSION {pad(focus.n)}</span>
			<span class="ml-2 machine-text text-[10px] text-text-muted">{shortDate(focus.date)}</span>
			<span class="ml-2 uppercase tracking-wider text-text-primary">{focus.title}</span>
			<span class="ml-2 text-text-muted">{focus.brief}</span>
		{:else}
			<span class="machine-text text-[10px] text-text-faint">
				HOVER A NIGHT TO READ THE SESSION · CLICK TO OPEN ITS LOG{longest ? ` · LONGEST BREAK: ${months(longest.days)} BEFORE SESSION ${pad(longest.before.n)}` : ''}
			</span>
		{/if}
	</div>
</div>

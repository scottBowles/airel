<script lang="ts">
	// Calendar: when the group played. A small month grid per month of the campaign, with
	// game nights lit, plus the rhythm of play (gaps, busiest month).
	import {
		buildPlaceTree,
		colourByOrder,
		dayKey,
		daysBetween,
		monthLabel,
		pad,
		primaryStop,
		sessionsByDay,
		shortDate,
		type Session
	} from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	let dated = $derived(sessions.filter((s): s is Session & { date: Date } => !!s.date));
	let colours = $derived(colourByOrder(buildPlaceTree(sessions).roots.map((r) => r.id)));
	let byDay = $derived(sessionsByDay(dated));

	// Every month from the first session to the last, including months with no play.
	let months = $derived.by(() => {
		if (!dated.length) return [];
		const first = dated[0].date;
		const last = dated.at(-1)!.date;
		const out = [];
		let y = first.getUTCFullYear();
		let m = first.getUTCMonth();
		while (y < last.getUTCFullYear() || (y === last.getUTCFullYear() && m <= last.getUTCMonth())) {
			const start = new Date(Date.UTC(y, m, 1));
			const days = new Date(Date.UTC(y, m + 1, 0)).getUTCDate();
			const cells = Array.from({ length: days }, (_, d) => ({ day: d + 1, sessions: byDay.get(dayKey(y, m, d + 1)) ?? [] }));
			out.push({ year: y, label: monthLabel(start), offset: start.getUTCDay(), cells, count: cells.reduce((n, c) => n + c.sessions.length, 0) });
			if (++m > 11) { m = 0; y++; }
		}
		// Years with no play at all (a stray old document, a long hiatus) are left out.
		const played = out.filter((m) => m.count).map((m) => m.year);
		return out.filter((m) => played.includes(m.year));
	});

	let gaps = $derived(dated.slice(1).map((s, i) => ({ days: daysBetween(dated[i].date, s.date) ?? 0, before: s })));
	let longest = $derived(gaps.reduce<(typeof gaps)[number] | null>((max, g) => (!max || g.days > max.days ? g : max), null));
	let average = $derived(gaps.length ? Math.round(gaps.reduce((n, g) => n + g.days, 0) / gaps.length) : 0);
	let busiest = $derived(months.reduce<(typeof months)[number] | null>((max, m) => (!max || m.count > max.count ? m : max), null));

	const tone = (session: Session) => {
		const stop = primaryStop(session);
		return stop ? (colours.get(stop.path[0].id) ?? '#ffb000') : '#ffb000';
	};
</script>

<div class="grid grid-cols-2 gap-px border border-border-dim bg-border-dim lg:grid-cols-4">
	{#each [['GAME NIGHTS', String(dated.length)], ['USUAL GAP', `${average} DAYS`], ['LONGEST GAP', longest ? `${longest.days} DAYS` : '—'], ['BUSIEST MONTH', busiest ? `${busiest.label} · ${busiest.count}` : '—']] as [label, value] (label)}
		<div class="bg-hull px-3 py-2.5">
			<p class="machine-text text-[9px] text-text-muted">{label}</p>
			<p class="mt-0.5 font-display text-sm text-accent-amber">{value}</p>
		</div>
	{/each}
</div>

<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
	{#each months as month (month.label)}
		<section class="border border-border-dim bg-hull p-3 {month.count ? '' : 'opacity-60'}">
			<header class="flex items-baseline justify-between">
				<h2 class="font-display text-[11px] tracking-widest text-text-primary">{month.label}</h2>
				<span class="machine-text text-[9px] text-text-muted">{month.count ? `${month.count} PLAYED` : 'NO SESSIONS'}</span>
			</header>
			<div class="mt-2 grid grid-cols-7 gap-0.5 text-center">
				{#each ['S', 'M', 'T', 'W', 'T', 'F', 'S'] as day, i (i)}
					<span class="machine-text text-[8px] text-text-faint">{day}</span>
				{/each}
				{#each { length: month.offset } as _, i (i)}<span></span>{/each}
				{#each month.cells as cell (cell.day)}
					{#if cell.sessions.length}
						{@const session = cell.sessions[0]}
						<a
							href="/chronicle/{session.id}"
							class="flex aspect-square items-center justify-center font-display text-[10px] text-void transition-transform hover:scale-110"
							style:background={tone(session)}
							style:box-shadow="0 0 8px {tone(session)}"
							title="Session {session.n}: {session.title}"
						>
							{pad(session.n)}
						</a>
					{:else}
						<span class="flex aspect-square items-center justify-center bg-panel text-[9px] text-text-faint">{cell.day}</span>
					{/if}
				{/each}
			</div>
			<ul class="mt-2 space-y-0.5">
				{#each month.cells.flatMap((c) => c.sessions) as session (session.id)}
					<li>
						<a href="/chronicle/{session.id}" class="flex items-baseline gap-2 text-[11px] text-text-secondary hover:text-accent-amber">
							<span class="machine-text shrink-0 text-[10px]" style:color={tone(session)}>{pad(session.n)}</span>
							<span class="truncate">{session.title}</span>
						</a>
					</li>
				{/each}
			</ul>
		</section>
	{/each}
</div>

{#if longest}
	<p class="machine-text text-[10px] text-text-faint">
		LONGEST GAP: {longest.days} DAYS BEFORE SESSION {pad(longest.before.n)} ({shortDate(longest.before.date)}) · SQUARES ARE COLOURED BY WORLD
	</p>
{/if}

<script lang="ts">
	// Saga: the campaign read as one book. Each stay on a world is a part with its own title
	// page; each session is a chapter. Logs from before the voyage open the book as a prologue.
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import {
		arcBySession,
		buildArcs,
		pad,
		primaryStop,
		roman,
		shortDate,
		wherePath,
		worldColours,
		type Session
	} from '$lib/chronicle/model';

	let { sessions, prologue = [] }: { sessions: Session[]; prologue?: Session[] } = $props();

	let colours = $derived(worldColours(sessions));
	let arcs = $derived(buildArcs(sessions, colours));
	let arcOf = $derived(arcBySession(arcs));

	const paragraphs = (session: Session) =>
		(session.synopsis || session.brief)
			.split(/\n\s*\n/)
			.map((p) => p.trim())
			.filter(Boolean);

	/** The sun a part's world orbits, from any stop on it. */
	const starOf = (arc: (typeof arcs)[number]) =>
		arc.sessions.flatMap((s) => s.stops).find((stop) => stop.path[0].id === arc.world?.id)?.star ?? null;

	let activeId = $state<string | null>(null);
	let activeIndex = $derived(Math.max(0, sessions.findIndex((s) => s.id === activeId)));
	let activeArc = $derived(arcOf.get(sessions[activeIndex]?.id ?? ''));
	let progress = $derived(sessions.length ? ((activeIndex + 1) / sessions.length) * 100 : 0);

	// Track the chapter being read, for the contents rail and progress bar.
	function spy(node: HTMLElement, id: string) {
		const observer = new IntersectionObserver(
			(entries) => {
				if (entries.some((entry) => entry.isIntersecting)) activeId = id;
			},
			{ rootMargin: '-30% 0px -60% 0px' }
		);
		observer.observe(node);
		return { destroy: () => observer.disconnect() };
	}

	function jump(event: Event, anchor: string) {
		event.preventDefault();
		document.getElementById(anchor)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
	}

	// Keep the active chapter visible in the contents rail as the reader scrolls.
	let rail: HTMLElement | undefined = $state();
	$effect(() => {
		const row = rail?.querySelector<HTMLElement>(`[data-chapter="${sessions[activeIndex]?.id}"]`);
		if (!rail || !row) return;
		const top = row.offsetTop - rail.scrollTop;
		if (top < 40 || top > rail.clientHeight - 40) rail.scrollTop = row.offsetTop - rail.clientHeight / 3;
	});
</script>

<div class="grid grid-cols-1 gap-4 lg:grid-cols-[250px_minmax(0,1fr)]">
	<!-- Contents: every part, with the chapters of the part being read -->
	<aside class="hidden lg:block">
		<div class="sticky top-0 border border-border-dim bg-hull">
			<p class="border-b border-border-dim px-3 py-1.5 machine-text text-[9px] text-text-muted">
				CONTENTS · {arcs.length} PARTS
			</p>
			<ol bind:this={rail} class="relative max-h-[70vh] overflow-y-auto py-1">
				{#if prologue.length}
					<li>
						<a href="#saga-prologue" onclick={(e) => jump(e, 'saga-prologue')} class="flex gap-2 px-3 py-1 font-display text-[10px] uppercase tracking-widest text-text-muted hover:text-text-primary">
							Prologue
						</a>
					</li>
				{/if}
				{#each arcs as arc (arc.n)}
					{@const open = arc === activeArc}
					<li>
						<a
							href="#part-{arc.n}"
							onclick={(e) => jump(e, `part-${arc.n}`)}
							class="flex items-center gap-1.5 px-3 py-1 font-display text-[10px] uppercase tracking-widest transition-colors hover:brightness-125"
							style:color={arc.colour}
							style:opacity={open ? 1 : 0.75}
						>
							<ChevronRight class="h-3 w-3 shrink-0 transition-transform {open ? 'rotate-90' : ''}" />
							<span class="w-6 shrink-0 text-text-faint">{roman(arc.n)}</span>
							<span class="min-w-0 flex-1 truncate">{arc.world?.name ?? 'Unrecorded'}</span>
							<span class="shrink-0 machine-text text-[9px] text-text-faint">{arc.sessions.length}</span>
						</a>
						{#if open}
							<ol class="mb-1 border-l border-border-dim ml-4">
								{#each arc.sessions as session (session.id)}
									<li data-chapter={session.id}>
										<a
											href="#chapter-{session.id}"
											onclick={(e) => jump(e, `chapter-${session.id}`)}
											class="flex gap-2 py-0.5 pl-3 pr-3 text-[11px] transition-colors {session.id === sessions[activeIndex]?.id
												? 'bg-accent-amber/10 text-accent-amber'
												: 'text-text-muted hover:text-text-primary'}"
										>
											<span class="machine-text shrink-0 text-[10px]">{pad(session.n)}</span>
											<span class="truncate">{session.title}</span>
										</a>
									</li>
								{/each}
							</ol>
						{/if}
					</li>
				{/each}
			</ol>
			<div class="border-t border-border-dim px-3 py-2">
				<div class="h-1 bg-void"><div class="h-full bg-accent-amber transition-all" style:width="{progress}%"></div></div>
				<p class="mt-1 machine-text text-[9px] text-text-muted">CHAPTER {activeIndex + 1} OF {sessions.length}</p>
			</div>
		</div>
	</aside>

	<!-- The story -->
	<article class="min-w-0 border border-border-dim bg-hull">
		<div class="sticky top-0 z-10 border-b border-border-dim bg-hull lg:hidden">
			<div class="h-0.5 bg-void"><div class="h-full bg-accent-amber transition-all" style:width="{progress}%"></div></div>
			<label class="flex items-center gap-2 px-3 py-1.5 machine-text text-[9px] text-text-muted">
				PART
				<select
					class="min-w-0 flex-1 border border-border-subtle bg-void px-2 py-1 text-[11px] uppercase tracking-wider text-text-primary"
					value={activeArc?.n ?? 1}
					onchange={(e) => jump(e, `part-${e.currentTarget.value}`)}
				>
					{#each arcs as arc (arc.n)}
						<option value={arc.n}>{roman(arc.n)} · {arc.world?.name ?? 'Unrecorded'} ({arc.sessions.length})</option>
					{/each}
				</select>
			</label>
		</div>

		<header class="border-b border-border-dim px-5 py-10 text-center sm:px-10">
			<p class="machine-text text-[10px] text-text-muted">THE CHRONICLE OF THE</p>
			<h2 class="title-display mt-1 text-2xl text-accent-amber text-glow-amber">KSS KONTULARIEN</h2>
			<p class="mt-2 text-xs text-text-secondary">
				{arcs.length} parts · {sessions.length} chapters · {shortDate(sessions[0]?.date ?? null)} to {shortDate(sessions.at(-1)?.date ?? null)}
			</p>
		</header>

		{#if prologue.length}
			<section id="saga-prologue" class="mx-auto max-w-[70ch] scroll-mt-14 border-b border-border-dim px-5 py-10 sm:px-10">
				<p class="font-display text-[10px] tracking-[0.3em] text-text-muted">PROLOGUE</p>
				{#each prologue as entry (entry.id)}
					<h3 class="mt-2 font-display text-xl uppercase leading-snug tracking-wider text-text-primary">{entry.title}</h3>
					<div class="mt-5 space-y-4 text-[15px] leading-8 text-text-secondary">
						{#each paragraphs(entry) as paragraph, i (i)}
							<p>{paragraph}</p>
						{/each}
					</div>
					<a href="/chronicle/{entry.id}" class="mt-4 inline-flex items-center gap-1 machine-text text-[10px] text-accent-amber hover:underline">
						FULL DOCUMENT <ArrowRight class="h-3 w-3" />
					</a>
				{/each}
			</section>
		{/if}

		{#each arcs as arc (arc.n)}
			{@const star = starOf(arc)}
			<!-- Part title page -->
			<section id="part-{arc.n}" class="scroll-mt-14 border-b border-border-dim px-5 py-14 text-center sm:px-10" style:--tone={arc.colour}>
				<p class="font-display text-[11px] tracking-[0.4em] text-text-muted">PART {roman(arc.n)}</p>
				<h3 class="part-title mt-3 font-display text-3xl uppercase tracking-[0.15em] sm:text-4xl" style:color={arc.colour}>
					{arc.world?.name ?? 'Unrecorded'}
				</h3>
				{#if star}
					<p class="mt-2 text-[11px] uppercase tracking-[0.3em] text-text-muted">{star}</p>
				{/if}
				<p class="mt-4 text-xs text-text-secondary">
					{arc.sessions.length} chapter{arc.sessions.length > 1 ? 's' : ''} ·
					{shortDate(arc.sessions[0].date)}{arc.sessions.length > 1 ? ` to ${shortDate(arc.sessions.at(-1)?.date ?? null)}` : ''}
				</p>
			</section>

			{#each arc.sessions as session, i (session.id)}
				{@const stop = primaryStop(session)}
				{@const prevStop = i > 0 ? primaryStop(arc.sessions[i - 1]) : null}
				{#if stop && prevStop && stop.id !== prevStop.id}
					<p class="px-5 pt-8 text-center text-xs italic tracking-wider" style:color={arc.colour}>— on to {stop.name} —</p>
				{/if}
				<section id="chapter-{session.id}" use:spy={session.id} class="mx-auto max-w-[70ch] scroll-mt-14 px-5 py-10 sm:px-10">
					<p class="font-display text-[10px] tracking-[0.3em] text-text-muted">CHAPTER {pad(session.n)}</p>
					<h4 class="mt-2 font-display text-xl uppercase leading-snug tracking-wider text-accent-amber sm:text-2xl">{session.title}</h4>
					<p class="mt-2 text-[11px] uppercase tracking-wider" style:color={arc.colour}>
						{stop ? `${wherePath(stop)} — ` : ''}{shortDate(session.date)}
					</p>

					<div class="saga-body mt-6 space-y-4 text-[15px] leading-8 text-text-primary">
						{#each paragraphs(session) as paragraph, j (j)}
							<p class:lead={j === 0}>{paragraph}</p>
						{:else}
							<p class="italic text-text-faint">No synopsis has been written for this session yet.</p>
						{/each}
					</div>

					<div class="mt-6 flex flex-wrap items-center gap-1.5">
						{#each session.characters as character (character.id)}
							<a href="/database/characters/{character.id}" class="border border-border-subtle px-1.5 py-0.5 text-[10px] uppercase tracking-wider text-text-muted hover:border-accent-amber hover:text-accent-amber">{character.name}</a>
						{/each}
						{#each session.artifacts as artifact (artifact.id)}
							<a href="/database/artifacts/{artifact.id}" class="border border-accent-purple/40 px-1.5 py-0.5 text-[10px] uppercase tracking-wider text-accent-purple hover:border-accent-purple">{artifact.name}</a>
						{/each}
						<a href="/chronicle/{session.id}" class="ml-auto flex items-center gap-1 machine-text text-[10px] text-accent-amber hover:underline">
							FULL LOG <ArrowRight class="h-3 w-3" />
						</a>
					</div>
					{#if i < arc.sessions.length - 1}
						<p class="mt-10 text-center tracking-[1em] text-text-faint" aria-hidden="true">◆◆◆</p>
					{/if}
				</section>
			{/each}
		{/each}
	</article>
</div>

<style>
	.part-title {
		text-shadow: 0 0 24px color-mix(in srgb, var(--tone) 40%, transparent);
	}
	.saga-body .lead::first-letter {
		float: left;
		margin: 0.35rem 0.6rem 0 0;
		font-family: var(--font-display);
		font-size: 3rem;
		line-height: 0.8;
		color: var(--color-accent-amber);
		text-shadow: 0 0 12px rgba(255, 176, 0, 0.4);
	}
</style>

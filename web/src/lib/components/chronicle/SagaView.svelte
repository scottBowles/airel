<script lang="ts">
	// Saga: the campaign read as one continuous story, a chapter per session.
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import { pad, primaryStop, shortDate, wherePath, type Session } from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	let chapters = $derived(
		sessions.map((session, i) => {
			const stop = primaryStop(session);
			const prevStop = i > 0 ? primaryStop(sessions[i - 1]) : null;
			return {
				session,
				stop,
				paragraphs: (session.synopsis || session.brief).split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean),
				// A line of travel between chapters when the story moves somewhere new.
				interlude: stop && prevStop && stop.id !== prevStop.id ? stop.name : null
			};
		})
	);

	let activeId = $state<string | null>(null);
	let activeIndex = $derived(Math.max(0, sessions.findIndex((s) => s.id === activeId)));
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

	function jump(event: MouseEvent, id: string) {
		event.preventDefault();
		document.getElementById(`chapter-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
	}
</script>

<div class="grid gap-4 lg:grid-cols-[230px_minmax(0,1fr)]">
	<!-- Contents -->
	<aside class="hidden lg:block">
		<div class="sticky top-0 border border-border-dim bg-hull">
			<p class="border-b border-border-dim px-3 py-1.5 machine-text text-[9px] text-text-muted">CONTENTS</p>
			<ol class="max-h-[70vh] overflow-y-auto py-1">
				{#each sessions as session (session.id)}
					<li>
						<a
							href="#chapter-{session.id}"
							onclick={(e) => jump(e, session.id)}
							class="flex gap-2 px-3 py-1 text-[11px] transition-colors {session.id === sessions[activeIndex]?.id
								? 'bg-accent-amber/10 text-accent-amber'
								: 'text-text-muted hover:text-text-primary'}"
						>
							<span class="machine-text shrink-0 text-[10px]">{pad(session.n)}</span>
							<span class="truncate">{session.title}</span>
						</a>
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
	<article class="border border-border-dim bg-hull">
		<div class="sticky top-0 z-10 h-0.5 bg-void lg:hidden"><div class="h-full bg-accent-amber transition-all" style:width="{progress}%"></div></div>
		<header class="border-b border-border-dim px-5 py-8 text-center sm:px-10">
			<p class="machine-text text-[10px] text-text-muted">THE CHRONICLE OF THE</p>
			<h2 class="title-display mt-1 text-2xl text-accent-amber text-glow-amber">KSS KONTULARIEN</h2>
			<p class="mt-2 text-xs text-text-secondary">
				{sessions.length} chapters · {shortDate(sessions[0]?.date ?? null)} to {shortDate(sessions.at(-1)?.date ?? null)}
			</p>
		</header>

		{#each chapters as chapter (chapter.session.id)}
			{@const session = chapter.session}
			{#if chapter.interlude}
				<p class="px-5 pt-8 text-center text-xs italic tracking-wider text-accent-cyan/80">
					— the Kontularien makes for {chapter.interlude} —
				</p>
			{/if}
			<section id="chapter-{session.id}" use:spy={session.id} class="mx-auto max-w-[70ch] scroll-mt-4 px-5 py-10 sm:px-10">
				<p class="font-display text-[10px] tracking-[0.3em] text-text-muted">CHAPTER {pad(session.n)}</p>
				<h3 class="mt-2 font-display text-xl uppercase leading-snug tracking-wider text-accent-amber sm:text-2xl">{session.title}</h3>
				<p class="mt-2 text-[11px] uppercase tracking-wider text-accent-cyan">
					{chapter.stop ? `${wherePath(chapter.stop)} — ` : ''}{shortDate(session.date)}
				</p>

				<div class="saga-body mt-6 space-y-4 text-[15px] leading-8 text-text-primary">
					{#each chapter.paragraphs as paragraph, i (i)}
						<p class:lead={i === 0}>{paragraph}</p>
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
				<p class="mt-10 text-center tracking-[1em] text-text-faint" aria-hidden="true">◆◆◆</p>
			</section>
		{/each}
	</article>
</div>

<style>
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

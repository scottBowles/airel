<script lang="ts">
	// Timeline: sessions along a spine of time, with course changes and the gaps between
	// game nights called out between them.
	import Rocket from '@lucide/svelte/icons/rocket';
	import MapPin from '@lucide/svelte/icons/map-pin';
	import Users from '@lucide/svelte/icons/users';
	import Gem from '@lucide/svelte/icons/gem';
	import {
		buildPlaceTree,
		colourByOrder,
		daysBetween,
		monthLabel,
		pad,
		primaryStop,
		shortDate,
		type Session
	} from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	let newestFirst = $state(false);
	let colours = $derived(colourByOrder(buildPlaceTree(sessions).roots.map((r) => r.id)));

	// Each entry knows how it relates to the session played before it.
	let entries = $derived.by(() => {
		const built = sessions.map((session, i) => {
			const prev = sessions[i - 1];
			const stop = primaryStop(session);
			const prevStop = prev ? primaryStop(prev) : null;
			const system = stop?.path[0] ?? null;
			return {
				session,
				stop,
				system,
				colour: system ? (colours.get(system.id) ?? '#8a7e60') : '#8a7e60',
				gap: prev ? daysBetween(prev.date, session.date) : null,
				newMonth: !!session.date && (!prev?.date || monthLabel(prev.date) !== monthLabel(session.date)),
				moved: !!stop && !!prevStop && stop.id !== prevStop.id,
				jumped: !!stop && !!prevStop && stop.path[0].id !== prevStop.path[0].id,
				treasures: [...session.artifacts, ...session.items]
			};
		});
		return newestFirst ? built.reverse() : built;
	});
</script>

<div class="flex items-center justify-between border border-border-dim bg-hull px-3 py-1.5">
	<span class="machine-text text-[9px] text-text-muted">LOG-04 // TIMELINE</span>
	<button type="button" class="machine-text text-[10px] text-accent-amber hover:underline" onclick={() => (newestFirst = !newestFirst)}>
		{newestFirst ? 'NEWEST FIRST ↓' : 'OLDEST FIRST ↓'}
	</button>
</div>

<div>
	{#each entries as entry, i (entry.session.id)}
		{@const session = entry.session}
		{@const left = i % 2 === 0}

		{#if entry.newMonth && session.date}
			<div class="tl-row">
				<div class="tl-spine"><span class="tl-line"></span></div>
				<div class="col-start-2 row-start-1 py-2 md:col-span-3 md:col-start-1 md:text-center">
					<span class="relative border border-border-subtle bg-void px-2 py-0.5 font-display text-[10px] tracking-widest text-text-muted">
						{monthLabel(session.date)}
					</span>
				</div>
			</div>
		{/if}

		{#if !newestFirst && (entry.moved || (entry.gap ?? 0) > 21)}
			<div class="tl-row">
				<div class="tl-spine"><span class="tl-line"></span></div>
				<div class="col-start-2 row-start-1 py-1.5 md:col-span-3 md:col-start-1 md:text-center">
					<span class="relative inline-flex flex-wrap items-center gap-1.5 bg-void px-2 text-[10px] uppercase tracking-wider" style:color={entry.colour}>
						{#if entry.moved}
							<Rocket class="h-3 w-3" />
							{entry.jumped ? `Course set for ${entry.system?.name}` : `Course set for ${entry.stop?.name}`}
						{/if}
						{#if (entry.gap ?? 0) > 21}
							<span class="text-text-faint">{entry.moved ? '· ' : ''}{entry.gap} days between sessions</span>
						{/if}
					</span>
				</div>
			</div>
		{/if}

		<div class="tl-row">
			<div class="tl-spine">
				<span class="tl-line"></span>
				<span class="tl-node" style:border-color={entry.colour} style:color={entry.colour}>{pad(session.n)}</span>
			</div>
			<a
				href="/chronicle/{session.id}"
				class="group col-start-2 row-start-1 my-2 block border border-border-dim bg-panel p-3 transition-all hover:border-accent-amber/40 hover:bg-panel-hover {left
					? 'md:col-start-1'
					: 'md:col-start-3'}"
				style:border-left-color={entry.colour}
				style:border-left-width="2px"
			>
				<div class="flex flex-wrap items-baseline justify-between gap-x-3">
					<span class="machine-text text-[10px] text-accent-amber">{shortDate(session.date)}</span>
					{#if entry.stop}
						<span class="flex items-center gap-1 text-[10px] uppercase tracking-wider" style:color={entry.colour}>
							<MapPin class="h-3 w-3" />{entry.stop.name}{entry.system && entry.system.id !== entry.stop.id ? ` · ${entry.system.name}` : ''}
						</span>
					{/if}
				</div>
				<h2 class="mt-1 text-sm font-bold uppercase tracking-wider text-text-primary transition-colors group-hover:text-accent-amber">
					{session.title}
				</h2>
				{#if session.brief}
					<p class="mt-1 text-xs leading-relaxed text-text-secondary">{session.brief}</p>
				{/if}
				{#if session.characters.length || entry.treasures.length}
					<div class="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[10px] uppercase tracking-wider text-text-muted">
						{#if session.characters.length}
							<span class="flex items-center gap-1">
								<Users class="h-3 w-3 shrink-0" />
								{session.characters.slice(0, 3).map((c) => c.name).join(', ')}{session.characters.length > 3 ? ` +${session.characters.length - 3}` : ''}
							</span>
						{/if}
						{#if entry.treasures.length}
							<span class="flex items-center gap-1 text-accent-purple">
								<Gem class="h-3 w-3 shrink-0" />{entry.treasures.map((t) => t.name).join(', ')}
							</span>
						{/if}
					</div>
				{/if}
			</a>
		</div>
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
	@media (min-width: 48rem) {
		.tl-row {
			grid-template-columns: minmax(0, 1fr) 2.75rem minmax(0, 1fr);
		}
		.tl-spine {
			grid-column-start: 2;
		}
	}
</style>

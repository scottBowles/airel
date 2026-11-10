<script lang="ts">
	// Every Chronicle view on one page, as cards, for choosing between them.
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import { CHRONICLE_VIEWS, viewHref } from '$lib/chronicle/views';
	import { buildPlaceTree, shortDate, type Session } from '$lib/chronicle/model';
	import { VIEW_ICONS } from './viewIcons';
	import ViewPreview from './ViewPreview.svelte';

	let { sessions }: { sessions: Session[] } = $props();

	let placeCount = $derived(buildPlaceTree(sessions).byId.size);
	let castCount = $derived(new Set(sessions.flatMap((s) => s.characters.map((c) => c.id))).size);
	let first = $derived(sessions[0]?.date ?? null);
	let last = $derived(sessions.at(-1)?.date ?? null);
</script>

<div class="grid grid-cols-2 gap-px border border-border-dim bg-border-dim sm:grid-cols-4">
	{#each [['SESSIONS', sessions.length], ['PLACES CHARTED', placeCount], ['CAST', castCount], ['SPAN', first && last ? `${shortDate(first)} → ${shortDate(last)}` : '—']] as [label, value] (label)}
		<div class="bg-hull px-3 py-2.5">
			<p class="machine-text text-[9px] text-text-muted">{label}</p>
			<p class="mt-0.5 font-display text-sm text-accent-amber">{value}</p>
		</div>
	{/each}
</div>

<div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
	{#each CHRONICLE_VIEWS as view, i (view.id)}
		{@const Icon = VIEW_ICONS[view.id]}
		<a
			href={viewHref(view.id)}
			class="group relative flex flex-col border border-border-dim bg-panel p-4 transition-all hover:border-accent-amber/40 hover:bg-panel-hover"
		>
			<ViewPreview view={view.id} />
			<div class="mt-3 flex items-start justify-between">
				<span
					class="flex h-10 w-10 items-center justify-center border border-border-subtle bg-void text-accent-amber transition-shadow group-hover:shadow-glow-amber"
				>
					<Icon class="h-5 w-5" />
				</span>
				<span class="machine-text text-[9px] text-text-faint">
					{view.code}-{String(i).padStart(2, '0')}{view.id === 'classic' ? ' // CURRENT' : ''}
				</span>
			</div>
			<h2 class="mt-3 font-display text-sm uppercase tracking-widest text-text-primary group-hover:text-accent-amber">
				{view.label}
			</h2>
			<p class="mt-0.5 text-[11px] uppercase tracking-wider text-accent-cyan">{view.tagline}</p>
			<p class="mt-2 flex-1 text-xs leading-relaxed text-text-secondary">{view.description}</p>
			<span class="mt-3 flex items-center gap-1 machine-text text-[10px] text-text-muted group-hover:text-accent-amber">
				OPEN VIEW <ArrowRight class="h-3 w-3 transition-transform group-hover:translate-x-1" />
			</span>
		</a>
	{/each}
</div>

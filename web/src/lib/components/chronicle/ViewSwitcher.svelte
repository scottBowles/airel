<script lang="ts">
	// The strip of Chronicle views. Each tab is a link, so a view can be bookmarked and shared.
	import { CHRONICLE_VIEWS, viewHref, type ChronicleViewId } from '$lib/chronicle/views';
	import { VIEW_ICONS } from './viewIcons';

	let { current }: { current: ChronicleViewId } = $props();

	const DeckIcon = VIEW_ICONS.deck;
</script>

<nav aria-label="Chronicle views" class="flex items-stretch border border-border-dim bg-hull">
	<span
		class="hidden shrink-0 items-center border-r border-border-dim px-3 machine-text text-[9px] text-text-muted sm:flex"
	>
		VIEW MODE
	</span>
	<div class="flex min-w-0 flex-1 overflow-x-auto">
		{#each CHRONICLE_VIEWS as view (view.id)}
			{@const Icon = VIEW_ICONS[view.id]}
			{@const active = current === view.id}
			<a
				href={viewHref(view.id)}
				data-sveltekit-noscroll
				aria-current={active ? 'page' : undefined}
				title={view.tagline}
				class="group flex shrink-0 items-center gap-1.5 border-r border-border-dim px-3 py-2.5 text-[11px] uppercase tracking-wider transition-colors
					{active
					? 'bg-accent-amber/10 text-accent-amber shadow-[inset_0_-2px_0_var(--color-accent-amber)]'
					: 'text-text-secondary hover:bg-panel-hover hover:text-accent-amber'}"
			>
				<Icon class="h-3.5 w-3.5" />
				{view.label}
			</a>
		{/each}
	</div>
	<a
		href={viewHref('deck')}
		data-sveltekit-noscroll
		aria-current={current === 'deck' ? 'page' : undefined}
		title="See every view side by side"
		class="flex shrink-0 items-center gap-1.5 border-l border-border-dim px-3 py-2.5 text-[11px] uppercase tracking-wider transition-colors
			{current === 'deck'
			? 'bg-accent-cyan/10 text-accent-cyan shadow-[inset_0_-2px_0_var(--color-accent-cyan)]'
			: 'text-accent-cyan/80 hover:bg-panel-hover hover:text-accent-cyan'}"
	>
		<DeckIcon class="h-3.5 w-3.5" />
		<span class="hidden sm:inline">All views</span>
	</a>
</nav>

<script lang="ts">
	// The strip of Chronicle views. Each tab is a link, so a view can be bookmarked and shared.
	// Tabs wrap onto a second row on wide screens and scroll sideways on phones.
	import { CHRONICLE_VIEWS, viewHref, type ChronicleViewId } from '$lib/chronicle/views';
	import { VIEW_ICONS } from './viewIcons';

	let { current }: { current: ChronicleViewId } = $props();

	const DeckIcon = VIEW_ICONS.deck;

	// On a phone the strip scrolls, so bring the selected tab into view.
	let strip: HTMLElement | undefined = $state();
	$effect(() => {
		const tab = strip?.querySelector<HTMLElement>(`[data-view="${current}"]`);
		if (strip && tab) strip.scrollLeft = tab.offsetLeft - strip.clientWidth / 2 + tab.clientWidth / 2;
	});
</script>

<nav aria-label="Chronicle views" class="flex items-stretch border border-border-dim bg-hull">
	<div bind:this={strip} class="relative flex min-w-0 flex-1 gap-px overflow-x-auto bg-border-dim md:flex-wrap md:overflow-visible">
		{#each CHRONICLE_VIEWS as view (view.id)}
			{@const Icon = VIEW_ICONS[view.id]}
			{@const active = current === view.id}
			<a
				href={viewHref(view.id)}
				data-view={view.id}
				data-sveltekit-noscroll
				aria-current={active ? 'page' : undefined}
				title={view.tagline}
				class="flex shrink-0 items-center gap-1.5 px-2.5 py-2.5 text-[11px] uppercase tracking-wider transition-colors md:grow
					{active
					? 'bg-[#1c1608] text-accent-amber shadow-[inset_0_-2px_0_var(--color-accent-amber)]'
					: 'bg-hull text-text-secondary hover:bg-panel-hover hover:text-accent-amber'}"
			>
				<Icon class="h-3.5 w-3.5 shrink-0" />
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

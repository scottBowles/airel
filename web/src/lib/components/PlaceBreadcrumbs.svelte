<script lang="ts">
	import { ChevronRight } from 'lucide-svelte';

	type PlaceNode = {
		id: string;
		name: string;
		placeType?: string | null;
		parent?: PlaceNode | null;
	};

	let {
		place,
	}: {
		place: PlaceNode;
	} = $props();

	let ancestors = $derived.by(() => {
		const chain: PlaceNode[] = [];
		let current = place.parent;
		while (current) {
			chain.unshift(current);
			current = current.parent;
		}
		return chain;
	});
</script>

{#if ancestors.length > 0}
	<nav class="flex flex-wrap items-center gap-1 text-[10px]">
		{#each ancestors as ancestor, i}
			<a
				href="/database/places/{ancestor.id}"
				class="machine-text text-text-muted transition-colors hover:text-accent-amber"
			>
				{ancestor.name}
			</a>
			<ChevronRight class="h-2.5 w-2.5 text-text-faint" />
		{/each}
		<span class="machine-text text-accent-amber">{place.name}</span>
	</nav>
{/if}

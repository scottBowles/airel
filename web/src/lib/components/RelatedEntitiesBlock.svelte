<script lang="ts">
	import type { Component } from 'svelte';
	import Panel from '$lib/components/Panel.svelte';

	type Section = {
		label: string;
		icon: Component;
		route: string;
		data: { edges: Array<{ node: { id: string; name: string } }> } | null;
	};

	let {
		sections,
	}: {
		sections: Section[];
	} = $props();

	let nonEmpty = $derived(sections.filter((s) => s.data && s.data.edges.length > 0));
</script>

{#each nonEmpty as section}
	<Panel>
		<h3 class="title-section mb-2 flex items-center gap-2">
			<section.icon class="h-3 w-3 text-text-muted" />
			{section.label}
		</h3>
		<div class="space-y-px">
			{#each section.data?.edges ?? [] as edge}
				<a
					href="{section.route}/{edge.node.id}"
					class="block px-2 py-1 text-xs text-text-secondary uppercase tracking-wider transition-colors hover:bg-accent-amber/5 hover:text-accent-amber"
				>
					{edge.node.name}
				</a>
			{/each}
		</div>
	</Panel>
{/each}

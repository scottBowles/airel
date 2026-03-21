<script lang="ts">
	import { resolve } from '$app/paths';
	import { detailSectionTitleClass, type RelationGroup } from '$lib/database-detail';

	let {
		title,
		groups,
		emptyMessage = 'No linked entities recorded.'
	}: {
		title: string;
		groups: RelationGroup[];
		emptyMessage?: string;
	} = $props();
</script>

<div>
	<h3 class={detailSectionTitleClass}>{title}</h3>

	{#if groups.length > 0}
		<div class="space-y-3.5">
			{#each groups as group (group.key)}
				<div class="border-b border-slate-700/90 pb-3 last:border-0 last:pb-0">
					<div class="space-y-1.5 sm:flex sm:items-baseline sm:gap-3 sm:space-y-0">
						<h4
							class="shrink-0 font-mono text-xs leading-6 tracking-[0.18em] text-zinc-500 uppercase sm:w-34"
						>
							{group.label}
						</h4>
						<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
							{#each group.nodes as node (node.id)}
								<a
									href={resolve(group.route, { id: node.id })}
									class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
								>
									{node.name}
								</a>
								{#if node !== group.nodes[group.nodes.length - 1]}
									<span class="text-zinc-700" aria-hidden="true">•</span>
								{/if}
							{/each}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{:else}
		<p class="text-sm text-zinc-500">{emptyMessage}</p>
	{/if}
</div>
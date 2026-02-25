<script lang="ts">
	import type { PageData } from './$types';
	import { resolve } from '$app/paths';
	import CldImage from '$lib/components/images/CldImage.svelte';
	import ScifiPlaceholder from '$lib/components/ui/ScifiPlaceholder.svelte';

	let { data }: { data: PageData } = $props();
	let { AssociationList } = $derived(data);
</script>

<div class="space-y-6">
	<div class="border-industrial-dim flex items-center justify-between border-b pb-4">
		<div>
			<div class="mb-1 font-mono text-xs text-slate-500">DATABASE / ORGANIZATIONS</div>
			<h2 class="text-3xl font-bold tracking-widest text-slate-100 uppercase">Associations</h2>
		</div>
		<div class="text-industrial-amber font-mono text-xs">
			Count: {$AssociationList.data?.associations?.edges.length || 0}
		</div>
	</div>

	<!-- Toolbar / Search -->
	<div class="flex gap-4 border border-slate-800 bg-slate-900 p-4">
		<input
			type="text"
			placeholder="FILTER ASSOCIATIONS..."
			class="industrial-input w-full max-w-sm bg-slate-950"
		/>
		<button class="industrial-btn">SEARCH</button>
	</div>

	<!-- Grid -->
	<div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#if $AssociationList.data?.associations?.edges}
			{#each $AssociationList.data.associations.edges as edge (edge.node.id)}
				<a
					href={resolve(`/database/associations/${edge.node.id}`)}
					class="group hover:border-industrial-amber block border border-slate-800 bg-slate-900/40 p-4 transition-colors"
				>
					<div class="mb-3 flex items-center gap-3">
						{#if edge.node.imageIds?.length > 0}
							<div
								class="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-sm bg-slate-800 font-mono text-xs text-slate-600"
							>
								<CldImage
									id={edge.node.imageIds[0]}
									alt={edge.node.name}
									width={40}
									height={40}
									class="h-full w-full object-cover"
								/>
							</div>
						{:else}
							<ScifiPlaceholder type="association" />
						{/if}
						<div class="min-w-0">
							<h3
								class="font-display group-hover:text-industrial-amber truncate text-xl text-slate-200"
							>
								{edge.node.name}
							</h3>
						</div>
					</div>

					<p class="font-body line-clamp-2 h-8 text-xs text-slate-400">
						{edge.node.description || 'No description available.'}
					</p>
				</a>
			{/each}
		{/if}
	</div>
</div>

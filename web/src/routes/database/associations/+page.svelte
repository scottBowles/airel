<script lang="ts">
	import type { PageData } from './$types';
	import { resolve } from '$app/paths';
	import CldImage from '$lib/components/images/CldImage.svelte';
	import ScifiPlaceholder from '$lib/components/ui/ScifiPlaceholder.svelte';

	let { data }: { data: PageData } = $props();
	let { AssociationList } = $derived(data);
</script>

<div class="db-page">
	<div class="db-header">
		<div>
			<div class="mb-1 font-mono text-xs text-slate-500">DATABASE / ORGANIZATIONS</div>
			<h2 class="db-title">Associations</h2>
		</div>
		<div class="text-industrial-amber font-mono text-xs">
			Count: {$AssociationList.data?.associations?.edges.length || 0}
		</div>
	</div>

	<!-- Grid -->
	<div class="db-grid">
		{#if $AssociationList.data?.associations?.edges}
			{#each $AssociationList.data.associations.edges as edge (edge.node.id)}
				<a href={resolve(`/database/associations/${edge.node.id}`)} class="group db-card">
					<div class="mb-3 flex items-center gap-3">
						{#if edge.node.imageIds?.length > 0}
							<div class="db-card-thumb">
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
							<h3 class="db-card-title">
								{edge.node.name}
							</h3>
						</div>
					</div>

					<p class="db-card-copy">
						{edge.node.description || 'No description available.'}
					</p>
				</a>
			{/each}
		{/if}
	</div>
</div>

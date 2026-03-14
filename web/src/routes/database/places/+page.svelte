<script lang="ts">
	import type { PageData } from './$types';
	import { resolve } from '$app/paths';
	import CldImage from '$lib/components/images/CldImage.svelte';
	import ScifiPlaceholder from '$lib/components/ui/ScifiPlaceholder.svelte';

	let { data }: { data: PageData } = $props();
	let { PlaceList } = $derived(data);
</script>

<div class="db-page">
	<div class="db-header">
		<div>
			<div class="mb-1 font-mono text-xs text-slate-500">DATABASE / LOCATIONS</div>
			<h2 class="db-title">Places</h2>
		</div>
		<div class="text-industrial-amber font-mono text-xs">
			Count: {$PlaceList.data?.places?.edges.length || 0}
		</div>
	</div>

	<!-- Toolbar / Search -->
	<div class="db-toolbar">
		<input
			type="text"
			placeholder="FILTER LOCATIONS..."
			class="industrial-input w-full bg-slate-950 sm:max-w-sm"
		/>
		<button class="industrial-btn w-full sm:w-auto">SEARCH</button>
	</div>

	<!-- Grid -->
	<div class="db-grid">
		{#if $PlaceList.data?.places?.edges}
			{#each $PlaceList.data.places.edges as edge (edge.node.id)}
				<a href={resolve(`/database/places/${edge.node.id}`)} class="group db-card">
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
							<ScifiPlaceholder type="place" />
						{/if}
						<div class="min-w-0">
							<h3 class="db-card-title">
								{edge.node.name}
							</h3>
							{#if edge.node.placeType}
								<div class="mt-1 text-xs tracking-wider text-slate-500 uppercase">
									{edge.node.placeType}
								</div>
							{/if}
						</div>
					</div>

					<p class="db-card-copy">
						{edge.node.description || 'No description available.'}
					</p>

					{#if edge.node.parent}
						<div class="mt-3 border-t border-slate-800 pt-2 text-xs text-slate-500">
							In: <span class="text-slate-400">{edge.node.parent.name}</span>
						</div>
					{/if}
				</a>
			{/each}
		{/if}
	</div>
</div>

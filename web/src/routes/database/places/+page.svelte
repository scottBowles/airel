<script lang="ts">
	import type { PageData } from './$types';
	import { resolve } from '$app/paths';
	import CldImage from '$lib/components/images/CldImage.svelte';
	import ScifiPlaceholder from '$lib/components/ui/ScifiPlaceholder.svelte';

	let { data }: { data: PageData } = $props();
	let { PlaceList } = $derived(data);
</script>

<div class="space-y-6">
	<div class="border-industrial-dim flex items-center justify-between border-b pb-4">
		<div>
			<div class="mb-1 font-mono text-xs text-slate-500">DATABASE / LOCATIONS</div>
			<h2 class="text-3xl font-bold tracking-widest text-slate-100 uppercase">Places</h2>
		</div>
		<div class="text-industrial-amber font-mono text-xs">
			Count: {$PlaceList.data?.places?.edges.length || 0}
		</div>
	</div>

	<!-- Toolbar / Search -->
	<div class="flex gap-4 border border-slate-800 bg-slate-900 p-4">
		<input
			type="text"
			placeholder="FILTER LOCATIONS..."
			class="industrial-input w-full max-w-sm bg-slate-950"
		/>
		<button class="industrial-btn">SEARCH</button>
	</div>

	<!-- Grid -->
	<div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#if $PlaceList.data?.places?.edges}
			{#each $PlaceList.data.places.edges as edge (edge.node.id)}
				<a
					href={resolve(`/database/places/${edge.node.id}`)}
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
									class="w-full h-full object-cover"
								/>
							</div>
						{:else}
							<ScifiPlaceholder type="place" />
						{/if}
						<div class="min-w-0">
							<h3
								class="font-display group-hover:text-industrial-amber truncate text-xl text-slate-200"
							>
								{edge.node.name}
							</h3>
							{#if edge.node.placeType}
								<div class="mt-1 text-xs tracking-wider text-slate-500 uppercase">
									{edge.node.placeType}
								</div>
							{/if}
						</div>
					</div>

					<p class="font-body line-clamp-2 h-8 text-xs text-slate-400">
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

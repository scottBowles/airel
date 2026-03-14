<script lang="ts">
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdatePlaceImagesStore } from '$houdini';
	import { resolve } from '$app/paths';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';

	let { data }: { data: PageData } = $props();
	let { PlaceDetail } = $derived(data);
	let place = $derived($PlaceDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);

	const updateStore = new UpdatePlaceImagesStore();

	async function saveImages(newIds: string[]) {
		await updateStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}
</script>

{#if place && place.__typename === 'Place'}
	<div class="db-detail">
		<!-- Header -->
		<div class="db-detail-header">
			<div>
				<div class="flex items-baseline gap-3">
					<h1 class="db-detail-title">{place.name}</h1>
				</div>
				{#if place.placeType}
					<div class="mt-1 text-xs font-bold tracking-widest text-zinc-500 uppercase">
						{place.placeType}
					</div>
				{/if}
			</div>
			<a href={resolve('/database/places')} class="db-back-link"> ← Back to Places </a>
		</div>

		<div class="db-detail-grid">
			<!-- Main Info -->
			<div class="db-detail-main">
				{#if place.description}
					<div class="db-detail-panel">
						<h3 class="db-detail-panel-title">Description</h3>
						<p class="leading-relaxed whitespace-pre-wrap text-zinc-300">{place.description}</p>
					</div>
				{/if}

				{#if place.markdownNotes}
					<div class="db-detail-panel">
						<h3 class="db-detail-panel-title">Notes</h3>
						<div class="prose prose-sm max-w-none text-zinc-400 prose-invert">
							{place.markdownNotes}
						</div>
					</div>
				{/if}
			</div>

			<!-- Stats & Meta -->
			<div class="db-detail-side">
				<AdminImageManager imageIds={place.imageIds || []} canEdit={isAdmin} onSave={saveImages} />
				<div class="rounded-sm border border-zinc-800 bg-zinc-900/50 p-4">
					<h3 class="mb-4 text-sm font-bold tracking-wide text-zinc-400 uppercase">Details</h3>
					<div class="space-y-3 text-sm">
						{#if place.population}
							<div class="flex justify-between border-b border-zinc-800 pb-2">
								<span class="text-zinc-500">Population</span>
								<span class="font-mono text-zinc-300">{place.population.toLocaleString()}</span>
							</div>
						{/if}
						{#if place.parent}
							<div class="flex items-center justify-between border-b border-zinc-800 pb-2">
								<span class="text-zinc-500">Located In</span>
								<a
									href={resolve(`/database/places/${place.parent.id}`)}
									class="max-w-37.5 truncate text-right text-emerald-400 hover:text-emerald-300"
								>
									{place.parent.name}
								</a>
							</div>
						{/if}
					</div>
				</div>

				<!-- Locations within -->
				{#if place.children?.edges && place.children.edges.length > 0}
					<div class="rounded-sm border border-zinc-800 bg-zinc-900/50 p-4">
						<h3 class="mb-4 text-sm font-bold tracking-wide text-zinc-400 uppercase">
							Locations Within
						</h3>
						<ul class="space-y-2">
							{#each place.children.edges as edge (edge.node.id)}
								<li>
									<a
										href={resolve(`/database/places/${edge.node.id}`)}
										class="group block border border-zinc-900 bg-zinc-950/50 p-2 text-sm transition-all hover:border-emerald-500/50 hover:bg-zinc-900"
									>
										<span class="text-zinc-300 group-hover:text-emerald-400">{edge.node.name}</span>
									</a>
								</li>
							{/each}
						</ul>
					</div>
				{/if}
			</div>
		</div>
	</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Place not found or failed to load.</p>
	</div>
{/if}

<script lang="ts">
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdateItemImagesStore } from '$houdini';
	import { resolve } from '$app/paths';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';

	let { data }: { data: PageData } = $props();
	let { ItemDetail } = $derived(data);
	let item = $derived($ItemDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);

	const updateStore = new UpdateItemImagesStore();

	async function saveImages(newIds: string[]) {
		await updateStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}
</script>

{#if item && item.__typename === 'Item'}
	<div class="db-detail">
		<!-- Header -->
		<div class="db-detail-header">
			<div>
				<div class="flex items-baseline gap-3">
					<h1 class="db-detail-title">{item.name}</h1>
				</div>
			</div>
			<a href={resolve('/database/items')} class="db-back-link"> ← Back to Items </a>
		</div>

		<div class="db-detail-grid">
			<!-- Main Info -->
			<div class="db-detail-main">
				{#if item.description}
					<div class="db-detail-panel">
						<h3 class="db-detail-panel-title">Description</h3>
						<p class="leading-relaxed whitespace-pre-wrap text-zinc-300">{item.description}</p>
					</div>
				{/if}

				{#if item.markdownNotes}
					<div class="db-detail-panel">
						<h3 class="db-detail-panel-title">Notes</h3>
						<div class="prose prose-sm max-w-none text-zinc-400 prose-invert">
							{item.markdownNotes}
						</div>
					</div>
				{/if}
			</div>

			<!-- Sidebar -->
			<div class="db-detail-side">
				<AdminImageManager imageIds={item.imageIds || []} canEdit={isAdmin} onSave={saveImages} />
				<div class="rounded-sm border border-zinc-800 bg-zinc-900/50 p-4">
					<h3 class="mb-4 text-sm font-bold tracking-wide text-zinc-400 uppercase">Details</h3>
					<div class="text-sm text-zinc-500 italic">No additional stats available yet.</div>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Item not found or failed to load.</p>
	</div>
{/if}

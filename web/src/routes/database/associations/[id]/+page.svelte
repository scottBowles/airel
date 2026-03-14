<script lang="ts">
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdateAssociationImagesStore } from '$houdini';
	import { resolve } from '$app/paths';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';

	let { data }: { data: PageData } = $props();
	let { AssociationDetail } = $derived(data);
	let association = $derived($AssociationDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);

	const updateStore = new UpdateAssociationImagesStore();

	async function saveImages(newIds: string[]) {
		await updateStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}
</script>

{#if association && association.__typename === 'Association'}
	<div class="db-detail">
		<!-- Header -->
		<div class="db-detail-header">
			<div>
				<div class="flex items-baseline gap-3">
					<h1 class="db-detail-title">{association.name}</h1>
				</div>
			</div>
			<a href={resolve('/database/associations')} class="db-back-link"> ← Back to Associations </a>
		</div>

		<div class="db-detail-grid">
			<!-- Images -->
			<div class="lg:col-span-1">
				<AdminImageManager
					imageIds={association.imageIds || []}
					canEdit={isAdmin}
					onSave={saveImages}
				/>
			</div>

			<!-- Main Info -->
			<div class="db-detail-main">
				{#if association.description}
					<div class="db-detail-panel">
						<h3 class="db-detail-panel-title">Description</h3>
						<p class="leading-relaxed whitespace-pre-wrap text-zinc-300">
							{association.description}
						</p>
					</div>
				{/if}

				{#if association.markdownNotes}
					<div class="db-detail-panel">
						<h3 class="db-detail-panel-title">Notes</h3>
						<div class="prose prose-sm max-w-none text-zinc-400 prose-invert">
							{association.markdownNotes}
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Association not found or failed to load.</p>
	</div>
{/if}

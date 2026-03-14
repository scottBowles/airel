<script lang="ts">
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdateArtifactImagesStore } from '$houdini';
	import { resolve } from '$app/paths';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';

	let { data }: { data: PageData } = $props();
	let { ArtifactDetail } = $derived(data);
	let artifact = $derived($ArtifactDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);

	const updateStore = new UpdateArtifactImagesStore();

	async function saveImages(newIds: string[]) {
		await updateStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}
</script>

{#if artifact && artifact.__typename === 'Artifact'}
	<div class="db-detail">
		<!-- Header -->
		<div class="db-detail-header">
			<div>
				<div class="flex items-baseline gap-3">
					<h1 class="db-detail-title">{artifact.name}</h1>
				</div>
			</div>
			<a href={resolve('/database/artifacts')} class="db-back-link"> ← Back to Artifacts </a>
		</div>

		<div class="db-detail-grid">
			<!-- Images -->
			<div class="lg:col-span-1">
				<AdminImageManager
					imageIds={artifact.imageIds || []}
					canEdit={isAdmin}
					onSave={saveImages}
				/>
			</div>

			<!-- Main Info -->
			<div class="db-detail-main">
				{#if artifact.description}
					<div class="db-detail-panel">
						<h3 class="db-detail-panel-title">Description</h3>
						<p class="leading-relaxed whitespace-pre-wrap text-zinc-300">
							{artifact.description}
						</p>
					</div>
				{/if}

				{#if artifact.markdownNotes}
					<div class="db-detail-panel">
						<h3 class="db-detail-panel-title">Notes</h3>
						<div class="prose prose-sm max-w-none text-zinc-400 prose-invert">
							{artifact.markdownNotes}
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Artifact not found or failed to load.</p>
	</div>
{/if}

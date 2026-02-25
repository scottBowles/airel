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
	<div class="flex h-full flex-col overflow-hidden p-4">
		<!-- Header -->
		<div class="mb-6 flex items-start justify-between border-b border-zinc-800 pb-4">
			<div>
				<div class="flex items-baseline gap-3">
					<h1 class="text-3xl font-bold text-emerald-400">{association.name}</h1>
				</div>
			</div>
			<a
				href={resolve('/database/associations')}
				class="text-sm text-zinc-500 transition-colors hover:text-emerald-400"
			>
				← Back to Associations
			</a>
		</div>

		<div class="custom-scrollbar flex-1 overflow-y-auto pr-4">
			<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
				<!-- Images -->
				<div class="lg:col-span-1">
					<AdminImageManager
						imageIds={association.imageIds || []}
						canEdit={isAdmin}
						onSave={saveImages}
					/>
				</div>

				<!-- Main Info -->
				<div class="space-y-6 lg:col-span-2">
					{#if association.description}
						<div class="rounded-sm border border-zinc-800/50 bg-zinc-900/30 p-4">
							<h3 class="mb-2 text-xs font-bold text-zinc-500 uppercase">Description</h3>
							<p class="leading-relaxed whitespace-pre-wrap text-zinc-300">
								{association.description}
							</p>
						</div>
					{/if}

					{#if association.markdownNotes}
						<div class="rounded-sm border border-zinc-800/50 bg-zinc-900/30 p-4">
							<h3 class="mb-2 text-xs font-bold text-zinc-500 uppercase">Notes</h3>
							<div class="prose prose-sm max-w-none text-zinc-400 prose-invert">
								{association.markdownNotes}
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Association not found or failed to load.</p>
	</div>
{/if}

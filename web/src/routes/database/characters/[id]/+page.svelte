<script lang="ts">
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdateCharacterImagesStore } from '$houdini';

	import { resolve } from '$app/paths';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';

	let { data }: { data: PageData } = $props();
	let CharacterDetail = $derived(data.CharacterDetail);
	let char = $derived($CharacterDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);

	const updateStore = new UpdateCharacterImagesStore();

	async function saveImages(newIds: string[]) {
		console.log('saving images with ids: ', newIds);
		await updateStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}
</script>

<div class="mx-auto max-w-5xl pb-20">
	<!-- Breadcrumbs -->
	<div class="mb-6 flex items-center gap-2 font-mono text-xs text-slate-500">
		<a href={resolve('/database')} class="hover:text-industrial-amber">DATABASE</a>
		<span>/</span>
		<a href={resolve('/database/characters')} class="hover:text-industrial-amber">CHARACTERS</a>
	</div>

	{#if char && char.__typename === 'Character'}
		<div
			class="border-industrial-dim mb-8 grid grid-cols-1 gap-8 border-b pb-8 md:grid-cols-[250px_1fr]"
		>
			<!-- Portrait Frame & Image Management -->
			<div class="relative w-full">
				<AdminImageManager imageIds={char.imageIds || []} canEdit={isAdmin} onSave={saveImages} />
				<!-- Decorative corners -->
				<div
					class="border-industrial-amber pointer-events-none absolute -top-1 -left-1 h-2 w-2 border-t border-l"
				></div>
				<div
					class="border-industrial-amber pointer-events-none absolute -right-1 -bottom-1 h-2 w-2 border-r border-b"
				></div>
			</div>

			<!-- Stats & Info -->
			<div class="space-y-4">
				<h1 class="font-display text-5xl font-bold tracking-widest text-white uppercase">
					{char.name}
				</h1>

				<div class="text-industrial-green flex gap-4 font-mono text-sm uppercase">
					<span class="border-industrial-green border px-2 py-1">Class: UNKNOWN</span>
					<span class="border-industrial-green border px-2 py-1">Race: UNKNOWN</span>
				</div>

				<div
					class="prose mt-4 max-w-none border-l border-slate-700 bg-slate-900/30 p-4 leading-relaxed text-slate-300 prose-invert"
				>
					<p>{char.description || 'No description provided.'}</p>
				</div>
			</div>
		</div>

		<!-- Relationship Matrix -->
		<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
			<!-- Features & Traits -->
			<div class="panel-border p-4">
				<h3
					class="text-industrial-amber mb-3 inline-block bg-slate-900 px-1 font-mono text-xs uppercase"
				>
					Biology & Skills
				</h3>
				<ul class="space-y-2">
					{#each char.featuresAndTraits?.edges || [] as { node } (node.name)}
						<li class="border-b border-slate-800 pb-2 last:border-0">
							<span class="font-display block text-slate-200">{node.name}</span>
							<span class="font-body block text-xs text-slate-500">{node.description || ''}</span>
						</li>
					{/each}
				</ul>
			</div>

			<!-- Associations -->
			<div class="panel-border p-4">
				<h3
					class="text-industrial-amber mb-3 inline-block bg-slate-900 px-1 font-mono text-xs uppercase"
				>
					Known Associates
				</h3>
				<div class="flex flex-wrap gap-2">
					{#each char.associations?.edges || [] as { node } (node.id)}
						<a
							href={resolve(`/database/associations/${node.id}`)}
							class="bg-slate-800 px-2 py-1 font-mono text-xs text-slate-300 transition-colors hover:bg-slate-700 hover:text-white"
						>
							{node.name}
						</a>
					{/each}
				</div>
			</div>
		</div>
	{:else if $CharacterDetail.fetching}
		<div class="text-industrial-amber animate-pulse p-12 text-center font-mono">
			DECRYPTING FILE...
		</div>
	{/if}
</div>

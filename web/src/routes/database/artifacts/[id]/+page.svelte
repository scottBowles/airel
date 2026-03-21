<script lang="ts">
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdateArtifactImagesStore } from '$houdini';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';
	import EntityLogManager from '$lib/components/logs/EntityLogManager.svelte';
	import {
		buildRelationGroups,
		detailPanelClass,
		detailRailCardClass,
		detailSectionTitleClass,
		getLogNodes,
		getNamedNodes
	} from '$lib/database-detail';

	let { data }: { data: PageData } = $props();
	let ArtifactDetail = $derived(data.ArtifactDetail);
	let artifact = $derived($ArtifactDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
	let itemNodes = $derived.by(() => {
		if (!artifact || artifact.__typename !== 'Artifact') {
			return [];
		}

		return getNamedNodes(artifact.items);
	});
	let relationGroups = $derived.by(() => {
		if (!artifact || artifact.__typename !== 'Artifact') {
			return [];
		}

		return buildRelationGroups({
			relatedArtifacts: artifact.relatedArtifacts,
			relatedAssociations: artifact.relatedAssociations,
			relatedCharacters: artifact.relatedCharacters,
			relatedItems: artifact.relatedItems,
			relatedPlaces: artifact.relatedPlaces,
			relatedRaces: artifact.relatedRaces
		});
	});
	let logEntries = $derived.by(() => {
		if (!artifact || artifact.__typename !== 'Artifact') {
			return [];
		}

		return getLogNodes(artifact.logs);
	});
	let hasMarkdownNotes = $derived(
		!!(artifact && artifact.__typename === 'Artifact' && artifact.markdownNotes?.trim())
	);
	let sanitizedMarkdownNotes = $derived.by(() => {
		if (!artifact || artifact.__typename !== 'Artifact' || !artifact.markdownNotes) {
			return '';
		}

		return DOMPurify.sanitize(artifact.markdownNotes);
	});

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
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				<h1 class="db-detail-title">{artifact.name}</h1>
			</div>
			<a href={resolve('/database/artifacts')} class="db-back-link"> ← Back to Artifacts </a>
		</div>

		<div class="db-detail-grid">
			<div class="db-detail-side order-1 lg:order-2">
				<AdminImageManager
					imageIds={artifact.imageIds || []}
					canEdit={isAdmin}
					onSave={saveImages}
				/>

				<div class={detailRailCardClass + ' hidden lg:block'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
			</div>

			<div class="db-detail-main order-2 lg:order-1">
				<div class={detailPanelClass}>
					<p class="text-sm leading-relaxed whitespace-pre-wrap text-zinc-300 sm:text-base">
						{artifact.description || 'No description provided.'}
					</p>
				</div>

				{#if itemNodes.length > 0}
					<div class={detailPanelClass}>
						<h3 class={detailSectionTitleClass}>Items</h3>
						<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
							{#each itemNodes as node (node.id)}
								<a
									href={resolve('/database/items/[id]', { id: node.id })}
									class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
								>
									{node.name}
								</a>
								{#if node !== itemNodes[itemNodes.length - 1]}
									<span class="text-zinc-700" aria-hidden="true">•</span>
								{/if}
							{/each}
						</div>
					</div>
				{/if}

				{#if hasMarkdownNotes}
					<div class={detailPanelClass}>
						<div class="text-sm leading-relaxed whitespace-pre-wrap text-zinc-300">
							<!-- eslint-disable-next-line svelte/no-at-html-tags -->
							{@html sanitizedMarkdownNotes}
						</div>
					</div>
				{/if}

				<div class={detailPanelClass}>
					<h3 class={detailSectionTitleClass}>Related Entities</h3>

					{#if relationGroups.length > 0}
						<div class="space-y-3.5">
							{#each relationGroups as group (group.key)}
								<div class="border-b border-slate-700/90 pb-3 last:border-0 last:pb-0">
									<div class="space-y-1.5 sm:flex sm:items-baseline sm:gap-3 sm:space-y-0">
										<h4
											class="shrink-0 font-mono text-xs leading-6 tracking-[0.18em] text-zinc-500 uppercase sm:w-34"
										>
											{group.label}
										</h4>
										<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
											{#each group.nodes as node (node.id)}
												<a
													href={resolve(group.route, { id: node.id })}
													class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
												>
													{node.name}
												</a>
												{#if node !== group.nodes[group.nodes.length - 1]}
													<span class="text-zinc-700" aria-hidden="true">•</span>
												{/if}
											{/each}
										</div>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-zinc-500">No linked entities recorded.</p>
					{/if}
				</div>

				<div class={detailPanelClass + ' lg:hidden'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
			</div>
		</div>
	</div>
{:else if $ArtifactDetail.fetching}
	<div class="p-12 text-center font-mono text-zinc-500">Retrieving artifact record...</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Artifact not found or failed to load.</p>
	</div>
{/if}

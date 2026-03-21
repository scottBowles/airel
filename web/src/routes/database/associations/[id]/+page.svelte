<script lang="ts">
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdateAssociationImagesStore } from '$houdini';
	import RelationGroupList from '$lib/components/database/RelationGroupList.svelte';
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
	let AssociationDetail = $derived(data.AssociationDetail);
	let association = $derived($AssociationDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
	let memberNodes = $derived.by(() => {
		if (!association || association.__typename !== 'Association') {
			return [];
		}

		return getNamedNodes(association.characters);
	});
	let relationGroups = $derived.by(() => {
		if (!association || association.__typename !== 'Association') {
			return [];
		}

		return buildRelationGroups({
			relatedArtifacts: association.relatedArtifacts,
			relatedAssociations: association.relatedAssociations,
			relatedCharacters: association.relatedCharacters,
			relatedItems: association.relatedItems,
			relatedPlaces: association.relatedPlaces,
			relatedRaces: association.relatedRaces
		});
	});
	let logEntries = $derived.by(() => {
		if (!association || association.__typename !== 'Association') {
			return [];
		}

		return getLogNodes(association.logs);
	});
	let hasMarkdownNotes = $derived(
		!!(association && association.__typename === 'Association' && association.markdownNotes?.trim())
	);
	let sanitizedMarkdownNotes = $derived.by(() => {
		if (!association || association.__typename !== 'Association' || !association.markdownNotes) {
			return '';
		}

		return DOMPurify.sanitize(association.markdownNotes);
	});

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
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				<h1 class="db-detail-title">{association.name}</h1>
			</div>
			<a href={resolve('/database/associations')} class="db-back-link"> ← Back to Associations </a>
		</div>

		<div class="db-detail-grid">
			<div class="db-detail-side order-1 lg:order-2">
				<AdminImageManager
					imageIds={association.imageIds || []}
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
						{association.description || 'No description provided.'}
					</p>
				</div>

				{#if memberNodes.length > 0}
					<div class={detailPanelClass}>
						<h3 class={detailSectionTitleClass}>Members</h3>
						<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
							{#each memberNodes as node (node.id)}
								<a
									href={resolve('/database/characters/[id]', { id: node.id })}
									class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
								>
									{node.name}
								</a>
								{#if node !== memberNodes[memberNodes.length - 1]}
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
					<RelationGroupList title="Related Entities" groups={relationGroups} />
				</div>

				<div class={detailPanelClass + ' lg:hidden'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
			</div>
		</div>
	</div>
{:else if $AssociationDetail.fetching}
	<div class="p-12 text-center font-mono text-zinc-500">Retrieving association record...</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Association not found or failed to load.</p>
	</div>
{/if}

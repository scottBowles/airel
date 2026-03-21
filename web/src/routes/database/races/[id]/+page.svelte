<script lang="ts">
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdateRaceImagesStore } from '$houdini';
	import RelationGroupList from '$lib/components/database/RelationGroupList.svelte';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';
	import EntityLogManager from '$lib/components/logs/EntityLogManager.svelte';
	import {
		buildRelationGroups,
		detailPanelClass,
		detailRailCardClass,
		getLogNodes
	} from '$lib/database-detail';

	let { data }: { data: PageData } = $props();
	let RaceDetail = $derived(data.RaceDetail);
	let race = $derived($RaceDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
	let relationGroups = $derived.by(() => {
		if (!race || race.__typename !== 'Race') {
			return [];
		}

		return buildRelationGroups({
			relatedArtifacts: race.relatedArtifacts,
			relatedAssociations: race.relatedAssociations,
			relatedCharacters: race.relatedCharacters,
			relatedItems: race.relatedItems,
			relatedPlaces: race.relatedPlaces,
			relatedRaces: race.relatedRaces
		});
	});
	let logEntries = $derived.by(() => {
		if (!race || race.__typename !== 'Race') {
			return [];
		}

		return getLogNodes(race.logs);
	});
	let hasMarkdownNotes = $derived(
		!!(race && race.__typename === 'Race' && race.markdownNotes?.trim())
	);
	let sanitizedMarkdownNotes = $derived.by(() => {
		if (!race || race.__typename !== 'Race' || !race.markdownNotes) {
			return '';
		}

		return DOMPurify.sanitize(race.markdownNotes);
	});

	const updateStore = new UpdateRaceImagesStore();

	async function saveImages(newIds: string[]) {
		await updateStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}
</script>

{#if race && race.__typename === 'Race'}
	<div class="db-detail">
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				<h1 class="db-detail-title">{race.name}</h1>
			</div>
			<a href={resolve('/database/races')} class="db-back-link"> ← Back to Races </a>
		</div>

		<div class="db-detail-grid">
			<div class="db-detail-side order-1 lg:order-2">
				<AdminImageManager imageIds={race.imageIds || []} canEdit={isAdmin} onSave={saveImages} />

				<div class={detailRailCardClass + ' hidden lg:block'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
			</div>

			<div class="db-detail-main order-2 lg:order-1">
				<div class={detailPanelClass}>
					<p class="text-sm leading-relaxed whitespace-pre-wrap text-zinc-300 sm:text-base">
						{race.description || 'No description provided.'}
					</p>
				</div>

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
{:else if $RaceDetail.fetching}
	<div class="p-12 text-center font-mono text-zinc-500">Retrieving race record...</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Race not found or failed to load.</p>
	</div>
{/if}

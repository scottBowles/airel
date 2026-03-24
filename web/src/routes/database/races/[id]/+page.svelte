<script lang="ts">
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData as RoutePageData } from './$houdini';
	import {
		type EntityEditorOptionsStore,
		LockRaceEditorStore,
		UnlockRaceEditorStore,
		UpdateRaceEditorStore,
		UpdateRaceImagesStore
	} from '$houdini';
	import RelationGroupList from '$lib/components/database/RelationGroupList.svelte';
	import DatabaseEntityEditor from '$lib/components/database/DatabaseEntityEditor.svelte';
	import {
		DEFAULT_DATABASE_ENTITY_DRAFT,
		type DatabaseEntityDraft,
		type DatabaseEntityEditorConfig
	} from '$lib/components/database/database-entity-editor-types';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';
	import EntityLogManager from '$lib/components/logs/EntityLogManager.svelte';
	import {
		buildEntityEditorRelationOptions,
		buildNodeInputList,
		getLockUserDisplayName,
		mapNamedRelationOptions,
		normalizeTextValue
	} from '$lib/database-entity-edit';
	import {
		buildRelationGroups,
		detailPanelClass,
		detailRailCardClass,
		getLogNodes
	} from '$lib/database-detail';
	import { extractMutationErrorMessage, getOperationInfoMessage } from '$lib/mutation-errors';
	import { fromStore } from 'svelte/store';
	import { Pencil } from 'lucide-svelte';
	import { toast } from 'svelte-sonner';

	type PageData = RoutePageData & {
		EntityEditorOptions: EntityEditorOptionsStore;
	};

	const raceEditorConfig: DatabaseEntityEditorConfig = {
		entityLabel: 'Race',
		primaryRelations: [{ key: 'characters', title: 'Characters' }]
	};

	let { data }: { data: PageData } = $props();
	let RaceDetail = $derived(data.RaceDetail);
	let race = $derived($RaceDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
	let EntityEditorOptionsResult = $derived.by(() =>
		fromStore(data.EntityEditorOptions).current
	);
	let relationOptions = $derived.by(() =>
		buildEntityEditorRelationOptions(EntityEditorOptionsResult?.data ?? undefined)
	);
	let lockOwnerName = $derived.by(() =>
		race && race.__typename === 'Race' && race.lockUser ? getLockUserDisplayName(race.lockUser) : null
	);
	let editableRace = $derived.by<DatabaseEntityDraft | null>(() => {
		if (!race || race.__typename !== 'Race') {
			return null;
		}

		return {
			...DEFAULT_DATABASE_ENTITY_DRAFT,
			id: race.id,
			name: race.name ?? '',
			description: race.description ?? '',
			markdownNotes: race.markdownNotes ?? '',
			characters: mapNamedRelationOptions('characters', race.characters),
			relatedArtifacts: mapNamedRelationOptions('artifacts', race.relatedArtifacts),
			relatedAssociations: mapNamedRelationOptions('associations', race.relatedAssociations),
			relatedCharacters: mapNamedRelationOptions('characters', race.relatedCharacters),
			relatedItems: mapNamedRelationOptions('items', race.relatedItems),
			relatedPlaces: mapNamedRelationOptions('places', race.relatedPlaces),
			relatedRaces: mapNamedRelationOptions('races', race.relatedRaces)
		};
	});
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

	const updateImagesStore = new UpdateRaceImagesStore();
	const lockStore = new LockRaceEditorStore();
	const unlockStore = new UnlockRaceEditorStore();
	const updateEditorStore = new UpdateRaceEditorStore();

	async function saveImages(newIds: string[]) {
		await updateImagesStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}

	async function acquireLock() {
		if (!race || race.__typename !== 'Race') {
			return;
		}

		const response = await lockStore.mutate({ id: race.id });
		const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

		if (responseErrorMessage) {
			toast.error(responseErrorMessage);
			return;
		}

		const payload = response.data?.lock;

		if (!payload) {
			throw new Error('No race lock payload returned.');
		}

		toast.success('Race lock acquired.');
	}

	async function discardChanges() {
		if (!race || race.__typename !== 'Race') {
			return;
		}

		const response = await unlockStore.mutate({ id: race.id });
		const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

		if (responseErrorMessage) {
			throw new Error(responseErrorMessage);
		}

		const payload = response.data?.unlock;

		if (!payload) {
			throw new Error('No race unlock payload returned.');
		}

		toast.success('Race changes discarded.');
		return payload;
	}

	async function saveChanges(draft: DatabaseEntityDraft) {
		const response = await updateEditorStore.mutate({
			id: draft.id,
			name: normalizeTextValue(draft.name, true),
			description: normalizeTextValue(draft.description),
			markdownNotes: normalizeTextValue(draft.markdownNotes),
			characters: buildNodeInputList(draft.characters),
			relatedArtifacts: buildNodeInputList(draft.relatedArtifacts),
			relatedAssociations: buildNodeInputList(draft.relatedAssociations),
			relatedCharacters: buildNodeInputList(draft.relatedCharacters),
			relatedItems: buildNodeInputList(draft.relatedItems),
			relatedPlaces: buildNodeInputList(draft.relatedPlaces),
			relatedRaces: buildNodeInputList(draft.relatedRaces)
		});
		const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

		if (responseErrorMessage) {
			throw new Error(responseErrorMessage);
		}

		const payload = response.data?.updateRace;

		if (!payload) {
			throw new Error('No race update payload returned.');
		}

		const operationInfoMessage = getOperationInfoMessage(payload, 'Failed to save race changes.');

		if (!operationInfoMessage) {
			toast.success('Race changes saved.');
		}

		return payload;
	}
</script>

{#if race && race.__typename === 'Race'}
	<div class="db-detail">
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				<h1 class="db-detail-title">{race.name}</h1>
			</div>
			<div class="flex flex-col items-start gap-3 sm:items-end">
				<a href={resolve('/database/races')} class="db-back-link"> ← Back to Races </a>
				{#if isAdmin}
					<div class="flex flex-wrap items-center gap-3">
						{#if race.lockUser && !race.lockedBySelf && lockOwnerName}
							<div class="rounded-sm border border-slate-800 bg-slate-950/80 px-3 py-2 font-mono text-sm text-slate-300">
								Locked by {lockOwnerName}
							</div>
						{/if}
						{#if !race.lockedBySelf}
							<button
								type="button"
								onclick={acquireLock}
								class="text-industrial-amber inline-flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-sm border border-slate-700 bg-slate-950 transition-colors hover:border-industrial-amber hover:text-white"
								aria-label="Edit race"
								title="Edit race"
							>
								<Pencil class="h-4 w-4" aria-hidden="true" />
							</button>
						{/if}
					</div>
				{/if}
			</div>
		</div>

		<div class="db-detail-grid">
			<div class="db-detail-side order-1 lg:order-2">
				<AdminImageManager imageIds={race.imageIds || []} canEdit={isAdmin} onSave={saveImages} />

				<div class={detailRailCardClass + ' hidden lg:block'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
			</div>

			<div class="db-detail-main order-2 lg:order-1">
				{#if isAdmin && race.lockedBySelf && editableRace}
					<DatabaseEntityEditor
						entity={editableRace}
						config={raceEditorConfig}
						relationOptions={relationOptions}
						onSave={saveChanges}
						onDiscard={discardChanges}
					/>
				{:else}
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
				{/if}
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

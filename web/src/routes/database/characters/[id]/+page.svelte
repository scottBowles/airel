<script lang="ts">
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData as RoutePageData } from './$houdini';
	import {
		type EntityEditorOptionsStore,
		LockCharacterEditorStore,
		UnlockCharacterEditorStore,
		UpdateCharacterEditorStore,
		UpdateCharacterImagesStore
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
		detailSectionTitleClass,
		getLogNodes,
		getNamedNodes,
		type LogNode,
		type NamedNode,
		type RelationGroup
	} from '$lib/database-detail';
import { extractMutationErrorMessage, getOperationInfoMessage } from '$lib/mutation-errors';
import { fromStore } from 'svelte/store';
import { Pencil } from 'lucide-svelte';
import { toast } from 'svelte-sonner';

type PageData = RoutePageData & {
	EntityEditorOptions: EntityEditorOptionsStore;
};

const characterEditorConfig: DatabaseEntityEditorConfig = {
	entityLabel: 'Character',
	showRace: true,
	primaryRelations: [{ key: 'associations', title: 'Affiliations' }]
};

	let { data }: { data: PageData } = $props();
	let CharacterDetail = $derived(data.CharacterDetail);
	let char = $derived($CharacterDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
let EntityEditorOptionsResult = $derived.by(() => fromStore(data.EntityEditorOptions).current);
let relationOptions = $derived.by(() =>
	buildEntityEditorRelationOptions(EntityEditorOptionsResult?.data ?? undefined)
);
let lockOwnerName = $derived.by(() =>
	char && char.__typename === 'Character' && char.lockUser ? getLockUserDisplayName(char.lockUser) : null
);
	let editableCharacter = $derived.by<DatabaseEntityDraft | null>(() => {
		if (!char || char.__typename !== 'Character') {
			return null;
		}

		return {
			...DEFAULT_DATABASE_ENTITY_DRAFT,
			id: char.id,
			name: char.name ?? '',
			description: char.description ?? '',
			markdownNotes: char.markdownNotes ?? '',
			size: char.size ?? '',
			raceId: char.race?.id ?? '',
			associations: mapNamedRelationOptions('associations', char.associations),
			relatedArtifacts: mapNamedRelationOptions('artifacts', char.relatedArtifacts),
			relatedAssociations: mapNamedRelationOptions('associations', char.relatedAssociations),
			relatedCharacters: mapNamedRelationOptions('characters', char.relatedCharacters),
			relatedItems: mapNamedRelationOptions('items', char.relatedItems),
			relatedPlaces: mapNamedRelationOptions('places', char.relatedPlaces),
			relatedRaces: mapNamedRelationOptions('races', char.relatedRaces)
		};
	});
	let affiliationNodes = $derived.by((): NamedNode[] => {
		if (!char || char.__typename !== 'Character') {
			return [];
		}

		return getNamedNodes(char.associations);
	});
	let relationGroups = $derived.by((): RelationGroup[] => {
		if (!char || char.__typename !== 'Character') {
			return [];
		}

		return buildRelationGroups({
			relatedArtifacts: char.relatedArtifacts,
			relatedAssociations: char.relatedAssociations,
			relatedCharacters: char.relatedCharacters,
			relatedItems: char.relatedItems,
			relatedPlaces: char.relatedPlaces,
			relatedRaces: char.relatedRaces
		});
	});
	let logEntries = $derived.by((): LogNode[] => {
		if (!char || char.__typename !== 'Character') {
			return [];
		}

		return getLogNodes(char.logs);
	});
	let hasMarkdownNotes = $derived(
		!!(char && char.__typename === 'Character' && char.markdownNotes?.trim())
	);
	let sanitizedMarkdownNotes = $derived.by(() => {
		if (!char || char.__typename !== 'Character' || !char.markdownNotes) {
			return '';
		}

		return DOMPurify.sanitize(char.markdownNotes);
	});

	const updateImagesStore = new UpdateCharacterImagesStore();
	const lockStore = new LockCharacterEditorStore();
	const unlockStore = new UnlockCharacterEditorStore();
	const updateEditorStore = new UpdateCharacterEditorStore();

	async function saveImages(newIds: string[]) {
	await updateImagesStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}

async function acquireLock() {
	if (!char || char.__typename !== 'Character') {
		return;
	}

	const response = await lockStore.mutate({ id: char.id });
	const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

	if (responseErrorMessage) {
		toast.error(responseErrorMessage);
		return;
	}

	const payload = response.data?.lock;

	if (!payload) {
		throw new Error('No character lock payload returned.');
	}

	toast.success('Character lock acquired.');
}

async function discardChanges() {
	if (!char || char.__typename !== 'Character') {
		return;
	}

	const response = await unlockStore.mutate({ id: char.id });
	const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

	if (responseErrorMessage) {
		throw new Error(responseErrorMessage);
	}

	const payload = response.data?.unlock;

	if (!payload) {
		throw new Error('No character unlock payload returned.');
	}

	toast.success('Character changes discarded.');
	return payload;
}

async function saveChanges(draft: DatabaseEntityDraft) {
	const response = await updateEditorStore.mutate({
		id: draft.id,
		name: normalizeTextValue(draft.name, true),
		description: normalizeTextValue(draft.description),
		markdownNotes: normalizeTextValue(draft.markdownNotes),
		size: normalizeTextValue(draft.size, true),
		race: draft.raceId ? { id: draft.raceId } : null,
		associations: buildNodeInputList(draft.associations),
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

	const payload = response.data?.updateCharacter;

	if (!payload) {
		throw new Error('No character update payload returned.');
	}

	const operationInfoMessage = getOperationInfoMessage(payload, 'Failed to save character changes.');

	if (!operationInfoMessage) {
		toast.success('Character changes saved.');
	}

	return payload;
}
</script>

{#if char && char.__typename === 'Character'}
	<div class="db-detail">
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				<h1 class="db-detail-title">{char.name}</h1>
				{#if char.race}
					<a
						href={resolve(`/database/races/${char.race.id}`)}
						class="inline-flex items-center text-base leading-none tracking-[0.14em] text-emerald-400 uppercase transition-colors hover:text-emerald-300 sm:text-lg"
					>
						<span class="font-display text-lg tracking-[0.14em] text-emerald-400 sm:text-xl">
							{char.race.name}
						</span>
					</a>
				{/if}
			</div>
			<div class="flex flex-col items-start gap-3 sm:items-end">
				<a href={resolve('/database/characters')} class="db-back-link"> ← Back to Characters </a>
				{#if isAdmin}
					<div class="flex flex-wrap items-center gap-3">
						{#if char.lockUser && !char.lockedBySelf && lockOwnerName}
							<div class="rounded-sm border border-slate-800 bg-slate-950/80 px-3 py-2 font-mono text-sm text-slate-300">
								Locked by {lockOwnerName}
							</div>
						{/if}
						{#if !char.lockedBySelf}
							<button
								type="button"
								onclick={acquireLock}
								class="text-industrial-amber inline-flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-sm border border-slate-700 bg-slate-950 transition-colors hover:border-industrial-amber hover:text-white"
								aria-label="Edit character"
								title="Edit character"
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
				<AdminImageManager imageIds={char.imageIds || []} canEdit={isAdmin} onSave={saveImages} />

				<div class={detailRailCardClass + ' hidden lg:block'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
			</div>

			<div class="db-detail-main order-2 lg:order-1">
				{#if isAdmin && char.lockedBySelf && editableCharacter}
					<DatabaseEntityEditor
						entity={editableCharacter}
						config={characterEditorConfig}
						relationOptions={relationOptions}
						onSave={saveChanges}
						onDiscard={discardChanges}
					/>
				{:else}
				<div class={detailPanelClass}>
					<p class="text-sm leading-relaxed whitespace-pre-wrap text-zinc-300 sm:text-base">
						{char.description || 'No description provided.'}
					</p>
				</div>

				{#if affiliationNodes.length > 0}
					<div class={detailPanelClass}>
						<h3 class={detailSectionTitleClass}>Affiliations</h3>
						<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
							{#each affiliationNodes as node (node.id)}
								<a
									href={resolve('/database/associations/[id]', { id: node.id })}
									class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
								>
									{node.name}
								</a>
								{#if node !== affiliationNodes[affiliationNodes.length - 1]}
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
				{/if}
			</div>
		</div>
	</div>
{:else if $CharacterDetail.fetching}
	<div class="p-12 text-center font-mono text-zinc-500">Retrieving character record...</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Character not found or failed to load.</p>
	</div>
{/if}

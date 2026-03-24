<script lang="ts">
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData as RoutePageData } from './$houdini';
	import {
		type EntityEditorOptionsStore,
		LockAssociationEditorStore,
		UnlockAssociationEditorStore,
		UpdateAssociationEditorStore,
		UpdateAssociationImagesStore
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
		getNamedNodes
	} from '$lib/database-detail';
	import { extractMutationErrorMessage, getOperationInfoMessage } from '$lib/mutation-errors';
	import { fromStore } from 'svelte/store';
	import { Pencil } from 'lucide-svelte';
	import { toast } from 'svelte-sonner';

	type PageData = RoutePageData & {
		EntityEditorOptions: EntityEditorOptionsStore;
	};

	const associationEditorConfig: DatabaseEntityEditorConfig = {
		entityLabel: 'Association',
		primaryRelations: [{ key: 'characters', title: 'Members' }]
	};

	let { data }: { data: PageData } = $props();
	let AssociationDetail = $derived(data.AssociationDetail);
	let association = $derived($AssociationDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
	let EntityEditorOptionsResult = $derived.by(() => fromStore(data.EntityEditorOptions).current);
	let relationOptions = $derived.by(() =>
		buildEntityEditorRelationOptions(EntityEditorOptionsResult?.data ?? undefined)
	);
	let lockOwnerName = $derived.by(() =>
		association && association.__typename === 'Association' && association.lockUser
			? getLockUserDisplayName(association.lockUser)
			: null
	);
		let editableAssociation = $derived.by<DatabaseEntityDraft | null>(() => {
			if (!association || association.__typename !== 'Association') {
				return null;
			}

			return {
				...DEFAULT_DATABASE_ENTITY_DRAFT,
				id: association.id,
				name: association.name ?? '',
				description: association.description ?? '',
				markdownNotes: association.markdownNotes ?? '',
				characters: mapNamedRelationOptions('characters', association.characters),
				relatedArtifacts: mapNamedRelationOptions('artifacts', association.relatedArtifacts),
				relatedAssociations: mapNamedRelationOptions('associations', association.relatedAssociations),
				relatedCharacters: mapNamedRelationOptions('characters', association.relatedCharacters),
				relatedItems: mapNamedRelationOptions('items', association.relatedItems),
				relatedPlaces: mapNamedRelationOptions('places', association.relatedPlaces),
				relatedRaces: mapNamedRelationOptions('races', association.relatedRaces)
			};
		});
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

	const updateImagesStore = new UpdateAssociationImagesStore();
	const lockStore = new LockAssociationEditorStore();
	const unlockStore = new UnlockAssociationEditorStore();
	const updateEditorStore = new UpdateAssociationEditorStore();

	async function saveImages(newIds: string[]) {
	await updateImagesStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}

async function acquireLock() {
	if (!association || association.__typename !== 'Association') {
		return;
	}

	const response = await lockStore.mutate({ id: association.id });
	const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

	if (responseErrorMessage) {
		toast.error(responseErrorMessage);
		return;
	}

	const payload = response.data?.lock;

	if (!payload) {
		throw new Error('No association lock payload returned.');
	}

	toast.success('Association lock acquired.');
}

async function discardChanges() {
	if (!association || association.__typename !== 'Association') {
		return;
	}

	const response = await unlockStore.mutate({ id: association.id });
	const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

	if (responseErrorMessage) {
		throw new Error(responseErrorMessage);
	}

	const payload = response.data?.unlock;

	if (!payload) {
		throw new Error('No association unlock payload returned.');
	}

	toast.success('Association changes discarded.');
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

	const payload = response.data?.updateAssociation;

	if (!payload) {
		throw new Error('No association update payload returned.');
	}

	const operationInfoMessage = getOperationInfoMessage(payload, 'Failed to save association changes.');

	if (!operationInfoMessage) {
		toast.success('Association changes saved.');
	}

	return payload;
}
</script>

{#if association && association.__typename === 'Association'}
	<div class="db-detail">
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				<h1 class="db-detail-title">{association.name}</h1>
			</div>
			<div class="flex flex-col items-start gap-3 sm:items-end">
				<a href={resolve('/database/associations')} class="db-back-link"> ← Back to Associations </a>
				{#if isAdmin}
					<div class="flex flex-wrap items-center gap-3">
						{#if association.lockUser && !association.lockedBySelf && lockOwnerName}
							<div class="rounded-sm border border-slate-800 bg-slate-950/80 px-3 py-2 font-mono text-sm text-slate-300">
								Locked by {lockOwnerName}
							</div>
						{/if}
						{#if !association.lockedBySelf}
							<button
								type="button"
								onclick={acquireLock}
								class="text-industrial-amber inline-flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-sm border border-slate-700 bg-slate-950 transition-colors hover:border-industrial-amber hover:text-white"
								aria-label="Edit association"
								title="Edit association"
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
				{#if isAdmin && association.lockedBySelf && editableAssociation}
					<DatabaseEntityEditor
						entity={editableAssociation}
						config={associationEditorConfig}
						relationOptions={relationOptions}
						onSave={saveChanges}
						onDiscard={discardChanges}
					/>
				{:else}
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
				{/if}
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

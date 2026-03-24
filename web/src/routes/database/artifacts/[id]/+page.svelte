<script lang="ts">
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData as RoutePageData } from './$houdini';
	import {
		type EntityEditorOptionsStore,
		LockArtifactEditorStore,
		UnlockArtifactEditorStore,
		UpdateArtifactEditorStore,
		UpdateArtifactImagesStore
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

	const artifactEditorConfig: DatabaseEntityEditorConfig = {
		entityLabel: 'Artifact',
		showNotes: true,
		primaryRelations: [{ key: 'items', title: 'Items' }]
	};

	let { data }: { data: PageData } = $props();
	let ArtifactDetail = $derived(data.ArtifactDetail);
	let artifact = $derived($ArtifactDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
	let EntityEditorOptionsResult = $derived.by(() => fromStore(data.EntityEditorOptions).current);
	let relationOptions = $derived.by(() =>
		buildEntityEditorRelationOptions(EntityEditorOptionsResult?.data ?? undefined)
	);
	let lockOwnerName = $derived.by(() =>
		artifact && artifact.__typename === 'Artifact' && artifact.lockUser
			? getLockUserDisplayName(artifact.lockUser)
			: null
	);
		let editableArtifact = $derived.by<DatabaseEntityDraft | null>(() => {
			if (!artifact || artifact.__typename !== 'Artifact') {
				return null;
			}

			return {
				...DEFAULT_DATABASE_ENTITY_DRAFT,
				id: artifact.id,
				name: artifact.name ?? '',
				description: artifact.description ?? '',
				markdownNotes: artifact.markdownNotes ?? '',
				notes: artifact.notes ?? '',
				items: mapNamedRelationOptions('items', artifact.items),
				relatedArtifacts: mapNamedRelationOptions('artifacts', artifact.relatedArtifacts),
				relatedAssociations: mapNamedRelationOptions('associations', artifact.relatedAssociations),
				relatedCharacters: mapNamedRelationOptions('characters', artifact.relatedCharacters),
				relatedItems: mapNamedRelationOptions('items', artifact.relatedItems),
				relatedPlaces: mapNamedRelationOptions('places', artifact.relatedPlaces),
				relatedRaces: mapNamedRelationOptions('races', artifact.relatedRaces)
			};
		});
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

		const updateImagesStore = new UpdateArtifactImagesStore();
		const lockStore = new LockArtifactEditorStore();
		const unlockStore = new UnlockArtifactEditorStore();
		const updateEditorStore = new UpdateArtifactEditorStore();

	async function saveImages(newIds: string[]) {
		await updateImagesStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}

	async function acquireLock() {
		if (!artifact || artifact.__typename !== 'Artifact') {
			return;
		}

		const response = await lockStore.mutate({ id: artifact.id });
		const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

		if (responseErrorMessage) {
			toast.error(responseErrorMessage);
			return;
		}

		const payload = response.data?.lock;

		if (!payload) {
			throw new Error('No artifact lock payload returned.');
		}

		toast.success('Artifact lock acquired.');
	}

	async function discardChanges() {
		if (!artifact || artifact.__typename !== 'Artifact') {
			return;
		}

		const response = await unlockStore.mutate({ id: artifact.id });
		const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

		if (responseErrorMessage) {
			throw new Error(responseErrorMessage);
		}

		const payload = response.data?.unlock;

		if (!payload) {
			throw new Error('No artifact unlock payload returned.');
		}

		toast.success('Artifact changes discarded.');
		return payload;
	}

	async function saveChanges(draft: DatabaseEntityDraft) {
		const response = await updateEditorStore.mutate({
			id: draft.id,
			name: normalizeTextValue(draft.name, true),
			description: normalizeTextValue(draft.description),
			markdownNotes: normalizeTextValue(draft.markdownNotes),
			notes: normalizeTextValue(draft.notes),
			items: buildNodeInputList(draft.items),
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

		const payload = response.data?.updateArtifact;

		if (!payload) {
			throw new Error('No artifact update payload returned.');
		}

		const operationInfoMessage = getOperationInfoMessage(payload, 'Failed to save artifact changes.');

		if (!operationInfoMessage) {
			toast.success('Artifact changes saved.');
		}

		return payload;
	}
</script>

{#if artifact && artifact.__typename === 'Artifact'}
	<div class="db-detail">
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				<h1 class="db-detail-title">{artifact.name}</h1>
			</div>
			<div class="flex flex-col items-start gap-3 sm:items-end">
				<a href={resolve('/database/artifacts')} class="db-back-link"> ← Back to Artifacts </a>
				{#if isAdmin}
					<div class="flex flex-wrap items-center gap-3">
						{#if artifact.lockUser && !artifact.lockedBySelf && lockOwnerName}
							<div class="rounded-sm border border-slate-800 bg-slate-950/80 px-3 py-2 font-mono text-sm text-slate-300">
								Locked by {lockOwnerName}
							</div>
						{/if}
						{#if !artifact.lockedBySelf}
							<button
								type="button"
								onclick={acquireLock}
								class="text-industrial-amber inline-flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-sm border border-slate-700 bg-slate-950 transition-colors hover:border-industrial-amber hover:text-white"
								aria-label="Edit artifact"
								title="Edit artifact"
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
					imageIds={artifact.imageIds || []}
					canEdit={isAdmin}
					onSave={saveImages}
				/>

				<div class={detailRailCardClass + ' hidden lg:block'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
			</div>

			<div class="db-detail-main order-2 lg:order-1">
				{#if isAdmin && artifact.lockedBySelf && editableArtifact}
					<DatabaseEntityEditor
						entity={editableArtifact}
						config={artifactEditorConfig}
						relationOptions={relationOptions}
						onSave={saveChanges}
						onDiscard={discardChanges}
					/>
				{:else}
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
					<RelationGroupList title="Related Entities" groups={relationGroups} />
				</div>

				<div class={detailPanelClass + ' lg:hidden'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
				{/if}
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

<script lang="ts">
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData as RoutePageData } from './$houdini';
	import {
		type EntityEditorOptionsStore,
		LockPlaceEditorStore,
		UnlockPlaceEditorStore,
		UpdatePlaceEditorStore,
		UpdatePlaceImagesStore
	} from '$houdini';
	import RelationGroupList from '$lib/components/database/RelationGroupList.svelte';
	import DatabaseEntityEditor from '$lib/components/database/DatabaseEntityEditor.svelte';
	import {
		type DatabasePlaceType,
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
		buildPlaceBreadcrumbs,
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

	const placeEditorConfig: DatabaseEntityEditorConfig = {
		entityLabel: 'Place',
		showPlaceType: true,
		showParentPlace: true
	};

	let { data }: { data: PageData } = $props();
	let PlaceDetail = $derived(data.PlaceDetail);
	let place = $derived($PlaceDetail.data?.node);
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
		place && place.__typename === 'Place' && place.lockUser
			? getLockUserDisplayName(place.lockUser)
			: null
	);
	let editablePlace = $derived.by<DatabaseEntityDraft | null>(() => {
		if (!place || place.__typename !== 'Place') {
			return null;
		}

		return {
			...DEFAULT_DATABASE_ENTITY_DRAFT,
			id: place.id,
			name: place.name ?? '',
			description: place.description ?? '',
			markdownNotes: place.markdownNotes ?? '',
			placeType: place.placeType ?? '',
			parentPlaceId: place.parent?.id ?? '',
			relatedArtifacts: mapNamedRelationOptions('artifacts', place.relatedArtifacts),
			relatedAssociations: mapNamedRelationOptions('associations', place.relatedAssociations),
			relatedCharacters: mapNamedRelationOptions('characters', place.relatedCharacters),
			relatedItems: mapNamedRelationOptions('items', place.relatedItems),
			relatedPlaces: mapNamedRelationOptions('places', place.relatedPlaces),
			relatedRaces: mapNamedRelationOptions('races', place.relatedRaces)
		};
	});
	let breadcrumbs = $derived.by(() => {
		if (!place || place.__typename !== 'Place') {
			return [];
		}

		return buildPlaceBreadcrumbs(place);
	});
	let childPlaces = $derived.by(() => {
		if (!place || place.__typename !== 'Place') {
			return [];
		}

		return getNamedNodes(place.children);
	});
	let relationGroups = $derived.by(() => {
		if (!place || place.__typename !== 'Place') {
			return [];
		}

		return buildRelationGroups({
			relatedArtifacts: place.relatedArtifacts,
			relatedAssociations: place.relatedAssociations,
			relatedCharacters: place.relatedCharacters,
			relatedItems: place.relatedItems,
			relatedPlaces: place.relatedPlaces,
			relatedRaces: place.relatedRaces
		});
	});
	let logEntries = $derived.by(() => {
		if (!place || place.__typename !== 'Place') {
			return [];
		}

		return getLogNodes(place.logs);
	});
	let hasMarkdownNotes = $derived(
		!!(place && place.__typename === 'Place' && place.markdownNotes?.trim())
	);
	let sanitizedMarkdownNotes = $derived.by(() => {
		if (!place || place.__typename !== 'Place' || !place.markdownNotes) {
			return '';
		}

		return DOMPurify.sanitize(place.markdownNotes);
	});

	const updateImagesStore = new UpdatePlaceImagesStore();
	const lockStore = new LockPlaceEditorStore();
	const unlockStore = new UnlockPlaceEditorStore();
	const updateEditorStore = new UpdatePlaceEditorStore();

	async function saveImages(newIds: string[]) {
		await updateImagesStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}

	async function acquireLock() {
		if (!place || place.__typename !== 'Place') {
			return;
		}

		const response = await lockStore.mutate({ id: place.id });
		const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

		if (responseErrorMessage) {
			toast.error(responseErrorMessage);
			return;
		}

		const payload = response.data?.lock;

		if (!payload) {
			throw new Error('No place lock payload returned.');
		}

		toast.success('Place lock acquired.');
	}

	async function discardChanges() {
		if (!place || place.__typename !== 'Place') {
			return;
		}

		const response = await unlockStore.mutate({ id: place.id });
		const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

		if (responseErrorMessage) {
			throw new Error(responseErrorMessage);
		}

		const payload = response.data?.unlock;

		if (!payload) {
			throw new Error('No place unlock payload returned.');
		}

		toast.success('Place changes discarded.');
		return payload;
	}

	async function saveChanges(draft: DatabaseEntityDraft) {
		const response = await updateEditorStore.mutate({
			id: draft.id,
			name: normalizeTextValue(draft.name, true),
			description: normalizeTextValue(draft.description),
			markdownNotes: normalizeTextValue(draft.markdownNotes),
			placeType: draft.placeType ? (draft.placeType as DatabasePlaceType) : null,
			parent: draft.parentPlaceId ? { id: draft.parentPlaceId } : null,
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

		const payload = response.data?.updatePlace;

		if (!payload) {
			throw new Error('No place update payload returned.');
		}

		const operationInfoMessage = getOperationInfoMessage(payload, 'Failed to save place changes.');

		if (!operationInfoMessage) {
			toast.success('Place changes saved.');
		}

		return payload;
	}
</script>

{#if place && place.__typename === 'Place'}
	<div class="db-detail">
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				{#if breadcrumbs.length > 0}
					<nav
						aria-label="Place hierarchy"
						class="flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[0.68rem] tracking-[0.18em] text-zinc-500 uppercase"
					>
						{#each breadcrumbs as crumb (crumb.id)}
							<a
								href={resolve('/database/places/[id]', { id: crumb.id })}
								class="transition-colors hover:text-emerald-300"
							>
								{crumb.name}
							</a>
							<span class="text-zinc-700" aria-hidden="true">/</span>
						{/each}
						<span class="text-zinc-300">{place.name}</span>
					</nav>
				{/if}
				<h1 class="db-detail-title">{place.name}</h1>
				{#if place.placeType}
					<div
						class="inline-flex items-center text-base leading-none tracking-[0.14em] text-emerald-400 uppercase sm:text-lg"
					>
						<span class="font-display text-lg tracking-[0.14em] text-emerald-400 sm:text-xl">
							{place.placeType}
						</span>
					</div>
				{/if}
			</div>
			<div class="flex flex-col items-start gap-3 sm:items-end">
				<a href={resolve('/database/places')} class="db-back-link"> ← Back to Places </a>
				{#if isAdmin}
					<div class="flex flex-wrap items-center gap-3">
						{#if place.lockUser && !place.lockedBySelf && lockOwnerName}
							<div class="rounded-sm border border-slate-800 bg-slate-950/80 px-3 py-2 font-mono text-sm text-slate-300">
								Locked by {lockOwnerName}
							</div>
						{/if}
						{#if !place.lockedBySelf}
							<button
								type="button"
								onclick={acquireLock}
								class="text-industrial-amber inline-flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-sm border border-slate-700 bg-slate-950 transition-colors hover:border-industrial-amber hover:text-white"
								aria-label="Edit place"
								title="Edit place"
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
				<AdminImageManager imageIds={place.imageIds || []} canEdit={isAdmin} onSave={saveImages} />

				<div class={detailRailCardClass + ' hidden lg:block'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
			</div>

			<div class="db-detail-main order-2 lg:order-1">
				{#if isAdmin && place.lockedBySelf && editablePlace}
					<DatabaseEntityEditor
						entity={editablePlace}
						config={placeEditorConfig}
						relationOptions={relationOptions}
						onSave={saveChanges}
						onDiscard={discardChanges}
					/>
				{:else}
				<div class={detailPanelClass}>
					<p class="text-sm leading-relaxed whitespace-pre-wrap text-zinc-300 sm:text-base">
						{place.description || 'No description provided.'}
					</p>
				</div>

				{#if childPlaces.length > 0}
					<div class={detailPanelClass}>
						<h3 class={detailSectionTitleClass}>Locations Within</h3>
						<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
							{#each childPlaces as node (node.id)}
								<a
									href={resolve('/database/places/[id]', { id: node.id })}
									class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
								>
									{node.name}
								</a>
								{#if node !== childPlaces[childPlaces.length - 1]}
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
{:else if $PlaceDetail.fetching}
	<div class="p-12 text-center font-mono text-zinc-500">Retrieving place record...</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Place not found or failed to load.</p>
	</div>
{/if}

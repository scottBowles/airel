<script lang="ts">
	import { resolve } from '$app/paths';
	import { Pencil } from 'lucide-svelte';
	import {
		LockLogStore,
		type LogDetail$result,
		type LogEditorOptionsStore,
		UnlockLogStore,
		UpdateLogStore
	} from '$houdini';
	import RelationGroupList from '$lib/components/database/RelationGroupList.svelte';
	import LogEditor from '$lib/components/logs/LogEditor.svelte';
	import {
		sortRelationOptions,
		type EditableLogData,
		type LogEditorOptions,
		type RelationOption
	} from '$lib/components/logs/log-editor-types';
	import {
		buildGameLogRelationGroups,
		detailPanelClass,
		detailSectionTitleClass,
		getNamedNodes
	} from '$lib/database-detail';
	import { extractMutationErrorMessage, getOperationInfoMessage } from '$lib/mutation-errors';
	import { formatGameDate } from '$lib/utils';
	import { fromStore } from 'svelte/store';
	import { toast } from 'svelte-sonner';
	import type { PageData as RoutePageData } from './$houdini';

	type PageData = RoutePageData & {
		LogEditorOptions: LogEditorOptionsStore;
	};

	type GameLogNode = Extract<LogDetail$result['node'], { __typename: 'GameLog' }>;
	type EntityRouteKey = 'artifacts' | 'associations' | 'characters' | 'items' | 'places' | 'races';
	type GameLogLockUser = NonNullable<GameLogNode['lockUser']>;

	let { data }: { data: PageData } = $props();
	let LogDetail = $derived.by(() => fromStore(data.LogDetail).current);
	let LogEditorOptionsResult = $derived.by(() => fromStore(data.LogEditorOptions).current);
	let Me = $derived.by(() => fromStore(data.Me).current);
	let me = $derived(Me?.data?.me);
	let isAdmin = $derived(!!(me?.isStaff || me?.isSuperuser));
	let gameLog = $derived<GameLogNode | null>(
		LogDetail?.data?.node?.__typename === 'GameLog' ? LogDetail.data.node : null
	);
	let lockOwnerName = $derived.by(() => {
		if (!gameLog?.lockUser) {
			return null;
		}

		return getLockUserDisplayName(gameLog.lockUser);
	});
	let lockPending = $state(false);
	let logRelationGroups = $derived.by(() => {
		if (!gameLog) {
			return [];
		}

		return buildGameLogRelationGroups({
			artifacts: gameLog.artifacts,
			associations: gameLog.associations,
			characters: gameLog.characters,
			items: gameLog.items,
			places: gameLog.places,
			races: gameLog.races
		});
	});
	let placesSetIn = $derived.by(() => (gameLog ? getNamedNodes(gameLog.placesSetIn) : []));
	let relationOptions = $derived.by<LogEditorOptions>(() => {
		const editorOptions = LogEditorOptionsResult?.data;

		const mapConnection = (
			entityType: EntityRouteKey,
			connection:
				| {
						edges?: Array<{ node: { id: string; name: string } }> | null;
				  }
				| null
				| undefined
		): RelationOption[] =>
			sortRelationOptions(
				connection?.edges?.map(({ node }) => ({
					id: node.id,
					name: node.name,
					href: buildEntityHref(entityType, node.id)
				})) ?? []
			);

		const mapPlaceConnection = (
			connection:
				| {
						edges?: Array<{
							node: {
								id: string;
								name: string;
								placeType?: string | null;
								parent?: { name: string } | null;
							};
						}> | null;
				  }
				| null
				| undefined
		): RelationOption[] =>
			sortRelationOptions(
				connection?.edges?.map(({ node }) => ({
					id: node.id,
					name: node.name,
					href: buildEntityHref('places', node.id),
					secondaryText: [node.placeType, node.parent?.name].filter(Boolean).join(' · ') || undefined
				})) ?? []
			);

		return {
			artifacts: mapConnection('artifacts', editorOptions?.artifacts),
			associations: mapConnection('associations', editorOptions?.associations),
			characters: mapConnection('characters', editorOptions?.characters),
			items: mapConnection('items', editorOptions?.items),
			places: mapPlaceConnection(editorOptions?.places),
			placesSetIn: mapPlaceConnection(editorOptions?.places),
			races: mapConnection('races', editorOptions?.races)
		};
	});
	let editableLog = $derived.by<EditableLogData | null>(() => {
		if (!gameLog) {
			return null;
		}

		const mapNamedNodes = (
			entityType: EntityRouteKey,
			connection:
				| {
						edges?: Array<{ node: { id: string; name: string } }> | null;
				  }
				| null
				| undefined
		): RelationOption[] =>
			sortRelationOptions(
				connection?.edges?.map(({ node }) => ({
					id: node.id,
					name: node.name,
					href: buildEntityHref(entityType, node.id)
				})) ?? []
			);

		return {
			id: gameLog.id,
			title: gameLog.title ?? '',
			brief: gameLog.brief ?? '',
			synopsis: gameLog.synopsis ?? '',
			gameDate: gameLog.gameDate ? formatGameDate(gameLog.gameDate) : '',
			artifacts: mapNamedNodes('artifacts', gameLog.artifacts),
			associations: mapNamedNodes('associations', gameLog.associations),
			characters: mapNamedNodes('characters', gameLog.characters),
			items: mapNamedNodes('items', gameLog.items),
			places: mapNamedNodes('places', gameLog.places),
			placesSetIn: mapNamedNodes('places', gameLog.placesSetIn),
			races: mapNamedNodes('races', gameLog.races)
		};
	});
	const lockStore = new LockLogStore();
	const unlockStore = new UnlockLogStore();
	const updateStore = new UpdateLogStore();

	function buildEntityHref(entityType: EntityRouteKey, id: string) {
		switch (entityType) {
			case 'artifacts':
				return resolve('/database/artifacts/[id]', { id });
			case 'associations':
				return resolve('/database/associations/[id]', { id });
			case 'characters':
				return resolve('/database/characters/[id]', { id });
			case 'items':
				return resolve('/database/items/[id]', { id });
			case 'places':
				return resolve('/database/places/[id]', { id });
			case 'races':
				return resolve('/database/races/[id]', { id });
		}
	}

	function getLockUserDisplayName(user: GameLogLockUser) {
		const firstName = user.firstName?.trim();
		const lastName = user.lastName?.trim();

		if (firstName && lastName) {
			return `${firstName} ${lastName}`;
		}

		if (firstName) {
			return firstName;
		}

		if (lastName) {
			return lastName;
		}

		return user.username;
	}

	function openExternalSource(url: string) {
		window.open(url, '_blank', 'noopener,noreferrer');
	}

	function buildNodeInputList(options: RelationOption[]) {
		return options.map((option) => ({ id: option.id }));
	}

	function normalizeTextValue(value: string, trim = false) {
		const normalizedValue = trim ? value.trim() : value;
		return normalizedValue ? normalizedValue : null;
	}

	function normalizeGameDateForMutation(value: string) {
		const normalizedValue = value.trim();
		return normalizedValue ? new Date(`${normalizedValue}T00:00:00Z`) : null;
	}

	async function acquireLock() {
		if (!gameLog || lockPending) {
			return;
		}

		lockPending = true;

		try {
			const response = await lockStore.mutate({ id: gameLog.id });
			const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

			if (responseErrorMessage) {
				toast.error(responseErrorMessage);
				return;
			}

			const payload = response.data?.lock;
			if (!payload) {
				throw new Error('No lock payload returned.');
			}

			toast.success('Log lock acquired.');
		} catch (error) {
			console.error('Failed to acquire log lock:', error);
			toast.error(extractMutationErrorMessage(error) ?? 'Failed to acquire log lock.');
		} finally {
			lockPending = false;
		}
	}

	async function discardChanges() {
		if (!gameLog) {
			return;
		}

		const response = await unlockStore.mutate({ id: gameLog.id });
		const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

		if (responseErrorMessage) {
			throw new Error(responseErrorMessage);
		}

		const payload = response.data?.unlock;

		if (!payload) {
			throw new Error('No unlock payload returned.');
		}

		toast.success('Log changes discarded.');
		return payload;
	}

	async function saveChanges(draft: EditableLogData) {
		const response = await updateStore.mutate({
			id: draft.id,
			title: normalizeTextValue(draft.title, true),
			brief: normalizeTextValue(draft.brief),
			synopsis: normalizeTextValue(draft.synopsis),
			gameDate: normalizeGameDateForMutation(draft.gameDate),
			artifacts: buildNodeInputList(draft.artifacts),
			associations: buildNodeInputList(draft.associations),
			characters: buildNodeInputList(draft.characters),
			items: buildNodeInputList(draft.items),
			places: buildNodeInputList(draft.places),
			placesSetIn: buildNodeInputList(draft.placesSetIn),
			races: buildNodeInputList(draft.races)
		});
		const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

		if (responseErrorMessage) {
			throw new Error(responseErrorMessage);
		}

		const payload = response.data?.updateGamelog;

		if (!payload) {
			throw new Error('No update payload returned.');
		}

		const operationInfoMessage = getOperationInfoMessage(payload, 'Failed to save log changes.');

		if (!operationInfoMessage) {
			toast.success('Log changes saved.');
		}

		return payload;
	}
</script>

<div class="log-detail-page">
	<div>
		<a href={resolve('/logs')} class="log-back-link">
			<span>&lt;</span> RETURN TO CHRONICLE
		</a>
	</div>

	{#if LogDetail?.fetching}
		<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80">
			<div class="text-industrial-amber animate-pulse font-mono">RETRIEVING RECORD...</div>
		</div>
	{:else if LogDetail?.errors}
		<div class="border border-red-500/50 bg-red-900/20 p-6 font-mono text-red-500">
			ERROR: UNABLE TO DECRYPT LOG DATA.
			<pre class="mt-4 text-xs">{JSON.stringify(LogDetail.errors, null, 2)}</pre>
		</div>
	{:else if gameLog}
		<header class="log-panel border-industrial-dim border-t-2">
			<div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
				<div>
					<h1 class="log-title mb-2">
						{gameLog.title}
					</h1>
					<div class="log-meta">
						<span>DATE: {formatGameDate(gameLog.gameDate)}</span>
						{#if gameLog.url}
							<span class="inline-flex items-center gap-2 whitespace-nowrap">
								<span class="text-slate-600" aria-hidden="true">|</span>
								<button
									type="button"
									onclick={() => openExternalSource(gameLog.url)}
									class="inline-flex min-h-11 items-center border border-transparent px-1 hover:text-white hover:underline"
								>
									SOURCE LINK ↗
								</button>
							</span>
						{/if}
					</div>
				</div>

				{#if isAdmin && !gameLog.lockUser}
					<button
						type="button"
						onclick={acquireLock}
						disabled={lockPending}
						class="text-industrial-amber inline-flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center self-start rounded-sm border border-slate-700 bg-slate-950 transition-colors hover:border-industrial-amber hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
						aria-label={lockPending ? 'Acquiring edit lock' : 'Edit log'}
						title={lockPending ? 'Acquiring edit lock' : 'Edit log'}
					>
						<Pencil class="h-4 w-4" aria-hidden="true" />
					</button>
				{:else if isAdmin && gameLog.lockUser && !gameLog.lockedBySelf && lockOwnerName}
					<div class="self-start rounded-sm border border-slate-800 bg-slate-950/80 px-3 py-2 font-mono text-sm text-slate-300">
						Locked by {lockOwnerName}
					</div>
				{/if}
			</div>
		</header>

		<div class="space-y-6">
			{#if isAdmin && gameLog.lockedBySelf && editableLog}
				<LogEditor log={editableLog} relationOptions={relationOptions} onSave={saveChanges} onDiscard={discardChanges} />
			{:else}
				{#if gameLog.brief}
					<div class="log-abstract border-industrial-amber border-l-3">
						<p class="font-body text-base text-slate-300 italic sm:text-lg">{gameLog.brief}</p>
					</div>
				{/if}

				<div class={detailPanelClass}>
					<h3 class={detailSectionTitleClass}>Places Set In</h3>

					{#if placesSetIn.length > 0}
						<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
							{#each placesSetIn as place (place.id)}
								<a
									href={resolve('/database/places/[id]', { id: place.id })}
									class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
								>
									{place.name}
								</a>
								{#if place !== placesSetIn[placesSetIn.length - 1]}
									<span class="text-zinc-700" aria-hidden="true">•</span>
								{/if}
							{/each}
						</div>
					{:else}
						<p class="text-sm text-zinc-500">No locations recorded for this log.</p>
					{/if}
				</div>

				<div class="log-panel prose prose-lg max-w-none text-slate-300 prose-invert">
					<p class="leading-relaxed whitespace-pre-wrap">
						{gameLog.synopsis || 'No detailed transcript available.'}
					</p>
				</div>

				<div class={detailPanelClass}>
					<RelationGroupList
						title="Found In This Log"
						groups={logRelationGroups}
						emptyMessage="No linked entities recorded for this log."
					/>
				</div>
			{/if}
		</div>
	{/if}
</div>

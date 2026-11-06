<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import EntityDetail from '$lib/components/EntityDetail.svelte';
	import EntityPicker from '$lib/components/EntityPicker.svelte';
	import Panel from '$lib/components/Panel.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import NotFound from '$lib/components/NotFound.svelte';
	import ErrorState from '$lib/components/ErrorState.svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.RaceDetail).current);
	let fetching = $derived(store?.fetching ?? true);
	let errors = $derived(store?.errors ?? null);
	let entity = $derived(store?.data?.node?.__typename === 'Race' ? store.data.node : null);

	const lockMutation = graphql(`
		mutation LockRace($id: ID!) {
			lock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const unlockMutation = graphql(`
		mutation UnlockRace($id: ID!) {
			unlock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const updateMutation = graphql(`
		mutation UpdateRaceDetail($input: RaceInputPartial!) {
			updateRace(input: $input) {
				... on Race {
					id name description markdownNotes lockedBySelf
					characters(first: 50) { edges { node { id name } } }
					relatedCharacters(first: 50) { edges { node { id name } } }
					relatedPlaces(first: 50) { edges { node { id name } } }
					relatedAssociations(first: 50) { edges { node { id name } } }
					relatedItems(first: 50) { edges { node { id name } } }
					relatedArtifacts(first: 50) { edges { node { id name } } }
					relatedRaces(first: 50) { edges { node { id name } } }
				}
				... on OperationInfo {
					messages { field kind message }
				}
			}
		}
	`);

	async function handleLock() {
		try {
			if (!entity) return;
			const result = await lockMutation.mutate({ id: entity.id });
			if (result.errors?.length) {
				toast.error(result.errors[0].message);
			}
		} catch {
			toast.error('Failed to lock for editing');
		}
	}
	async function handleUnlock() {
		try {
			if (!entity) return;
			const result = await unlockMutation.mutate({ id: entity.id });
			if (result.errors?.length) {
				toast.error(result.errors[0].message);
			}
		} catch {
			toast.error('Failed to unlock');
		}
	}

	async function handleSave(fields: Record<string, unknown> & { name: string; description: string; markdownNotes: string }) {
		if (!entity) return false;
		try {
			const { name: n, description: d, markdownNotes: m, ...relatedChanges } = fields;
			const result = await updateMutation.mutate({
				input: {
					id: entity.id,
					name: n,
					description: d,
					markdownNotes: m,
					characters: editMemberChanges.add.length || editMemberChanges.remove.length
						? { ...(editMemberChanges.add.length ? { add: editMemberChanges.add.map(e => ({ id: e.id })) } : {}), ...(editMemberChanges.remove.length ? { remove: editMemberChanges.remove.map(id => ({ id })) } : {}) }
						: undefined,
					...relatedChanges,
				},
			});
			if (result.errors?.length) {
				toast.error(result.errors[0].message);
				return false;
			}
			if (result.data?.updateRace?.__typename === 'Race') {
				toast.success('Race updated');
				return true;
			}
			toast.error('Failed to update race');
			return false;
		} catch {
			toast.error('An error occurred');
			return false;
		}
	}

	// Members editing state
	let editMemberChanges = $state<{ add: Array<{ id: string; name: string }>; remove: string[] }>({ add: [], remove: [] });

	function getEffectiveMembers() {
		const existing = entity?.characters?.edges.map(e => e.node) ?? [];
		const removedSet = new Set(editMemberChanges.remove);
		return {
			kept: existing.filter(e => !removedSet.has(e.id)),
			removed: existing.filter(e => removedSet.has(e.id)),
			added: editMemberChanges.add,
		};
	}

	$effect(() => {
		if (!entity?.lockedBySelf) {
			editMemberChanges = { add: [], remove: [] };
		}
	});
</script>

<svelte:head>
	<title>{entity?.name ?? 'Race'} — Database — Kontularien</title>
</svelte:head>

{#if fetching && !entity}
	<LoadingState message="SCANNING RACE RECORDS" />
{:else if errors}
	<ErrorState {errors} />
{:else if entity}
	<EntityDetail
		entityId={entity.id}
		name={entity.name}
		description={entity.description}
		thumbnailId={entity.thumbnailId}
		imageIds={entity.imageIds}
		markdownNotes={entity.markdownNotes}
		backHref="/database/races"
		backLabel="Back to Races"
		locked={!!entity.lockUser && !entity.lockedBySelf}
		lockedBySelf={entity.lockedBySelf}
		lockUser={entity.lockUser}
		onlock={handleLock}
		onunlock={handleUnlock}
		onsave={handleSave}
		relatedCharacters={entity.relatedCharacters}
		relatedPlaces={entity.relatedPlaces}
		relatedAssociations={entity.relatedAssociations}
		relatedItems={entity.relatedItems}
		relatedArtifacts={entity.relatedArtifacts}
		relatedRaces={entity.relatedRaces}
		logs={entity.logs}
	>
		{#snippet extraInfo()}
			{#if entity.characters && entity.characters.edges.length > 0}
				<Panel>
					<h2 class="title-section mb-3">Known Members</h2>
					<div class="flex flex-wrap gap-2">
						{#each entity.characters.edges as edge}
							<a
								href="/database/characters/{edge.node.id}"
								class="border border-border-dim bg-void px-2 py-0.5 text-xs text-accent-amber transition-colors hover:bg-accent-amber/10"
							>
								{edge.node.name}
							</a>
						{/each}
					</div>
				</Panel>
			{/if}
		{/snippet}
		{#snippet editExtraInfo()}
			<Panel>
				<h2 class="title-section mb-3">Known Members</h2>
				{@const effective = getEffectiveMembers()}
				{#if effective.kept.length || effective.added.length || effective.removed.length}
					<div class="flex flex-wrap gap-2 mb-3">
						{#each effective.kept as member}
							<span class="inline-flex items-center gap-1 border border-border-dim bg-void px-2 py-0.5 text-xs text-accent-amber">
								{member.name}
								<button type="button" onclick={() => { editMemberChanges.remove = [...editMemberChanges.remove, member.id]; }} class="cursor-pointer text-text-muted hover:text-accent-red ml-1">✕</button>
							</span>
						{/each}
						{#each effective.added as member}
							<span class="inline-flex items-center gap-1 border border-accent-green/30 bg-accent-green/5 px-2 py-0.5 text-xs text-accent-green">
								+ {member.name}
								<button type="button" onclick={() => { editMemberChanges.add = editMemberChanges.add.filter(e => e.id !== member.id); }} class="cursor-pointer text-text-muted hover:text-accent-red ml-1">✕</button>
							</span>
						{/each}
						{#each effective.removed as member}
							<span class="inline-flex items-center gap-1 border border-border-dim bg-void px-2 py-0.5 text-xs text-text-muted line-through opacity-50">
								{member.name}
								<button type="button" onclick={() => { editMemberChanges.remove = editMemberChanges.remove.filter(id => id !== member.id); }} class="cursor-pointer text-accent-amber hover:text-accent-amber ml-1 no-underline">↩</button>
							</span>
						{/each}
					</div>
				{/if}
				<EntityPicker
					entityType="Character"
					onselect={(e) => {
						if (!editMemberChanges.add.some(a => a.id === e.id)) {
							editMemberChanges.add = [...editMemberChanges.add, { id: e.id, name: e.name }];
						}
					}}
					exclude={[...(entity?.characters?.edges.map(e => e.node.id) ?? []), ...editMemberChanges.add.map(e => e.id)].filter(id => !editMemberChanges.remove.includes(id))}
				/>
			</Panel>
		{/snippet}
	</EntityDetail>
{:else}
	<NotFound entityName="Race" />
{/if}

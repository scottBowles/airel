<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import EntityDetail from '$lib/components/EntityDetail.svelte';
	import EntityPicker from '$lib/components/EntityPicker.svelte';
	import Panel from '$lib/components/Panel.svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.ArtifactDetail).current);
	let entity = $derived(store?.data?.node?.__typename === 'Artifact' ? store.data.node : null);

	const lockMutation = graphql(`
		mutation LockArtifact($id: ID!) {
			lock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const unlockMutation = graphql(`
		mutation UnlockArtifact($id: ID!) {
			unlock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const updateMutation = graphql(`
		mutation UpdateArtifactDetail($input: ArtifactInputPartial!) {
			updateArtifact(input: $input) {
				... on Artifact {
					id name description markdownNotes lockedBySelf
					items(first: 50) { edges { node { id name } } }
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
		if (entity) await lockMutation.mutate({ id: entity.id });
	}
	async function handleUnlock() {
		if (entity) await unlockMutation.mutate({ id: entity.id });
	}

	async function handleSave(fields: Record<string, unknown> & { name: string; description: string; markdownNotes: string }) {
		if (!entity) return false;
		const { name: n, description: d, markdownNotes: m, ...relatedChanges } = fields;
		const result = await updateMutation.mutate({
			input: {
				id: entity.id,
				name: n,
				description: d,
				markdownNotes: m,
				items: editItemChanges.add.length || editItemChanges.remove.length
					? { ...(editItemChanges.add.length ? { add: editItemChanges.add.map(e => ({ id: e.id })) } : {}), ...(editItemChanges.remove.length ? { remove: editItemChanges.remove.map(id => ({ id })) } : {}) }
					: undefined,
				...relatedChanges,
			},
		});
		if (result.data?.updateArtifact?.__typename === 'Artifact') {
			toast.success('Artifact updated');
			return true;
		}
		toast.error('Failed to update artifact');
		return false;
	}

	// Items editing state
	let editItemChanges = $state<{ add: Array<{ id: string; name: string }>; remove: string[] }>({ add: [], remove: [] });

	function getEffectiveItems() {
		const existing = entity?.items?.edges.map(e => e.node) ?? [];
		const removedSet = new Set(editItemChanges.remove);
		return {
			kept: existing.filter(e => !removedSet.has(e.id)),
			removed: existing.filter(e => removedSet.has(e.id)),
			added: editItemChanges.add,
		};
	}

	$effect(() => {
		if (!entity?.lockedBySelf) {
			editItemChanges = { add: [], remove: [] };
		}
	});
</script>

<svelte:head>
	<title>{entity?.name ?? 'Artifact'} — Database — Kontularien</title>
</svelte:head>

{#if entity}
	<EntityDetail
		entityId={entity.id}
		name={entity.name}
		description={entity.description}
		thumbnailId={entity.thumbnailId}
		imageIds={entity.imageIds}
		markdownNotes={entity.markdownNotes}
		backHref="/database/artifacts"
		backLabel="Back to Artifacts"
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
			{#if entity.items && entity.items.edges.length > 0}
				<Panel>
					<h2 class="title-section mb-3">Items</h2>
					<div class="flex flex-wrap gap-2">
						{#each entity.items.edges as edge}
							<a
								href="/database/items/{edge.node.id}"
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
				<h2 class="title-section mb-3">Items</h2>
				{@const effective = getEffectiveItems()}
				{#if effective.kept.length || effective.added.length || effective.removed.length}
					<div class="flex flex-wrap gap-2 mb-3">
						{#each effective.kept as item}
							<span class="inline-flex items-center gap-1 border border-border-dim bg-void px-2 py-0.5 text-xs text-accent-amber">
								{item.name}
								<button type="button" onclick={() => { editItemChanges.remove = [...editItemChanges.remove, item.id]; }} class="cursor-pointer text-text-muted hover:text-accent-red ml-1">✕</button>
							</span>
						{/each}
						{#each effective.added as item}
							<span class="inline-flex items-center gap-1 border border-accent-green/30 bg-accent-green/5 px-2 py-0.5 text-xs text-accent-green">
								+ {item.name}
								<button type="button" onclick={() => { editItemChanges.add = editItemChanges.add.filter(e => e.id !== item.id); }} class="cursor-pointer text-text-muted hover:text-accent-red ml-1">✕</button>
							</span>
						{/each}
						{#each effective.removed as item}
							<span class="inline-flex items-center gap-1 border border-border-dim bg-void px-2 py-0.5 text-xs text-text-muted line-through opacity-50">
								{item.name}
								<button type="button" onclick={() => { editItemChanges.remove = editItemChanges.remove.filter(id => id !== item.id); }} class="cursor-pointer text-accent-amber hover:text-accent-amber ml-1 no-underline">↩</button>
							</span>
						{/each}
					</div>
				{/if}
				<EntityPicker
					entityType="Item"
					onselect={(e) => {
						if (!editItemChanges.add.some(a => a.id === e.id)) {
							editItemChanges.add = [...editItemChanges.add, { id: e.id, name: e.name }];
						}
					}}
					exclude={[...(entity?.items?.edges.map(e => e.node.id) ?? []), ...editItemChanges.add.map(e => e.id)].filter(id => !editItemChanges.remove.includes(id))}
				/>
			</Panel>
		{/snippet}
	</EntityDetail>
{:else}
	<div class="content-pad">
		<div class="panel-border panel-bg panel-pad text-center">
			<p class="machine-text text-text-muted">Artifact not found</p>
		</div>
	</div>
{/if}

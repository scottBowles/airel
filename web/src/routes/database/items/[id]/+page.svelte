<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import EntityDetail from '$lib/components/EntityDetail.svelte';
	import Panel from '$lib/components/Panel.svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.ItemDetail).current);
	let entity = $derived(store?.data?.node?.__typename === 'Item' ? store.data.node : null);

	const lockMutation = graphql(`
		mutation LockItem($id: ID!) {
			lock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const unlockMutation = graphql(`
		mutation UnlockItem($id: ID!) {
			unlock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const updateMutation = graphql(`
		mutation UpdateItemDetail($input: ItemInputPartial!) {
			updateItem(input: $input) {
				... on Item {
					id name description markdownNotes lockedBySelf
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

	async function handleSave(fields: { name: string; description: string; markdownNotes: string }) {
		if (!entity) return false;
		const result = await updateMutation.mutate({
			input: {
				id: entity.id,
				name: fields.name,
				description: fields.description,
				markdownNotes: fields.markdownNotes,
			},
		});
		if (result.data?.updateItem?.__typename === 'Item') {
			toast.success('Item updated');
			return true;
		}
		toast.error('Failed to update item');
		return false;
	}
</script>

<svelte:head>
	<title>{entity?.name ?? 'Item'} — Database — KSS Kontularien</title>
</svelte:head>

{#if entity}
	<EntityDetail
		name={entity.name}
		description={entity.description}
		thumbnailId={entity.thumbnailId}
		imageIds={entity.imageIds}
		markdownNotes={entity.markdownNotes}
		backHref="/database/items"
		backLabel="Back to Items"
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
			<div class="flex flex-wrap gap-4">
				{#if entity.weapon}
					<Panel class="flex-1">
						<h2 class="title-section mb-1">Weapon</h2>
						<p class="text-text-primary">Attack Bonus: +{entity.weapon.attackBonus}</p>
					</Panel>
				{/if}
				{#if entity.armor}
					<Panel class="flex-1">
						<h2 class="title-section mb-1">Armor</h2>
						<p class="text-text-primary">AC Bonus: +{entity.armor.acBonus}</p>
					</Panel>
				{/if}
				{#if entity.equipment}
					<Panel class="flex-1">
						<h2 class="title-section mb-1">Equipment</h2>
						<p class="copy-readable text-sm text-text-secondary">{entity.equipment.briefDescription}</p>
					</Panel>
				{/if}
			</div>
		{/snippet}
	</EntityDetail>
{:else}
	<div class="content-pad">
		<div class="panel-border panel-bg panel-pad text-center">
			<p class="machine-text text-text-muted">Item not found</p>
		</div>
	</div>
{/if}

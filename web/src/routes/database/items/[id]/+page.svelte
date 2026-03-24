<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { mutation } from '$houdini';
	import EntityDetail from '$lib/components/EntityDetail.svelte';
	import Panel from '$lib/components/Panel.svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.ItemDetail).current);
	let entity = $derived(store?.data?.node?.__typename === 'Item' ? store.data.node : null);

	const lockMutation = mutation(/* GraphQL */ `
		mutation LockItem($id: ID!) {
			lock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const unlockMutation = mutation(/* GraphQL */ `
		mutation UnlockItem($id: ID!) {
			unlock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);

	async function handleLock() {
		if (entity) await lockMutation.mutate({ id: entity.id });
	}
	async function handleUnlock() {
		if (entity) await unlockMutation.mutate({ id: entity.id });
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

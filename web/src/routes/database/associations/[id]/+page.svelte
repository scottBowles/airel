<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import EntityDetail from '$lib/components/EntityDetail.svelte';
	import Panel from '$lib/components/Panel.svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.AssociationDetail).current);
	let entity = $derived(store?.data?.node?.__typename === 'Association' ? store.data.node : null);

	const lockMutation = graphql(`
		mutation LockAssociation($id: ID!) {
			lock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const unlockMutation = graphql(`
		mutation UnlockAssociation($id: ID!) {
			unlock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const updateMutation = graphql(`
		mutation UpdateAssociationDetail($input: AssociationInputPartial!) {
			updateAssociation(input: $input) {
				... on Association {
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
		if (result.data?.updateAssociation?.__typename === 'Association') {
			toast.success('Association updated');
			return true;
		}
		toast.error('Failed to update association');
		return false;
	}
</script>

<svelte:head>
	<title>{entity?.name ?? 'Association'} — Database — KSS Kontularien</title>
</svelte:head>

{#if entity}
	<EntityDetail
		name={entity.name}
		description={entity.description}
		thumbnailId={entity.thumbnailId}
		imageIds={entity.imageIds}
		markdownNotes={entity.markdownNotes}
		backHref="/database/associations"
		backLabel="Back to Associations"
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
					<h2 class="title-section mb-3">Members</h2>
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
	</EntityDetail>
{:else}
	<div class="content-pad">
		<div class="panel-border panel-bg panel-pad text-center">
			<p class="machine-text text-text-muted">Association not found</p>
		</div>
	</div>
{/if}

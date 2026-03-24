<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import EntityDetail from '$lib/components/EntityDetail.svelte';
	import Panel from '$lib/components/Panel.svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.CharacterDetail).current);
	let entity = $derived(store?.data?.node?.__typename === 'Character' ? store.data.node : null);

	let editSize = $state('');

	const lockMutation = graphql(`
		mutation LockCharacter($id: ID!) {
			lock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const unlockMutation = graphql(`
		mutation UnlockCharacter($id: ID!) {
			unlock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const updateMutation = graphql(`
		mutation UpdateCharacterDetail($input: CharacterInputPartial!) {
			updateCharacter(input: $input) {
				... on Character {
					id name description markdownNotes size lockedBySelf
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
				size: editSize,
			},
		});
		if (result.data?.updateCharacter?.__typename === 'Character') {
			toast.success('Character updated');
			return true;
		}
		toast.error('Failed to update character');
		return false;
	}
</script>

<svelte:head>
	<title>{entity?.name ?? 'Character'} — Database — KSS Kontularien</title>
</svelte:head>

{#if entity}
	<EntityDetail
		name={entity.name}
		description={entity.description}
		thumbnailId={entity.thumbnailId}
		imageIds={entity.imageIds}
		markdownNotes={entity.markdownNotes}
		backHref="/database/characters"
		backLabel="Back to Characters"
		locked={!!entity.lockUser && !entity.lockedBySelf}
		lockedBySelf={entity.lockedBySelf}
		lockUser={entity.lockUser}
		onlock={handleLock}
		onunlock={handleUnlock}
		onsave={handleSave}
		onstartediting={() => { editSize = entity?.size ?? ''; }}
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
				{#if entity.race}
					<Panel class="flex-1">
						<h2 class="title-section mb-1">Race</h2>
						<a href="/database/races/{entity.race.id}" class="text-accent-amber hover:text-accent-amber/80">
							{entity.race.name}
						</a>
					</Panel>
				{/if}
				{#if entity.size}
					<Panel class="flex-1">
						<h2 class="title-section mb-1">Size</h2>
						<p class="text-text-primary">{entity.size}</p>
					</Panel>
				{/if}
			</div>

			{#if entity.featuresAndTraits && entity.featuresAndTraits.edges.length > 0}
				<Panel>
					<h2 class="title-section mb-3">Features & Traits</h2>
					<div class="space-y-3">
						{#each entity.featuresAndTraits.edges as edge}
							<div>
								<h3 class="text-sm font-semibold text-text-primary">{edge.node.name}</h3>
								{#if edge.node.description}
									<p class="copy-readable mt-0.5 text-sm text-text-secondary">{edge.node.description}</p>
								{/if}
							</div>
						{/each}
					</div>
				</Panel>
			{/if}

			{#if entity.associations && entity.associations.edges.length > 0}
				<Panel>
					<h2 class="title-section mb-3">Associations</h2>
					<div class="flex flex-wrap gap-2">
						{#each entity.associations.edges as edge}
							<a
								href="/database/associations/{edge.node.id}"
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
				<h2 class="title-section mb-2">Character Details</h2>
				<div class="space-y-3">
					<div>
						<label class="machine-text mb-1 block text-[10px] text-text-muted uppercase">Size</label>
						<input
							bind:value={editSize}
							placeholder="e.g. Medium, Small..."
							class="w-full border border-border-dim bg-bg-inset px-2 py-1 text-xs text-text-primary outline-none focus:border-accent-amber"
						/>
					</div>
				</div>
			</Panel>
		{/snippet}
	</EntityDetail>
{:else}
	<div class="content-pad">
		<div class="panel-border panel-bg panel-pad text-center">
			<p class="machine-text text-text-muted">Character not found</p>
		</div>
	</div>
{/if}

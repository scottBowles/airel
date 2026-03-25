<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import EntityDetail from '$lib/components/EntityDetail.svelte';
	import EntityPicker from '$lib/components/EntityPicker.svelte';
	import Panel from '$lib/components/Panel.svelte';
	import { X } from 'lucide-svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.CharacterDetail).current);
	let entity = $derived(store?.data?.node?.__typename === 'Character' ? store.data.node : null);

	let editRaceId = $state<string | null>(null);
	let editRaceName = $state('');
	let raceCleared = $state(false);

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
					id name description markdownNotes lockedBySelf
					race { id name }
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
				race: editRaceId ? { id: editRaceId } : undefined,
				...relatedChanges,
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
	<title>{entity?.name ?? 'Character'} — Database — Kontularien</title>
</svelte:head>

{#if entity}
	<EntityDetail
		entityId={entity.id}
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
		onstartediting={() => {
			editRaceId = entity?.race?.id ?? null;
			editRaceName = entity?.race?.name ?? '';
			raceCleared = false;
		}}
		relatedCharacters={entity.relatedCharacters}
		relatedPlaces={entity.relatedPlaces}
		relatedAssociations={entity.relatedAssociations}
		relatedItems={entity.relatedItems}
		relatedArtifacts={entity.relatedArtifacts}
		relatedRaces={entity.relatedRaces}
		logs={entity.logs}
	>
		{#snippet extraInfo()}
			{#if entity.race}
				<Panel>
					<h2 class="title-section mb-1">Race</h2>
					<a href="/database/races/{entity.race.id}" class="text-accent-amber hover:text-accent-amber/80">
						{entity.race.name}
					</a>
				</Panel>
			{/if}

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
						<label class="machine-text mb-1 block text-[10px] text-text-muted uppercase">Race</label>
						{#if editRaceId && !raceCleared}
							<div class="flex items-center gap-2">
								<span class="text-xs text-accent-amber">{editRaceName}</span>
								<button onclick={() => { editRaceId = null; editRaceName = ''; raceCleared = true; }} class="cursor-pointer text-xs text-text-muted hover:text-accent-red">
									<X class="h-3 w-3" />
								</button>
							</div>
						{:else}
							<EntityPicker entityType="Race" onselect={(e) => { editRaceId = e.id; editRaceName = e.name; raceCleared = false; }} />
						{/if}
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

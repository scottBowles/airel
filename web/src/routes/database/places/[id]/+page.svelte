<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import EntityDetail from '$lib/components/EntityDetail.svelte';
	import EntityPicker from '$lib/components/EntityPicker.svelte';
	import PlaceBreadcrumbs from '$lib/components/PlaceBreadcrumbs.svelte';
	import Panel from '$lib/components/Panel.svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.PlaceDetail).current);
	let entity = $derived(store?.data?.node?.__typename === 'Place' ? store.data.node : null);

	let editPlaceType = $state('');
	let editParentId = $state<string | null>(null);
	let editParentName = $state('');
	let parentCleared = $state(false);

	const lockMutation = graphql(`
		mutation LockPlace($id: ID!) {
			lock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const unlockMutation = graphql(`
		mutation UnlockPlace($id: ID!) {
			unlock(input: { id: $id }) { id lockedBySelf lockUser { id username } lockTime }
		}
	`);
	const updateMutation = graphql(`
		mutation UpdatePlaceDetail($input: PlaceInputPartial!) {
			updatePlace(input: $input) {
				... on Place {
					id name description markdownNotes placeType lockedBySelf
					parent { id name placeType }
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
		const parentInput = editParentId
			? { id: editParentId }
			: parentCleared
				? null
				: undefined;
		const result = await updateMutation.mutate({
			input: {
				id: entity.id,
				name: n,
				description: d,
				markdownNotes: m,
				placeType: editPlaceType || undefined,
				...(parentInput !== undefined ? { parent: parentInput } : {}),
				...relatedChanges,
			},
		});
		if (result.data?.updatePlace?.__typename === 'Place') {
			toast.success('Place updated');
			return true;
		}
		toast.error('Failed to update place');
		return false;
	}

	const placeTypes = ['DISTRICT', 'LOCATION', 'MOON', 'PLANET', 'REGION', 'STAR', 'TOWN'];
</script>

<svelte:head>
	<title>{entity?.name ?? 'Place'} — Database — KSS Kontularien</title>
</svelte:head>

{#if entity}
	<EntityDetail
		entityId={entity.id}
		name={entity.name}
		description={entity.description}
		thumbnailId={entity.thumbnailId}
		imageIds={entity.imageIds}
		markdownNotes={entity.markdownNotes}
		backHref="/database/places"
		backLabel="Back to Places"
		locked={!!entity.lockUser && !entity.lockedBySelf}
		lockedBySelf={entity.lockedBySelf}
		lockUser={entity.lockUser}
		onlock={handleLock}
		onunlock={handleUnlock}
		onsave={handleSave}
		onstartediting={() => { editPlaceType = entity?.placeType ?? ''; editParentId = null; editParentName = ''; parentCleared = false; }}
		relatedCharacters={entity.relatedCharacters}
		relatedPlaces={entity.relatedPlaces}
		relatedAssociations={entity.relatedAssociations}
		relatedItems={entity.relatedItems}
		relatedArtifacts={entity.relatedArtifacts}
		relatedRaces={entity.relatedRaces}
		logs={entity.logs}
	>
		{#snippet breadcrumbs()}
			<PlaceBreadcrumbs place={entity} />
		{/snippet}
		{#snippet extraInfo()}
			<div class="flex flex-wrap gap-4">
				{#if entity.placeType}
					<Panel class="flex-1">
						<h2 class="title-section mb-1">Type</h2>
						<p class="text-text-primary capitalize">{entity.placeType.toLowerCase()}</p>
					</Panel>
				{/if}
				{#if entity.population}
					<Panel class="flex-1">
						<h2 class="title-section mb-1">Population</h2>
						<p class="text-text-primary">{entity.population.toLocaleString()}</p>
					</Panel>
				{/if}
				{#if entity.parent}
					<Panel class="flex-1">
						<h2 class="title-section mb-1">Located In</h2>
						<a href="/database/places/{entity.parent.id}" class="text-accent-amber hover:text-accent-amber/80">
							{entity.parent.name}
						</a>
					</Panel>
				{/if}
			</div>

			{#if entity.children && entity.children.edges.length > 0}
				<Panel>
					<h2 class="title-section mb-3">Sub-locations</h2>
					<div class="flex flex-wrap gap-2">
						{#each entity.children.edges as edge}
							<a
								href="/database/places/{edge.node.id}"
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
				<h2 class="title-section mb-2">Place Details</h2>
				<div class="space-y-3">
					<div>
						<label class="machine-text mb-1 block text-[10px] text-text-muted uppercase">Place Type</label>
						<select
							bind:value={editPlaceType}
							class="w-full border border-border-dim bg-bg-inset px-2 py-1 text-xs text-text-primary outline-none focus:border-accent-amber"
						>
							<option value="">— None —</option>
							{#each placeTypes as pt}
								<option value={pt}>{pt.charAt(0) + pt.slice(1).toLowerCase()}</option>
							{/each}
						</select>
					</div>
					<div>
						<label class="machine-text mb-1 block text-[10px] text-text-muted uppercase">Parent Place</label>
						{#if editParentId}
							<div class="flex items-center gap-2">
								<span class="text-xs text-accent-amber">{editParentName}</span>
								<button type="button" onclick={() => { editParentId = null; editParentName = ''; parentCleared = true; }} class="cursor-pointer text-xs text-text-muted hover:text-accent-red">✕</button>
							</div>
						{:else if !parentCleared && entity?.parent}
							<div class="flex items-center gap-2">
								<span class="text-xs text-accent-amber">{entity.parent.name}</span>
								<button type="button" onclick={() => { parentCleared = true; }} class="cursor-pointer text-xs text-text-muted hover:text-accent-red">✕</button>
							</div>
						{:else}
							{#if parentCleared && entity?.parent}
								<div class="mb-1">
									<span class="text-xs text-text-muted line-through opacity-50">{entity.parent.name}</span>
									<button type="button" onclick={() => { parentCleared = false; }} class="cursor-pointer text-xs text-accent-amber hover:text-accent-amber ml-1">↩</button>
								</div>
							{/if}
							<EntityPicker
								entityType="Place"
								onselect={(e) => { editParentId = e.id; editParentName = e.name; parentCleared = false; }}
								exclude={[entity?.id ?? '']}
							/>
						{/if}
					</div>
				</div>
			</Panel>
		{/snippet}
	</EntityDetail>
{:else}
	<div class="content-pad">
		<div class="panel-border panel-bg panel-pad text-center">
			<p class="machine-text text-text-muted">Place not found</p>
		</div>
	</div>
{/if}

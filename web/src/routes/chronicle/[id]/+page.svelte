<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { formatGameDate } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import {
		ArrowLeft,
		Calendar,
		ExternalLink,
		Users,
		MapPin,
		Globe,
		Swords,
		Gem,
		Dna,
		Save,
		X,
	} from 'lucide-svelte';
	import { graphql } from '$houdini';
	import Button from '$lib/components/Button.svelte';
	import Panel from '$lib/components/Panel.svelte';
	import LockIndicator from '$lib/components/LockIndicator.svelte';
	import RelatedEntitiesBlock from '$lib/components/RelatedEntitiesBlock.svelte';
	import EntityPicker from '$lib/components/EntityPicker.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import NotFound from '$lib/components/NotFound.svelte';
	import ErrorState from '$lib/components/ErrorState.svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.GameLogDetail).current);
	let fetching = $derived(store?.fetching ?? true);
	let errors = $derived(store?.errors ?? null);
	let log = $derived(store?.data?.node?.__typename === 'GameLog' ? store.data.node : null);

	let editTitle = $state('');
	let editBrief = $state('');
	let editSynopsis = $state('');
	let saving = $state(false);
	let editSetInChanges: { add: { id: string; name: string }[]; remove: string[] } = $state({ add: [], remove: [] });

	function getEffectiveSetIn() {
		const original = log?.placesSetIn?.edges.map(e => e.node) ?? [];
		const kept = original.filter(p => !editSetInChanges.remove.includes(p.id));
		const removed = original.filter(p => editSetInChanges.remove.includes(p.id));
		return { kept, added: editSetInChanges.add, removed };
	}

	const lockMutation = graphql(`
		mutation LockGameLog($id: ID!) {
			lock(input: { id: $id }) {
				id
				lockedBySelf
				lockUser { id username }
				lockTime
			}
		}
	`);

	const unlockMutation = graphql(`
		mutation UnlockGameLog($id: ID!) {
			unlock(input: { id: $id }) {
				id
				lockedBySelf
				lockUser { id username }
				lockTime
			}
		}
	`);

	const updateMutation = graphql(`
		mutation UpdateGameLogDetail($input: GameLogInputPartial!) {
			updateGamelog(input: $input) {
				... on GameLog {
					id
					title
					brief
					synopsis
					lockedBySelf
					placesSetIn(first: 50) { edges { node { id name } } }
				}
				... on OperationInfo {
					messages { field kind message }
				}
			}
		}
	`);

	async function handleLock() {
		if (!log) return;
		await lockMutation.mutate({ id: log.id });
	}

	function handleUnlock() {
		if (!log) return;
		unlockMutation.mutate({ id: log.id });
	}

	$effect(() => {
		if (log?.lockedBySelf) {
			editTitle = log.title ?? '';
			editBrief = log.brief ?? '';
			editSynopsis = log.synopsis ?? '';
			editSetInChanges = { add: [], remove: [] };
		}
	});

	let editing = $derived(!!log?.lockedBySelf);

	function discardEdits() {
		editSetInChanges = { add: [], remove: [] };
		handleUnlock();
	}

	async function saveEdits() {
		if (!log) return;
		if (!editTitle.trim()) {
			toast.error('Title is required');
			return;
		}
		saving = true;
		const placesSetIn = editSetInChanges.add.length || editSetInChanges.remove.length
			? {
				...(editSetInChanges.add.length ? { add: editSetInChanges.add.map(e => ({ id: e.id })) } : {}),
				...(editSetInChanges.remove.length ? { remove: editSetInChanges.remove.map(id => ({ id })) } : {}),
			}
			: undefined;
		const result = await updateMutation.mutate({
			input: {
				id: log.id,
				title: editTitle,
				brief: editBrief,
				synopsis: editSynopsis,
				placesSetIn,
			},
		});
		saving = false;
		if (result.data?.updateGamelog?.__typename === 'GameLog') {
			editSetInChanges = { add: [], remove: [] };
			handleUnlock();
			toast.success('Log updated');
		} else {
			toast.error('Failed to update log');
		}
	}

	type RelatedEntity = { id: string; name: string; thumbnailId?: string | null; imageIds?: string[] | null };
	type RelatedEdge = { node: RelatedEntity };

	const relatedSections = $derived(
		log
			? [
					{ label: 'Characters', icon: Users, data: log.characters, route: '/database/characters' },
					{ label: 'Places', icon: MapPin, data: log.places, route: '/database/places' },
					{ label: 'Associations', icon: Globe, data: log.associations, route: '/database/associations' },
					{ label: 'Items', icon: Swords, data: log.items, route: '/database/items' },
					{ label: 'Artifacts', icon: Gem, data: log.artifacts, route: '/database/artifacts' },
					{ label: 'Races', icon: Dna, data: log.races, route: '/database/races' },
				]
			: [],
	);
</script>

<svelte:head>
	<title>{log?.title ?? 'Log'} — Chronicle — Kontularien</title>
</svelte:head>

<div class="content-pad db-page">
	<!-- Back link -->
	<a
		href="/chronicle"
		class="inline-flex items-center gap-2 text-xs text-text-muted uppercase tracking-wider transition-colors hover:text-accent-amber"
	>
		<ArrowLeft class="h-3.5 w-3.5" />
		<span>Back to Chronicle</span>
	</a>

	{#if fetching && !log}
		<LoadingState message="RETRIEVING LOG ENTRY" />
	{:else if errors}
		<ErrorState {errors} />
	{:else if log}
		<!-- Header panel -->
		<div class="border border-border-dim bg-hull">
			<div class="border-b border-border-dim px-3 py-1.5 flex items-center justify-between">
				<span class="machine-text text-[9px] text-text-muted">LOG ENTRY</span>
				<div class="flex items-center gap-3">
					<span class="machine-text text-[10px] text-accent-amber flex items-center gap-1.5">
						<Calendar class="h-3 w-3" />
						{formatGameDate(log.gameDate)}
					</span>
					{#if log.url}
						<a
							href={log.url}
							target="_blank"
							rel="noopener noreferrer"
							class="machine-text text-[10px] text-text-muted transition-colors hover:text-accent-amber flex items-center gap-1"
						>
							<ExternalLink class="h-3 w-3" />
							SOURCE
						</a>
					{/if}
				</div>
			</div>
			<div class="flex flex-col gap-3 px-3 py-3 sm:flex-row sm:items-start sm:justify-between">
				<div class="flex-1">
					{#if editing}
						<input
							bind:value={editTitle}
							class="title-display w-full bg-transparent text-lg text-accent-amber outline-none border-b border-border-accent pb-1 focus:border-accent-amber"
							placeholder="LOG TITLE"
						/>
					{:else}
						<h1 class="title-display text-lg text-accent-amber text-glow-amber">
							{log.title ?? 'UNTITLED LOG'}
						</h1>
					{/if}
				</div>
				<div class="flex items-center gap-2">
					<LockIndicator
						locked={!!log.lockUser && !log.lockedBySelf}
						lockedBySelf={log.lockedBySelf}
						lockUser={log.lockUser}
						onlock={handleLock}
						onunlock={handleUnlock}
					/>
					{#if editing}
						<Button size="sm" onclick={saveEdits} disabled={saving}>
							<Save class="h-3 w-3" />
							{saving ? 'Saving...' : 'Commit'}
						</Button>
						<Button variant="ghost" size="sm" onclick={discardEdits} disabled={saving}>
							<X class="h-3 w-3" />
							Discard
						</Button>
					{/if}
				</div>
			</div>
		</div>

		<div class="grid gap-3 lg:grid-cols-[1fr_260px]">
			<!-- Main content -->
			<div class="stack-space">
				<!-- Set In -->
				{#if editing}
					<Panel>
						<h2 class="title-section mb-3">Set In</h2>
						{@const effective = getEffectiveSetIn()}
						{#if effective.kept.length || effective.added.length || effective.removed.length}
							<div class="flex flex-wrap gap-2 mb-3">
								{#each effective.kept as place}
									<span class="inline-flex items-center gap-1 border border-border-dim bg-void px-2 py-0.5 text-xs text-accent-amber">
										{place.name}
										<button type="button" onclick={() => { editSetInChanges.remove = [...editSetInChanges.remove, place.id]; }} class="cursor-pointer text-text-muted hover:text-accent-red ml-1">✕</button>
									</span>
								{/each}
								{#each effective.added as place}
									<span class="inline-flex items-center gap-1 border border-accent-green/30 bg-accent-green/5 px-2 py-0.5 text-xs text-accent-green">
										+ {place.name}
										<button type="button" onclick={() => { editSetInChanges.add = editSetInChanges.add.filter(e => e.id !== place.id); }} class="cursor-pointer text-text-muted hover:text-accent-red ml-1">✕</button>
									</span>
								{/each}
								{#each effective.removed as place}
									<span class="inline-flex items-center gap-1 border border-border-dim bg-void px-2 py-0.5 text-xs text-text-muted line-through opacity-50">
										{place.name}
										<button type="button" onclick={() => { editSetInChanges.remove = editSetInChanges.remove.filter(id => id !== place.id); }} class="cursor-pointer text-accent-amber hover:text-accent-amber ml-1 no-underline">↩</button>
									</span>
								{/each}
							</div>
						{/if}
						<EntityPicker
							entityType="Place"
							onselect={(e) => {
								if (!editSetInChanges.add.some(a => a.id === e.id)) {
									editSetInChanges.add = [...editSetInChanges.add, { id: e.id, name: e.name }];
								}
							}}
							exclude={[...(log?.placesSetIn?.edges.map(e => e.node.id) ?? []), ...editSetInChanges.add.map(e => e.id)].filter(id => !editSetInChanges.remove.includes(id))}
						/>
					</Panel>
				{:else if log.placesSetIn && log.placesSetIn.edges.length > 0}
					<Panel>
						<h2 class="title-section mb-3 flex items-center gap-2">
							<MapPin class="h-3 w-3 text-text-muted" />
							Set In
						</h2>
						<div class="flex flex-wrap gap-2">
							{#each log.placesSetIn.edges as edge}
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
				{#if log.brief || editing}
					<Panel>
						<h2 class="title-section mb-2">Brief</h2>
						{#if editing}
							<textarea
								bind:value={editBrief}
								class="w-full resize-y bg-void border border-border-dim p-2 text-xs text-text-primary focus:border-accent-amber focus:outline-none"
								rows="3"
								placeholder="Brief summary..."
							></textarea>
						{:else}
							<p class="text-xs text-text-secondary leading-relaxed">{log.brief}</p>
						{/if}
					</Panel>
				{/if}

				{#if log.synopsis || editing}
					<Panel>
						<h2 class="title-section mb-2">Synopsis</h2>
						{#if editing}
							<textarea
								bind:value={editSynopsis}
								class="w-full resize-y bg-void border border-border-dim p-2 text-xs text-text-primary focus:border-accent-amber focus:outline-none"
								rows="8"
								placeholder="Full synopsis..."
							></textarea>
						{:else}
							<p class="whitespace-pre-wrap text-xs text-text-secondary leading-relaxed">{log.synopsis}</p>
						{/if}
					</Panel>
				{/if}
			</div>

			<!-- Sidebar — Related entities -->
			<aside class="stack-space">
				<RelatedEntitiesBlock sections={relatedSections} />
			</aside>
		</div>
	{:else}
		<NotFound entityName="Log" />
	{/if}
</div>

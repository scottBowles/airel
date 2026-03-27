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
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
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

	// Related entity editing state (generic, like EntityDetail)
	let relatedAdds = $state<Record<string, Array<{ id: string; name: string }>>>({});
	let relatedRemoves = $state<Record<string, string[]>>({});

	type RelatedConnection = {
		edges: Array<{ node: { id: string; name: string } }>;
	} | null;

	type SectionDef = {
		key: string;
		label: string;
		icon: typeof Users;
		data: RelatedConnection;
		route: string;
		entityType: 'Character' | 'Place' | 'Association' | 'Item' | 'Artifact' | 'Race';
	};

	function addRelated(key: string, entity: { id: string; name: string }) {
		relatedAdds[key] = [...(relatedAdds[key] ?? []), entity];
	}

	function removeRelated(key: string, id: string) {
		const current = relatedRemoves[key] ?? [];
		if (!current.includes(id)) {
			relatedRemoves[key] = [...current, id];
		}
	}

	function undoAdd(key: string, id: string) {
		relatedAdds[key] = (relatedAdds[key] ?? []).filter((e) => e.id !== id);
	}

	function undoRemove(key: string, id: string) {
		relatedRemoves[key] = (relatedRemoves[key] ?? []).filter((x) => x !== id);
	}

	function getEffectiveItems(section: SectionDef) {
		const existing = section.data?.edges.map((e) => e.node) ?? [];
		const removes = relatedRemoves[section.key] ?? [];
		const adds = relatedAdds[section.key] ?? [];
		return {
			kept: existing.filter((e) => !removes.includes(e.id)),
			removed: existing.filter((e) => removes.includes(e.id)),
			added: adds,
		};
	}

	function getExcludeIds(section: SectionDef): string[] {
		const existing = section.data?.edges.map((e) => e.node.id) ?? [];
		const addedIds = (relatedAdds[section.key] ?? []).map((e) => e.id);
		const removedIds = relatedRemoves[section.key] ?? [];
		const inList = [...existing, ...addedIds].filter((id) => !removedIds.includes(id));
		return inList;
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
					characters(first: 50) { edges { node { id name thumbnailId imageIds } } }
					places(first: 50) { edges { node { id name thumbnailId imageIds } } }
					associations(first: 50) { edges { node { id name } } }
					items(first: 50) { edges { node { id name } } }
					artifacts(first: 50) { edges { node { id name } } }
					races(first: 50) { edges { node { id name } } }
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
			relatedAdds = {};
			relatedRemoves = {};
		}
	});

	let editing = $derived(!!log?.lockedBySelf);

	let confirmDiscardOpen = $state(false);

	let hasChanges = $derived(
		editTitle !== (log?.title ?? '') ||
		editBrief !== (log?.brief ?? '') ||
		editSynopsis !== (log?.synopsis ?? '') ||
		Object.values(relatedAdds).some((a) => a.length > 0) ||
		Object.values(relatedRemoves).some((r) => r.length > 0),
	);

	function discardEdits() {
		if (hasChanges) {
			confirmDiscardOpen = true;
			return;
		}
		forceDiscard();
	}

	function forceDiscard() {
		confirmDiscardOpen = false;
		relatedAdds = {};
		relatedRemoves = {};
		handleUnlock();
	}

	type NodeInputList = { add?: Array<{ id: string }>; remove?: Array<{ id: string }> };

	async function saveEdits() {
		if (!log) return;
		if (!editTitle.trim()) {
			toast.error('Title is required');
			return;
		}
		saving = true;
		const relatedFields: Record<string, NodeInputList> = {};
		for (const section of allSections) {
			const adds = relatedAdds[section.key] ?? [];
			const removes = [...(relatedRemoves[section.key] ?? [])];
			if (adds.length || removes.length) {
				relatedFields[section.key] = {
					...(adds.length ? { add: adds.map((e) => ({ id: e.id })) } : {}),
					...(removes.length ? { remove: removes.map((id) => ({ id })) } : {}),
				};
			}
		}
		// placesSetIn is handled separately since it has its own key
		const placesSetInAdds = relatedAdds['placesSetIn'] ?? [];
		const placesSetInRemoves = relatedRemoves['placesSetIn'] ?? [];
		const placesSetIn = (placesSetInAdds.length || placesSetInRemoves.length)
			? {
				...(placesSetInAdds.length ? { add: placesSetInAdds.map((e) => ({ id: e.id })) } : {}),
				...(placesSetInRemoves.length ? { remove: placesSetInRemoves.map((id) => ({ id })) } : {}),
			}
			: undefined;
		const result = await updateMutation.mutate({
			input: {
				id: log.id,
				title: editTitle,
				brief: editBrief,
				synopsis: editSynopsis,
				placesSetIn,
				...relatedFields,
			},
		});
		saving = false;
		if (result.data?.updateGamelog?.__typename === 'GameLog') {
			relatedAdds = {};
			relatedRemoves = {};
			handleUnlock();
			toast.success('Log updated');
		} else {
			toast.error('Failed to update log');
		}
	}

	const allSections: SectionDef[] = $derived(
		log
			? [
					{ key: 'characters', label: 'Characters', icon: Users, data: log.characters, route: '/database/characters', entityType: 'Character' as const },
					{ key: 'places', label: 'Places', icon: MapPin, data: log.places, route: '/database/places', entityType: 'Place' as const },
					{ key: 'associations', label: 'Associations', icon: Globe, data: log.associations, route: '/database/associations', entityType: 'Association' as const },
					{ key: 'items', label: 'Items', icon: Swords, data: log.items, route: '/database/items', entityType: 'Item' as const },
					{ key: 'artifacts', label: 'Artifacts', icon: Gem, data: log.artifacts, route: '/database/artifacts', entityType: 'Artifact' as const },
					{ key: 'races', label: 'Races', icon: Dna, data: log.races, route: '/database/races', entityType: 'Race' as const },
				]
			: [],
	);

	const relatedSections = $derived(
		allSections.filter((s) => s.data && s.data.edges.length > 0),
	);

	const setInSection: SectionDef = $derived(
		{ key: 'placesSetIn', label: 'Set In', icon: MapPin, data: log?.placesSetIn ?? null, route: '/database/places', entityType: 'Place' as const },
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

		<ConfirmDialog
			open={confirmDiscardOpen}
			title="Discard Changes"
			message="You have unsaved changes. Are you sure you want to discard them?"
			confirmLabel="Discard"
			onconfirm={forceDiscard}
			oncancel={() => { confirmDiscardOpen = false; }}
		/>

		<div class="grid gap-3 lg:grid-cols-[1fr_260px]">
			<!-- Main content -->
			<div class="stack-space">
				<!-- Set In -->
				{#if editing}
					<Panel>
						<h2 class="title-section mb-3">Set In</h2>
						{@const effective = getEffectiveItems(setInSection)}
						{#if effective.kept.length || effective.added.length || effective.removed.length}
							<div class="flex flex-wrap gap-2 mb-3">
								{#each effective.kept as place}
									<span class="inline-flex items-center gap-1 border border-border-dim bg-void px-2 py-0.5 text-xs text-accent-amber">
										{place.name}
										<button type="button" onclick={() => removeRelated('placesSetIn', place.id)} class="cursor-pointer text-text-muted hover:text-accent-red ml-1">✕</button>
									</span>
								{/each}
								{#each effective.added as place}
									<span class="inline-flex items-center gap-1 border border-accent-green/30 bg-accent-green/5 px-2 py-0.5 text-xs text-accent-green">
										+ {place.name}
										<button type="button" onclick={() => undoAdd('placesSetIn', place.id)} class="cursor-pointer text-text-muted hover:text-accent-red ml-1">✕</button>
									</span>
								{/each}
								{#each effective.removed as place}
									<span class="inline-flex items-center gap-1 border border-border-dim bg-void px-2 py-0.5 text-xs text-text-muted line-through opacity-50">
										{place.name}
										<button type="button" onclick={() => undoRemove('placesSetIn', place.id)} class="cursor-pointer text-accent-amber hover:text-accent-amber ml-1 no-underline">↩</button>
									</span>
								{/each}
							</div>
						{/if}
						<EntityPicker
							entityType="Place"
							onselect={(e) => addRelated('placesSetIn', e)}
							exclude={getExcludeIds(setInSection)}
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
				{#if editing}
					{#each allSections as section}
						{@const effective = getEffectiveItems(section)}
						{@const hasContent = effective.kept.length > 0 || effective.added.length > 0}
						<Panel>
							<h3 class="title-section mb-2 flex items-center gap-2">
								<section.icon class="h-3 w-3 text-text-muted" />
								{section.label}
							</h3>
							{#if hasContent}
								<div class="space-y-px">
									{#each effective.kept as item}
										<div class="group flex items-center justify-between">
											<a
												href="{section.route}/{item.id}"
												class="flex-1 truncate px-2 py-1 text-[11px] text-text-secondary uppercase tracking-wider transition-colors hover:text-accent-amber"
											>
												{item.name}
											</a>
											<button
												onclick={() => removeRelated(section.key, item.id)}
												class="shrink-0 cursor-pointer p-0.5 text-text-muted opacity-0 transition-opacity hover:text-accent-red group-hover:opacity-100 focus-visible:opacity-100"
												aria-label="Remove {item.name}"
											>
												<X class="h-3 w-3" />
											</button>
										</div>
									{/each}
									{#each effective.added as item}
										<div class="group flex items-center justify-between">
											<span class="flex-1 truncate px-2 py-1 text-[11px] text-accent-green uppercase tracking-wider">
												+ {item.name}
											</span>
											<button
												onclick={() => undoAdd(section.key, item.id)}
												class="shrink-0 cursor-pointer p-0.5 text-text-muted opacity-0 transition-opacity hover:text-accent-red group-hover:opacity-100 focus-visible:opacity-100"
												aria-label="Undo add {item.name}"
											>
												<X class="h-3 w-3" />
											</button>
										</div>
									{/each}
								</div>
							{/if}
							{#if effective.removed.length > 0}
								<div class="mt-1 space-y-px border-t border-border-dim pt-1">
									{#each effective.removed as item}
										<div class="group flex items-center justify-between opacity-50">
											<span class="flex-1 truncate px-2 py-1 text-[11px] text-text-muted line-through uppercase tracking-wider">
												{item.name}
											</span>
											<button
												onclick={() => undoRemove(section.key, item.id)}
												class="shrink-0 cursor-pointer p-0.5 text-text-muted opacity-0 transition-opacity hover:text-accent-green group-hover:opacity-100"
												title="Undo remove"
											>
												↩
											</button>
										</div>
									{/each}
								</div>
							{/if}
							<div class="mt-1.5">
								<EntityPicker
									entityType={section.entityType}
									onselect={(e) => addRelated(section.key, e)}
									exclude={getExcludeIds(section)}
									placeholder="Add {section.label.toLowerCase()}..."
								/>
							</div>
						</Panel>
					{/each}
				{:else}
					<RelatedEntitiesBlock sections={relatedSections} />
				{/if}
			</aside>
		</div>
	{:else}
		<NotFound entityName="Log" />
	{/if}
</div>

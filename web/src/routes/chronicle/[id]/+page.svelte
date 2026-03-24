<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { goto } from '$app/navigation';
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
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.GameLogDetail).current);
	let log = $derived(store?.data?.node?.__typename === 'GameLog' ? store.data.node : null);

	let editTitle = $state('');
	let editBrief = $state('');
	let editSynopsis = $state('');

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

	async function handleUnlock() {
		if (!log) return;
		await unlockMutation.mutate({ id: log.id });
	}

	$effect(() => {
		if (log?.lockedBySelf) {
			editTitle = log.title ?? '';
			editBrief = log.brief ?? '';
			editSynopsis = log.synopsis ?? '';
		}
	});

	let editing = $derived(!!log?.lockedBySelf);

	function discardEdits() {
		handleUnlock();
	}

	async function saveEdits() {
		if (!log) return;
		const result = await updateMutation.mutate({
			input: {
				id: log.id,
				title: editTitle,
				brief: editBrief,
				synopsis: editSynopsis,
			},
		});
		if (result.data?.updateGamelog?.__typename === 'GameLog') {
			await handleUnlock();
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
	<title>{log?.title ?? 'Log'} — Chronicle — KSS Kontularien</title>
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

	{#if log}
		<!-- Header panel -->
		<div class="border border-border-dim bg-hull">
			<div class="border-b border-border-dim px-3 py-1.5 flex items-center justify-between">
				<span class="machine-text text-[9px] text-text-muted/60">LOG ENTRY</span>
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
						<Button variant="primary" size="sm" onclick={saveEdits}>
							<Save class="h-3 w-3" />
							Commit
						</Button>
						<Button variant="ghost" size="sm" onclick={discardEdits}>
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
		<div class="border border-border-dim bg-panel px-4 py-8 text-center">
			<p class="machine-text text-text-muted">LOG NOT FOUND</p>
		</div>
	{/if}
</div>

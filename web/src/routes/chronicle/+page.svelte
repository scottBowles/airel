<script lang="ts">
	import { goto } from '$app/navigation';
	import { fromStore } from 'svelte/store';
	import { toast } from 'svelte-sonner';
	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';
	import { graphql } from '$houdini';
	import Button from '$lib/components/Button.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import { toChronicle } from '$lib/chronicle/model';
	import ViewSwitcher from '$lib/components/chronicle/ViewSwitcher.svelte';
	import ClassicView from '$lib/components/chronicle/ClassicView.svelte';
	import ViewDeck from '$lib/components/chronicle/ViewDeck.svelte';
	import ControlView from '$lib/components/chronicle/ControlView.svelte';
	import PostcardsView from '$lib/components/chronicle/PostcardsView.svelte';
	import VoyageView from '$lib/components/chronicle/VoyageView.svelte';
	import StarChartView from '$lib/components/chronicle/StarChartView.svelte';
	import TimelineView from '$lib/components/chronicle/TimelineView.svelte';
	import SagaView from '$lib/components/chronicle/SagaView.svelte';
	import ReplayView from '$lib/components/chronicle/ReplayView.svelte';
	import ThreadsView from '$lib/components/chronicle/ThreadsView.svelte';
	import AtlasView from '$lib/components/chronicle/AtlasView.svelte';
	import CalendarView from '$lib/components/chronicle/CalendarView.svelte';
	import { getUserContext } from '$lib/auth';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let view = $derived(data.view);
	// The classic list reads GameLogList; every other view reads ChronicleJourney.
	let listStore = $derived('GameLogList' in data ? fromStore(data.GameLogList).current : null);
	let journeyStore = $derived(
		'ChronicleJourney' in data ? fromStore(data.ChronicleJourney).current : null
	);
	let store = $derived(listStore ?? journeyStore);
	let fetching = $derived(store?.fetching ?? true);
	let logs = $derived(listStore?.data?.gameLogs?.edges ?? []);
	let chronicle = $derived(toChronicle(journeyStore?.data?.gameLogs?.edges));
	let sessions = $derived(chronicle.sessions);
	let recordCount = $derived(
		view === 'classic' ? logs.length : sessions.length + chronicle.prologue.length
	);

	const getUser = getUserContext();
	let isStaff = $derived(!!getUser()?.isStaff);

	let showNewForm = $state(false);
	let url = $state('');
	let loading = $state(false);
	let urlInput: HTMLInputElement | undefined = $state();

	$effect(() => {
		if (showNewForm) urlInput?.focus();
	});

	const getOrCreateGameLog = graphql(`
		mutation CreateNewGameLogInline($input: GetOrCreateGameLogInput!) {
			getOrCreateGameLog(input: $input) {
				__typename
				... on GameLog {
					id
					title
					url
				}
				... on OperationInfo {
					messages { field kind message }
				}
			}
		}
	`);

	async function handleSubmit() {
		if (!url.trim()) {
			toast.error('Please enter a Google Docs URL');
			return;
		}
		loading = true;
		try {
			const result = await getOrCreateGameLog.mutate({
				input: { url: url.trim(), lock: false },
			});
			const payload = result.data?.getOrCreateGameLog;
			if (payload?.__typename === 'GameLog') {
				toast.success('Log created');
				goto(`/chronicle/${payload.id}`);
			} else if (payload?.__typename === 'OperationInfo') {
				toast.error(payload.messages?.[0]?.message ?? 'Failed to create log');
			}
		} catch (err) {
			toast.error('An error occurred');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Chronicle — Kontularien</title>
</svelte:head>

<div class="content-pad db-page">
	<!-- Header bar -->
	<div class="border border-border-dim bg-hull">
		<div class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<div class="flex items-center gap-2">
				<span class="status-dot text-accent-green"></span>
				<span class="machine-text text-[9px] text-text-muted">LOG-01 // CHRONICLE</span>
			</div>
			<span class="machine-text text-[9px] text-text-muted">{fetching && !recordCount ? '...' : recordCount} RECORDS</span>
		</div>
		<div class="flex items-center justify-between px-3 py-3">
			<div>
				<h1 class="title-display text-lg text-accent-amber text-glow-amber">CHRONICLE</h1>
				<p class="machine-text text-[10px] text-text-muted mt-0.5">Mission logs and session records</p>
			</div>
		{#if isStaff}
			<Button variant="primary" onclick={() => { showNewForm = !showNewForm; }}>
				{#if showNewForm}
					<X class="h-3 w-3" />
					Cancel
				{:else}
					<Plus class="h-3 w-3" />
					New Log
				{/if}
			</Button>
		{/if}
		</div>
	</div>

	<!-- Inline new log form -->
	{#if isStaff && showNewForm}
		<form onsubmit={handleSubmit} class="flex gap-2 border border-accent-amber/30 bg-hull px-3 py-3">
			<input
				type="url"
				bind:this={urlInput}
				bind:value={url}
				placeholder="https://docs.google.com/document/d/..."
				class="flex-1 bg-void border border-border-dim px-2.5 py-1.5 text-xs text-text-primary placeholder:text-text-faint focus:border-accent-amber focus:outline-none"
			/>
			<Button type="submit" variant="primary" disabled={loading}>
				<Plus class="h-3 w-3" />
				{loading ? 'IMPORTING...' : 'IMPORT'}
			</Button>
		</form>
	{/if}

	<ViewSwitcher current={view} />

	<!-- The selected view -->
	{#if fetching && !recordCount}
		<LoadingState message="RETRIEVING LOG ENTRIES" />
	{:else}
	{#if view === 'classic'}
		<ClassicView {logs} />
	{:else if view === 'deck'}
		<ViewDeck {sessions} />
	{:else if !sessions.length}
		<div class="border border-border-dim bg-panel px-4 py-8 text-center">
			<p class="machine-text text-text-muted">NO LOGS RECORDED</p>
			<p class="machine-text text-[10px] text-text-faint mt-1">IMPORT A SESSION TO BEGIN</p>
		</div>
	{:else if view === 'control'}
		<ControlView {sessions} />
	{:else if view === 'postcards'}
		<PostcardsView {sessions} />
	{:else if view === 'voyage'}
		<VoyageView {sessions} />
	{:else if view === 'starchart'}
		<StarChartView {sessions} />
	{:else if view === 'timeline'}
		<TimelineView {sessions} />
	{:else if view === 'saga'}
		<SagaView {sessions} prologue={chronicle.prologue} />
	{:else if view === 'replay'}
		<ReplayView {sessions} />
	{:else if view === 'threads'}
		<ThreadsView {sessions} />
	{:else if view === 'atlas'}
		<AtlasView {sessions} />
	{:else if view === 'calendar'}
		<CalendarView {sessions} />
	{/if}
	{/if}
</div>

<script lang="ts">
	import { goto } from '$app/navigation';
	import { fromStore } from 'svelte/store';
	import { formatGameDate } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import { ExternalLink, Plus, X } from 'lucide-svelte';
	import { graphql } from '$houdini';
	import Button from '$lib/components/Button.svelte';
	import { getUserContext } from '$lib/auth';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.GameLogList).current);
	let logs = $derived(store?.data?.gameLogs?.edges ?? []);

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
			<span class="machine-text text-[9px] text-text-muted">{logs.length} RECORDS</span>
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

	<!-- Log list -->
	<div class="space-y-px">
		{#each logs as edge, i}
			{@const log = edge.node}
			<div class="flex border border-border-dim transition-all hover:border-accent-amber/20">
				<!-- Main clickable area -->
				<a
					href="/chronicle/{log.id}"
					class="group flex flex-1 flex-col gap-2 bg-panel px-3 py-3 transition-all hover:bg-panel-hover sm:flex-row sm:items-start sm:gap-4"
				>
					<!-- Date -->
					<div class="shrink-0 sm:w-24">
						<span class="machine-text text-[10px] text-accent-amber">{formatGameDate(log.gameDate)}</span>
					</div>

					<!-- Content -->
					<div class="min-w-0 flex-1">
						<h2 class="text-xs font-bold text-text-primary uppercase tracking-wider group-hover:text-accent-amber transition-colors">
							{log.title ?? 'UNTITLED LOG'}
						</h2>
						{#if log.brief}
							<p class="mt-1 line-clamp-2 text-xs text-text-secondary leading-relaxed">
								{log.brief}
							</p>
						{/if}
					</div>

					<!-- Record number -->
					<span class="hidden machine-text text-[9px] text-text-faint sm:block">
						#{String(i + 1).padStart(3, '0')}
					</span>
				</a>

				<!-- External link gutter -->
				{#if log.url}
					<a
						href={log.url}
						target="_blank"
						rel="noopener noreferrer"
						class="flex items-center border-l border-border-dim bg-panel px-2.5 text-text-muted transition-colors hover:bg-accent-amber/5 hover:text-accent-amber"
						title="Open Google Doc"
					>
						<ExternalLink class="h-3.5 w-3.5" />
					</a>
				{/if}
			</div>
		{:else}
			<div class="border border-border-dim bg-panel px-4 py-8 text-center">
				<p class="machine-text text-text-muted">NO LOGS RECORDED</p>
				<p class="machine-text text-[10px] text-text-faint mt-1">IMPORT A SESSION TO BEGIN</p>
			</div>
		{/each}
	</div>
</div>

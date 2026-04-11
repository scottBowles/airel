<script lang="ts">
	import { fromStore } from 'svelte/store';
	import Dna from '@lucide/svelte/icons/dna';
	import Plus from '@lucide/svelte/icons/plus';
	import { getUserContext } from '$lib/auth';
	import Button from '$lib/components/Button.svelte';
	import EntityGrid from '$lib/components/EntityGrid.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import type { PageData } from './$houdini';

	const getUser = getUserContext();
	let isStaff = $derived(!!getUser()?.isStaff);

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.RaceList).current);
	let fetching = $derived(store?.fetching ?? true);
	let entities = $derived(
		(store?.data?.races?.edges ?? []).map((e) => e.node),
	);
</script>

<svelte:head>
	<title>Races — Database — Kontularien</title>
</svelte:head>

<div class="content-pad db-page">
	<div class="border border-border-dim bg-hull">
		<div class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<div class="flex items-center gap-2">
				<Dna class="h-3 w-3 text-accent-amber/40" />
				<span class="machine-text text-[9px] text-text-muted">RCE // RACES</span>
			</div>
			<span class="machine-text text-[9px] text-text-muted">{fetching && !entities.length ? '...' : entities.length} RECORDS</span>
		</div>
		<div class="flex items-center justify-between px-3 py-3">
			<h1 class="title-display text-lg text-accent-amber text-glow-amber">RACES</h1>
			{#if isStaff}
				<Button variant="primary" href="/database/races/new">
					<Plus class="h-3 w-3" />
					New
				</Button>
			{/if}
		</div>
	</div>

	{#if fetching && !entities.length}
		<LoadingState message="SCANNING RACE RECORDS" />
	{:else}
		<EntityGrid {entities} basePath="/database/races" emptyMessage="No races in database" />
	{/if}
</div>

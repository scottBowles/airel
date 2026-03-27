<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { Swords, Plus } from 'lucide-svelte';
	import { getUserContext } from '$lib/auth';
	import Button from '$lib/components/Button.svelte';
	import EntityGrid from '$lib/components/EntityGrid.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import type { PageData } from './$houdini';

	const getUser = getUserContext();
	let isStaff = $derived(!!getUser()?.isStaff);

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.ItemList).current);
	let fetching = $derived(store?.fetching ?? true);
	let entities = $derived(
		(store?.data?.items?.edges ?? []).map((e) => e.node),
	);
</script>

<svelte:head>
	<title>Items — Database — Kontularien</title>
</svelte:head>

<div class="content-pad db-page">
	<div class="border border-border-dim bg-hull">
		<div class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<div class="flex items-center gap-2">
				<Swords class="h-3 w-3 text-accent-amber/40" />
				<span class="machine-text text-[9px] text-text-muted">ITM // ITEMS</span>
			</div>
			<span class="machine-text text-[9px] text-text-muted">{fetching && !entities.length ? '...' : entities.length} RECORDS</span>
		</div>
		<div class="flex items-center justify-between px-3 py-3">
			<h1 class="title-display text-lg text-accent-amber text-glow-amber">ITEMS</h1>
			{#if isStaff}
				<Button variant="primary" href="/database/items/new">
					<Plus class="h-3 w-3" />
					New
				</Button>
			{/if}
		</div>
	</div>

	{#if fetching && !entities.length}
		<LoadingState message="SCANNING ITEM RECORDS" />
	{:else}
		<EntityGrid {entities} basePath="/database/items" emptyMessage="No items in database" />
	{/if}
</div>

<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { Gem, Plus } from 'lucide-svelte';
	import { getUserContext } from '$lib/auth';
	import Button from '$lib/components/Button.svelte';
	import EntityGrid from '$lib/components/EntityGrid.svelte';
	import type { PageData } from './$houdini';

	const getUser = getUserContext();
	let isStaff = $derived(!!getUser()?.isStaff);

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.ArtifactList).current);
	let entities = $derived(
		(store?.data?.artifacts?.edges ?? []).map((e) => e.node),
	);
</script>

<svelte:head>
	<title>Artifacts — Database — KSS Kontularien</title>
</svelte:head>

<div class="content-pad db-page">
	<div class="border border-border-dim bg-hull">
		<div class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<div class="flex items-center gap-2">
				<Gem class="h-3 w-3 text-accent-amber/40" />
				<span class="machine-text text-[9px] text-text-muted">ART // ARTIFACTS</span>
			</div>
			<span class="machine-text text-[9px] text-text-muted">{entities.length} RECORDS</span>
		</div>
		<div class="flex items-center justify-between px-3 py-3">
			<h1 class="title-display text-lg text-accent-amber text-glow-amber">ARTIFACTS</h1>
			{#if isStaff}
				<Button variant="primary" href="/database/artifacts/new">
					<Plus class="h-3 w-3" />
					New
				</Button>
			{/if}
		</div>
	</div>

	<EntityGrid {entities} basePath="/database/artifacts" emptyMessage="No artifacts in database" />
</div>

<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { formatGameDate } from '$lib/utils';
	import { Calendar, Users, MapPin, Plus } from 'lucide-svelte';
	import Button from '$lib/components/Button.svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.GameLogList).current);
	let logs = $derived(store?.data?.gameLogs?.edges ?? []);
</script>

<svelte:head>
	<title>Chronicle — KSS Kontularien</title>
</svelte:head>

<div class="content-pad db-page">
	<!-- Header bar -->
	<div class="border border-border-dim bg-hull">
		<div class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<div class="flex items-center gap-2">
				<span class="status-dot text-accent-green"></span>
				<span class="machine-text text-[9px] text-text-muted/60">LOG-01 // CHRONICLE</span>
			</div>
			<span class="machine-text text-[9px] text-text-muted/40">{logs.length} RECORDS</span>
		</div>
		<div class="flex items-center justify-between px-3 py-3">
			<div>
				<h1 class="title-display text-lg text-accent-amber text-glow-amber">CHRONICLE</h1>
				<p class="machine-text text-[10px] text-text-muted mt-0.5">Mission logs and session records</p>
			</div>
			<Button variant="primary" href="/chronicle/new">
				<Plus class="h-3 w-3" />
				New Log
			</Button>
		</div>
	</div>

	<!-- Log list -->
	<div class="space-y-px">
		{#each logs as edge, i}
			{@const log = edge.node}
			<a
				href="/chronicle/{log.id}"
				class="group flex flex-col gap-2 border border-border-dim bg-panel px-3 py-3 transition-all hover:bg-panel-hover hover:border-accent-amber/20 sm:flex-row sm:items-start sm:gap-4"
			>
				<!-- Date badge -->
				<div class="flex shrink-0 items-center gap-2 sm:w-24 sm:flex-col sm:items-start sm:gap-0.5">
					<Calendar class="h-3 w-3 text-accent-amber/40" />
					<span class="machine-text text-[10px] text-accent-amber">{formatGameDate(log.gameDate)}</span>
				</div>

				<!-- Content -->
				<div class="min-w-0 flex-1">
					<h2 class="text-xs font-bold text-text-primary uppercase tracking-wider group-hover:text-accent-amber transition-colors">
						{log.title ?? 'UNTITLED LOG'}
					</h2>
					{#if log.brief}
						<p class="mt-1 line-clamp-2 text-[11px] text-text-muted leading-relaxed">
							{log.brief}
						</p>
					{/if}

					<!-- Tags -->
					<div class="mt-2 flex flex-wrap gap-1.5">
						{#each log.characters?.edges ?? [] as charEdge}
							<span class="inline-flex items-center gap-1 bg-accent-cyan/5 border border-accent-cyan/10 px-1.5 py-px text-[10px] text-accent-cyan/60 uppercase tracking-wider">
								<Users class="h-2.5 w-2.5" />
								{charEdge.node.name}
							</span>
						{/each}
						{#each log.places?.edges ?? [] as placeEdge}
							<span class="inline-flex items-center gap-1 bg-accent-amber/5 border border-accent-amber/10 px-1.5 py-px text-[10px] text-accent-amber/60 uppercase tracking-wider">
								<MapPin class="h-2.5 w-2.5" />
								{placeEdge.node.name}
							</span>
						{/each}
					</div>
				</div>

				<!-- Record number -->
				<span class="hidden machine-text text-[9px] text-text-muted/30 sm:block">
					#{String(i + 1).padStart(3, '0')}
				</span>
			</a>
		{:else}
			<div class="border border-border-dim bg-panel px-4 py-8 text-center">
				<p class="machine-text text-text-muted">NO LOGS RECORDED</p>
				<p class="machine-text text-[10px] text-text-muted/50 mt-1">IMPORT A SESSION TO BEGIN</p>
			</div>
		{/each}
	</div>
</div>

<script lang="ts">
	import { resolve } from '$app/paths';
	import RelationGroupList from '$lib/components/database/RelationGroupList.svelte';
	import {
		buildGameLogRelationGroups,
		detailPanelClass,
		detailSectionTitleClass,
		getNamedNodes
	} from '$lib/database-detail';
	import { formatGameDate } from '$lib/utils';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let LogDetail = $derived(data.LogDetail);
	let gameLog = $derived(
		$LogDetail?.data?.node?.__typename === 'GameLog' ? $LogDetail.data.node : null
	);
	let logRelationGroups = $derived.by(() => {
		if (!gameLog) {
			return [];
		}

		return buildGameLogRelationGroups({
			artifacts: gameLog.artifacts,
			associations: gameLog.associations,
			characters: gameLog.characters,
			items: gameLog.items,
			places: gameLog.places,
			races: gameLog.races
		});
	});
	let placesSetIn = $derived.by(() => (gameLog ? getNamedNodes(gameLog.placesSetIn) : []));

	function openExternalSource(url: string) {
		window.open(url, '_blank', 'noopener,noreferrer');
	}
</script>

<div class="log-detail-page">
	<div>
		<a href={resolve('/logs')} class="log-back-link">
			<span>&lt;</span> RETURN TO CHRONICLE
		</a>
	</div>

	{#if $LogDetail?.fetching}
		<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80">
			<div class="text-industrial-amber animate-pulse font-mono">RETRIEVING RECORD...</div>
		</div>
	{:else if $LogDetail?.errors}
		<div class="border border-red-500/50 bg-red-900/20 p-6 font-mono text-red-500">
			ERROR: UNABLE TO DECRYPT LOG DATA.
			<pre class="mt-4 text-xs">{JSON.stringify($LogDetail.errors, null, 2)}</pre>
		</div>
	{:else if gameLog}
		<header class="log-panel border-industrial-dim border-t-2">
			<h1 class="log-title mb-2">
				{gameLog.title}
			</h1>
			<div class="log-meta">
				<span>DATE: {formatGameDate(gameLog.gameDate)}</span>
				{#if gameLog.url}
					<span class="inline-flex items-center gap-2 whitespace-nowrap">
						<span class="text-slate-600" aria-hidden="true">|</span>
						<button
							type="button"
							onclick={() => openExternalSource(gameLog.url)}
							class="inline-flex min-h-11 items-center border border-transparent px-1 hover:text-white hover:underline"
						>
							SOURCE LINK ↗
						</button>
					</span>
				{/if}
			</div>
		</header>

		{#if gameLog.brief}
			<div class="log-abstract border-industrial-amber border-l-3">
				<p class="font-body text-base text-slate-300 italic sm:text-lg">{gameLog.brief}</p>
			</div>
		{/if}

		<div class="space-y-6">
			<div class={detailPanelClass}>
				<h3 class={detailSectionTitleClass}>Places Set In</h3>

				{#if placesSetIn.length > 0}
					<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
						{#each placesSetIn as place (place.id)}
							<a
								href={resolve('/database/places/[id]', { id: place.id })}
								class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
							>
								{place.name}
							</a>
							{#if place !== placesSetIn[placesSetIn.length - 1]}
								<span class="text-zinc-700" aria-hidden="true">•</span>
							{/if}
						{/each}
					</div>
				{:else}
					<p class="text-sm text-zinc-500">No locations recorded for this log.</p>
				{/if}
			</div>

			<div class="log-panel prose prose-lg max-w-none text-slate-300 prose-invert">
				<p class="leading-relaxed whitespace-pre-wrap">
					{gameLog.synopsis || gameLog.summary || 'No detailed transcript available.'}
				</p>
			</div>

			<div class={detailPanelClass}>
				<RelationGroupList
					title="Found In This Log"
					groups={logRelationGroups}
					emptyMessage="No linked entities recorded for this log."
				/>
			</div>
		</div>
	{/if}
</div>

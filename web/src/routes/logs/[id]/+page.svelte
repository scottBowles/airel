<script lang="ts">
	import type { PageData } from './$houdini';
	import { resolve } from '$app/paths';
	import { formatGameDate } from '$lib/utils';

	let { data }: { data: PageData } = $props();
	let LogDetail = $derived(data.LogDetail);

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
	{:else if $LogDetail?.data?.node?.__typename === 'GameLog'}
		{@const gameLog = $LogDetail.data.node}
		<!-- Header Section -->
		<header class="log-panel border-industrial-dim border-t-2">
			<h1 class="log-title mb-2">
				{gameLog.title}
			</h1>
			<div class="log-meta">
				<span class="whitespace-nowrap">DATE: {formatGameDate(gameLog.gameDate)}</span>
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

		<!-- Brief / Abstract -->
		{#if gameLog.brief}
			<div class="log-abstract border-industrial-amber border-l-3">
				<h3 class="text-industrial-amber mb-2 font-mono text-xs uppercase">Abstract</h3>
				<p class="font-body text-base text-slate-300 italic sm:text-lg">{gameLog.brief}</p>
			</div>
		{/if}

		<!-- Main Content (Synopsis/Summary for now) -->
		<div class="log-panel prose prose-lg max-w-none text-slate-300 prose-invert">
			<h3 class="log-panel-title">Record</h3>
			<p class="leading-relaxed whitespace-pre-wrap">
				{gameLog.synopsis || gameLog.summary || 'No detailed transcript available.'}
			</p>
		</div>

		<!-- Related Associations -->
		<div class="log-related-grid">
			<!-- Characters -->
			{#if gameLog.characters?.edges.length}
				<div class="log-related-group">
					<h4 class="font-display text-lg text-slate-300 uppercase">Personnel</h4>
					<ul class="space-y-1">
						{#each gameLog.characters.edges as { node } (node.id)}
							<li>
								<a
									href={resolve(`/database/characters/${node.id}`)}
									class="log-related-link text-industrial-green"
								>
									{node.name}
								</a>
							</li>
						{/each}
					</ul>
				</div>
			{/if}

			<!-- Places -->
			{#if gameLog.placesSetIn?.edges.length}
				<div class="log-related-group">
					<h4 class="font-display text-lg text-slate-300 uppercase">Locations</h4>
					<ul class="space-y-1">
						{#each gameLog.placesSetIn.edges as { node } (node.id)}
							<li>
								<a
									href={resolve(`/database/places/${node.id}`)}
									class="log-related-link text-industrial-amber"
								>
									{node.name}
								</a>
							</li>
						{/each}
					</ul>
				</div>
			{/if}

			<!-- Items -->
			{#if gameLog.items?.edges.length}
				<div class="log-related-group">
					<h4 class="font-display text-lg text-slate-300 uppercase">Assets</h4>
					<ul class="space-y-1">
						{#each gameLog.items.edges as { node } (node.id)}
							<li>
								<a
									href={resolve(`/database/items/${node.id}`)}
									class="log-related-link text-slate-400 hover:text-slate-200"
								>
									{node.name}
								</a>
							</li>
						{/each}
					</ul>
				</div>
			{/if}
		</div>
	{/if}
</div>

<script lang="ts">
	import type { PageData } from './$houdini';
	import { resolve } from '$app/paths';

	let { data }: { data: PageData } = $props();
	let LogDetail = $derived(data.LogDetail);
</script>

<div class="mx-auto max-w-4xl space-y-8 pb-20">
	<div class="mb-6">
		<a
			href={resolve('/logs')}
			class="machine-text hover:text-industrial-amber mb-4 flex items-center gap-2 text-xs text-slate-500"
		>
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
	{:else if $LogDetail?.data?.node}
		<!-- Header Section -->
		<header class="border-industrial-dim border-b pb-6">
			<h1 class="font-display mb-2 text-4xl font-bold tracking-widest text-slate-100 uppercase">
				{$LogDetail.data.node.title}
			</h1>
			<div class="text-industrial-amber flex items-center gap-4 font-mono text-sm">
				<span>DATE: {$LogDetail.data.node.gameDate || 'UNKNOWN'}</span>
				{#if $LogDetail.data.node.url}
					<span class="text-slate-600">|</span>
					<a
						href={$LogDetail.data.node.url}
						target="_blank"
						rel="noopener noreferrer"
						class="hover:text-white hover:underline"
					>
						SOURCE LINK ↗
					</a>
				{/if}
			</div>
		</header>

		<!-- Brief / Abstract -->
		{#if $LogDetail.data.node.brief}
			<div class="border-industrial-amber border-l-2 bg-slate-900/50 p-4">
				<h3 class="text-industrial-amber mb-2 font-mono text-xs uppercase">Abstract</h3>
				<p class="font-body text-lg text-slate-300 italic">{$LogDetail.data.node.brief}</p>
			</div>
		{/if}

		<!-- Main Content (Synopsis/Summary for now) -->
		<div class="prose prose-lg max-w-none text-slate-300 prose-invert">
			<p class="leading-relaxed whitespace-pre-wrap">
				{$LogDetail.data.node.synopsis ||
					$LogDetail.data.node.summary ||
					'No detailed transcript available.'}
			</p>
		</div>

		<!-- Related Associations -->
		<div class="grid grid-cols-1 gap-6 border-t border-slate-800 pt-8 md:grid-cols-3">
			<!-- Characters -->
			{#if $LogDetail.data.node.characters?.edges.length}
				<div class="space-y-3">
					<h4 class="font-display text-lg text-slate-500 uppercase">Personnel</h4>
					<ul class="space-y-1">
						{#each $LogDetail.data.node.characters.edges as { node } (node.id)}
							<li>
								<a
									href={resolve(`/database/characters/${node.id}`)}
									class="machine-text text-industrial-green text-sm hover:underline"
								>
									{node.name}
								</a>
							</li>
						{/each}
					</ul>
				</div>
			{/if}

			<!-- Places -->
			{#if $LogDetail.data.node.placesSetIn?.edges.length}
				<div class="space-y-3">
					<h4 class="font-display text-lg text-slate-500 uppercase">Locations</h4>
					<ul class="space-y-1">
						{#each $LogDetail.data.node.placesSetIn.edges as { node } (node.id)}
							<li>
								<a
									href={resolve(`/database/places/${node.id}`)}
									class="machine-text text-industrial-amber text-sm hover:underline"
								>
									{node.name}
								</a>
							</li>
						{/each}
					</ul>
				</div>
			{/if}

			<!-- Items -->
			{#if $LogDetail.data.node.items?.edges.length}
				<div class="space-y-3">
					<h4 class="font-display text-lg text-slate-500 uppercase">Assets</h4>
					<ul class="space-y-1">
						{#each $LogDetail.data.node.items.edges as { node } (node.id)}
							<li>
								<a
									href={resolve(`/database/items/${node.id}`)}
									class="machine-text text-xs text-slate-400 hover:text-slate-200"
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

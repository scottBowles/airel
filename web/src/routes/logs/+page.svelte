<script lang="ts">
	import type { PageData } from './$houdini';
	import { resolve } from '$app/paths';
	import { formatGameDate } from '$lib/utils';

	let { data }: { data: PageData } = $props();

	let LogList = $derived(data.LogList);
</script>

<div class="log-page">
	<div class="log-header">
		<h2 class="log-title">Chronicle</h2>
		<div class="text-industrial-amber font-mono text-xs">
			<!-- Safe access to store data -->
			Records Found: {$LogList?.data?.gameLogs?.edges?.length || 0}
		</div>
	</div>

	<div class="grid gap-4">
		{#if $LogList?.fetching}
			<div class="log-panel text-industrial-dim animate-pulse text-center font-mono">
				INITIALIZING DATALINK...
			</div>
		{:else if $LogList?.errors}
			<div class="border border-red-900/50 bg-red-900/10 p-4 font-mono text-red-500">
				DATA CORRUPTION DETECTED.
				<pre class="mt-2 text-xs">{JSON.stringify($LogList.errors, null, 2)}</pre>
			</div>
		{:else if $LogList?.data}
			{#each $LogList.data.gameLogs.edges as { node: log } (log.id)}
				<a href={resolve(`/logs/${log.id}`)} class="group log-card">
					<!-- Status Strip -->
					<div
						class="group-hover:bg-industrial-amber absolute top-0 bottom-0 left-0 w-1.5 bg-slate-700 transition-colors"
					></div>

					<div class="log-card-body">
						<div class="mb-2 flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between">
							<h3
								class="font-display group-hover:text-industrial-amber text-xl font-medium text-slate-100 transition-colors"
							>
								{log.title}
							</h3>
							<span class="font-mono text-xs text-slate-500">{formatGameDate(log.gameDate)}</span>
						</div>

						<p class="font-body line-clamp-2 text-sm leading-relaxed text-slate-300 sm:text-[15px]">
							{log.brief || log.synopsis}
						</p>
						<!-- Tech Chips removed as tags don't exist yet -->
					</div>
				</a>
			{/each}
		{/if}
	</div>
</div>

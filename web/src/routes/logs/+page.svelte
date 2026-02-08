<script lang="ts">
	import type { PageData } from './$houdini';
	import { resolve } from '$app/paths';
	import { formatGameDate } from '$lib/utils';

	let { data }: { data: PageData } = $props();

	let LogList = $derived(data.LogList);
</script>

<div class="space-y-4">
	<div class="border-industrial-dim flex items-center justify-between border-b pb-4">
		<h2 class="text-3xl font-bold tracking-widest text-slate-100 uppercase">Chronicle</h2>
		<div class="text-industrial-amber font-mono text-xs">
			<!-- Safe access to store data -->
			Records Found: {$LogList?.data?.gameLogs?.edges?.length || 0}
		</div>
	</div>

	<div class="grid gap-4">
		{#if $LogList?.fetching}
			<div class="text-industrial-dim animate-pulse p-8 text-center font-mono">
				INITIALIZING DATALINK...
			</div>
		{:else if $LogList?.errors}
			<div class="border border-red-900/50 bg-red-900/10 p-4 font-mono text-red-500">
				DATA CORRUPTION DETECTED.
				<pre class="mt-2 text-xs">{JSON.stringify($LogList.errors, null, 2)}</pre>
			</div>
		{:else if $LogList?.data}
			{#each $LogList.data.gameLogs.edges as { node: log } (log.id)}
				<a
					href={resolve(`/logs/${log.id}`)}
					class="group hover:border-industrial-amber/50 relative block overflow-hidden border border-slate-800 bg-slate-900/40 transition-all duration-150"
				>
					<!-- Status Strip -->
					<div
						class="group-hover:bg-industrial-amber absolute top-0 bottom-0 left-0 w-1 bg-slate-800 transition-colors"
					></div>

					<div class="p-4 pl-6">
						<div class="mb-2 flex items-baseline justify-between">
							<h3
								class="font-display group-hover:text-industrial-amber text-xl font-medium text-slate-200 transition-colors"
							>
								{log.title}
							</h3>
							<span class="font-mono text-xs text-slate-500">{formatGameDate(log.gameDate)}</span>
						</div>

						<p class="font-body line-clamp-2 text-sm text-slate-400">
							{log.brief || log.synopsis}
						</p>
						<!-- Tech Chips removed as tags don't exist yet -->
					</div>
				</a>
			{/each}
		{/if}
	</div>
</div>

<script lang="ts">
	// The original Chronicle list, unchanged: newest first, one row per session.
	import { formatGameDate } from '$lib/utils';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import Tooltip from '$lib/components/Tooltip.svelte';

	type LogEdge = {
		readonly node: {
			readonly id: string;
			readonly title: string | null;
			readonly brief: string | null;
			readonly gameDate: Date | string | null;
			readonly sessionNumber: number | null;
			readonly url: string;
		};
	};

	let { logs }: { logs: readonly LogEdge[] } = $props();
</script>

<div class="space-y-px">
	{#each logs as edge}
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

				<!-- Session number: left out when the log has none -->
				{#if log.sessionNumber != null}
					<span class="hidden machine-text text-[9px] text-text-faint sm:block">
						#{String(log.sessionNumber).padStart(3, '0')}
					</span>
				{/if}
			</a>

			<!-- External link gutter -->
			{#if log.url}
				<Tooltip text="Open Google Doc" side="left">
					{#snippet children(props)}
						<a
							{...props}
							href={log.url}
							target="_blank"
							rel="noopener noreferrer"
							class="flex items-center border-l border-border-dim bg-panel px-2.5 text-text-muted transition-colors hover:bg-accent-amber/5 hover:text-accent-amber"
						>
							<ExternalLink class="h-3.5 w-3.5" />
						</a>
					{/snippet}
				</Tooltip>
			{/if}
		</div>
	{:else}
		<div class="border border-border-dim bg-panel px-4 py-8 text-center">
			<p class="machine-text text-text-muted">NO LOGS RECORDED</p>
			<p class="machine-text text-[10px] text-text-faint mt-1">IMPORT A SESSION TO BEGIN</p>
		</div>
	{/each}
</div>

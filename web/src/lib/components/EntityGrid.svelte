<script lang="ts">
	import { cn } from '$lib/utils';
	import CloudinaryImage from '$lib/components/CloudinaryImage.svelte';

	let {
		entities,
		basePath,
		emptyMessage = 'No records found',
	}: {
		entities: Array<{
			id: string;
			name: string;
			description?: string | null;
			thumbnailId?: string | null;
			imageIds?: string[] | null;
		}>;
		basePath: string;
		emptyMessage?: string;
	} = $props();
</script>

{#if entities.length > 0}
	<div class="db-grid">
		{#each entities as entity, i}
			<a
				href="{basePath}/{entity.id}"
				class="group panel-bg flex flex-col border border-border-dim transition-all hover:border-accent-amber/30 hover:shadow-glow-amber"
			>
				<!-- Thumbnail with overlay -->
				<div class="relative">
					<CloudinaryImage
						imageId={entity.thumbnailId ?? entity.imageIds?.[0]}
						alt={entity.name}
						width={400}
						height={240}
						class="aspect-[5/3] w-full"
					/>
					<div class="absolute inset-0 bg-gradient-to-t from-panel via-transparent to-transparent"></div>
					<span class="absolute left-2 top-2 machine-text text-[9px] text-text-muted">
						REC-{String(i + 1).padStart(3, '0')}
					</span>
				</div>

				<!-- Content -->
				<div class="flex flex-1 flex-col gap-1 border-t border-border-dim px-2.5 py-2">
					<h3 class="text-xs font-bold text-text-primary uppercase tracking-wider group-hover:text-accent-amber transition-colors line-clamp-1">
						{entity.name}
					</h3>
					{#if entity.description}
						<p class="line-clamp-2 text-xs text-text-secondary leading-relaxed">
							{entity.description}
						</p>
					{/if}
				</div>
			</a>
		{/each}
	</div>
{:else}
	<div class="panel-border panel-bg panel-pad text-center console-frame">
		<p class="machine-text text-text-muted">{emptyMessage}</p>
	</div>
{/if}

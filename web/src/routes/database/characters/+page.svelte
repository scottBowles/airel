<script lang="ts">
	import type { PageData } from './$houdini';
	import { resolve } from '$app/paths';
	import { sortEdgesByUpdatedDesc } from '$lib/utils';
	import CldImage from '$lib/components/images/CldImage.svelte';
	import ScifiPlaceholder from '$lib/components/ui/ScifiPlaceholder.svelte';

	let { data }: { data: PageData } = $props();
	let CharacterList = $derived(data.CharacterList);
	let characterEdges = $derived(sortEdgesByUpdatedDesc($CharacterList.data?.characters?.edges));
</script>

<div class="db-page">
	<div class="db-header">
		<div>
			<div class="mb-1 font-mono text-xs text-slate-500">DATABASE / PERSONNEL</div>
			<h2 class="db-title">Characters</h2>
		</div>
		<div class="text-industrial-amber font-mono text-xs">
			Count: {characterEdges.length}
		</div>
	</div>

	<!-- Grid -->
	<div class="db-grid">
		{#if characterEdges.length}
			{#each characterEdges as { node: char } (char.id)}
				<a href={resolve(`/database/characters/${char.id}`)} class="group db-card">
					<div class="mb-3 flex items-center gap-3">
						{#if char.imageIds?.length > 0}
							<div class="db-card-thumb">
								<CldImage
									id={char.imageIds[0]}
									alt={char.name}
									width={40}
									height={40}
									class="h-full w-full object-cover"
								/>
							</div>
						{:else}
							<ScifiPlaceholder type="character" />
						{/if}
						<div class="min-w-0">
							<h3 class="db-card-title">
								{char.name}
							</h3>
						</div>
					</div>
					<p class="db-card-copy">
						{char.description || 'No data available.'}
					</p>
				</a>
			{/each}
		{/if}
	</div>
</div>

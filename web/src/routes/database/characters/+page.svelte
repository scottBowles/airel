<script lang="ts">
	import type { PageData } from './$houdini';
	import { resolve } from '$app/paths';
	import CldImage from '$lib/components/images/CldImage.svelte';
	import ScifiPlaceholder from '$lib/components/ui/ScifiPlaceholder.svelte';

	let { data }: { data: PageData } = $props();
	let CharacterList = $derived(data.CharacterList);
</script>

<div class="db-page">
	<div class="db-header">
		<div>
			<div class="mb-1 font-mono text-xs text-slate-500">DATABASE / PERSONNEL</div>
			<h2 class="db-title">Characters</h2>
		</div>
		<div class="text-industrial-amber font-mono text-xs">
			Count: {$CharacterList.data?.characters.edges.length || 0}
		</div>
	</div>

	<!-- Toolbar / Search -->
	<div class="db-toolbar">
		<input
			type="text"
			placeholder="FILTER PERSONNEL..."
			class="industrial-input w-full bg-slate-950 sm:max-w-sm"
		/>
		<button class="industrial-btn w-full sm:w-auto">SEARCH</button>
	</div>

	<!-- Grid -->
	<div class="db-grid">
		{#if $CharacterList.data}
			{#each $CharacterList.data.characters.edges as { node: char } (char.id)}
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

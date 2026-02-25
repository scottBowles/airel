<script lang="ts">
	import CldImage from '$lib/components/images/CldImage.svelte';

	let { imageIds }: { imageIds: string[] } = $props();
	// We'll track the currently visible index
	let selected = $state(0);
	let indicatorIndexes = $derived(imageIds.map((_, index) => index));
	let carousel = $state<HTMLDivElement | null>(null);

	function setCarousel(node: HTMLDivElement) {
		carousel = node;

		return () => {
			if (carousel === node) {
				carousel = null;
			}
		};
	}

	function handleScroll() {
		if (!carousel) return;
		const index = Math.round(carousel.scrollLeft / carousel.clientWidth);
		selected = index;
	}

	function scroll(index: number) {
		if (!carousel) return;
		// Clamp index
		if (index < 0) index = 0;
		if (index >= imageIds.length) index = imageIds.length - 1;

		selected = index;
		carousel.scrollTo({
			left: index * carousel.clientWidth,
			behavior: 'smooth'
		});
	}
</script>

<div class="group relative h-87.5 w-full overflow-hidden border border-slate-700 bg-slate-900">
	<!-- Main Carousel -->
	{#if imageIds.length > 0}
		<!-- Scroll Container -->
		<div
			{@attach setCarousel}
			onscroll={handleScroll}
			class="
        absolute inset-0 flex
        snap-x snap-mandatory overflow-x-auto scroll-smooth
        [&::-webkit-scrollbar]:hidden
      "
		>
			{#each imageIds as id, i (id + i)}
				<div
					class="
          relative flex h-full w-full
          shrink-0 snap-center items-center
          justify-center
        "
				>
					<!-- Image -->
					<CldImage
						{id}
						alt={`Image ${i + 1}`}
						width={1200}
						height={1200}
						mode="limit"
						class="max-h-full max-w-full object-contain"
					/>
				</div>
			{/each}
		</div>

		<!-- Navigation Arrows -->
		{#if imageIds.length > 1}
			<!-- Left Arrow -->
			{#if selected > 0}
				<button
					onclick={() => scroll(selected - 1)}
					class="absolute top-1/2 left-2 z-10 -translate-y-1/2 rounded-full bg-black/30 p-2 text-white/70 transition-all hover:bg-black/50 hover:text-white"
					aria-label="Previous image"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"><polyline points="15 18 9 12 15 6" /></svg
					>
				</button>
			{/if}

			<!-- Right Arrow -->
			{#if selected < imageIds.length - 1}
				<button
					onclick={() => scroll(selected + 1)}
					class="absolute top-1/2 right-2 z-10 -translate-y-1/2 rounded-full bg-black/30 p-2 text-white/70 transition-all hover:bg-black/50 hover:text-white"
					aria-label="Next image"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"><polyline points="9 18 15 12 9 6" /></svg
					>
				</button>
			{/if}
		{/if}
	{:else}
		<div class="flex h-full items-center justify-center font-mono text-sm text-slate-500">
			NO VISUAL RECORD
		</div>
	{/if}

	<!-- Indicators -->
	{#if imageIds.length > 1}
		<div
			class="pointer-events-none absolute right-0 bottom-4 left-0 z-10 flex justify-center gap-2"
		>
			{#each indicatorIndexes as i (i)}
				<button
					onclick={() => scroll(i)}
					class="
            pointer-events-auto h-2 w-2 cursor-pointer rounded-full transition-colors
            {i === selected
						? 'bg-industrial-amber shadow-[0_0_8px_rgba(255,176,0,0.5)]'
						: 'bg-slate-600 hover:bg-slate-400'}
          "
					aria-label={`Go to image ${i + 1}`}
				></button>
			{/each}
		</div>
	{/if}
</div>

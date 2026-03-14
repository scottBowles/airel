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

	function prefersReducedMotion() {
		return (
			typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
		);
	}

	function scroll(index: number) {
		if (!carousel) return;
		const nextIndex = ((index % imageIds.length) + imageIds.length) % imageIds.length;

		selected = nextIndex;
		carousel.scrollTo({
			left: nextIndex * carousel.clientWidth,
			behavior: prefersReducedMotion() ? 'auto' : 'smooth'
		});
	}
</script>

<div
	class="group relative h-64 w-full overflow-hidden border border-slate-700 bg-slate-900 sm:h-75 lg:h-87.5"
	role="region"
	aria-label={imageIds.length > 1
		? `Image carousel, image ${selected + 1} of ${imageIds.length}`
		: 'Image preview'}
	aria-roledescription={imageIds.length > 1 ? 'carousel' : undefined}
>
	<!-- Main Carousel -->
	{#if imageIds.length > 0}
		{#if imageIds.length > 1}
			<p class="sr-only">Use the previous, next, or dot buttons to navigate between images.</p>
		{/if}

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
			<button
				onclick={() => scroll(selected - 1)}
				class="absolute top-1/2 left-2 z-10 inline-flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-black/40 p-1.5 text-white/70 transition-all hover:bg-black/60 hover:text-white"
				aria-label="Previous image"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="20"
					height="20"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"><polyline points="15 18 9 12 15 6" /></svg
				>
			</button>

			<button
				onclick={() => scroll(selected + 1)}
				class="absolute top-1/2 right-2 z-10 inline-flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-black/40 p-1.5 text-white/70 transition-all hover:bg-black/60 hover:text-white"
				aria-label="Next image"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="20"
					height="20"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"><polyline points="9 18 15 12 9 6" /></svg
				>
			</button>
		{/if}
	{:else}
		<div class="flex h-full items-center justify-center font-mono text-sm text-slate-500">
			NO VISUAL RECORD
		</div>
	{/if}

	<!-- Indicators -->
	{#if imageIds.length > 1}
		<div
			class="pointer-events-none absolute right-0 bottom-4 left-0 z-10 flex justify-center gap-1"
		>
			{#each indicatorIndexes as i (i)}
				<button
					onclick={() => scroll(i)}
					class="pointer-events-auto inline-flex h-3.5 w-3.5 cursor-pointer items-center justify-center rounded-full transition-transform hover:scale-110 focus-visible:scale-110"
					aria-label={`Go to image ${i + 1}`}
					aria-current={i === selected ? 'true' : undefined}
				>
					<span
						class={`h-2 w-2 rounded-full transition-colors ${i === selected ? 'bg-industrial-amber shadow-[0_0_8px_rgba(255,176,0,0.5)]' : 'bg-slate-600 hover:bg-slate-400'}`}
					></span>
				</button>
			{/each}
		</div>
	{/if}

	{#if imageIds.length > 1}
		<div class="sr-only" aria-live="polite">Viewing image {selected + 1} of {imageIds.length}</div>
	{/if}
</div>

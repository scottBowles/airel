<script lang="ts">
	import { dndzone, type DndEvent } from 'svelte-dnd-action';
	import CldImage from '$lib/components/images/CldImage.svelte';

	let {
		images,
		onUpdate
	}: {
		images: string[];
		onUpdate: (images: string[]) => void;
	} = $props();

	// Create a stable local state for dndzone.
	// Initialize empty to avoid "state_referenced_locally".
	let items = $state<{ id: string; realId: string }[]>([]);

	// We use an effect to sync prop changes to local state.
	// To avoid recreating items (and losing drag state or animation context) on every prop update,
	// we only update if the length or content fundamentally changes.
	// However, naive 'map' creates new objects every time.
	// Since parent 'images' is just strings, we don't have stable IDs.
	// Using index-based IDs (img_{index}) is problematic for reordering animations
	// because swapping items keeps the IDs in the same DOM positions (if keyed by ID).
	// If keyed by index, Svelte reuses DOM, which is okay but dndzone needs unique IDs to track moves.
	// The best we can do without stable IDs from parent is to assume usage of unique image IDs,
	// or generate random IDs once and try to preserve them?
	// No, that's complex synchronization.
	// Let's assume unique image IDs for now as they are Cloudinary public IDs.
	// If duplicates exist, this might glitch.
	$effect(() => {
		// Use untrack? No, we WANT to track images.
		// Construct items. We use the image string itself as ID, assuming uniqueness.
		// If duplicates are possible, we'd need a robust ID generation strategy or
		// wrap string[] in an object[] with IDs in the parent.
		items = images.map((id) => ({ id, realId: id }));
	});

	function handleDndConsider(e: CustomEvent<DndEvent<{ id: string; realId: string }>>) {
		items = e.detail.items;
	}

	function handleDndFinalize(e: CustomEvent<DndEvent<{ id: string; realId: string }>>) {
		items = e.detail.items;
		onUpdate(items.map((i) => i.realId));
	}

	function removeImage(idToRemove: string) {
		items = items.filter((item) => item.id !== idToRemove);
		onUpdate(items.map((i) => i.realId));
	}
</script>

<div
	class="grid max-h-[600px] grid-cols-2 gap-4 overflow-y-auto rounded border border-slate-700 bg-slate-900 p-4 shadow-inner md:grid-cols-3 xl:grid-cols-4"
	use:dndzone={{
		items,
		flipDurationMs: 300,
		dropTargetStyle: { outline: '2px solid rgba(255,176,0,0.5)' }
	}}
	onconsider={handleDndConsider}
	onfinalize={handleDndFinalize}
>
	{#each items as item (item.id)}
		<div
			class="group hover:border-industrial-amber relative rounded border border-slate-700/50 bg-slate-800 p-1 shadow-md transition-colors"
		>
			<div
				class="flex aspect-square items-center justify-center overflow-hidden rounded bg-slate-950"
			>
				<CldImage
					id={item.realId}
					width={250}
					height={250}
					alt="Grid item"
					class="h-full w-full object-cover"
				/>
			</div>

			<!-- Drag Handle indicator (optional visual hint) -->
			<div
				class="absolute inset-0 cursor-grab bg-black opacity-0 transition-opacity group-hover:opacity-10 active:cursor-grabbing"
			></div>

			<!-- Delete Button -->
			<button
				onclick={() => removeImage(item.id)}
				class="absolute -top-2 -right-2 z-10 rounded-full bg-red-500/90 p-1 text-white shadow-lg transition-colors hover:bg-red-600"
				title="Remove"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="14"
					height="14"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="3"
					stroke-linecap="round"
					stroke-linejoin="round"
					><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"
					></line></svg
				>
			</button>
		</div>
	{/each}

	{#if items.length === 0}
		<div
			class="col-span-full flex h-32 items-center justify-center rounded-lg border-2 border-dashed border-slate-700 text-slate-500 italic"
		>
			No images. Upload some!
		</div>
	{/if}
</div>

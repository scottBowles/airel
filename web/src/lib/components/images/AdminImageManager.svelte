<script lang="ts">
	import { fade, slide } from 'svelte/transition';
	import { cubicInOut } from 'svelte/easing';
	import { toast } from 'svelte-sonner';
	import ImageCarousel from './ImageCarousel.svelte';
	import ImageSortableGrid from './ImageSortableGrid.svelte';
	import UploadWidget from './UploadWidget.svelte';

	let {
		imageIds,
		canEdit = false,
		onSave
	}: {
		imageIds: string[];
		canEdit?: boolean;
		onSave: (newIds: string[]) => void;
	} = $props();

	// Initialize empty to avoid "state_referenced_locally" warning.
	// The effect below will populate it.
	let localImages = $state<string[]>([]);
	let isEditing = $state(false);
	let saving = $state(false);

	// Sync localImages when imageIds prop changes (if not editing)
	$effect(() => {
		// Only update if not editing to prevent overwriting WIP changes.
		// Also consider untracking isEditing to avoid re-running when isEditing changes?
		// Actually, if isEditing changes from true -> false, we might WANT to reset?
		// No, cancelEditing handles reset. startEditing handles init.
		// So we only want to react to imageIds changes.
		if (!isEditing) {
			localImages = [...imageIds];
		}
	});

	function startEditing() {
		localImages = [...imageIds];
		isEditing = true;
	}

	function cancelEditing() {
		isEditing = false;
		localImages = [...imageIds];
	}

	async function saveChanges() {
		saving = true;
		try {
			await onSave(localImages);
			isEditing = false;
		} catch (e) {
			console.error('Failed to save images:', e);
			toast.error('Failed to save changes.');
		} finally {
			saving = false;
		}
	}

	function handleGridUpdate(newIds: string[]) {
		localImages = newIds;
	}

	function handleUpload(publicId: string) {
		localImages = [...localImages, publicId];
	}
</script>

<div class="space-y-4">
	<div class="flex items-center justify-between border-b border-white/5 pb-2">
		<h3 class="font-display text-sm font-bold tracking-widest text-slate-400 uppercase">
			VISUAL RECORDS
		</h3>
		{#if canEdit}
			{#if !isEditing}
				<button
					onclick={startEditing}
					class="text-industrial-amber font-mono text-xs uppercase underline decoration-dotted underline-offset-4 transition-colors hover:text-white"
				>
					[EDIT MODE]
				</button>
			{:else}
				<div class="flex gap-2">
					<button
						onclick={cancelEditing}
						disabled={saving}
						class="rounded border border-transparent px-3 py-1 text-xs text-slate-400 transition-colors hover:border-slate-600 hover:text-white"
					>
						CANCEL
					</button>
					<button
						onclick={saveChanges}
						disabled={saving}
						class="bg-industrial-amber rounded px-3 py-1 text-xs font-bold text-black shadow-lg transition-colors hover:bg-white disabled:opacity-50"
					>
						{saving ? 'SAVING...' : 'SAVE CHANGES'}
					</button>
				</div>
			{/if}
		{/if}
	</div>

	<div class="relative min-h-75 overflow-hidden rounded-lg border border-white/5 bg-black/20">
		{#if !isEditing}
			<div in:fade={{ duration: 200 }} out:fade={{ duration: 0 }}>
				<ImageCarousel {imageIds} />
			</div>
		{:else}
			<div
				in:fade={{ duration: 200 }}
				out:fade={{ duration: 0 }}
				class="space-y-4 bg-slate-900/90 p-4"
			>
				<div class="flex justify-end">
					<UploadWidget onUpload={handleUpload} />
				</div>

				<ImageSortableGrid images={localImages} onUpdate={handleGridUpdate} />

				<p class="mt-4 text-center font-mono text-xs text-slate-500">
					Drag to reorder. Changes are local until you click SAVE.
				</p>
			</div>
		{/if}
	</div>
</div>

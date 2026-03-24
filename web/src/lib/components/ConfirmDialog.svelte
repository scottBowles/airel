<script lang="ts">
	let {
		open = false,
		title = 'Confirm',
		message = 'Are you sure?',
		confirmLabel = 'Delete',
		onconfirm,
		oncancel,
	}: {
		open: boolean;
		title?: string;
		message?: string;
		confirmLabel?: string;
		onconfirm: () => void;
		oncancel: () => void;
	} = $props();

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') oncancel();
	}
</script>

{#if open}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-[100] flex items-center justify-center bg-void/80"
		onkeydown={handleKeydown}
	>
		<div class="w-full max-w-sm border border-border-dim bg-hull p-4 shadow-lg">
			<h3 class="title-section mb-2">{title}</h3>
			<p class="mb-4 text-xs text-text-secondary">{message}</p>
			<div class="flex justify-end gap-2">
				<button
					onclick={oncancel}
					class="cursor-pointer border border-border-dim px-3 py-1 text-xs text-text-muted transition-colors hover:text-text-primary"
				>
					Cancel
				</button>
				<button
					onclick={onconfirm}
					class="cursor-pointer border border-accent-red/30 bg-accent-red/10 px-3 py-1 text-xs text-accent-red transition-colors hover:bg-accent-red/20"
				>
					{confirmLabel}
				</button>
			</div>
		</div>
	</div>
{/if}

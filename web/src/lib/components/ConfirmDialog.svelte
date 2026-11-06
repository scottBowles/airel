<script lang="ts">
	import { AlertDialog } from 'bits-ui';

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

	let cancelButtonEl = $state<HTMLElement | null>(null);
</script>

<AlertDialog.Root
	{open}
	onOpenChange={(value) => {
		if (!value) oncancel();
	}}
>
	<AlertDialog.Portal>
		<AlertDialog.Overlay
			class="fixed inset-0 z-[100] flex items-center justify-center bg-void/80"
		/>
		<AlertDialog.Content
			class="fixed top-1/2 left-1/2 z-[100] w-full max-w-sm -translate-x-1/2 -translate-y-1/2 border border-border-dim bg-hull p-4 shadow-lg"
			onOpenAutoFocus={(e) => {
				e.preventDefault();
				cancelButtonEl?.focus();
			}}
		>
			<AlertDialog.Title class="title-section mb-2">{title}</AlertDialog.Title>
			<AlertDialog.Description class="mb-4 text-xs text-text-secondary">
				{message}
			</AlertDialog.Description>
			<div class="flex justify-end gap-2">
				<AlertDialog.Cancel
					bind:ref={cancelButtonEl}
					class="cursor-pointer border border-border-dim px-3 py-1 text-xs text-text-muted transition-colors hover:text-text-primary"
				>
					Cancel
				</AlertDialog.Cancel>
				<AlertDialog.Action
					onclick={onconfirm}
					class="cursor-pointer border border-accent-red/30 bg-accent-red/10 px-3 py-1 text-xs text-accent-red transition-colors hover:bg-accent-red/20"
				>
					{confirmLabel}
				</AlertDialog.Action>
			</div>
		</AlertDialog.Content>
	</AlertDialog.Portal>
</AlertDialog.Root>

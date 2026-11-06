<script lang="ts">
	import { Tooltip } from 'bits-ui';
	import type { Snippet } from 'svelte';

	let {
		text,
		children,
		side = 'top',
	}: {
		text: string;
		children: Snippet<[Record<string, unknown>]>;
		side?: 'top' | 'bottom' | 'left' | 'right';
	} = $props();
</script>

<Tooltip.Root>
	<Tooltip.Trigger>
		{#snippet child({ props })}
			{@render children(props)}
		{/snippet}
	</Tooltip.Trigger>
	<Tooltip.Portal>
		<Tooltip.Content
			{side}
			sideOffset={4}
			class="z-200 border border-border-dim bg-hull px-2 py-1 text-[10px] text-text-secondary shadow-lg"
		>
			{text}
		</Tooltip.Content>
	</Tooltip.Portal>
</Tooltip.Root>

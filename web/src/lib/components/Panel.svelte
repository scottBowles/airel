<script lang="ts">
	import { cn } from '$lib/utils';

	let {
		class: className,
		glow = false,
		children,
		...rest
	}: {
		class?: string;
		glow?: boolean;
		children: import('svelte').Snippet;
		[key: string]: unknown;
	} = $props();
</script>

<div
	class={cn(
		'panel-border panel-bg panel-pad console-frame',
		glow && 'shadow-glow-amber border-accent-amber/20',
		className,
	)}
	{...rest}
>
	{@render children()}
</div>

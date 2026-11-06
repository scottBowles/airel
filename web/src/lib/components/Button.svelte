<script lang="ts">
	import { cn } from '$lib/utils';

	let {
		variant = 'primary',
		size = 'md',
		href,
		disabled = false,
		class: className,
		children,
		onclick,
		type = 'button',
		...rest
	}: {
		variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
		size?: 'sm' | 'md' | 'lg';
		href?: string;
		disabled?: boolean;
		class?: string;
		children: import('svelte').Snippet;
		onclick?: (e: MouseEvent) => void;
		type?: 'button' | 'submit' | 'reset';
		[key: string]: unknown;
	} = $props();

	const baseClasses =
		'inline-flex items-center justify-center gap-2 font-mono text-xs tracking-widest uppercase transition-all duration-150 cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed';

	const variants = {
		primary:
			'bg-accent-amber/10 text-accent-amber border border-accent-amber/40 hover:bg-accent-amber/20 hover:border-accent-amber/60 hover:shadow-glow-amber active:bg-accent-amber/25',
		secondary:
			'bg-panel-light text-text-primary border border-border-subtle hover:bg-panel-hover hover:border-accent-amber/20',
		ghost: 'text-text-secondary hover:text-accent-amber hover:bg-accent-amber/5 border border-transparent',
		danger:
			'bg-accent-red/8 text-accent-red border border-accent-red/30 hover:bg-accent-red/15 hover:border-accent-red/50',
	};

	const sizes = {
		sm: 'h-7 px-2.5 text-[10px]',
		md: 'h-8 px-3 text-[11px]',
		lg: 'h-10 px-5 text-xs',
	};

	let classes = $derived(cn(baseClasses, variants[variant], sizes[size], className));
</script>

{#if href}
	<a {href} class={classes} {...rest}>
		{@render children()}
	</a>
{:else}
	<button {type} {disabled} {onclick} class={classes} {...rest}>
		{@render children()}
	</button>
{/if}

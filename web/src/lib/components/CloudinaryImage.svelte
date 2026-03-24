<script lang="ts">
	import { cloudinaryUrl } from '$lib/cloudinary';
	import { cn } from '$lib/utils';

	let {
		imageId,
		alt = '',
		width = 400,
		height,
		crop,
		class: className,
		...rest
	}: {
		imageId: string | null | undefined;
		alt?: string;
		width?: number;
		height?: number;
		crop?: 'fill' | 'fit';
		class?: string;
		[key: string]: unknown;
	} = $props();

	let src = $derived(imageId ? cloudinaryUrl(imageId, { width, height, crop }) : null);
</script>

{#if src}
	<img
		{src}
		{alt}
		class={cn('object-cover', className)}
		loading="lazy"
		{...rest}
	/>
{:else}
	<div
		class={cn(
			'flex items-center justify-center bg-panel-light text-text-muted',
			className,
		)}
		{...rest}
	>
		<svg class="h-8 w-8 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="1.5"
				d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
			/>
		</svg>
	</div>
{/if}

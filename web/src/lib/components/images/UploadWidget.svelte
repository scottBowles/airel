<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		PUBLIC_CLOUDINARY_CLOUD_NAME,
		PUBLIC_CLOUDINARY_UPLOAD_PRESET
	} from '$env/static/public';

	let { onUpload }: { onUpload: (publicId: string) => void } = $props();
	let widget: any;
	let error: string | null = $state(null);

	onMount(async () => {
		if (typeof (window as any).cloudinary === 'undefined') {
			const script = document.createElement('script');
			script.src = 'https://upload-widget.cloudinary.com/global/all.js';
			script.onload = initWidget;
			document.head.appendChild(script);
		} else {
			initWidget();
		}
	});

	function initWidget() {
		if (!PUBLIC_CLOUDINARY_CLOUD_NAME) {
			error = 'Missing Cloudinary Cloud Name';
			return;
		}

		widget = (window as any).cloudinary.createUploadWidget(
			{
				cloudName: PUBLIC_CLOUDINARY_CLOUD_NAME || 'demo',
				uploadPreset: PUBLIC_CLOUDINARY_UPLOAD_PRESET || 'ml_default', // Fallback preset
				sources: ['local', 'url'],
				multiple: false,
				resourceType: 'image',
				folder: 'airel' // Optional folder
			},
			(error: any, result: any) => {
				if (!error && result && result.event === 'success') {
					console.log('Done! Here is the image info: ', result.info);
					onUpload(result.info.public_id);
				} else if (error) {
					console.error('Cloudinary widget error:', error);
				}
			}
		);
	}

	function openWidget() {
		if (widget) {
			widget.open();
		} else if (error) {
			toast.error(error);
		}
	}
</script>

<button
	onclick={openWidget}
	class="panel-border text-industrial-amber flex cursor-pointer items-center justify-center gap-2 bg-slate-900/50 px-4 py-2 font-mono text-sm transition-colors hover:bg-slate-800/80"
>
	<svg
		xmlns="http://www.w3.org/2000/svg"
		width="16"
		height="16"
		viewBox="0 0 24 24"
		fill="none"
		stroke="currentColor"
		stroke-width="2"
		stroke-linecap="round"
		stroke-linejoin="round"
		class="lucide lucide-upload"
		><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line
			x1="12"
			x2="12"
			y1="3"
			y2="15"
		/></svg
	>
	UPLOAD IMAGE
</button>

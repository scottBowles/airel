<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		PUBLIC_CLOUDINARY_CLOUD_NAME,
		PUBLIC_CLOUDINARY_UPLOAD_PRESET
	} from '$env/static/public';

	interface CloudinaryUploadResult {
		event?: string;
		info?: {
			public_id: string;
		};
	}

	interface CloudinaryWidget {
		open: () => void;
	}

	interface CloudinaryGlobal {
		createUploadWidget: (
			options: Record<string, unknown>,
			callback: (error: unknown, result: CloudinaryUploadResult) => void
		) => CloudinaryWidget;
	}

	interface CloudinaryWindow extends Window {
		cloudinary?: CloudinaryGlobal;
	}

	let { onUpload }: { onUpload: (publicId: string) => void } = $props();
	let widget: CloudinaryWidget | null = null;
	let error: string | null = $state(null);

	function getCloudinaryWindow() {
		return window as CloudinaryWindow;
	}

	onMount(async () => {
		if (typeof getCloudinaryWindow().cloudinary === 'undefined') {
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

		const cloudinary = getCloudinaryWindow().cloudinary;
		if (!cloudinary) {
			error = 'Cloudinary widget failed to initialize';
			return;
		}

		widget = cloudinary.createUploadWidget(
			{
				cloudName: PUBLIC_CLOUDINARY_CLOUD_NAME || 'demo',
				uploadPreset: PUBLIC_CLOUDINARY_UPLOAD_PRESET || 'ml_default', // Fallback preset
				sources: ['local', 'url'],
				multiple: false,
				resourceType: 'image',
				folder: 'airel' // Optional folder
			},
			(error: unknown, result: CloudinaryUploadResult) => {
				if (!error && result && result.event === 'success') {
					console.log('Done! Here is the image info: ', result.info);
					if (result.info?.public_id) {
						onUpload(result.info.public_id);
					}
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
	class="panel-border text-industrial-amber flex min-h-11 w-full cursor-pointer items-center justify-center gap-2 bg-slate-900/50 px-4 py-2 font-mono text-sm transition-colors hover:bg-slate-800/80 sm:w-auto"
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

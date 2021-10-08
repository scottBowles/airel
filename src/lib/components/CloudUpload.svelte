<script lang="typescript">
	import { onMount } from 'svelte';

	export let handleUploadResponse;
	let uploadWidget;
	let openWidget;

	onMount(() => {
		uploadWidget = window?.cloudinary?.createUploadWidget(
			{
				cloudName: 'scottBowles',
				uploadPreset: 'ubste3oi'
			},
			handleUploadResponse
		);

		openWidget = () => uploadWidget && uploadWidget.open();
	});
</script>

<span on:click={openWidget}>
	<slot>this is a slot for a component which will open the cloudinary upload widget on click</slot>
</span>

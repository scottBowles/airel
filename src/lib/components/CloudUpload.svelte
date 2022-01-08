<script lang="ts">
	export let handleUploadResponse;
	let uploadWidget;

	function initializeCloudinaryWidget() {
		uploadWidget = window?.cloudinary?.createUploadWidget(
			{
				cloudName: 'scottBowles',
				uploadPreset: 'ubste3oi'
			},
			handleUploadResponse
		);
	}

	function openWidget() {
		uploadWidget.open();
	}
</script>

<svelte:head>
	<script
		src="https://upload-widget.cloudinary.com/global/all.js"
		type="text/javascript"
		async
		on:load={initializeCloudinaryWidget}></script>
</svelte:head>

<span on:click={openWidget}>
	<slot
		>this is a slot for a component which will open the cloudinary upload widget
		on click</slot
	>
</span>

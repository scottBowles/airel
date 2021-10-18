<script lang="ts">
	import CloudUpload from '$lib/components/CloudUpload.svelte';

	let handleUploadResponse = (error, response: { event: string; info: { public_id: string } }) => {
		if (error) {
			console.error(error);
		} else {
			if (response.event === 'success') {
				// save public_id to database and use it to display image
				console.log(response.info.public_id);
			}
		}
	};
</script>

<CloudUpload {handleUploadResponse}><p>Click this to open upload widget</p></CloudUpload>
<img
	src={'https://res.cloudinary.com/scottBowles/image/upload/w_100,h_100,c_thumb,g_faces,f_auto/dnd/wqtwgehqwfcvzxjg8pdu.jpg'}
	alt="please work"
/>

<script lang="ts">
	import { Cloudinary } from '@cloudinary/url-gen';
	import { fill, limitFit, fit } from '@cloudinary/url-gen/actions/resize';
	import { format, quality } from '@cloudinary/url-gen/actions/delivery';
	import { auto } from '@cloudinary/url-gen/qualifiers/format';
	import { auto as qAuto } from '@cloudinary/url-gen/qualifiers/quality';
	import { PUBLIC_CLOUDINARY_CLOUD_NAME } from '$env/static/public';

	let {
		id,
		alt,
		width = 800,
		height = 600,
		mode = 'fill',
		class: className = ''
	}: {
		id: string;
		alt: string;
		width?: number;
		height?: number;
		mode?: 'fill' | 'limit' | 'fit';
		class?: string;
	} = $props();

	// Create a Cloudinary instance and set your cloud name.
	const cld = new Cloudinary({
		cloud: {
			cloudName: PUBLIC_CLOUDINARY_CLOUD_NAME || 'demo' // Fallback to demo if not set
		}
	});

	const url = $derived.by(() => {
		// Instantiate a CloudinaryImage object for the image with the public ID.
		const myImage = cld.image(id);

		// Resize based on mode
		if (mode === 'limit') {
			myImage.resize(limitFit().width(width).height(height));
		} else if (mode === 'fit') {
			myImage.resize(fit().width(width).height(height));
		} else {
			// Default to fill
			myImage.resize(fill().width(width).height(height));
		}

		// Optimize delivery by resizing and applying auto-format and auto-quality
		myImage.delivery(format(auto()));
		myImage.delivery(quality(qAuto()));

		return myImage.toURL();
	});
</script>

<img src={url} {alt} {width} {height} class={className} />

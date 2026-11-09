import { Cloudinary } from '@cloudinary/url-gen';
import { fill, scale } from '@cloudinary/url-gen/actions/resize';
import { autoGravity } from '@cloudinary/url-gen/qualifiers/gravity';
import { env } from '$env/dynamic/public';

let cld: Cloudinary | null = null;

function getCloudinary() {
	if (!cld) {
		cld = new Cloudinary({
			cloud: { cloudName: env.PUBLIC_CLOUDINARY_CLOUD_NAME },
			// The SDK's `_a` analytics param encodes the runtime (Node on the server, the
			// browser on the client), so URLs differed between SSR and hydration and Svelte
			// warned `hydration_attribute_changed` on every <img src>. See #62.
			url: { analytics: false }
		});
	}
	return cld;
}

export function cloudinaryUrl(
	publicId: string,
	options?: { width?: number; height?: number; crop?: 'fill' | 'fit' }
): string {
	const img = getCloudinary().image(publicId);
	if (options?.width || options?.height) {
		const mode = options.crop ?? 'fill';
		const resize = mode === 'fit' ? scale() : fill().gravity(autoGravity());
		if (options.width) resize.width(options.width);
		if (options.height) resize.height(options.height);
		img.resize(resize);
	}
	return img.toURL();
}

// Where the planets' maps and pins are served from. The app serves them at /system (from
// web/static/system); a standalone build of the system view sets its own folder before mounting.
export const assets = { root: '/system' };

/** Which size of a body's maps to load: full (4096 wide), mid (2048, made for phones) or far (512). */
export type MapSize = 'full' | 'mid' | 'far';

export const mapUrl = (slug: string, file: string, size: MapSize = 'full') =>
	`${assets.root}/${slug}/${size === 'full' ? '' : size + '/'}${file}`;

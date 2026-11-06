import { load_Me } from '$houdini';
import type { LayoutLoad } from './$types';

export const _houdini_session = true;

export const load: LayoutLoad = async (event) => {
	return {
		...(await load_Me({ event }))
	};
};

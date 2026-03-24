import { load_PlaceDetail } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	return {
		...(await load_PlaceDetail({ event, variables: { id: event.params.id } }))
	};
};

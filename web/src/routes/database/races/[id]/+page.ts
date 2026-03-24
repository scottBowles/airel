import { load_RaceDetail } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	return {
		...(await load_RaceDetail({ event, variables: { id: event.params.id } }))
	};
};

import { load_ItemDetail } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	return {
		...(await load_ItemDetail({ event, variables: { id: event.params.id } }))
	};
};

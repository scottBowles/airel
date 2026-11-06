import { load_GameLogDetail } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	return {
		...(await load_GameLogDetail({
			event,
			variables: { id: event.params.id }
		}))
	};
};

import { load_ChatSessionDetail } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	return {
		...(await load_ChatSessionDetail({ event, variables: { id: event.params.id } }))
	};
};

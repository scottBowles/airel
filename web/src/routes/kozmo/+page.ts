import { load_ChatSessionList } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	return {
		...(await load_ChatSessionList({ event, variables: { first: 50 } }))
	};
};

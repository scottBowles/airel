import { load_GameLogList } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	return {
		...(await load_GameLogList({
			event,
			variables: {
				first: 50,
				order: { gameDate: 'DESC' }
			}
		}))
	};
};

import { load_CharacterDetail } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	return {
		...(await load_CharacterDetail({ event, variables: { id: event.params.id } }))
	};
};

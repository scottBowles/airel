import { load_CharacterDetail, load_EntityEditorOptions } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	const { id } = event.params;
	return {
		...(await load_CharacterDetail({ event, variables: { id } })),
		...(await load_EntityEditorOptions({ event }))
	};
};

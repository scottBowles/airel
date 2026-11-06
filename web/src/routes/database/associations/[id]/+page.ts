import { load_AssociationDetail } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	return {
		...(await load_AssociationDetail({ event, variables: { id: event.params.id } }))
	};
};

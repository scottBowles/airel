import { load_AssociationDetail } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	const { id } = event.params;
	return {
		...(await load_AssociationDetail({ event, variables: { id } }))
	};
};

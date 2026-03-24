import { load_LogDetail, load_LogEditorOptions } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	const { id } = event.params;
	const [logDetail, logEditorOptions] = await Promise.all([
		load_LogDetail({ event, variables: { id } }),
		load_LogEditorOptions({ event })
	]);

	return {
		...logDetail,
		...logEditorOptions
	};
};

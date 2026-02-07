import type { LayoutServerLoad } from './$types';

export const _houdini_session = true;

export const load: LayoutServerLoad = async ({ locals }) => {
	return {
		user: locals.user,
		token: locals.token
	};
};

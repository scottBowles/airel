import * as api from '$lib/api.js';

export async function get(request) {
	const res = await api.get('auth/users/me/', request.locals.token);
	return res;
}

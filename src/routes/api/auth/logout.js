import * as api from '$lib/api.js';

export async function post(request) {
	await api.post('/auth/token/logout/');

	return {
		headers: {
			'set-cookie':
				'token=deleted; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
		},
		body: {
			ok: true
		}
	};
}

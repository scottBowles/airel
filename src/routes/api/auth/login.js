import * as api from '$lib/api.js';

export async function post(request) {
	const res = await api.post('auth/token/login/', {
		username: request.body.username,
		password: request.body.password
	});

	if (!res.ok) {
		return { status: res.status, body: res.body, headers: res.headers };
	}

	return {
		status: res.status,
		body: res.body,
		headers: {
			'set-cookie': `token=${res.body.auth_token}; Path=/; HttpOnly`
		}
	};
}

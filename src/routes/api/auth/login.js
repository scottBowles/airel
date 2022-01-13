import api from '$lib/api.js';

export async function post(request) {
	const res = await api.post('auth/token/login/', {
		username: request.body.username,
		password: request.body.password
	});
	const json = await res.json();

	if (!res.ok) {
		return { status: res.status, body: json, headers: res.headers };
	}

	return {
		status: res.status,
		body: json,
		headers: {
			'set-cookie': `token=${json.auth_token}; Path=/; HttpOnly`
		}
	};
}

import * as api from '$lib/api.js';
import { post as login } from './login';

export async function post(request) {
	await api.post('/auth/users/', {
		username: request.body.username,
		password: request.body.password,
		re_password: request.body.re_password
	});

	return login(request);
}

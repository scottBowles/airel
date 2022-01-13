import { API_ROOT } from './constants';

function addSlashesIfNeeded(endpoint) {
	if (!endpoint.startsWith('/')) {
		endpoint = '/' + endpoint;
	}
	const qIndex = endpoint.indexOf('?');
	if (!endpoint.endsWith('/') && qIndex === -1) {
		endpoint = endpoint + '/';
	}
	if (qIndex !== -1 && !endpoint[qIndex - 1].startsWith('/')) {
		endpoint = endpoint.substring(0, qIndex) + '/' + endpoint.substring(qIndex);
	}
	return endpoint;
}

// function getDefaultHeaders(token) {
// 	const headers = new Headers();
// 	headers.append('Content-Type', 'application/json');
// 	if (token) {
// 		headers.append('Authorization', `Token ${token}`);
// 	}
// 	return headers;
// }

// async function registerUser({ username, password, re_password }) {
// 	const res = await fetch(`${API_ROOT}/auth/users/`, {
// 		method: 'POST',
// 		headers: { 'Content-Type': 'application/json' },
// 		body: JSON.stringify({ username, password, re_password })
// 	});
// 	// TODO: pass on error from bad response
// 	if (!res.ok) throw new Error('Registration failed');
// 	return login({ username, password });
// }

// async function login({ username, password }) {
// 	const res = await fetch(`${API_ROOT}/auth/token/login/`, {
// 		method: 'POST',
// 		headers: { 'Content-Type': 'application/json' },
// 		body: JSON.stringify({ username, password })
// 	});
// 	const { auth_token, error } = await res.json();
// 	// TODO: what is the shape of the error? `new Error` expects a string
// 	if (!res.ok) throw new Error(error);
// 	setToken(auth_token);

// 	// TODO: surely the user needs to be parsed?
// 	const user = await fetch('/users/me/', {
// 		method: 'POST',
// 		headers: getDefaultHeaders(auth_token)
// 	});
// 	localStorage.setItem('user', JSON.stringify(user));
// 	return user;
// }

// async function logout({ redirect }) {
// 	redirect = redirect || '/login';
// 	await fetch(`${API_ROOT}/token/logout/`, {
// 		method: 'POST'
// 	});
// 	removeToken();
// 	if (redirect) window.location.href = redirect;
// }

/** customFetch is here so load functions can pass their fetch function */
async function send({ method, path, data, token, customFetch = fetch }) {
	const endpoint = API_ROOT + addSlashesIfNeeded(path);

	const opts = { method, headers: { 'Content-Type': 'application/json' } };
	if (data) opts.body = JSON.stringify(data);
	if (token) opts.headers.Authorization = `Token ${token}`;

	const res = await customFetch(endpoint, opts);
	return res;
}

function get(path, token, customFetch) {
	return send({ method: 'GET', path, token, customFetch });
}

function del(path, token, customFetch) {
	return send({ method: 'DELETE', path, token, customFetch });
}

function post(path, data, token, customFetch) {
	return send({ method: 'POST', path, data, token, customFetch });
}

function put(path, data, token, customFetch) {
	return send({ method: 'PUT', path, data, token, customFetch });
}

function patch(path, data, token, customFetch) {
	return send({ method: 'PATCH', path, data, token, customFetch });
}

export default { get, del, post, put, patch };

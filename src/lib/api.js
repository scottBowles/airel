import { API_ROOT } from './constants';
import browserStorage from './browserStorage';

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

// function isLoggedIn() {
// 	return !!getToken();
// }

async function send({ method, path, data, token }) {
	token = token || (await browserStorage.getToken()); // if running from an endpoint, get the token from request.locals.token, defined in the handle hook
	const endpoint = API_ROOT + addSlashesIfNeeded(path);
	const opts = { method, headers: {} };

	if (data) {
		opts.headers['Content-Type'] = 'application/json';
		opts.body = JSON.stringify(data);
	}

	if (token) {
		opts.headers.Authorization = `Token ${token}`;
	}

	const res = await fetch(endpoint, opts);
	const json = await res.json();
	return { status: res.status, body: json, ok: res.ok };

	// return (
	// 	fetch(endpoint, opts)
	// 		// TODO: pass on error from bad response? pass on status code? pass on headers?
	// 		.then((res) => {
	// 			if (!res.ok)
	// 			console.log({ res, status: res.status, ok: res.ok, error: res.error });
	// 			return res.json();
	// 		})
	// 		.then((json) => {
	// 			console.log({ json });
	// 			try {
	// 				console.log('trying to parse json', json);
	// 				return JSON.parse(json);
	// 			} catch (err) {
	// 				console.log("couldn't parse json", json);
	// 				return json;
	// 			}
	// 		})
	// );
}

function get(path, token) {
	return send({ method: 'GET', path, token });
}

function del(path, token) {
	return send({ method: 'DELETE', path, token });
}

function post(path, data, token) {
	return send({ method: 'POST', path, data, token });
}

function put(path, data, token) {
	return send({ method: 'PUT', path, data, token });
}

function patch(path, data, token) {
	return send({ method: 'PATCH', path, data, token });
}

export default { get, del, post, put, patch };

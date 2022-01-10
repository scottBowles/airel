// import { API_ROOT } from '$lib/constants';

// function setToken(token) {
// 	localStorage.setItem('token', token);
// }

// function getToken() {
// 	return localStorage.getItem('token');
// }

// function removeToken() {
// 	localStorage.removeItem('token');
// }

// function getDefaultHeaders(token) {
// 	token = token || getToken();
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

// export { getDefaultHeaders, registerUser, login, logout, isLoggedIn };

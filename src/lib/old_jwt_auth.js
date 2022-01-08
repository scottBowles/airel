import jwt_decode from 'jwt-decode';
import { API_ROOT } from '$lib/constants';

const REFRESH_JWT_URL = `${API_ROOT}/auth/jwt/refresh`;

// checks whether jwt is expired, erring toward yes to ensure
// jwt is refreshed rather than resulting in a bad request
function isJwtExpired(jwt) {
	const decoded = jwt_decode(jwt);
	const jwtIsExpired = decoded.exp < Date.now() / 1000 - 10;
	return jwtIsExpired;
}

function refreshJwt() {
	return fetch(REFRESH_JWT_URL, { method: 'POST' });
}

function setAccessJwt(accessJwt) {
	localStorage.setItem('accessJwt', accessJwt);
}

async function getAccessJwt() {
	console.log('fn: getAccessJwt');
	let accessJwt = localStorage.getItem('accessJwt');
	console.log('accessJwt from localStorage: ', accessJwt);
	if (!accessJwt) throw new Error('No access token');
	if (isJwtExpired(accessJwt)) {
		console.log('access token is expired');
		accessJwt = await refreshToken();
		console.log('accessJwt from refreshToken: ', accessJwt);
	}
	return accessJwt;
}

function setRefreshJwt(refreshJwt) {
	localStorage.setItem('refreshJwt', refreshJwt);
}

function getRefreshJwt() {
	return localStorage.getItem('refreshJwt');
}

function removeJwtTokens() {
	localStorage.removeItem('accessJwt');
	localStorage.removeItem('refreshJwt');
}

async function refreshToken() {
	console.log('fn: refreshToken');
	const refreshJwt = getRefreshJwt();
	if (!refreshJwt) throw new Error('No refresh token');

	const headers = getDefaultHeaders();

	const res = await fetch(REFRESH_JWT_URL, {
		method: 'POST',
		headers,
		body: JSON.stringify({ refresh: refreshJwt })
	});
	// TODO: allow 500 and notify the user that they are offline
	if (res.status !== 200) throw new Error('Refresh token failed');
	const { access, refresh } = await res.json();
	setAccessJwt(access);
	setRefreshJwt(refresh);
	return access;
}

function getDefaultHeaders() {
	const headers = new Headers();
	headers.append('Content-Type', 'application/json');
	return headers;
}

async function login({ username, password }) {
	const res = await fetch(`${API_ROOT}/auth/jwt/create`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ username, password })
	});
	const tokens = await res.json();
	if (!res.ok) throw new Error(tokens.error);
	setAccessJwt(tokens.access);
	setRefreshJwt(tokens.refresh);
	const user = await fetch('/users/me', {
		method: 'POST',
		headers: getDefaultHeaders(tokens.access)
	});
	localStorage.setItem('user', JSON.stringify(user));
	return user;
}

function logout({ redirect } = {}) {
	redirect = redirect || '/login';

	removeJwtTokens();
	if (redirect) window.location.href = redirect;
}

export {
	isJwtExpired,
	refreshJwt,
	getAccessJwt,
	removeJwtTokens,
	setAccessJwt,
	setRefreshJwt,
	getDefaultHeaders,
	login,
	logout
};

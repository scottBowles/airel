import jwt_decode from 'jwt-decode';

const ROOT_URL = 'http://127.0.0.1:8000';
const REFRESH_JWT_URL = `${ROOT_URL}/auth/jwt/refresh`;

function isJwtExpired(jwt) {
	console.log({ jwt });
	const decoded = jwt_decode(jwt);
	const jwtIsExpired = decoded.exp < Date.now() / 1000;
	return jwtIsExpired;
}

async function getAccessJwt() {
	console.log('fn: getAccessJwt');
	let accessJwt = localStorage.getItem('accessJwt');
	console.log("accessJwt from localStorage: ", accessJwt);
	if (!accessJwt) throw new Error('No access token');
	if (isJwtExpired(accessJwt)) {
		console.log('access token is expired');
		accessJwt = await refreshToken();
		console.log("accessJwt from refreshToken: ", accessJwt);
	}
	return accessJwt;
}

async function refreshToken() {
	console.log('fn: refreshToken');
	const refreshJwt = localStorage.getItem('refreshJwt');
	if (!refreshJwt) throw new Error('No refresh token');

	const headers = getDefaultHeaders();

	const res = await fetch(REFRESH_JWT_URL, { 
		method: 'POST', 
		headers,
		body: JSON.stringify({ refresh: refreshJwt })
});
	// TODO: allow 500 and notify the user that they are offline
	if (res.status !== 200) throw new Error('Refresh token failed');
	const { access } = await res.json();
	setAccessJwt(access);
	return access;
}

function removeJwtTokens() {
	localStorage.removeItem('accessJwt');
	localStorage.removeItem('refreshJwt');
}

function setAccessJwt(accessJwt) {
	localStorage.setItem('accessJwt', accessJwt);
}

function setRefreshJwt(refreshJwt) {
	localStorage.setItem('refreshJwt', refreshJwt);
}

function getDefaultHeaders(accessJwt) {
	const headers = new Headers();
	headers.append('Content-Type', 'application/json');
	if (accessJwt) {
		headers.append('Authorization', `JWT ${accessJwt}`);
	}
	return headers;
}

async function login({ username, password }) {
	const res = await fetch('http://127.0.0.1:8000/auth/jwt/create', {
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

// type LogoutArgs = { redirect: string };

function logout({ redirect } = {}) {
	redirect = redirect || '/login';

	removeJwtTokens();
	if (redirect) window.location.href = redirect;
}

export {
	getAccessJwt,
	removeJwtTokens,
	setAccessJwt,
	setRefreshJwt,
	getDefaultHeaders,
	login,
	logout
};

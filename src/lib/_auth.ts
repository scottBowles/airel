// import jwt_decode from 'jwt-decode';
import { API_ROOT } from '$lib/constants';

// const REFRESH_JWT_URL = `${API_ROOT}/auth/jwt/refresh`;

type LoginCredentials = {
	username: string;
	password: string;
};

type LoginResponse = {
	auth_token: string;
	error: unknown;
};

// type AccessTokenResponse = {
// 	access: string;
// 	refresh: string;
// };

// type RefreshTokenResponse = {
// 	access: string;
// 	refresh: string;
// };

type LogoutOptions = { redirect?: string };

// function isJwtExpired(jwt: string): boolean {
// 	console.log({ jwt });
// 	const decoded: { exp: number } = jwt_decode(jwt);
// 	const jwtIsExpired = decoded.exp < Date.now() / 1000;
// 	return jwtIsExpired;
// }

// function setAccessJwt(accessJwt: string): void {
// 	localStorage.setItem('accessJwt', accessJwt);
// }

function setToken(token: string): void {
	localStorage.setItem('token', token);
}

function getToken(): string | null {
	return localStorage.getItem('token');
}

function removeToken(): void {
	localStorage.removeItem('token');
}

// async function getAccessJwt(): Promise<string> {
// 	console.log('fn: getAccessJwt');
// 	let accessJwt = localStorage.getItem('accessJwt');
// 	console.log('accessJwt from localStorage: ', accessJwt);
// 	if (!accessJwt) throw new Error('No access token');
// 	if (isJwtExpired(accessJwt)) {
// 		console.log('access token is expired');
// 		accessJwt = await refreshToken();
// 		console.log('accessJwt from refreshToken: ', accessJwt);
// 	}
// 	return accessJwt;
// }

// function setRefreshJwt(refreshJwt: string): void {
// 	localStorage.setItem('refreshJwt', refreshJwt);
// }

// function getRefreshJwt(): string | null {
// 	return localStorage.getItem('refreshJwt');
// }

// function removeJwtTokens(): void {
// 	localStorage.removeItem('accessJwt');
// 	localStorage.removeItem('refreshJwt');
// }

// async function refreshToken(): Promise<string> {
// 	console.log('fn: refreshToken');
// 	const refreshJwt = getRefreshJwt();
// 	if (!refreshJwt) throw new Error('No refresh token');

// 	const headers = getDefaultHeaders();

// 	const res = await fetch(REFRESH_JWT_URL, {
// 		method: 'POST',
// 		headers,
// 		body: JSON.stringify({ refresh: refreshJwt })
// 	});
// 	// TODO: allow 500 and notify the user that they are offline
// 	if (res.status !== 200) throw new Error('Refresh token failed');
// 	const { access, refresh }: RefreshTokenResponse = await res.json();
// 	setAccessJwt(access);
// 	setRefreshJwt(refresh);
// 	return access;
// }

function getDefaultHeaders(token: string): Headers {
	token = token || getToken();
	const headers = new Headers();
	headers.append('Content-Type', 'application/json');
	if (token) {
		headers.append('Authorization', `Token ${token}`);
	}
	return headers;
}

async function registerUser({
	username,
	password
}: LoginCredentials): Promise<Response> {
	const res = await fetch(`${API_ROOT}/auth/users/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ username, password })
	});
	if (!res.ok) throw new Error('Registration failed');
	return login({ username, password });
}

async function login({
	username,
	password
}: LoginCredentials): Promise<Response> {
	const res = await fetch(`${API_ROOT}/auth/token/login/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ username, password })
	});
	const { auth_token, error }: LoginResponse = await res.json();
	// TODO: what is the shape of the error? `new Error` expects a string
	if (!res.ok) throw new Error(error);
	// if (!res.ok) throw new Error(error);
	setToken(auth_token);
	// setAccessJwt(tokens.access);
	// setRefreshJwt(tokens.refresh);

	// TODO: surely the user needs to be parsed?
	const user = await fetch('/users/me/', {
		method: 'POST',
		headers: getDefaultHeaders(auth_token)
	});
	localStorage.setItem('user', JSON.stringify(user));
	return user;
}

// function logout({ redirect }: LogoutOptions = {}): void {
// 	redirect = redirect || '/login';

// 	removeJwtTokens();
// 	if (redirect) window.location.href = redirect;
// }

async function logout({ redirect }: LogoutOptions = {}): Promise<void> {
	redirect = redirect || '/login';
	await fetch(`${API_ROOT}/token/logout/`, {
		method: 'POST'
	});
	removeToken();
	if (redirect) window.location.href = redirect;
}

export {
	// getAccessJwt,
	// removeJwtTokens,
	// setAccessJwt,
	// setRefreshJwt,
	getDefaultHeaders,
	registerUser,
	login,
	logout
};

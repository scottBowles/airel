import jwt_decode from 'jwt-decode';

const ROOT_URL = 'http://127.0.0.1:8000';
const REFRESH_JWT_URL = `${ROOT_URL}/auth/jwt/refresh`;

type LoginCredentials = {
	username: string,
	password: string
};

type AccessTokenResponse = {
	access: string,
	refresh: string
};

type RefreshTokenResponse = {
	access: string,
	refresh: string
};

type LogoutOptions = { redirect?: string };

function isJwtExpired(jwt: string): boolean {
	console.log({ jwt });
	const decoded = jwt_decode(jwt);
	const jwtIsExpired = decoded.exp < Date.now() / 1000;
	return jwtIsExpired;
}

function setAccessJwt(accessJwt: string): void {
	localStorage.setItem('accessJwt', accessJwt);
}

async function getAccessJwt(): Promise<string> {
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

function setRefreshJwt(refreshJwt: string): void {
	localStorage.setItem('refreshJwt', refreshJwt);
}

function getRefreshJwt(): string | null {
	return localStorage.getItem('refreshJwt');
}

function removeJwtTokens(): void {
	localStorage.removeItem('accessJwt');
	localStorage.removeItem('refreshJwt');
}

async function refreshToken(): Promise<string> {
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
	const { access, refresh }: RefreshTokenResponse = await res.json();
	setAccessJwt(access);
	setRefreshJwt(refresh);
	return access;
}

function getDefaultHeaders(accessJwt: string): Headers {
	const headers = new Headers();
	headers.append('Content-Type', 'application/json');
	if (accessJwt) {
		headers.append('Authorization', `JWT ${accessJwt}`);
	}
	return headers;
}

async function login({
	username,
	password
}: LoginCredentials): Promise<Response> {
	const res = await fetch('http://127.0.0.1:8000/auth/jwt/create', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ username, password })
	});
	const tokens: AccessTokenResponse = await res.json();
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

function logout({ redirect }: LogoutOptions = {}): void {
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

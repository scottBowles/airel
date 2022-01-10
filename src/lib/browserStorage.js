export async function getToken() {
	const { browser } = await import('$app/env');
	if (browser) {
		const localForage = await import('localforage');
		return localForage?.getItem('token');
	}
	return null;
}

export async function setToken(token) {
	const { browser } = await import('$app/env');
	if (browser) {
		const localForage = await import('localforage');
		return localForage?.setItem('token', token);
	}
	return null;
}

export async function removeToken() {
	return setToken(null);
}

export default {
	getToken,
	setToken,
	removeToken
};

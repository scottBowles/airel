import { browser } from '$app/env';
import localForage from 'localforage';

export async function getToken() {
	if (browser) {
		return localForage?.getItem('token');
	}
	return null;
}

export async function setToken(token) {
	if (browser) {
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

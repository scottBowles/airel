import { browser } from '$app/env';
import { writable } from 'svelte/store';
import { getAccessJwt, getDefaultHeaders, logout } from '$lib/utils/auth.js';

export default function <Readonly extends boolean>({
	initial = {},
	listPath = '',
	detailPath = (id) => `${listPath}/${id}`,
	readonly = true
}) {
	// create the underlying store
	const store = writable(initial || { loading: {}, errors: {} });

	// before render, set loading to true and return the readonly store
	if (!browser) {
		store.update((data) => ({ ...data, loading: { list: true }, errors: {} }));
		return { subscribe: store.subscribe };
	}

	// url utils
	const ROOT_URL = 'http://127.0.0.1:8000';
	const normalizeUrl = (url) =>
		url.startsWith('http') ? url : url.startsWith('/') ? `${ROOT_URL}${url}` : `${ROOT_URL}/${url}`;

	// define a request function that will do `fetch` and update store when request finishes
	const request = async (method = 'GET', { url = listPath, params = null, id }) => {
		console.log('Request: ', { method, url, params });
		// prefix with ROOT_URL if it doesn't start with `http` and add trailing slash if needed
		url = normalizeUrl(url);

		// before we fetch, clear out previous errors for the relevant query and set loading to true
		store.update((state) => {
			state.errors = id ? { [id]: null } : {};
			state.loading = id ? { ...state.loading, [id]: true } : { ...state.loading, list: true };

			return state;
		});

		// get the access token
		let accessJwt;
		try {
			accessJwt = await getAccessJwt();
		} catch (e) {
			store.update((state) => {
				state.loading = id ? { ...state.loading, [id]: false } : { ...state.loading, list: false };
				state.errors = id
					? { ...state.errors, [id]: e.message }
					: { ...state.errors, list: e.message };
				return state;
			});
			logout();
		}

		// define headers and body
		const headers = getDefaultHeaders(accessJwt);
		const body = params ? JSON.stringify(params) : undefined;

		// execute fetch
		console.log('Fetching: ', { method, url, body, headers });
		const response = await fetch(url, { method, body, headers });
		// pull out json body
		const json = await response.json();

		// if response is 2xx
		if (response.ok) {
			// update the store
			store.update((state) => {
				if (id) {
					state.loading = { ...state.loading, [id]: false };
					state.errors = { ...state.errors, [id]: null };
					state.data = { ...state.data, [id]: json };
				} else {
					state.loading = { list: false };
					state.errors = { list: null };
					state.data = json;
				}
				return state;
			});
		} else {
			// response failed, set `errors` and clear `loading` flag
			store.update((state) => {
				state.loading = id ? { ...state.loading, [id]: false } : { ...state.loading, list: false };
				state.errors = id
					? { ...state.errors, [id]: json.message }
					: { ...state.errors, list: json.message };
				return state;
			});
		}
	};

	// convenience wrappers for http requests

	const getList = () => request('GET', { url: listPath });

	const postToList = (params: Record<string, unknown>) =>
		request('POST', { url: listPath, params });

	const getDetail = (id) => request('GET', { id, url: detailPath(id) });

	const patchDetail = (id: string, params: Record<string, unknown>) =>
		request('PATCH', { id, url: detailPath(id), params });

	const deleteDetail = (id: string, params: Record<string, unknown>) => {
		request('DELETE', { id, url: detailPath(id), params });
	};

	// return the customized store
	const { set, update } = store;
	const httpMethods = { getList, postToList, getDetail, patchDetail, deleteDetail };
	const readonlyMethods = { subscribe: store.subscribe, ...httpMethods };
	const writableMethods = { set, update };

	return readonly ? readonlyMethods : { ...readonlyMethods, ...writableMethods };
}

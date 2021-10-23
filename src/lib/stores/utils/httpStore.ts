import jwt_decode from 'jwt-decode';
import { writable } from 'svelte/store';
import { getAccessJwt, getDefaultHeaders, logout } from '$lib/utils/auth.js';

interface HttpMethods {
	get: (url: string) => Promise<void>;
	post: ({ url: string, params: any }) => Promise<void>;
	patch: ({ url: string, params: any }) => Promise<void>;
	delete: ({ url: string, params: any }) => Promise<void>;
}

// IMPORTING THIS STUFF SEEMS TO BREAK IT
// interface ReadonlyMethods {
// 	subscribe(this: void, run: Subscriber<any>, invalidate?: any): Unsubscriber;
// }

// interface WritableMethods {
// 	subscribe(this: void, run: Subscriber<any>, invalidate?: any): Unsubscriber;
// 	set(this: void, value: unknown): void;
// 	update(this: void, updater: Updater<any>): void;
// }

// returns a store with HTTP access functions for get, post, patch, delete
// anytime an HTTP request is made, the store is updated and all subscribers are notified.
export default function <Readonly extends boolean>(
	initial = {},
	defaultPath = '',
	readonly: Readonly | true = true,
	getDataFromJson = (json) => json[0]
) {
	// create the underlying store
	const store = writable(initial || {});

	const ROOT_URL = 'http://127.0.0.1:8000';

	const normalizeUrl = (url) =>
		url.startsWith('http') ? url : url.startsWith('/') ? `${ROOT_URL}${url}` : `${ROOT_URL}/${url}`;

	// define a request function that will do `fetch` and update store when request finishes
	store.request = async (method, url = defaultPath, params = null) => {
		console.log('Request: ', { method, url, params });
		// prefix with ROOT_URL if it doesn't start with `http` and add trailing slash if needed
		url = normalizeUrl(url);

		// before we fetch, clear out previous errors and set `loading` to `true`
		store.update((data) => {
			console.log({ data });
			delete data.errors;
			data.loading = true;

			return data;
		});

		// get the access token
		let accessJwt;
		try {
			accessJwt = await getAccessJwt();
		} catch (e) {
			store.update((data) => {
				data.loading = false;
				data.errors = [e.message];
				return data;
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
			// update the store, which will cause subscribers to be notified
			// add the decoded jwt to locals
			const currentUser = localStorage.getItem('user') || jwt_decode(accessJwt);
			const data = getDataFromJson(json);
			store.set(data);
			// store.set({ ...json, locals: { user } });
		} else {
			// response failed, set `errors` and clear `loading` flag
			store.update((data) => {
				data.loading = false;
				data.errors = json.errors;
				return data;
			});
		}
	};

	// convenience wrappers for get, post, patch, and delete

	const get = (url: string = defaultPath) => store.request('GET', url);
	const post = ({ url, params }: { url: string; params: Record<string, unknown> }) =>
		store.request('POST', url, params);
	const patch = ({ url, params }: { url: string; params: Record<string, unknown> }) =>
		store.request('PATCH', url, params);
	const del = ({ url, params }: { url: string; params: Record<string, unknown> }) =>
		store.request('DELETE', url, params);

	// return the customized store
	const { subscribe, set, update } = store;
	const httpMethods = { get, post, patch, del };
	const readonlyMethods = { subscribe, ...httpMethods };
	const writableMethods = { set, update };

	return readonly ? { ...readonlyMethods } : { ...readonlyMethods, writableMethods };
}

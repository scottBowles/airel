import { API_ROOT } from '$lib/constants';
import { getDefaultHeaders } from '/auth';

export async function get() {
	const headers = getDefaultHeaders();
	const res = await fetch(`${API_ROOT}/characters`, { headers });
	const json = await res.json();
	console.log({ res, json });
	return {
		status: json.status,
		body: json.body
	};
}

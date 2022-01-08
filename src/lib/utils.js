export function get(endpoint, data) {
	return fetch(endpoint, {
		method: 'GET',
		credentials: 'include',
		headers: {
			'Content-Type': 'application/json'
		}
	});
}

export function post(endpoint, data) {
	return fetch(endpoint, {
		method: 'POST',
		credentials: 'include',
		body: JSON.stringify(data || {}),
		headers: {
			'Content-Type': 'application/json'
		}
	});
}

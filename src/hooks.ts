import * as cookie from 'cookie';
import { PUBLIC_PAGES } from '$lib/constants';

export async function handle({ request, resolve }) {
	const cookies = cookie.parse(request.headers.cookie || '');
	const { token } = cookies;

	request.locals.token = token;
	request.locals.isLoggedIn = !!token;

	if (
		!request.locals.isLoggedIn &&
		!PUBLIC_PAGES.includes(request.path) &&
		!request.path.startsWith('/api')
	) {
		// what else should we do to log the user out? remove user from session?
		return {
			status: 301,
			headers: {
				location: '/login'
			}
		};
	}

	return resolve(request);
}

export function getSession(request) {
	const { isLoggedIn, token } = request.locals;
	return { isLoggedIn, token };
}

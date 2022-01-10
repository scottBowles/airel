import * as cookie from 'cookie';
import { PUBLIC_PAGES } from '$lib/constants';

export async function handle({ request, resolve }) {
	const cookies = cookie.parse(request.headers.cookie || '');
	const authHeader = request.headers.authorization || '';
	const token = authHeader.split(' ')[1] || cookies.token;

	request.locals.token = token;
	request.locals.isLoggedIn = !!token;

	// TODO: is there reason to resolve here rather than immediately returning if
	// the user isn't logged in and we want to redirect? Is this how we want to handle
	// this anyway?
	const response = await resolve(request);

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

	return response;
}

export function getSession(request) {
	const { isLoggedIn, token } = request.locals;
	return { isLoggedIn, token };
}

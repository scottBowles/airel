import * as cookie from 'cookie';
import { PUBLIC_PAGES } from '$lib/constants';

export async function handle({ request, resolve }) {
	const cookies = cookie.parse(request.headers.cookie || '');
	const token = cookies.token;
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

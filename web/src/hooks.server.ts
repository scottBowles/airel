import type { Handle } from '@sveltejs/kit';
import { decodeJwt, refreshAuthToken, setAuthCookies } from '$lib/server/auth';
import { setSession } from '$houdini';

export const handle: Handle = async ({ event, resolve }) => {
	const accessToken = event.cookies.get('access_token');
	const refreshToken = event.cookies.get('refresh_token');

	let token = accessToken;
	let payload = accessToken ? decodeJwt(accessToken) : null;

	// Check expiration
	// payload.exp is usually in seconds. Date.now() is ms.
	if (payload && payload.exp * 1000 < Date.now()) {
		payload = null; // Expired
		token = undefined;
	}

	if (!token && refreshToken) {
		// Attempt refresh
		const refreshResult = await refreshAuthToken(refreshToken);
		if (refreshResult?.success) {
			token = refreshResult.token.token;
			// Update cookies for the browser
			setAuthCookies(event.cookies, token, refreshResult.refreshToken.token);
			payload = decodeJwt(token);
		}
	}

	if (token && payload) {
		event.locals.token = token;
		// Ideally we would populate event.locals.user here too,
		// but the JWT payload might only contain minimal info (username/exp).
		// If we need the full user, we would fetch it here or in layout.server.ts
		event.locals.user = {
			username: payload.username,
			id: payload.user_id || '', // Fallback or check if your JWT custom claims include it
			email: payload.email || ''
		};
		setSession(event, { token });
	} else {
		event.locals.token = null;
		event.locals.user = null;
	}

	const response = await resolve(event);

	// Fix for Google Sign-In popup communication
	response.headers.set('Cross-Origin-Opener-Policy', 'same-origin-allow-popups');

	return response;
};

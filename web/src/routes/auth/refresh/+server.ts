import { json } from '@sveltejs/kit';
import { refreshAuthToken, setAuthCookies } from '$lib/server/auth';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies }) => {
	const refreshToken = cookies.get('refresh_token');

	if (!refreshToken) {
		return json({ error: 'No refresh token' }, { status: 401 });
	}

	const result = await refreshAuthToken(refreshToken);

	if (result?.success) {
		setAuthCookies(cookies, result.token.token, result.refreshToken.token);
		return json({
			accessToken: result.token.token
		});
	}

	return json({ error: 'Refresh failed' }, { status: 401 });
};
